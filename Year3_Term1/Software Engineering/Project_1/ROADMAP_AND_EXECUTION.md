# AI-Combine — Roadmap, Verification & Execution Guide

Companion to [AI_COMBINE_SPEC.md](AI_COMBINE_SPEC.md).

---

## 1. 8-Week (2-Month) Academic Sprint Roadmap

```
Week:    1   2 | 3   4 | 5   6 | 7   8
         [Sprint 1]  [Sprint 2]  [Sprint 3]  [Sprint 4]
         Proxy +     Circuit     A2A Agent   GUI + Pack +
         Adapters    Breaker     Engine      Defense
Milestones:  M1 (end W2)  M2 (end W4)  M3 (end W6)  M4 (end W8)
```

### Sprint 1 (Weeks 1–2): Core Proxy & Provider Adapters

**Goal:** a working OpenAI-compatible server that can talk to four providers, with streaming.

**Deliverables**

| # | Deliverable | Detail |
|---|---|---|
| 1.1 | FastAPI server | `POST /v1/chat/completions`, `GET /v1/models`, `GET /health`; Pydantic request/response models matching the OpenAI schema |
| 1.2 | Adapter interface | `ProviderAdapter` protocol with normalized error types |
| 1.3 | Ollama adapter | Gemma 2B/9B through `http://localhost:11434/v1` |
| 1.4 | Google AI Studio adapter | Gemini Flash; message-format translation to/from Gemini `generateContent` |
| 1.5 | Groq adapter | Llama 3.3 70B versatile via OpenAI-compatible endpoint |
| 1.6 | OpenRouter adapter | `:free` model discovery and calls |
| 1.7 | SSE streaming | `text/event-stream`, `data: {...}\n\n` chunks, terminal `data: [DONE]` |
| 1.8 | Basic config + CI | `pyproject.toml`, ruff, mypy, pytest, GitHub Actions |

**Acceptance criteria**

- AC-1.1: The official `openai` Python SDK (`base_url=http://localhost:3001/v1`) completes both streaming and non-streaming requests against each of the 4 providers.
- AC-1.2: `GET /v1/models` returns a valid OpenAI-style list including models from every configured provider.
- AC-1.3: Streaming time-to-first-token overhead vs. direct provider call ≤ 50 ms p95.
- AC-1.4: Adapter contract tests pass for all adapters using recorded fixtures (`respx`), ≥ 85% line coverage on `gateway/`.
- AC-1.5: Provider errors are mapped to normalized types (unit-tested table of status codes).

**Milestone M1:** "Hello, four providers" demo — one curl command per provider through the proxy.

---

### Sprint 2 (Weeks 3–4): Circuit Breaker & Resilient Failover

**Goal:** the gateway survives rate limits and outages without the client noticing.

**Deliverables**

| # | Deliverable | Detail |
|---|---|---|
| 2.1 | Token bucket limiter | Per provider, RPM and TPM dimensions; async-safe; monotonic clock |
| 2.2 | 429 interception | `Retry-After` / `x-ratelimit-*` parsing; circuit opens for the indicated duration |
| 2.3 | Circuit breaker | CLOSED/OPEN/HALF-OPEN with exponential cooldown |
| 2.4 | Failover queue | Ranked provider list per request; local Gemma as terminal fallback |
| 2.5 | Mid-stream failover | Partial-text capture, continuation prompt, de-duplicated splice into the live SSE stream |
| 2.6 | Key-health endpoints | `POST /internal/providers/{id}/verify`, `GET /internal/providers/health` |
| 2.7 | Browser deep-link helpers | Functions returning/opening provider key pages (AI Studio, Groq console, OpenRouter keys) |
| 2.8 | Encrypted vault | SQLCipher storage, OS keystore key, log redaction |
| 2.9 | Hardware profiler | P0/P1/P2 detection and Gemma selection |

**Acceptance criteria**

- AC-2.1: Token bucket never admits more than `capacity + refill*t` in property-based tests (Hypothesis).
- AC-2.2: On injected 429, the next provider is used and the client receives a normal 200 response; no 429 surfaces to the client.
- AC-2.3: Mid-stream drop at a random token index results in a complete stream with no duplicated or missing text segments larger than 1 token boundary (checked by the chaos harness).
- AC-2.4: Circuit transitions follow the specified state machine (state-table unit tests).
- AC-2.5: No API key appears in plaintext on disk or in logs (automated grep scan of data dir and log files).
- AC-2.6: Hardware profiler returns the correct profile for 8 mocked hardware fixtures.

