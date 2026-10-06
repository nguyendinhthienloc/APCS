# AI-Combine — Software Requirements & Architecture Specification

| Field | Value |
|---|---|
| Document version | 2.0 (pivot from AI-Combine) |
| Status | Approved for implementation |
| Package / CLI | `ai-combine` |
| Primary language under test | Python 3.11+ (TypeScript: AST probing only, stretch goal) |

---

## 1. Executive Summary & Problem Formulation

### 1.1 The Crisis of LLM Code Generation

Large language models produce code that is syntactically convincing, and they produce tests that are equally convincing but structurally weak. When one model writes both the implementation and its tests, the tests encode the *same assumptions* as the implementation. This is **happy-path bias**:

- Tests exercise typical inputs (`add(2, 3) == 5`) and ignore `None`, empty collections, `NaN`, negative or overflow values, surrogate Unicode, and concurrent access.
- Tests are *cooperative*: they are written to pass, not to fail.
- Coverage numbers look healthy while behavior at the boundaries is untested. A function can reach 100% line coverage and still crash on `[]`.
- Passive tools do not fix this. Mutation engines (Mutmut) measure test weakness but neither generate hostile inputs nor repair code.

### 1.2 The Adversarial Solution

AI-Combine assigns two agents **opposing loss functions** and a **deterministic referee**:

| Role | Objective | Loss function |
|---|---|---|
| Red Agent (Attacker) | Produce tests that make the target fail | `L_red = −(new failing tests)` |
| Blue Agent (Defender) | Patch the target so all tests pass without regressions | `L_blue = failing tests + λ·patch_lines + μ·regressions` |
| Sandbox Oracle (Referee) | Run `pytest` in isolation | Binary ground truth: exit code `0` or non-zero |

Because the oracle is the real interpreter, neither agent can "talk its way" to a win. A hostile test is only a valid finding if it **fails against the current code in the sandbox** and **is deterministic across 3 replays**. A patch is only valid if the full suite (old + new tests) passes.

### 1.3 Goals and Non-Goals

**Goals**

- G1. Discover semantic edge-case bugs missed by cooperative LLM-generated tests.
- G2. Produce minimal, verifiable defensive patches (unified diff).
- G3. Operate locally; usable with free-tier or local models (Gemma via Ollama, Groq, Google AI Studio).
- G4. Provide measurable evidence: mutation kill rate, branch coverage gain, bug catch rate.

**Non-Goals**

- Proving program correctness (formal verification).
- Fixing logic bugs requiring product-level requirements the code does not express.
- Executing untrusted code outside the sandbox.

### 1.4 Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Parse Python source via `ast` and emit an `ASTVulnerabilityReport` | Must |
| FR-02 | Red Agent generates pytest/Hypothesis suites from the report | Must |
| FR-03 | Sandbox runs generated tests with CPU/memory/time/network limits and captures stdout, stderr, duration, exit code | Must |
| FR-04 | Blue Agent receives trace + code and returns a minimal unified diff | Must |
| FR-05 | Regression check reruns the pre-existing and accumulated suites after every patch | Must |
| FR-06 | Duel orchestrator runs up to N rounds with termination at `K=3` stagnant rounds | Must |
| FR-07 | Generated tests are AST-linted before execution (no fork bombs, no network, no escapes) | Must |
| FR-08 | CLI `ai-combine run <file> --rounds N` | Must |
| FR-09 | Token and cost tracking per agent and per round | Should |
| FR-10 | Desktop dashboard with side-by-side duel log | Should |
| FR-11 | TypeScript AST probing | Could |

### 1.5 Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Determinism | Every accepted finding reproduces in 3/3 sandbox replays |
| NFR-02 | Isolation | No test process can read outside the work directory or open sockets |
| NFR-03 | Performance | Single sandbox execution ≤ 2.0 s hard timeout; full 3-round duel on a 100-line module ≤ 5 min with free-tier models |
| NFR-04 | Portability | Windows 10+, Ubuntu 22.04+, macOS 12+; Docker optional |
| NFR-05 | Privacy | Source code is sent only to the model endpoints the user configures; local-only mode available |
| NFR-06 | Safety | Original files are never modified without `--apply`; patches go to a copy |

---

## 2. System Architecture & The Duel Engine

### 2.1 Component Overview

