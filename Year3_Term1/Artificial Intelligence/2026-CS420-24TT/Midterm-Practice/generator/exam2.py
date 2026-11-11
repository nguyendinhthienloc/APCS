from qbank import *
import itertools
import math


def fwgc():
    def legal(s):
        F, W, G, C = s
        return not ((W == G and F != W) or (G == C and F != G))

    def succ(s):
        F = s[0]
        o = "R" if F == "L" else "L"
        out = []
        for i in (None, 1, 2, 3):
            if i is not None and s[i] != F:
                continue
            t = list(s)
            t[0] = o
            if i:
                t[i] = o
            t = tuple(t)
            if legal(t):
                out.append(t)
        return out
    start = ("L",) * 4
    par = {start: None}
    q = [start]
    while q:
        u = q.pop(0)
        for v in succ(u):
            if v not in par:
                par[v] = u
                q.append(v)
    p = [("R",) * 4]
    while par[p[-1]]:
        p.append(par[p[-1]])
    nlegal = sum(legal(s) for s in itertools.product("LR", repeat=4))
    return nlegal, len(par), p[::-1]


def build():
    E = Exam(2)

    # Q1 ------------------------------------------------------------------ formulation
    nlegal, nreach, path = fwgc()
    E.question(r"A farmer must take a wolf, a goat and a cabbage across a river. The boat holds the farmer and at most one of the three items, and "
               r"only the farmer can row. Left unattended (without the farmer), the wolf eats the goat and the goat eats the cabbage.",
               title="Farmer, wolf, goat and cabbage")
    E.sub(r"Consider a state as a tuple of values. Which values should be included in the tuple?",
          r"$(F, W, G, C)$: the bank (L or R) on which the farmer, the wolf, the goat and the cabbage are. (The boat is always with the farmer.)", 1.0)
    E.sub(r"Define the initial state and the goal state.", r"Initial $(L,L,L,L)$; goal $(R,R,R,R)$.", 0.8)
    E.sub(r"Define the action function.",
          r"The farmer crosses alone or with one item that is on \emph{his} bank: Cross, CrossW, CrossG, CrossC. An action is legal only if the result "
          r"does not leave W with G, or G with C, on the bank without the farmer.", 1.8)
    E.sub(r"What is the action cost?", r"1 per crossing.", 0.6)
    E.sub(r"What is the maximum number of states (including illegal ones)? How many states are legal, and how many are reachable? Give a shortest solution.",
          r"$2^4=\mathbf{16}$ tuples, \textbf{%d} legal, \textbf{%d} reachable. Shortest solution (%d crossings): %s."
          % (nlegal, nreach, len(path) - 1, r" $\to$ ".join("".join(s) for s in path)), 2.0)

    # Q2 ------------------------------------------------------------------ graph search
    nodes = {"S": (0, 0, 10, "left"), "A": (2.2, 1.9, 13, "above"), "B": (2.2, 0, 10, "above left"), "C": (2.2, -1.9, 8, "below"),
             "D": (4.8, 1.9, 9, "above"), "E": (4.8, 0, 3, "above left"), "F": (4.8, -1.9, 5, "below"),
             "H": (7.2, 1.0, 2, "above"), "G": (7.2, -1.0, 0, "right")}
    edges = [("S", "A", 8), ("S", "B", 9), ("S", "C", 2), ("A", "D", 4), ("A", "B", 7), ("B", "E", 8, "pos=0.4"), ("C", "F", 5),
             ("B", "C", 6), ("D", "H", 8), ("E", "D", 9), ("E", "G", 6, "pos=0.4"), ("F", "E", 3), ("F", "G", 9), ("H", "G", 2), ("E", "H", 1, "pos=0.62")]
    g = Graph(nodes, edges, "S", ["G"], directed=True)
    rb, rd, ru, rg, ra = graph_search_question(E, g, r"Consider the \emph{directed} graph below; $S$ is the initial state and $G$ the goal state. ")
    chk = check_h(g)
    E.sub(r"Is $h$ admissible? Is it consistent? Justify (only the direction of each edge matters).",
          r"$h^*$: " + ", ".join(r"%s$=%s$" % (k, fmt(v)) for k, v in chk["hstar"].items())
          + r". $h\le h^*$ everywhere $\Rightarrow$ admissible; $h(u)\le c(u,v)+h(v)$ for every directed edge $u\to v$ $\Rightarrow$ consistent.",
          1.8, label="(d)")
    E.sub(r"UCS and A* return the same path. Why does A* expand fewer states?",
          r"Both are optimal here (cost %s). A* never expands a state with $f(n)>C^*$: $A$ ($f=8+13=21$) and $B$ ($f=9+10=19$) are never expanded, "
          r"so A* expands %d states versus %d for UCS." % (fmt(ra["cost"]), len(ra["order"]), len(ru["order"])), 1.5, label="(e)")

    # Q3 ------------------------------------------------------------------ 4-bishops
    E.newpage("exam")
    pop = ["1324", "2143", "3412", "4132"]
    fit = [6 - len(bishops_attacks([int(c) for c in s])) for s in pop]
    tot = sum(fit)
    c1, c2 = pop[0][:2] + pop[3][2:], pop[3][:2] + pop[0][2:]
    f1, f2 = [6 - len(bishops_attacks([int(c) for c in s])) for s in (c1, c2)]
    E.question(r"Consider the 4-bishops problem: every state has 4 bishops on a $4\times4$ board, one in each column. A bishop attacks along the "
               r"diagonals (count attacking pairs regardless of pieces in between)." + center(queens_board_tikz([1, 3, 2, 4], piece=r"$\mathbb{B}$")),
               title="4-bishops")
    E.sub(r"What is the total number of states in the state space? Explain.", r"$4^4=\mathbf{256}$: each of the 4 bishops can be in any of the 4 rows of its column.", 0.9)
    E.sub(r"Each step moves one bishop within its own column. How many successors does a state have? Explain.",
          r"$4\times3=\mathbf{12}$: choose the bishop (4 ways) and one of the 3 other rows of its column.", 0.9)
    E.sub(r"A state is written as 4 digits giving the row of the bishop in columns 1--4 (the board above is 1324). Let $n_b$ be the number of "
          r"attacking pairs of bishops of state $n$. Define a fitness function Fit$(n)$ to be maximised by the genetic algorithm.",
          r"Fit$(n)=\binom42-n_b=6-n_b$ (the number of non-attacking pairs); the goal has Fit $=6$.", 0.9)
    tb = (r"\begin{center}\begin{tabular}{|l|c|c|c|c|}\hline State $n$ & $S_1=%s$ & $S_2=%s$ & $S_3=%s$ & $S_4=%s$\\\hline " % tuple(pop))
    E.sub(r"The current generation is $S_1=%s$, $S_2=%s$, $S_3=%s$, $S_4=%s$. Compute Fit$(n)$ and the probability that each state is chosen in "
          r"the roulette-wheel selection step. Then cross $S_1$ with $S_4$ after the 2nd digit and give the two children with their fitness." % tuple(pop),
          tb + r"Fit$(n)$ & " + " & ".join(r"\textcolor{blue!60!black}{%d}" % f for f in fit)
          + r"\\\hline Prob$(n)$ & " + " & ".join(r"\textcolor{blue!60!black}{%d/%d = %.1f\%%}" % (f, tot, 100.0 * f / tot) for f in fit) + r"\\\hline\end{tabular}\end{center}"
          + r"Attacking pairs (by column): " + "; ".join(r"$S_%d$: %s" % (i + 1, ", ".join("(%d,%d)" % p for p in bishops_attacks([int(c) for c in s])) or "none")
                                                     for i, s in enumerate(pop))
          + r". Children: \textbf{%s} (Fit %d) and \textbf{%s} (Fit %d)." % (c1, f1, c2, f2),
          tb + r"Fit$(n)$ & & & & \\[2mm]\hline Prob$(n)$ & & & & \\[2mm]\hline\end{tabular}\end{center}" + box(1.2))

    # Q4 ------------------------------------------------------------------ minimax / alpha-beta
    E.newpage("exam")
    t1 = build_tree([[[18, 6], [30, 15]], [[21, 20], [29, 3], [25, 14]], [[5, 12], [1, 16]]], "max")
    minimax_question(E, t1, r"Consider the following game tree. The root is a MAX node; children are visited left to right.", dx=0.85)

    # Q5 ------------------------------------------------------------------ MIN root
    E.newpage("exam")
    t2 = build_tree([[[15, 19], [8, 17]], [[29, 28, 20], [5, 24]], [[14, 18], [9, 1], [12, 25]]], "min")
    alphabeta_question(E, t2, r"Consider the game tree below, in which \textbf{MIN moves first} (the root is a MIN node).", dx=0.8, who="MIN")

    # Q6 ------------------------------------------------------------------ expectimax
    t3 = build_tree(("max", [("chance", [10, 8, 8], [0.5, 0.25, 0.25]), ("chance", [2, 10, 16], [0.5, 0.25, 0.25]),
                             ("chance", [6, 4, 12], [0.5, 0.25, 0.25])]))
    minimax(t3)
    sq = build_tree(("max", [("chance", [100, 64, 64], [0.5, 0.25, 0.25]), ("chance", [4, 100, 256], [0.5, 0.25, 0.25]),
                             ("chance", [36, 16, 144], [0.5, 0.25, 0.25])]))
    minimax(sq)
    bestc = max(t3.children, key=lambda c: c.mm)
    bests = max(sq.children, key=lambda c: c.mm)
    E.newpage("exam")
    E.question(r"Consider the following game tree with chance nodes (outcome probabilities on the edges)."
               + center(tikz_gtree(t3, "blank", dx=1.15, dy=1.4)))
    E.sub(r"Calculate the expectimax value of every node. Which move does MAX choose?",
          center(tikz_gtree(t3, "minimax", dx=1.15, dy=1.4))
          + "; ".join(r"%s $=%s$" % (c.name, r"+".join(r"%s\cdot%s" % (prob_tex(p).strip("$"), fmt(l.value)) for p, l in zip(c.probs, c.children)) + "=" + fmt(c.mm)) for c in t3.children)
          + r". MAX chooses \textbf{%s} (%s)." % (bestc.name, fmt(t3.mm)), 2.0)
    E.sub(r"Which move would MAX choose if the chance nodes were MIN nodes?",
          ", ".join("%s$=%s$" % (c.name, fmt(min(l.value for l in c.children))) for c in t3.children)
          + r" $\Rightarrow$ %s." % max(t3.children, key=lambda c: min(l.value for l in c.children)).name, 1.0)
    E.sub(r"Replace every leaf value $x$ by $x^2$ (order-preserving for these positive values). Does the expectimax decision change? What does this "
          r"tell you about evaluation functions in stochastic games?",
          ", ".join(r"%s $=%s$" % (c.name, fmt(c.mm)) for c in sq.children) + r" $\Rightarrow$ MAX now chooses \textbf{%s}: the decision changes. "
          r"For expectimax the magnitudes of the values matter (only a positive linear transformation is safe), whereas minimax only needs the order."
          % bests.name, 1.8)

    # Q7 ------------------------------------------------------------------ MCTS
    E.newpage("exam")
    em = {"R": ["A", "B", "C"], "A": ["A1", "A2"], "B": ["B1", "B2"], "C": ["C1", "C2"], "A1": ["A3", "A4"], "A2": ["A5", "A6"],
          "B1": ["B3", "B4"], "B2": ["B5", "B6"], "C1": ["C3", "C4"], "C2": ["C5", "C6"]}
    root = MNode("R")
    mcts_run(root, em, [0, 0, 0, 0, 0, 1, 1, 0, 0, 0], math.sqrt(2), r"\sqrt2")
    given = clone_mcts(root)
    q = [1, 0, 0]
    ucb0 = [(c.name, ucb_tex(c, root, math.sqrt(2), r"\sqrt2"), ucb(c, root, math.sqrt(2))) for c in root.children]
    log = mcts_run(root, em, q, math.sqrt(2), r"\sqrt2")
    E.question(r"Consider the MCTS tree below; rollouts return 1 (win for the root player) or 0 (loss), $t$ is the total reward and $n$ the number of "
               r"visits. Use $\mathrm{UCB1}=\bar V_i + C\sqrt{\ln N/n_i}$ with $C=\sqrt2$ (unvisited $=\infty$, ties to the left). A leaf never visited is "
               r"rolled out directly; otherwise all its children are added and the rollout starts at the first. Expansions create: "
               r"$A_1\to A_3,A_4$; $A_2\to A_5,A_6$; $B_1\to B_3,B_4$; $B_2\to B_5,B_6$; $C_1\to C_3,C_4$; $C_2\to C_5,C_6$."
               + center(tikz_mcts(given, scale=0.85, dx=1.75)))
    E.sub(r"Calculate UCB1 for $A$, $B$ and $C$. Which child is selected?",
          "; ".join(r"%s: %s" % (mname(nm), tx) for nm, tx, _ in ucb0) + r" $\Rightarrow$ \textbf{%s}." % mname(max(ucb0, key=lambda x: x[2])[0]), 1.6)
    E.sub(r"Perform three iterations whose rollouts return $%s$ (in order); update the statistics and draw the final tree." % r",\ ".join(map(str, q)),
          mcts_log_tex(log) + r"\par Final tree:" + center(tikz_mcts(root, scale=0.8, dx=1.6)), 8.0)
    bn = max(root.children, key=lambda c: c.n)
    ba = max(root.children, key=lambda c: c.t / c.n)
    E.sub(r"If the search stopped now, which move is played by the robust-child rule (the lecture's \texttt{best\_child})? Does the max-child rule agree?",
          ", ".join(r"%s: $%s/%d$" % (mname(c.name), fmt(c.t), c.n) for c in root.children)
          + r" $\Rightarrow$ robust child \textbf{%s}; max child \textbf{%s}%s." % (mname(bn.name), mname(ba.name), "" if bn is ba else " (they disagree)"), 1.2)

    # Q8 ------------------------------------------------------------------ map colouring
    E.newpage("exam")
    cn = {"A": (0, 1), "B": (1.7, 2.1), "C": (1.7, -0.1), "F": (3.4, 1.4), "E": (3.4, -0.7), "D": (5.1, 0.4)}
    ce = [("A", "B"), ("A", "C"), ("B", "C"), ("B", "F"), ("C", "E"), ("C", "F"), ("D", "E"), ("D", "F"), ("E", "F")]
    map_coloring_question(E, cn, ce)
    csp = CSP(list("ABCDEF"), {v: ["R", "G", "B"] for v in "ABCDEF"})
    csp.neq(ce)
    sol, tr = backtrack_fc(csp, "static", "given", "fc")
    nback = sum(1 for t in tr if t["type"] == "undo")
    nwipe = sum(1 for t in tr if t["type"] == "assign" and t["wipe"])
    E.sub(r"Now solve the CSP again with forward checking but \emph{without} MRV/DH: variables in the fixed order A, B, C, D, E, F and values in the "
          r"order R, G, B. Draw the search tree and mark every node where forward checking empties a domain.",
          bt_table(csp, tr) + center(bt_search_tree_tikz(tr, scale=0.95, dx=2.1))
          + r"Forward checking empties a domain %d times and the search backtracks %d times (solution %s). After $D=G$, FC leaves $E=\{R\}$ and "
            r"$F=\{R\}$ although E and F are adjacent: FC does not check arcs between unassigned variables, while arc consistency would." %
          (nwipe, nback, ", ".join("%s=%s" % (k, sol[k]) for k in csp.vars)), 7.0)

    # Q9 ------------------------------------------------------------------ AC-3
    E.newpage("exam")
    c2 = CSP(["A", "B", "C"], {v: [1, 2, 3, 4, 5, 6] for v in "ABC"})
    c2.add("A", "B", lambda a, b: a == 2 * b)
    c2.add("B", "C", lambda b, c: b + c == 7)
    c2.add("A", "C", lambda a, c: a < c)
    q0 = [("A", "B"), ("B", "A"), ("B", "C"), ("C", "B"), ("A", "C"), ("C", "A")]
    okk, D, tr3 = ac3(c2, q0)
    sols = [(a, b, c) for a in D["A"] for b in D["B"] for c in D["C"] if a == 2 * b and b + c == 7 and a < c]
    full = [1, 2, 3, 4, 5, 6]
    E.question(r"Variables $A,B,C\in\{1,\dots,6\}$ with the constraints $A=2B$, $B+C=7$ and $A<C$.")
    E.sub(r"Run AC-3 starting from the queue $A\to B,\ B\to A,\ B\to C,\ C\to B,\ A\to C,\ C\to A$ (pop from the front; when $D_i$ shrinks, append "
          r"every arc $X_k\to X_i$, $k\neq j$, not already queued). Show every revision.", ac3_table(tr3), 5.0)
    E.sub(r"Cross out the eliminated values, and give all solutions." + dom_row_table(["A", "B", "C"], [r"1\ 2\ 3\ 4\ 5\ 6"] * 3),
          dom_row_table(["A", "B", "C"], [strike_dom(full, D[v]) for v in "ABC"]) + r"Solutions $(A,B,C)$: "
          + ", ".join(r"$(%d,%d,%d)$" % s for s in sols) + ".", 0.9)

    # Q10 ----------------------------------------------------------------- theory
    E.question(r"Answer the following questions briefly.")
    E.sub(r"What is a rational agent? Using the lecture's examples (fingers on a hot stove; crossing at a crosswalk), distinguish a reflex action "
          r"from an intelligent action. Can a reflex action be rational?",
          r"A rational agent acts to achieve the best outcome, or the best expected outcome under uncertainty. A reflex action is immediate, without "
          r"deliberation (withdrawing the fingers); an intelligent action results from reasoning or learning (crossing at the crosswalk). A reflex "
          r"action can be rational or not; intelligent actions are usually rational.", 2.4)
    E.sub(r"What is abstraction in problem formulation? When is an abstraction valid and when is it useful? Illustrate with route finding in Romania.",
          r"Removing detail from the representation (the state is just the current city; weather, traffic, companions are ignored). Valid: every "
          r"abstract solution can be turned into a real one; useful: each abstract action (drive Arad$\to$Sibiu) is easier than the original problem.", 2.4)
    E.sub(r"For 8-queens, compare the naive incremental formulation, the improved incremental formulation and the complete-state formulation used by "
          r"hill climbing (size of the space / number of successors).",
          r"Naive (add a queen to any empty square): $64\cdot63\cdots57\approx1.8\times10^{14}$ sequences. Improved (one queen per column, leftmost "
          r"empty column, non-attacked squares only): 2{,}057 states. Complete-state (8 queens, one per column, move a queen in its column): "
          r"$8\times7=56$ successors per state.", 2.4)
    E.sub(r"List the four steps of an MCTS iteration and explain the difference between the tree policy and the default policy.",
          r"Selection, Expansion, Simulation (rollout), Backpropagation. The tree policy (e.g.\ UCB1) chooses nodes inside the tree; the default "
          r"policy plays the rollout outside the tree (uniformly random and fast by default).", 2.0)

    # Q11 ----------------------------------------------------------------- true / false
    E.question(r"True or false?")
    tf_block(E, [
        (r"Tree-search DFS without any cycle checking is complete on every finite state space.", False,
         r"With cycles (e.g.\ two states linked both ways) it can loop forever; checking the current path fixes this."),
        (r"Uniform-cost search is complete if every action cost is at least some $\epsilon>0$.", True,
         r"Then any path cost grows without bound with its length, so UCS cannot get stuck on an infinite path of tiny costs."),
        (r"Tree-search DFS needs only $O(bm)$ memory.", True, r"It stores one path and the unexpanded siblings along it."),
        (r"Greedy best-first graph search is complete in finite state spaces.", True, r"It never re-expands a state, so it eventually exhausts a finite space."),
        (r"Weighted A* ($f=g+W\cdot h$, $W>1$) always returns an optimal path when $h$ is admissible.", False,
         r"$W\cdot h$ may overestimate; weighted A* trades optimality for speed."),
        (r"Minimax has time complexity $O(b^m)$ and space complexity $O(bm)$.", True, r"It is a complete depth-first exploration of the game tree."),
        (r"An order-preserving transformation of the leaf values never changes the move chosen by expectimax.", False,
         r"True for minimax, not for expectimax (see Question 6)."),
        (r"The robust child of the MCTS root is the child with the highest average reward.", False, r"Robust = most visited; highest average = max child."),
        (r"AC-3 runs in $O(cd^3)$ in the worst case.", True, r"Each arc is re-queued at most $d$ times and each revision costs $O(d^2)$."),
        (r"Forward checking makes the neighbours of the just-assigned variable consistent with it, but does not look further ahead.", True,
         r"That is exactly FC; MAC continues propagating with AC-3."),
    ])
    return E
