# Mock Test 3 — Precedence Graph & Concurrency Solution

## Question 4: Serialization & Concurrency
Given schedule $S$:
$$S = r_1(A)\ r_2(A)\ w_1(B)\ w_3(A)\ r_2(B)\ w_2(C)\ r_3(C)\ w_1(C)$$

---

## 1. Conflict Analysis & Precedence Graph

### Conflicting Operations Breakdown

| Data Item | Preceding Op | Succeeding Op | Edge Direction | Conflict Type | Rationale |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **A** | $r_1(A)$ | $w_3(A)$ | $T_1 \to T_3$ | **WAR** (Write-After-Read) | $T_1$ reads $A$ before $T_3$ overwrites $A$ |
| **A** | $r_2(A)$ | $w_3(A)$ | $T_2 \to T_3$ | **WAR** (Write-After-Read) | $T_2$ reads $A$ before $T_3$ overwrites $A$ |
| **B** | $w_1(B)$ | $r_2(B)$ | $T_1 \to T_2$ | **RAW** (Read-After-Write) | $T_2$ reads $B$ written by $T_1$ |
| **C** | $w_2(C)$ | $r_3(C)$ | $T_2 \to T_3$ | **RAW** (Read-After-Write) | $T_3$ reads $C$ written by $T_2$ |
| **C** | $w_2(C)$ | $w_1(C)$ | $T_2 \to T_1$ | **WAW** (Write-After-Write) | $T_2$ writes $C$ before $T_1$ writes $C$ |
| **C** | $r_3(C)$ | $w_1(C)$ | $T_3 \to T_1$ | **WAR** (Write-After-Read) | $T_3$ reads $C$ before $T_1$ overwrites $C$ |

---

### Precedence Graph $P(S)$

```mermaid
flowchart TD
    T1(("T1"))
    T2(("T2"))
    T3(("T3"))

    T1 -->|"A: r1(A) -> w3(A)"| T3
    T2 -->|"A: r2(A) -> w3(A)<br/>C: w2(C) -> r3(C)"| T3
    T1 -->|"B: w1(B) -> r2(B)"| T2
    T2 -->|"C: w2(C) -> w1(C)"| T1
    T3 -->|"C: r3(C) -> w1(C)"| T1
```

---

## 2. Conflict Serializability Test

- **Cycles Identified:**
  - Cycle 1: $T_1 \xrightarrow{\text{B}} T_2 \xrightarrow{\text{C}} T_1$ (Length 2)
  - Cycle 2: $T_1 \xrightarrow{\text{A}} T_3 \xrightarrow{\text{C}} T_1$ (Length 2)
  - Cycle 3: $T_1 \xrightarrow{\text{B}} T_2 \xrightarrow{\text{C}} T_3 \xrightarrow{\text{C}} T_1$ (Length 3)

- **Conclusion:**
  > [!IMPORTANT]
  > Schedule $S$ is **NOT conflict-serializable** because its precedence graph contains multiple cycles.

---

## 3. Recoverability & Cascadelessness

- **Commit Order:** $c_1 \to c_3 \to c_2$
- **Read-From Dependencies:**
  - $T_2$ reads $B$ from $T_1$ ($w_1(B) \to r_2(B)$) $\implies T_2$ depends on $T_1$ (requires $c_1 < c_2$).
  - $T_3$ reads $C$ from $T_2$ ($w_2(C) \to r_3(C)$) $\implies T_3$ depends on $T_2$ (requires $c_2 < c_3$).

- **Evaluation:**
  - For $T_2 \implies T_1$: $c_1 < c_2$ is satisfied.
  - For $T_3 \implies T_2$: $T_3$ reads $C$ from $T_2$, but the commit order has $c_3 < c_2$ ($T_3$ commits **before** $T_2$). If $T_2$ aborts, $T_3$ has already committed with bad data.

> [!WARNING]
> - **Recoverable:** **No**, because $T_3$ reads from $T_2$ but commits ($c_3$) before $T_2$ ($c_2$).
> - **Cascadeless:** **No**, because $T_2$ and $T_3$ read uncommitted data.

---

## 4. Two-Phase Locking (2PL) Rules

- **Growing Phase:** Transaction acquires all needed locks (shared or exclusive) and cannot release any lock.
- **Shrinking Phase:** Transaction releases locks and cannot acquire any new locks.
- **Rule Violation:** Acquiring a new lock after releasing the first lock switches the transaction back to the growing phase from the shrinking phase, breaking the two-phase property and opening the schedule to non-serializable interleavings.