```
                      +--------------------------------------------+
   target.py -------> |        STATIC AST VULNERABILITY PROBER     |
                      |  (stdlib ast; no LLM, deterministic)       |
                      +----------------------+---------------------+
                                             | ASTVulnerabilityReport
                                             v
   +----------------------+      +---------------------+      +---------------------+
   |   RED AGENT          | ---> |   TEST LINTER       | ---> |   SANDBOX ORACLE    |
   |   (Attacker)         |      |   (AST safety gate) |      |   (pytest, isolated)|
   |   Hypothesis / edge  |      +---------------------+      +----------+----------+
   +----------^-----------+                                              |
              | history of caught/uncaught                               | ExecutionTrace
              |                                                          v
   +----------+-----------+      +---------------------+      +---------------------+
   |  DUEL ORCHESTRATOR   | <--- |   SCORER            | <--- |  verdict: exit code |
   |  (rounds, budgets)   |      |   (points, K-rule)  |      +---------------------+
   +----------+-----------+      +---------------------+
              | traceback + code + AST hints
              v
   +----------------------+      +---------------------+
   |   BLUE AGENT         | ---> |  REGRESSION CHECK   |---> HardenedDiff
   |   (Defender)         |      |  (all prior suites) |
   +----------------------+      +---------------------+
```

### 2.2 Static AST Vulnerability Prober

A deterministic analyzer built on Python's `ast` module (and `tree-sitter-typescript` for the TypeScript stretch goal). It does not call a model. It outputs ranked **attack surfaces** that focus the Red Agent.

| Detector | Pattern | Example finding |
|---|---|---|
| Implicit type assumptions | Parameters without annotations used in arithmetic, indexing, `len()`, attribute access | `def mean(xs): return sum(xs)/len(xs)` — assumes sized, non-empty iterable |
| Missing guard clauses | Division/modulo by a variable; `x[i]` / `x[0]`; `dict[key]`; `.attr` on a possibly-`None` value with no preceding check | `a / b` with no `b == 0` guard |
| Unbounded loops | `while` loops whose condition variables are not demonstrably monotone; recursion without a base-case reduction | `while n != 1:` (Collatz-style non-termination for `n <= 0`) |
| Unhandled exception branches | Calls to `int()`, `float()`, `open()`, `json.loads()`, `next()`, `.index()` outside `try`; bare `except:` that swallows errors | `int(s)` on arbitrary string |
| Boundary operations | Slicing, `range()` bounds, off-by-one comparisons (`<` vs `<=`), integer overflow-prone casts | `arr[len(arr)]` |
| Mutable defaults and shared state | `def f(x=[])`; module-level mutable globals touched in functions | Cross-call state leakage |
| Concurrency hazards | Module-level state mutated without locks; `threading`/`asyncio` use | Race-prone counters |

Cyclomatic-complexity weighting ranks functions; each finding carries line numbers, a severity (`low|medium|high`), and a short natural-language hint.

### 2.3 Red Agent (The Attacker)

**Input:** target source, `ASTVulnerabilityReport`, prior-round history (which attacks already failed to break the code, which succeeded).
**Output:** an `AdversarialTestSuite` (a single pytest module as text, plus metadata).

Attack repertoire (the system prompt requires at least one test per high-severity finding):

1. **Boundary numerics:** `0`, `-1`, `1`, `-0.0`, `float('nan')`, `float('inf')`, `-inf`, `2**31 - 1`, `2**31`, `-2**31`, `2**63 - 1`, `sys.maxsize`.
2. **Property-based tests (Hypothesis):** `@given(st.lists(st.integers()))`, `st.text()`, `st.floats(allow_nan=True, allow_infinity=True)`, `st.recursive(...)`; properties include idempotence, round-trip, monotonicity, and "never raises an undeclared exception".
3. **Encoding quirks:** lone surrogates (`"\ud800"`), combining characters, zero-width joiners, RTL marks, NUL bytes, very long strings, mixed normalization (NFC vs NFD).
4. **Collection limits:** empty, single-element, duplicates, all-equal, huge (bounded to safe size), nested, unhashable members, generators exhausted twice.
5. **Concurrency races:** bounded `threading` with a fixed thread count (≤ 4) hammering shared state; barrier-synchronized starts.
6. **Malicious mocks:** `unittest.mock` objects whose methods raise, return `None`, or return wrong types; objects with hostile `__eq__`, `__hash__`, `__len__`.
7. **Exception contract probing:** asserting that documented exceptions are raised and undocumented ones are not.