**Milestone M2:** live demo — kill Groq mid-sentence; answer finishes via Gemma.

---

### Sprint 3 (Weeks 5–6): Hierarchical Agent-to-Agent (A2A) Engine

**Goal:** Supervisor–Worker–Critic loop with measurable token savings.

**Deliverables**

| # | Deliverable | Detail |
|---|---|---|
| 3.1 | Supervisor prompts | System prompt + JSON schema; JSON-mode where available; repair prompt on invalid output |
| 3.2 | Plan validator | Pydantic models, DAG/cycle check, size limits (max 12 subtasks) |
| 3.3 | Dispatcher | Topological layering; `asyncio.gather(..., return_exceptions=True)`; semaphore; per-task timeout |
| 3.4 | Error handling | Per-task retry on alternate provider; failed tasks reported to Critic |
| 3.5 | Critic loop | Score, synthesis, selective redo, `max_retries=2` |
| 3.6 | Context compression | Summaries of worker output before frontier calls |
| 3.7 | Metrics tracker | Per-role token counts; `T_mono` estimator; Savings % and ATL computation; SQLite persistence |
| 3.8 | `ai-combine-agent` model | Agent mode exposed via the OpenAI endpoint, streaming progress as comment events or final content |

**Acceptance criteria**

- AC-3.1: ≥ 95% of Supervisor outputs on a 100-prompt corpus validate against the schema (after at most 1 repair attempt).
- AC-3.2: One failing worker (forced exception) does not cancel sibling workers; the final answer is still produced.
- AC-3.3: Wall-clock time for a plan with 5 independent subtasks is ≤ 40% of sequential execution time (with mocked latency).
- AC-3.4: Metrics report per-task `T_plan`, `T_crit`, `T_exec`, and Savings %; values reconcile with provider-reported usage within 5%.
- AC-3.5: Critic-triggered redo re-runs only the flagged subtasks (verified by call-count assertions).

**Milestone M3:** end-to-end agent run on a coding task with a visible savings figure.

---

### Sprint 4 (Weeks 7–8): GUI Dashboard, Packaging & Capstone Defense

**Goal:** a non-technical-ready product and a defensible evaluation.

**Deliverables**

| # | Deliverable | Detail |
|---|---|---|
| 4.1 | Setup wizard | Steps: welcome → hardware scan → provider connect (Google OAuth or OpenRouter key) → optional Gemma install → test prompt |
| 4.2 | Dashboard | Provider health tiles, bucket levels, live logs (redacted) |
| 4.3 | Task tree visualization | Supervisor plan DAG with per-node provider, status, tokens |
| 4.4 | Token savings gauges | Savings %, ATL ratio, cumulative tokens saved |
| 4.5 | Packaging | Gateway frozen with PyInstaller; Tauri/Flutter shell; `.exe` (Windows, NSIS/MSI), `.dmg` (macOS), `.AppImage` (Linux) |
| 4.6 | Capstone test suite | Chaos, economic benchmark, HCI study (Section 2) |
| 4.7 | Evaluation report | Charts: savings by task category, latency overhead CDF, failover success rate, onboarding time distribution |
| 4.8 | Defense package | Slides, live demo script, reproducibility README |

**Acceptance criteria**

- AC-4.1: Fresh install on clean Windows VM reaches first successful prompt without a terminal.
- AC-4.2: Installers build in CI for all three OS targets; smoke test launches the app and calls `/health`.
- AC-4.3: Dashboard reflects a provider circuit opening within 2 seconds.
- AC-4.4: All Section 2 experiments run via a single command and regenerate the report figures.
- AC-4.5: Zero open P0/P1 defects at freeze (end of Week 8, day 3); Days 4–5 reserved for defense rehearsal.

**Milestone M4:** capstone defense.

---

### Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Free-tier limits change | High | Medium | Limits are config-driven; discovery via headers; OpenRouter pool as redundancy |
| Supervisor JSON invalid | Medium | High | JSON mode, repair prompt, single-task fallback |
| Mid-stream splice artifacts | Medium | Medium | Overlap de-duplication; chaos tests; fallback to restart-with-notice flag |
| SQLCipher build issues on Windows | Medium | Medium | Use prebuilt `sqlcipher3-binary`; fallback to field-level AES-GCM encryption (`cryptography`) |
| GUI framework learning curve | Medium | Medium | Choose Tauri if team knows web stack, Flutter otherwise; decide by end of Week 1 |
| Provider ToS issues | Low | High | Only user-supplied keys; no key pooling/sharing |

---

## 2. Empirical Verification & Academic Testing Protocol

### 2.1 Chaos Proxy Testing

**Objective:** verify *zero dropped streams* under hostile network and provider conditions (NFR-02).

**Apparatus:** a fault-injecting mock provider layer (`tests/chaos/fault_server.py`) sitting between adapters and real/mocked providers. It can:

| Fault | Parameterization |
|---|---|
| Random HTTP 429 with/without `Retry-After` | probability p ∈ {0.1, 0.3, 0.5} |
| HTTP 500/503 | p ∈ {0.05, 0.1} |
| Connection reset mid-stream | at uniformly random token index |
| Stalled stream (no bytes for > 10 s) | p ∈ {0.05} |
| Slow-loris latency | added delay 200–2000 ms |
| Total outage of a single provider | duration 30–120 s |
| Total outage of *all* clouds | duration 60 s (forces local Gemma) |

**Procedure**

1. Fix PRNG seed per run for reproducibility; log seeds.
2. Issue N = 1,000 streaming requests per fault profile (concurrency 8) using prompts from the benchmark corpus.
3. For each stream, record: HTTP status, whether `[DONE]` was received, assembled text, number of failovers, total time.
4. Validate integrity: assembled text must be coherent with no duplicated prefix > 5 tokens and no truncation (checked by sentinel-based prompts, e.g., "Count from 1 to 200 separated by commas," where the sequence can be verified mechanically).

**Metrics & pass criteria**

| Metric | Definition | Pass threshold |
|---|---|---|
| Dropped-stream rate | streams ending without `[DONE]` or with non-200 / error event | **0 / 1,000** at p(429) = 0.3 |
| Integrity error rate | sentinel sequence mismatches | ≤ 0.5% |
| Failover success rate | failovers resulting in completed stream | ≥ 99.5% |
| Added latency on failover | extra time to resume tokens | p95 ≤ 3 s (local Gemma warm) |
| Circuit correctness | transitions matching spec | 100% |

Statistical reporting: Clopper–Pearson 95% confidence interval on the dropped-stream rate (with 0/1000, upper bound ≈ 0.37%).

### 2.2 Economic Benchmark Suite

**Objective:** quantify Asymmetric Token Leverage versus a monolithic frontier baseline.

**Corpus (120 tasks, 4 categories × 30):**

| Category | Examples | Scoring |
|---|---|---|
| Code generation / refactor | HumanEval-style, multi-file refactors | Unit tests pass-rate |
| Repository Q&A / summarization | Summarize module, explain bug | Rubric + LLM judge (blind) with human spot check (10%) |
| Data extraction / transformation | Parse logs to JSON | Exact/field-level match |
| Multi-step reasoning / planning | Design tasks, math word problems | Reference answer match / rubric |

**Systems compared**

| ID | System |
|---|---|
| B0 | **Baseline:** single monolithic GPT-4o call (reference for tokens, latency, accuracy) |
| B1 | Free-only: a single free model (Gemini Flash) with no hierarchy |
| S1 | **AI-Combine**, frontier Supervisor/Critic (GPT-4o) + free/local workers |
| S2 | AI-Combine, free-model Supervisor/Critic (degraded zero-cost mode) |

**Metrics**

| Metric | Formula / method |
|---|---|
| Token Savings % | `(1 − (T_plan + T_crit) / T_mono) × 100`, using provider-reported usage on frontier calls only |
| Leverage Ratio (ATL) | `T_exec / (T_plan + T_crit)` |
| Monetary cost | frontier tokens × published price; free tiers counted as \$0 |
| Latency overhead | `latency(S) − latency(B0)`; end-to-end and TTFT; median, p95 |
| Task accuracy | category-specific score above, normalized 0–1 |
| Relative accuracy | `acc(S) / acc(B0)` |
| Retry rate | fraction of tasks triggering Critic redo |

