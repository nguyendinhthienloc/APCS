from qbank import *
import math


def puzzle_tex(state):
    cells = [("" if v == 0 else str(v)) for v in state]
    rows = [" & ".join(cells[i * 3:(i + 1) * 3]) + r" \\ \hline" for i in range(3)]
    return r"{\renewcommand{\arraystretch}{1.3}\begin{tabular}{|c|c|c|}\hline " + "\n".join(rows) + r"\end{tabular}}"


def queens_hc(rows):
    """steepest descent; ties -> leftmost column, then top row."""
    steps = []
    rows = list(rows)
    while True:
        hb = queens_hboard(rows)
        h = queens_h(rows)
        best = None
        for c in range(4):
            for r in range(4):
                if rows[c] == r + 1:
                    continue
                if best is None or hb[r][c] < best[0]:
                    best = (hb[r][c], r + 1, c + 1)
        steps.append((list(rows), hb, best))
        if best[0] >= h:
            return steps, "stuck"
        rows[best[2] - 1] = best[1]
        if best[0] == 0:
            steps.append((list(rows), None, None))
            return steps, "solved"


def build():
    E = Exam(3)

    # Q1 ------------------------------------------------------------------ formulation
    E.question(r"Three disks of different sizes are stacked on peg 1 (largest at the bottom). The goal is to move the stack to peg 3, moving one "
               r"disk at a time and never placing a larger disk on a smaller one.", title="Tower of Hanoi with 3 pegs and 3 disks")
    E.sub(r"Consider a state as a tuple of values. Which values should be included in the tuple?",
          r"$(p_1,p_2,p_3)$ = the peg of the small, medium and large disk. On a peg the order of the disks is forced by their sizes, so it does not need "
          r"to be stored.", 1.0)
    E.sub(r"Define the initial state and the goal state.", r"Initial $(1,1,1)$; goal $(3,3,3)$.", 0.8)
    E.sub(r"Define the action function.",
          r"Move the top disk of peg $a$ (the smallest $i$ with $p_i=a$) to peg $b\neq a$, provided peg $b$ is empty or its top disk is larger; "
          r"the result sets $p_i=b$.", 1.5)
    E.sub(r"What is the action cost?", r"1 per move.", 0.6)
    E.sub(r"What is the maximum number of states? How many are reachable? What is the length of an optimal solution?",
          r"$3^3=\mathbf{27}$ tuples; every tuple is legal and all \textbf{27} are reachable. Optimal solution: $2^3-1=\mathbf{7}$ moves.", 1.2)

    # Q2 ------------------------------------------------------------------ graph search (inconsistent h)
    nodes = {"S": (0, 0, 21, "left"), "A": (2.0, 1.9, 15, "above"), "B": (2.0, -1.9, 17, "below"), "C": (4.0, 0, 11, "below"),
             "D": (4.0, 2.8, 17, "above"), "E": (6.0, -1.9, 6, "below"), "F": (6.0, 1.9, 7, "above"), "G": (8.0, 0, 0, "right")}
    edges = [("S", "A", 4), ("S", "B", 9), ("S", "C", 9), ("A", "C", 3), ("A", "D", 4), ("B", "C", 4), ("B", "E", 9), ("C", "F", 5),
             ("C", "E", 7), ("D", "F", 9), ("E", "G", 8), ("F", "G", 9)]
    g = Graph(nodes, edges, "S", ["G"])
    rb, rd, ru, rg, ra = graph_search_question(E, g, r"Consider the undirected graph below; $S$ is the initial state and $G$ the goal state. ")
    chk = check_h(g)
    hf = {k: g.h(k) for k in g.nodes}
    changed = True
    while changed:
        changed = False
        for u in g.adj:
            for v, c in g.adj[u].items():
                if hf[u] > c + hf[v]:
                    hf[u] = c + hf[v]
                    changed = True
    fixes = [(k, g.h(k), hf[k]) for k in g.nodes if hf[k] != g.h(k)]
    E.sub(r"Is $h$ admissible? Justify.",
          r"$h^*$: " + ", ".join(r"%s$=%s$" % (k, fmt(v)) for k, v in chk["hstar"].items()) + r"; $h\le h^*$ everywhere $\Rightarrow$ \textbf{admissible}.",
          1.2, label="(d)")
    E.sub(r"Is $h$ consistent? List every violated inequality.",
          r"\textbf{No}: " + "; ".join(r"$h(%s)=%s>c(%s,%s)+h(%s)=%s$" % (u, fmt(hu), u, v, v, fmt(c + hv)) for u, v, hu, c, hv in chk["con_viol"]) + ".",
          1.6, label="(e)")
    E.sub(r"Decrease as few $h$-values as possible so that $h$ becomes consistent. Does the new heuristic dominate the old one, or the opposite?",
          r"Lower " + ", ".join(r"$h(%s)$ from %s to %s" % (k, fmt(a), fmt(b)) for k, a, b in fixes)
          + r". Every value was only decreased, so the new $h'$ is still admissible, and the \emph{old} $h$ dominates $h'$ ($h\ge h'$ everywhere). "
            r"Dominance alone is not enough here: the lecture's guarantee that the dominating heuristic expands no more nodes assumes both are consistent.",
          1.8, label="(f)")

    # Q3 ------------------------------------------------------------------ 4-queens hill climbing
    E.newpage("exam")
    S0 = [1, 1, 1, 1]
    steps, res = queens_hc(S0)
    E.question(r"The 4-queens problem asks to place four queens on a $4\times4$ board so that no queen attacks another. States are configurations "
               r"with all four queens on the board, one per column; a successor moves one queen to another square of its column; $h(\text{state})$ is "
               r"the number of attacking pairs. The initial state $S$ (written as rows $1,1,1,1$; row 1 at the top) is shown below."
               + center(queens_board_tikz(S0)))
    E.sub(r"How many states are there in total? How many successors does each state have? Explain.",
          r"$4^4=\mathbf{256}$ states (each queen in any row of its column); $4\times3=\mathbf{12}$ successors.", 1.0)
    E.sub(r"What is $h(S)$? Explain.", r"All four queens share row 1: every pair attacks, $h(S)=\binom42=\mathbf{6}$.", 0.8)
    sol = []
    for k, (rows, hb, best) in enumerate(steps):
        if hb is None:
            sol.append(r"Level %d: state $(%s)$ with $h=0$ --- \textbf{solved}." % (k, ",".join(map(str, rows))))
            break
        sol.append(r"\begin{minipage}[t]{0.32\linewidth}\centering %s\\ \small state $(%s)$, $h=%d$\end{minipage}"
                   % (queens_board_tikz(rows, hb, hl=(best[1], best[2])), ",".join(map(str, rows)), queens_h(rows)))
    E.sub(r"Apply steepest-descent hill climbing from $S$. At every step write the $h$ value of each of the 12 successors on the board (in the square "
          r"the queen would move to) and choose the best one (ties: left-most column, then top row). Stop at a solution or when no successor is better.",
          r"Numbers = $h$ after moving the queen of that column to that square; red = chosen move.\par\begin{center}" + r"\hfill ".join(sol[:-1])
          + r"\end{center}" + sol[-1] + r" Hill climbing reaches a solution in %d moves here (from other states, e.g.\ $(4,3,2,1)$, it gets stuck "
          r"at $h=1$ without sideways moves)." % (len(steps) - 1),
          8.0)

    # Q4 ------------------------------------------------------------------ 4-ply minimax / alpha-beta
    E.newpage("exam")
    vals = iter([16, 5, 2, 25, 14, 9, 39, 28, 10, 12, 11, 19, 3, 18, 32, 8, 1, 15, 31, 24])
    spec1 = [[[[next(vals), next(vals)], [next(vals), next(vals)]] for _ in range(3)],
             [[[next(vals), next(vals)], [next(vals), next(vals)]] for _ in range(2)]]
    t1 = build_tree(spec1, "max")
    minimax_question(E, t1, r"Consider the following 4-ply game tree (MAX at the root, children visited left to right).", dx=0.8)

    # Q5 ------------------------------------------------------------------ parametric
    E.newpage("exam")
    tp = build_tree([[7, "x"], [5, 9, 6], [8, 4, 10]], "max")
    for x in range(0, 13):
        t = build_tree([[7, x], [5, 9, 6], [8, 4, 10]], "max")
        minimax(t)
        ab = alphabeta(t)
        pl = [l.name for l in ab["pruned_leaves"]]
        assert (x >= 5) == ("4" in pl and "5" in pl) and "8" in pl and t.mm == min(7, max(x, 5))
    E.question(r"The game tree below contains an unknown integer leaf value $x$. Alpha-beta visits children left to right."
               + center(tikz_gtree(tp, "blank", dx=0.95, leaf_index=True)))
    E.sub(r"For which values of $x$ are leaves \#4 and \#5 pruned?",
          r"After B, $\alpha=\min(7,x)$. C sees leaf \#3 $=5$, so it is cut off iff $5\le\min(7,x)$, i.e.\ $\mathbf{x\ge5}$.", 1.4)
    E.sub(r"Is leaf \#8 ever evaluated?",
          r"\textbf{Never}: $\alpha\ge5$ when D is entered; after 8 and then 4, $v_D=4\le\alpha$, so leaf \#8 (10) is pruned.", 1.2)
    E.sub(r"Give the root value as a function of $x$ and say for which $x$ MAX chooses B.",
          r"Root $=\max(\min(7,x),5,4)$: $5$ if $x\le5$; $x$ if $5\le x\le7$; $7$ if $x\ge7$. MAX chooses B iff $x\ge5$ (tie at $x=5$ keeps the "
          r"left-most child). Checked for $x=0,\dots,12$.", 1.6)

    # Q6 ------------------------------------------------------------------ expectimax with bounds
    t3 = build_tree(("max", [("chance", [6, 9, 6], [1 / 3] * 3), ("chance", [3, 2, 9], [1 / 3] * 3), ("chance", [10, 9, 4], [1 / 3] * 3)]))
    minimax(t3)
    E.question(r"Consider the expectimax tree below; each chance node has three equally likely outcomes."
               + center(tikz_gtree(t3, "blank", dx=1.1, dy=1.4, leaf_index=True)))
    E.sub(r"Calculate the expectimax value of every node.",
          center(tikz_gtree(t3, "minimax", dx=1.1, dy=1.4, leaf_index=True)) + r"B $=7$, C $=14/3\approx4.67$, D $=23/3\approx7.67$; MAX chooses D.", 1.4)
    E.sub(r"Now assume every leaf value is at most 10 (and at least 0). Evaluating leaves left to right, identify the branches that can be pruned and "
          r"explain each.",
          r"After B, $\alpha=7$. At C, after leaves 3 and 2 the best possible value is $(3+2+10)/3=5\le7$ $\Rightarrow$ \textbf{prune leaf \#6}. "
          r"At D, after 10 the bound is $10$, after 9 it is $9.67$, both $>7$, so leaf \#9 must be seen. Only leaf \#6 is pruned. Without an upper "
          r"bound on the values no pruning is possible.", 2.0)

    # Q7 ------------------------------------------------------------------ MCTS
    E.newpage("exam")
    em = {"R": ["A", "B", "C"], "A": ["A1", "A2"], "B": ["B1", "B2"], "C": ["C1", "C2"], "A1": ["A3", "A4"], "A2": ["A5", "A6"],
          "B1": ["B3", "B4"], "B2": ["B5", "B6"], "C1": ["C3", "C4"], "C2": ["C5", "C6"]}
    C = math.sqrt(2)
    root = MNode("R")
    mcts_run(root, em, [0, 1, 0, 0.5, 0, 0.5, 0.5, 0.5, 1, 0.5, 0], C, r"\sqrt2")
    given = clone_mcts(root)
    A_, B_, C_ = given.children
    N = given.n
    ua = [(c.name, ucb_tex(c, given, C, r"\sqrt2"), ucb(c, given, C)) for c in given.children]
    sa, sc = math.sqrt(math.log(N) / A_.n), math.sqrt(math.log(N) / C_.n)
    cstar = (C_.t / C_.n - A_.t / A_.n) / (sa - sc)
    q = [0, 0.5, 0]
    log = mcts_run(root, em, q, C, r"\sqrt2")
    E.question(r"Rollouts return 1 (win), 0.5 (draw) or 0 (loss) for the root player. Use $\mathrm{UCB1}=\bar V_i+C\sqrt{\ln N/n_i}$ "
               r"(unvisited $=\infty$, ties to the left; a never-visited leaf is rolled out directly, otherwise all its children are added and the rollout "
               r"starts at the first; $X_1\to X_3,X_4$ and $X_2\to X_5,X_6$ for $X\in\{A,B,C\}$). The current tree is:"
               + center(tikz_mcts(given, scale=0.85, dx=1.75)))
    E.sub(r"With $C=\sqrt2$, calculate UCB1 of $A$, $B$, $C$. Which child is selected? For which values of $C$ would the root select $C$ instead of $A$?",
          "; ".join(r"%s: %s" % (mname(nm), tx) for nm, tx, _ in ua) + r" $\Rightarrow$ \textbf{%s}. " % mname(max(ua, key=lambda x: x[2])[0])
          + r"$C$ is preferred iff $%s+c\sqrt{\ln %d/%d}>%s+c\sqrt{\ln %d/%d}$, i.e.\ $c<\frac{%s-%s}{%.4f-%.4f}\approx\mathbf{%.2f}$: a small constant "
            r"favours exploitation (best average), a large one exploration of the less-visited $A$."
          % (fmt(C_.t / C_.n, 3), N, C_.n, fmt(A_.t / A_.n, 3), N, A_.n, fmt(C_.t / C_.n, 3), fmt(A_.t / A_.n, 3), sa, sc, cstar), 2.4)
    E.sub(r"Perform three iterations whose rollouts return $%s$ (in order); update the statistics and draw the final tree." % r",\ ".join(fmt(v) for v in q),
          mcts_log_tex(log) + r"\par Final tree:" + center(tikz_mcts(root, scale=0.78, dx=1.55)), 8.0)

    # Q8 ------------------------------------------------------------------ map colouring
    E.newpage("exam")
    pos = {"A": (0, 1.2), "B": (1.6, 2.2), "C": (3.4, 2.2), "D": (1.6, 0), "E": (3.4, 0), "F": (5.0, 1.1)}
    map_coloring_question(E, pos, [("A", "B"), ("A", "D"), ("B", "C"), ("B", "D"), ("B", "E"), ("C", "E"), ("C", "F"), ("D", "E"), ("E", "F")])

    # Q9 ------------------------------------------------------------------ cryptarithmetic
    E.newpage("exam")
    E.question(r"Cryptarithmetic: $\;\begin{array}{r} T\,O\\ +\;G\,O\\ \hline O\,U\,T\end{array}\;$ --- distinct letters are distinct digits and "
               r"leading digits are non-zero.")
    E.sub(r"Formulate the CSP: variables (including carries), domains and constraints.",
          r"Variables $T,O,G,U$, carries $C_1,C_2$; domains $\{0..9\}$, carries $\{0,1\}$. Constraints: Alldiff$(T,O,G,U)$; $O+O=T+10C_1$; "
          r"$C_1+T+G=U+10C_2$; $C_2=O$; $T,G,O\neq0$.", 2.0)
    E.sub(r"Solve it by constraint propagation, explaining each deduction.",
          r"$O=C_2\in\{0,1\}$, $O\ne0$ $\Rightarrow O=1$. $2=T+10C_1\Rightarrow T=2, C_1=0$. $2+G=U+10\Rightarrow G=U+8$, so $(G,U)\in\{(8,0),(9,1)\}$; "
          r"$U=1$ clashes with $O$ $\Rightarrow G=8,U=0$: \textbf{21 + 81 = 102}.", 2.4)

    # Q10 ----------------------------------------------------------------- TA scheduling (formulation + AC)
    tn = {"P1": (0, 0), "P2": (1.6, 0), "P3": (3.2, 0), "P4": (4.8, 0), "P5": (6.4, 0)}
    te = [("P1", "P2"), ("P2", "P3"), ("P3", "P4"), ("P4", "P5")]
    avail = {"H": ["P1", "P2", "P4", "P5"], "L": ["P2", "P3"], "M": ["P1", "P3", "P4"]}
    dom = {p: [t for t in ("H", "L", "M") if p in avail[t]] for p in tn}
    csp = CSP(list(tn), dom)
    csp.neq(te)
    q0 = []
    for a, b in te:
        q0 += [(a, b), (b, a)]
    okk, D, tr = ac3(csp, q0)
    E.question(r"Five lab sessions must each be run by one TA, and a TA cannot run two overlapping sessions: P1 8:00--9:30, P2 9:00--10:30, "
               r"P3 9:30--11:00, P4 10:30--12:00, P5 11:30--13:00 (sessions that only touch do not overlap). TA \textbf{H} can run P1, P2, P4, P5; "
               r"\textbf{L} can run P2, P3; \textbf{M} can run P1, P3, P4.", title="Lab scheduling")
    E.sub(r"Formulate the CSP (one variable per session; apply the availability constraints to the domains) and draw the constraint graph.",
          dom_row_table(list(tn), [", ".join(dom[p]) for p in tn]) + r"Binary constraints: " + ", ".join(r"$%s\ne %s$" % e for e in te)
          + center(tikz_cgraph(tn, te, scale=0.85)),
          dom_row_table(list(tn), [""] * 5) + box(2.4))
    E.sub(r"Run AC-3 with the initial queue " + ", ".join(r"$%s\to %s$" % a for a in q0)
          + r". Cross out the values it eliminates from your domains in (a), and give the solution.",
          ac3_table(tr) + dom_row_table(list(tn), [strike_dom(dom[p], D[p]) for p in tn])
          + r"Every domain becomes a singleton: " + ", ".join("%s=%s" % (k, v[0]) for k, v in D.items()) + ".", 5.0)

    # Q11 ----------------------------------------------------------------- theory
    E.newpage("exam")
    E.question(r"Answer the following questions briefly.")
    E.sub(r"Match each field with its contribution to AI: (1) Philosophy, (2) Mathematics, (3) Economics, (4) Neuroscience, (5) Psychology, "
          r"(6) Control theory. (a) neurons as information-processing units; (b) utility and decision theory; (c) logic, reasoning, mind as a physical "
          r"system; (d) maximising an objective function over time; (e) formal proof, algorithms, (in)tractability, probability; (f) how people "
          r"perceive, process information and represent knowledge.", r"(1)c, (2)e, (3)b, (4)a, (5)f, (6)d.", 1.0)
    E.sub(r"Order chronologically and explain the AI winter: Deep Blue beats Kasparov; Dartmouth meeting; McCulloch \& Pitts; AlphaGo beats Lee Sedol; "
          r"Turing's ``Computing Machinery and Intelligence''; the expert-systems boom.",
          r"1943 McCulloch \& Pitts, 1950 Turing, 1956 Dartmouth, 1980--88 expert-systems boom, 1997 Deep Blue, 2016 AlphaGo. The AI winter "
          r"(1988--93) was the bust after the expert-systems boom, when expectations were not met and funding collapsed.", 2.0)
    st = [4, 1, 2, 0, 8, 7, 6, 3, 5]
    gl = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    h1, h2, det = puzzle_h(st, gl)
    E.sub(r"For the 8-puzzle below compute $h_1$ (misplaced tiles) and $h_2$ (total Manhattan distance). Which heuristic dominates the other, and "
          r"what does dominance imply for A*?\par\begin{center}Start: " + puzzle_tex(st) + r"\qquad Goal: " + puzzle_tex(gl) + r"\end{center}",
          r"$h_1=\mathbf{%d}$ (tiles %s); $h_2=\mathbf{%d}$ (%s). $h_2$ dominates $h_1$: every misplaced tile is at Manhattan distance $\ge1$, so "
          r"$h_2(n)\ge h_1(n)$ for all $n$. With both consistent, A* using $h_2$ never expands more nodes than A* using $h_1$, since every node surely "
          r"expanded with $h_2$ ($f<C^*$) is also surely expanded with $h_1$."
          % (h1, ", ".join(str(v) for v, d in det if d > 0), h2, ", ".join("%d:%d" % (v, d) for v, d in det)), 2.4)
    E.sub(r"A CSP has $n=5$ variables with domain size $d=3$. How many leaves does a naive search tree (any unassigned variable at each level) have, "
          r"and how many with backtracking? Which property justifies the difference?",
          r"Naive: $n!\,d^n=120\cdot243=\mathbf{29{,}160}$ leaves for only $d^n=243$ complete assignments. Assignments are \textbf{commutative}, so "
          r"backtracking fixes one variable per level: $d^n=\mathbf{243}$ leaves.", 2.0)

    # Q12 ----------------------------------------------------------------- true / false
    E.question(r"True or false?")
    tf_block(E, [
        (r"Uniform-cost search expands nodes in order of their optimal path cost.", True,
         r"By the separation property, the first time a state is expanded its $g$ is optimal (positive costs)."),
        (r"A* is optimally efficient among optimal algorithms using the same heuristic.", True,
         r"Any such algorithm must expand all nodes with $f<C^*$, otherwise it could miss the optimum."),
        (r"If $h(n)=0$ for every node, A* behaves exactly like UCS.", True, r"$f=g+0=g$."),
        (r"If $h_2$ dominates $h_1$ and both are consistent, A* with $h_2$ never expands more nodes than A* with $h_1$ (ignoring ties).", True,
         r"$h_1\le h_2<C^*-g$ for every node surely expanded with $h_2$."),
        (r"Local beam search with $k$ states is the same as $k$ independent random-restart hill climbs run in parallel.", False,
         r"The $k$ best successors are chosen from the pooled list, so information passes between the threads."),
        (r"The amount of alpha-beta pruning does not depend on the move ordering.", False,
         r"Perfect ordering gives $O(b^{m/2})$, random about $O(b^{3m/4})$, the worst ordering no pruning at all."),
        (r"Against a sub-optimal MIN player, the minimax move always gives MAX the best possible outcome.", False,
         r"MAX does at least as well as against an optimal MIN, but a riskier move may do better."),
        (r"MCTS grows its tree symmetrically, level by level.", False, r"It grows asymmetrically towards the more promising moves."),
        (r"Node consistency concerns binary constraints.", False, r"It concerns unary constraints; arc consistency handles binary ones."),
        (r"The degree heuristic is mainly used as a tie-breaker for MRV.", True,
         r"At the start all domains are full, so MRV ties and degree decides."),
    ])
    return E