**Validity rule:** a test counts as a *finding* only if it fails in the oracle against the unmodified code, fails identically in 3/3 replays, and its failure is not a test-authoring error (e.g., `NameError`, `SyntaxError`, import of non-existent symbol). Authoring errors are returned to the Red Agent once for self-repair.

### 2.4 Sandbox Oracle (The Referee)

Executes `pytest` against `target + generated tests` and returns an `ExecutionTrace`. Two interchangeable backends:

| Backend | Isolation mechanism | Default |
|---|---|---|
| `subprocess` | Fresh temp dir; new process group; `resource` limits on POSIX (`RLIMIT_AS`, `RLIMIT_CPU`, `RLIMIT_NPROC`, `RLIMIT_FSIZE`); Windows Job Object memory cap via `psutil`/ctypes; stripped environment; network blocked by an injected `sitecustomize` that replaces `socket` | Yes |
| `docker` | `docker run --rm --network none --memory 256m --cpus 1 --pids-limit 64 --read-only --tmpfs /tmp` with a pinned Python image | If Docker detected and `--sandbox docker` |

Limits: **2.0 s wall-clock per test-suite execution**, 256 MB memory, 64 processes/threads, 1 MB output cap. On timeout the whole process tree is killed and the trace is flagged `timed_out=true`; a timeout on code that previously passed is a valid finding (non-termination).

### 2.5 Blue Agent (The Defender)

**Input:** original code, `ExecutionTrace` (traceback, failing test names, assertion diffs), AST hints for the failing lines, and the current regression suite.
**Output:** a `HardenedDiff` (unified diff).

Constraints enforced by prompt and by validation:

- **Minimality:** the diff must touch only lines relevant to the failure; patches over 40 changed lines are rejected and re-requested with an instruction to narrow.
- **Behavior preservation:** the pre-existing test suite must still pass (Regression Check).
- **No test tampering:** the diff may not modify test files; only the target module.
- **No suppression:** blanket `try/except: pass`, `# type: ignore`-style evasion, or special-casing the literal inputs from the failing test are rejected by an AST-based "patch sanity" linter (hard-coded return values keyed on test constants are detected by literal matching).
- **Preferred repairs:** input validation, explicit guard clauses, correct exception types, loop-bound fixes, safe defaults.

---

## 3. Formal Minimax Protocol & State Machine

### 3.1 Game Definition

Let `C_r` be the code at round `r`, `T_r` the Red suite, and `S_r` the cumulative accepted test set (`S_r = S_{r-1} ∪ valid_findings(T_r)`).

- **Verdict:** `V(C, T) = 0` if `pytest` exits `0`, else `1`.
- **Attacker score in round r:** `a_r = |{t ∈ T_r : valid finding}|`
- **Defender score in round r:** `d_r = 1 if V(C_{r+1}, S_r ∪ R) = 0 else 0`, where `R` is the original regression suite.
- **Equilibrium estimate:** the duel is at equilibrium when `a_r = 0` for `K` consecutive rounds, with `K = 3`.

### 3.2 State Machine

```
   +--------------+   report    +-----------------------+   suite    +------------------+
   | ANALYZE_AST  | ----------> | GENERATE_ATTACK_TESTS | ---------> | SANDBOX_EXECUTE  |
   +--------------+             +-----------------------+            +--------+---------+
          ^                                ^                                  | trace
          |                                | stagnant: a_r = 0                v
          |                                | and stagnation < K      +------------------+
          |                                +-------------------------| EVALUATE_SCORE   |
          |                                                          +--------+---------+
          |                                              a_r > 0             |  a_r = 0
          |                                                |                 |
          |                                                v                 v
          |                                       +----------------+   (stagnation++ ;
          |                                       | DEFENDER_PATCH |    if stagnation = K
          |                                       +--------+-------+    or budget hit)
          |                                                | diff             |
          |                                                v                  v
          |                                       +-----------------+   +-------------+
          +---------------------------------------| REGRESSION_CHECK|   |  TERMINATE  |
              (new C_{r+1}; AST re-probed)        +--------+--------+   +-------------+
                                                           | fail: Blue retry (max 2),
                                                           | then revert patch, mark UNRESOLVED
```

### 3.3 Transitions