**Targets**

| Target | Threshold |
|---|---|
| Token Savings % (S1) | ≥ 70% mean across corpus |
| Relative accuracy (S1) | ≥ 90% of B0 |
| Latency overhead (S1) | ≤ +25% median; parallelism should offset planning cost on multi-subtask tasks |
| S2 accuracy | ≥ B1 accuracy (hierarchy must help even with free planner) |

**Analysis:** each system runs 3 repetitions per task; report mean ± std. Use paired Wilcoxon signed-rank tests (α = 0.05) for accuracy differences between S1 and B0, and bootstrap 95% CIs for Savings %. Ablations: no Critic, no parallelism, no compression, Supervisor temperature sweep.

**Threats to validity:** LLM-judge bias (mitigated by blind human spot check), free-tier nondeterminism (repetitions, logged provider choices), token-count differences across tokenizers (use provider-reported usage; note estimator error).

### 2.3 HCI / Usability Testing

**Objective:** validate that non-technical users can onboard in **< 90 seconds to first prompt** (NFR-05).

**Participants:** n ≥ 12 non-technical users (no programming background), recruited from outside the CS program; plus n = 5 developers as a comparison group. Informed consent and anonymized data.

**Protocol**

1. Provide a clean machine/VM with the installer. Task: "Install the app and get an AI answer to a question."
2. No help provided except in-app text. Facilitator observes and records.
3. Timer starts at installer launch and stops at first rendered model response. Sub-timings: install, hardware scan, provider connect, first prompt.
4. Post-task: System Usability Scale (SUS) questionnaire, Single Ease Question (SEQ, 1–7), and 3 open questions.

**Metrics & pass criteria**

| Metric | Threshold |
|---|---|
| Median time-to-first-prompt (excluding installer download/model pull) | **< 90 s** |
| 90th percentile | < 150 s |
| Task completion without assistance | ≥ 90% |
| SUS score | ≥ 80 (grade A−) |
| SEQ mean | ≥ 6.0 |
| Critical errors (stuck > 60 s on one screen) | ≤ 1 per 12 participants |
| Terminal/config file opened | 0 |

Time budget breakdown target: hardware scan ≤ 10 s, OAuth/key connect ≤ 40 s, test prompt ≤ 15 s, navigation ≤ 25 s.

### 2.4 Additional Verification

| Area | Method |
|---|---|
| Security | Static scan (`bandit`), secret scan of data dir, network egress allow-list test via packet capture (only allow-listed hosts) |
| Compatibility | Scripted sessions with Aider, Cline, Codex CLI, OpenAI SDK |
| Performance | `locust` load test, 50 concurrent streams; overhead ≤ 50 ms p95 |
| Regression | CI runs unit + contract + a reduced chaos run (N = 100) on every PR |

---

## 3. Antigravity Implementation & Verification Guide

All commands are for **Windows PowerShell** from the workspace root `d:\APCS\Year3_Term1\Software Engineering\Project`. Linux/macOS equivalents are noted where they differ.

### 3.1 Prerequisites

```powershell
python --version      # 3.11+
git --version
node --version        # 20+ (only if Tauri GUI)
ollama --version      # optional, for local Gemma
```

### 3.2 Scaffolding

```powershell
cd "d:\APCS\Year3_Term1\Software Engineering\Project"
git init

$dirs = @(
  "ai_combine/gateway/adapters", "ai_combine/gateway/routing", "ai_combine/orchestrator",
  "ai_combine/vault", "ai_combine/hardware", "ai_combine/metrics",
  "tests/unit", "tests/contract", "tests/chaos", "tests/bench",
  "gui", "scripts", "docs"
)
$dirs | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }

# Python package markers
Get-ChildItem ai_combine -Directory -Recurse | ForEach-Object {
  New-Item -ItemType File -Force -Path (Join-Path $_.FullName "__init__.py") | Out-Null
}
New-Item -ItemType File -Force -Path "ai_combine/__init__.py" | Out-Null
```

