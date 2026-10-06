# Project Overview

| Project name | Description | Similar existing Apps/Systems |
|---|---|---|
| **AI-Combine** | An adversarial multi-agent code hardening arena. A Red Team agent analyzes the AST and synthesizes hostile, property-based tests (pytest/Hypothesis) to intentionally break code. A Blue Team agent diagnoses the failures and generates verifiable defensive patches. Both run inside an isolated execution sandbox, and a deterministic test runner (`exit code 0` vs `1`) decides every round. | **LLM test generators:** Codium / Qodo, TestGen-LLM, GitHub Copilot test generation. **Mutation and fuzzing tools:** Mutmut, Hypothesis, AFL / Atheris. **Automated program repair:** SWE-agent, Aider, GenProg. **Multi-agent frameworks:** CrewAI, AutoGPT, ChatDev. |

## Elevator Pitch

AI-Combine pits an attacker AI against a defender AI over your code. One tries to break it with hostile, property-based tests, the other patches it, and a sandboxed test runner decides who wins. Instead of trusting an LLM to grade its own work, every round ends in a deterministic pass/fail verdict.

## Core Architectural Paradigm: Minimax Edge-Case Discovery

AI-Combine treats hardening as a two-player, zero-sum game over a code artifact `C` and a test suite `T`:

$$
\min_{\Delta C}\;\max_{T}\;\;\mathrm{Fail}(C \oplus \Delta C,\; T)
$$

- The **Red Agent** chooses `T` to *maximize* new failing behaviors.
- The **Blue Agent** chooses a minimal patch `ΔC` to *minimize* failures without breaking the existing regression suite.
- The **Sandbox Oracle** is the referee, with binary ground truth. No LLM judges the outcome.

The duel converges when the Red Agent cannot produce a new failing test within `K = 3` consecutive rounds.

## How AI-Combine Differs From Existing Tools

| Tool category | What it does | What AI-Combine adds |
|---|---|---|
| Codium / TestGen-LLM | Cooperative tests that validate stated behavior and raise coverage | Adversarial tests written to fail, not to pass |
| Mutmut | Passively measures how weak a test suite is | Actively generates the missing hostile tests, then fixes the code |
| Hypothesis / fuzzers | Random input search with no semantic targeting | AST-guided attacks aimed at specific unguarded branches |
| SWE-agent / Aider | Repair code from a human-provided failing issue | Finds the failure itself, then repairs it with regression checks |
| CrewAI / ChatDev | Cooperative role-playing agents with no ground truth | Opposing loss functions judged by a real interpreter |