| State | Action | Next state |
|---|---|---|
| `ANALYZE_AST` | Parse current `C_r`; build report | `GENERATE_ATTACK_TESTS` |
| `GENERATE_ATTACK_TESTS` | Red Agent emits suite; lint passes (else repair ≤ 1×, then skip round) | `SANDBOX_EXECUTE` |
| `SANDBOX_EXECUTE` | Run suite on `C_r`; replay failures 3× to confirm determinism | `EVALUATE_SCORE` |
| `EVALUATE_SCORE` | Compute `a_r`; update scoreboard and stagnation counter | `DEFENDER_PATCH` if `a_r > 0`; else `GENERATE_ATTACK_TESTS` or `TERMINATE` |
| `DEFENDER_PATCH` | Blue Agent returns diff; apply to a working copy | `REGRESSION_CHECK` |
| `REGRESSION_CHECK` | Run `R ∪ S_r` on `C_{r+1}` | Success → `ANALYZE_AST` (next round); failure → Blue retry (≤ 2), then revert and mark finding `UNRESOLVED` |

### 3.4 Termination Criteria

A duel ends when **any** holds:

1. **Equilibrium:** `a_r = 0` for `K = 3` consecutive rounds.
2. **Round cap:** `r = max_rounds` (default 3 for the CLI; 8 for benchmarks).
3. **Time budget:** wall-clock exceeds `max_duration_s` (default 600).
4. **Token budget:** cumulative tokens exceed `max_tokens` (default 200,000).
5. **Fatal error:** the oracle itself fails (sandbox cannot start).

The final report lists findings (resolved/unresolved), the cumulative patch, scoreboard, coverage delta, and token use.

---

## 4. Data Models & Schemas

All inter-component messages are validated Pydantic v2 models.

```python
from __future__ import annotations
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SandboxBackend(str, Enum):
    SUBPROCESS = "subprocess"
    DOCKER = "docker"


class DuelConfig(BaseModel):
    target_path: str
    regression_tests_path: str | None = None
    max_rounds: int = Field(3, ge=1, le=20)
    stagnation_k: int = Field(3, ge=1, le=10)
    sandbox: SandboxBackend = SandboxBackend.SUBPROCESS
    timeout_s: float = Field(2.0, gt=0, le=30)
    memory_mb: int = Field(256, ge=64, le=2048)
    max_duration_s: int = Field(600, ge=10)
    max_tokens: int = Field(200_000, ge=1_000)
    replay_count: int = Field(3, ge=1, le=10)
    max_patch_lines: int = Field(40, ge=1)
    red_model: str = "gemma2:9b"
    blue_model: str = "llama-3.3-70b-versatile"
    apply_patch: bool = False
    seed: int = 1337


class VulnerabilityFinding(BaseModel):
    id: str
    kind: Literal[
        "implicit_type", "missing_guard", "unbounded_loop", "unhandled_exception",
        "boundary_op", "mutable_default", "concurrency",
    ]
    function: str
    lineno: int = Field(ge=1)
    end_lineno: int = Field(ge=1)
    severity: Severity
    hint: str


class ASTVulnerabilityReport(BaseModel):
    module: str
    source_sha256: str
    functions: list[str]
    complexity: dict[str, int]
    findings: list[VulnerabilityFinding]


class AttackTest(BaseModel):
    name: str
    targets_finding: str | None = None
    technique: Literal[
        "boundary_numeric", "property_based", "encoding", "collection_limit",
        "concurrency", "malicious_mock", "exception_contract",
    ]


class AdversarialTestSuite(BaseModel):
    round: int = Field(ge=1)
    code: str                       # full pytest module text
    tests: list[AttackTest]
    rationale: str = ""

    @field_validator("code")
    @classmethod
    def non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("test suite code is empty")
        return v


class TestOutcome(BaseModel):
    nodeid: str
    passed: bool
    error_type: str | None = None
    message: str | None = None


class ExecutionTrace(BaseModel):
    exit_code: int
    timed_out: bool
    duration_s: float
    stdout: str
    stderr: str
    outcomes: list[TestOutcome]
    memory_peak_mb: float | None = None
    deterministic: bool = True      # False if replays disagreed


class HardenedDiff(BaseModel):
    round: int
    unified_diff: str
    changed_lines: int = Field(ge=0)
    addressed_tests: list[str]
    explanation: str
    regression_passed: bool = False
```

**Scoreboard record (persisted as JSON/SQLite):**