Resulting layout:

```
Project/
├── AI_COMBINE_SPEC.md
├── ROADMAP_AND_EXECUTION.md
├── pyproject.toml
├── ai_combine/
│   ├── main.py                    # FastAPI app entrypoint
│   ├── gateway/
│   │   ├── api.py                 # /v1/chat/completions, /v1/models
│   │   ├── schemas.py             # OpenAI-compatible Pydantic models
│   │   ├── sse.py                 # SSE helpers
│   │   ├── adapters/
│   │   │   ├── base.py            # ProviderAdapter protocol + errors
│   │   │   ├── ollama.py
│   │   │   ├── google_ai.py
│   │   │   ├── groq.py
│   │   │   └── openrouter.py
│   │   └── routing/
│   │       ├── router.py
│   │       ├── token_bucket.py
│   │       └── circuit_breaker.py
│   ├── orchestrator/
│   │   ├── supervisor.py
│   │   ├── dispatcher.py
│   │   ├── critic.py
│   │   └── plan_schema.py
│   ├── vault/store.py             # SQLCipher storage
│   ├── hardware/profiler.py
│   └── metrics/tracker.py
├── tests/{unit,contract,chaos,bench}/
├── gui/                           # Tauri/Flutter app
└── scripts/
```

### 3.3 Environment & Dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
```

Create `pyproject.toml`:

```toml
[project]
name = "ai-combine"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.110",
  "uvicorn[standard]>=0.29",
  "httpx>=0.27",
  "pydantic>=2.6",
  "psutil>=5.9",
  "keyring>=25.0",
  "sqlcipher3-binary>=0.5",
  "cryptography>=42.0",
  "sse-starlette>=2.0",
]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-asyncio>=0.23", "respx>=0.21", "hypothesis>=6",
       "ruff>=0.4", "mypy>=1.9", "openai>=1.30", "locust>=2.24", "bandit>=1.7"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
```

```powershell
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 3.4 Minimal Server Skeleton

`ai_combine/main.py`:

```python
import uvicorn
from fastapi import FastAPI
from ai_combine.gateway.api import router as v1_router

app = FastAPI(title="AI-Combine Gateway")
app.include_router(v1_router, prefix="/v1")

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("ai_combine.main:app", host="127.0.0.1", port=3001, reload=False)
```

`ai_combine/gateway/api.py` (Sprint 1 starting point):

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/models")
async def list_models():
    return {"object": "list", "data": [
        {"id": "ai-combine-auto", "object": "model", "owned_by": "ai_combine"},
        {"id": "ai-combine-agent", "object": "model", "owned_by": "ai_combine"},
    ]}

@router.post("/chat/completions")
async def chat_completions(body: dict):
    # TODO(Sprint 1): validate, route via Router, adapt provider streams.
    async def gen():
        yield 'data: {"choices":[{"delta":{"content":"hello"}}]}\n\n'
        yield "data: [DONE]\n\n"
    if body.get("stream"):
        return StreamingResponse(gen(), media_type="text/event-stream")
    return {"object": "chat.completion", "choices": [
        {"index": 0, "message": {"role": "assistant", "content": "hello"},
         "finish_reason": "stop"}]}
```

### 3.5 Run & Smoke Test

```powershell
# Terminal 1: start gateway
python -m ai_combine.main

# Terminal 2: verify
curl.exe http://localhost:3001/health
curl.exe http://localhost:3001/v1/models
curl.exe -N http://localhost:3001/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d '{\"model\":\"ai-combine-auto\",\"stream\":true,\"messages\":[{\"role\":\"user\",\"content\":\"Hi\"}]}'
```

Local Gemma setup (optional, per hardware profile):

```powershell
ollama pull gemma2:2b      # P1
ollama pull gemma2:9b      # P2
curl.exe http://localhost:11434/api/tags
```

Provide keys during development via the vault CLI helper (never `.env`):

```powershell
python -m ai_combine.vault.store set groq        # prompts for key (hidden input)
python -m ai_combine.vault.store set google_ai
python -m ai_combine.vault.store set openrouter
python -m ai_combine.vault.store list            # shows masked values only
```

### 3.6 Verification Commands

```powershell
# Static checks
ruff check ai_combine tests
mypy ai_combine
bandit -r ai_combine