| Field | Meaning |
|---|---|
| `round` | Round number |
| `red_points` | Valid findings in the round |
| `blue_points` | 1 if regression-clean patch accepted |
| `tokens_red`, `tokens_blue` | Provider-reported token usage |
| `coverage_branch_pct` | Branch coverage after round |
| `stagnation` | Consecutive rounds with `red_points = 0` |

---

## 5. Security & Sandboxing Invariants

Generated tests and patches are **untrusted code**. The following invariants must hold and each has an automated test.

| ID | Invariant | Enforcement |
|---|---|---|
| SEC-01 | **Process isolation:** test code runs in a separate process group/job (or container) with no inherited handles | `subprocess` with `creationflags`/`start_new_session`, stripped env; Docker `--read-only` |
| SEC-02 | **Resource caps:** memory 256 MB, CPU/wall 2.0 s, ≤ 64 processes, output ≤ 1 MB | `resource` (POSIX), Job Objects (Windows), Docker flags; process-tree kill on breach |
| SEC-03 | **Network disabled** during execution | Docker `--network none`; subprocess `sitecustomize` replaces `socket.socket` and `getaddrinfo` with raising stubs; AST linter rejects network imports |
| SEC-04 | **Path traversal prevention:** all file access confined to the temp working directory | Canonical-path check (`Path.resolve()` must be inside root) for any path the orchestrator reads/writes; linter rejects `open()` with absolute paths, `..`, `os.chdir`, `shutil` on outside paths |
| SEC-05 | **AST linting of generated tests before execution** | Rejects the constructs below |
| SEC-06 | **Original files are immutable** unless `--apply`; patches are applied to a working copy | Copy-on-write workspace; diff applied with a path-checked patcher |
| SEC-07 | **No secrets in the sandbox:** environment cleared; API keys never passed to test processes | Explicit env allow-list (`PATH`, `PYTHONHASHSEED`, `PYTHONPATH`) |
| SEC-08 | **Prompt-injection resistance:** target source is placed in clearly delimited, quoted blocks; agent output is parsed only as structured data | Schema validation; comments in target never treated as instructions |

**AST linter rejection list for Red-generated tests:**

- Imports of `os` (except `os.path`), `subprocess`, `socket`, `ctypes`, `multiprocessing`, `shutil`, `pty`, `signal`, `urllib`, `http`, `requests`, `importlib` hooks, `sys` modification of `modules`/`path`.
- Calls to `eval`, `exec`, `compile`, `__import__`, `os.fork`, `os.system`, `os.popen`, `os.kill`, `open` for writing.
- Fork-bomb and runaway patterns: `while True` without a bounded counter or `break`; recursion with no depth bound; `threading.Thread` creation inside loops or more than 4 threads in total; allocating objects whose static size expression exceeds 10⁷ elements (`[0] * 10**9`).
- Attribute access to dunder escape hatches: `__subclasses__`, `__globals__`, `__builtins__`, `__code__`.
- Modification of `pytest` internals or monkeypatching of the sandbox's `sitecustomize` guard.

A suite that fails linting is never executed; the Red Agent receives the violation list for one repair attempt, after which the round is recorded as forfeited.

---

## 6. Agent Model Adapters

| Provider | Endpoint | Use |
|---|---|---|
| Ollama (local) | `http://localhost:11434/v1` | `gemma2:2b` / `gemma2:9b`; offline Red/Blue |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile`, free tier |
| Google AI Studio | Gemini `generateContent` | `gemini-1.5-flash`, free tier |

Adapters share an async interface `complete(messages, *, json_schema=None, temperature, max_tokens) -> Completion` returning text plus provider-reported token usage. Red runs at temperature 0.8 (diversity); Blue at 0.2 (precision). Credentials come from the OS keyring or environment variables and are never logged.

---

## 7. Evaluation Metrics (Summary)

| Metric | Definition |
|---|---|
| Bug Catch Rate | `findings confirmed on seeded-bug set / seeded bugs` |
| Mutation Kill Rate | `killed mutants / total non-equivalent mutants` (via `mutmut`) |
| Branch Coverage Gain | `cov_branch(after) − cov_branch(before)` (percentage points, `coverage.py`) |
| Patch Success Rate | `findings resolved with regression-clean patch / findings` |
| Regression Rate | `patches that break previously passing tests / patches` (target 0) |
| Token Cost per Finding | `total tokens / confirmed findings` |

Full methodology is in [ROADMAP_AND_EXECUTION.md](ROADMAP_AND_EXECUTION.md).