# Unit + contract tests (Sprint 1–3)
pytest tests/unit tests/contract -q --maxfail=1

# SDK compatibility check
python scripts/sdk_smoke.py

# Chaos suite (Sprint 2+)
pytest tests/chaos -q -m chaos --chaos-seed=1337
python -m tests.chaos.run --profile p429_30 --requests 1000 --concurrency 8

# Economic benchmark (Sprint 3+)
python -m tests.bench.run --systems B0,B1,S1,S2 --repeats 3 --out tests/bench/results.json
python -m tests.bench.report tests/bench/results.json --out docs/figures

# Load test
locust -f tests/bench/locustfile.py --headless -u 50 -r 10 -t 2m --host http://localhost:3001

# Secret leakage scan (must print nothing)
Select-String -Path "$env:APPDATA\AI-Combine\*" -Pattern "AIza|gsk_|sk-or-|sk-[A-Za-z0-9]{20,}" -ErrorAction SilentlyContinue
```

`scripts/sdk_smoke.py`:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:3001/v1", api_key="ai-combine-local")
print([m.id for m in client.models.list().data])

stream = client.chat.completions.create(
    model="ai-combine-auto",
    messages=[{"role": "user", "content": "Say hello in five words."}],
    stream=True,
)
text = "".join((c.choices[0].delta.content or "") for c in stream if c.choices)
assert text.strip(), "empty stream"
print("OK:", text)
```

### 3.7 Pointing External Developer Tools at AI-Combine

The gateway ignores the client API key value (use any placeholder, e.g., `ai-combine-local`); real provider keys stay in the Vault. Use `ai-combine-auto` for transparent routing/failover or `ai-combine-agent` for the Supervisor–Worker engine.

**Codex CLI**

```powershell
$env:OPENAI_BASE_URL = "http://localhost:3001/v1"
$env:OPENAI_API_KEY  = "ai-combine-local"
codex --model ai-combine-auto
```

Or in `~/.codex/config.toml`:

```toml
model = "ai-combine-auto"
model_provider = "ai_combine"

[model_providers.ai_combine]
name = "AI-Combine"
base_url = "http://localhost:3001/v1"
env_key = "OPENAI_API_KEY"
```

**Aider**

```powershell
$env:OPENAI_API_BASE = "http://localhost:3001/v1"
$env:OPENAI_API_KEY  = "ai-combine-local"
aider --model openai/ai-combine-auto
# Agent mode for larger edits:
aider --model openai/ai-combine-agent
```

**Cline (VS Code)**

1. Open Cline settings → **API Provider**: *OpenAI Compatible*.
2. **Base URL:** `http://localhost:3001/v1`
3. **API Key:** `ai-combine-local`
4. **Model ID:** `ai-combine-auto` (or `ai-combine-agent`).
5. Disable "Use prompt caching" and "Computer use" (not supported by the gateway); set max output tokens ≤ 4096.

**Verification from any tool:** open the AI-Combine dashboard (or `GET /internal/metrics/tasks/latest`) and confirm that the request appears with the chosen provider; then disable one provider's key and repeat the request to confirm failover without client-side errors.

### 3.8 Packaging (Sprint 4)

```powershell
# Freeze gateway
pip install pyinstaller
pyinstaller --onefile --name ai-combine-gateway ai_combine/main.py

# Tauri shell (if chosen)
cd gui
npm install
npm run tauri build            # produces .exe/.msi on Windows

# Flutter alternative
# flutter build windows | macos | linux
```

Linux AppImage / macOS DMG are built in CI (GitHub Actions matrix: `windows-latest`, `macos-latest`, `ubuntu-22.04`) because they require native toolchains. Smoke-test each artifact by launching it headlessly and calling `GET http://localhost:3001/health`.

### 3.9 Definition of Done (per sprint)

- [ ] All sprint acceptance criteria demonstrably met, with test evidence committed.
- [ ] `ruff`, `mypy`, `bandit` clean; coverage ≥ 85% on new modules.
- [ ] Spec and README updated for any behavior changes.
- [ ] Milestone demo recorded.
- [ ] Retrospective notes added to `docs/retro-sprint-N.md`.
