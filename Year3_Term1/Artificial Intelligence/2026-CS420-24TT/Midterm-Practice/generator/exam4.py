from qbank import *
import math


def multiplayer_tikz(tree, solved=None, dx=1.75, dy=1.4):
    players = "ABC"
    L = [r"\begin{tikzpicture}[pn/.style={draw, thick, circle, minimum size=6.6mm, inner sep=0pt, font=\small},"
         r" lv/.style={draw, rectangle, inner sep=2pt, font=\footnotesize}]"]
    cnt = [0]
    pos = {}

    def lay(n, d, path):
        if isinstance(n, tuple):
            pos[path] = (cnt[0] * dx, -d * dy)
            cnt[0] += 1
        else:
            for i, c in enumerate(n):
                lay(c, d + 1, path + (i,))
            xs = [pos[path + (i,)][0] for i in range(len(n))]
            pos[path] = ((xs[0] + xs[-1]) / 2, -d * dy)
    lay(tree, 0, ())
    for d, p in enumerate(players):
        L.append(r"\node[font=\footnotesize, anchor=east] at (-0.6,%.2f) {Player %s};" % (-d * dy, p))

    def nm(path):
        return "p" + "".join(str(i) for i in path)

    def emit(n, d, path):
        x, y = pos[path]
        if isinstance(n, tuple):
            L.append(r"\node[lv] (%s) at (%.2f,%.2f) {$(%s)$};" % (nm(path), x, y, ",".join(map(str, n))))
        else:
            lab = ""
            if solved is not None:
                side = "left" if d > 0 and path[-1] == 0 else "right"
                lab = r", label={[font=\footnotesize\bfseries, text=red!80!black]%s:$(%s)$}" % (side, ",".join(map(str, solved[path])))
            L.append(r"\node[pn%s] (%s) at (%.2f,%.2f) {%s};" % (lab, nm(path), x, y, players[d]))
            for i, c in enumerate(n):
                emit(c, d + 1, path + (i,))
                L.append(r"\draw (%s) -- (%s);" % (nm(path), nm(path + (i,))))
    emit(tree, 0, ())
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


def solve_multi(tree):
    out = {}

    def rec(n, d, path):
        if isinstance(n, tuple):
            out[path] = n
            return n
        vals = [rec(c, d + 1, path + (i,)) for i, c in enumerate(n)]
        best = vals[0]
        for v in vals[1:]:
            if v[d] > best[d]:
                best = v
        out[path] = best
        return best
    rec(tree, 0, ())
    return out


def vacuum():
    def succ(s):
        l, d = s[0], list(s[1:])
        dd = list(d)
        dd[l - 1] = 0
        return [(max(1, l - 1), *d), (min(3, l + 1), *d), (l, *dd)]
    start = (1, 1, 1, 1)
    par = {start: None}
    q = [start]
    while q:
        u = q.pop(0)
        for v in succ(u):
            if v not in par:
                par[v] = u
                q.append(v)
    best = None
    for s in par:
        if s[1:] == (0, 0, 0):
            p = [s]
            while par[p[-1]]:
                p.append(par[p[-1]])
            if best is None or len(p) < len(best):
                best = p
    return len(par), best[::-1]


def build():
    E = Exam(4)

    # Q1 ------------------------------------------------------------------ formulation
    nreach, vp = vacuum()
    E.question(r"A vacuum-cleaner robot lives in a row of \textbf{three} cells (1, 2, 3). Each cell is either dirty or clean. The robot can move "
               r"Left, move Right, or Suck (clean its current cell).", title="Vacuum world with three cells")
    E.sub(r"Consider a state as a tuple of values. Which values should be included in the tuple?",
          r"$(\ell, d_1, d_2, d_3)$: robot location $\ell\in\{1,2,3\}$ and the dirt status of each cell.", 0.9)
    E.sub(r"Define the initial state (robot in cell 1, all cells dirty) and the goal state(s).",
          r"Initial $(1,D,D,D)$. Goal: any state with all cells clean, $(\ell,C,C,C)$ for $\ell=1,2,3$ (three goal states).", 0.9)
    E.sub(r"Define the action function. What happens when moving Left in cell 1, Right in cell 3, or Sucking a clean cell?",
          r"Left: $\ell\to\max(1,\ell-1)$; Right: $\ell\to\min(3,\ell+1)$; Suck: $d_\ell\to C$. Those three cases have \emph{no effect} (same state).", 1.4)
    E.sub(r"What is the action cost?", r"1 per action.", 0.6)
    E.sub(r"What is the maximum number of states? How many are reachable from the initial state? Give a shortest solution.",
          r"$3\cdot2^3=\mathbf{24}$ states (in general $n\cdot2^n$); all \textbf{%d} are reachable from $(1,D,D,D)$. Shortest solution (%d actions): "
          r"Suck, Right, Suck, Right, Suck." % (nreach, len(vp) - 1), 1.4)

    # Q2 ------------------------------------------------------------------ two goals
    nodes = {"S": (0, 0, 11, "left"), "A": (2.0, 1.7, 5, "above"), "B": (2.0, -1.7, 5, "below"), "C": (4.0, 2.6, 8, "above"),
             "D": (4.0, 0, 5, "below"), "E": (4.0, -2.6, 3, "below"), "F": (6.0, 1.4, 2, "above"), "H": (6.0, -1.4, 6, "below"),
             "G1": (8.0, 2.6, 0, "right"), "G2": (8.0, -1.4, 0, "right")}
    edges = [("S", "A", 6), ("S", "B", 8), ("A", "C", 3), ("A", "D", 1), ("B", "D", 9), ("B", "E", 4), ("C", "F", 8), ("C", "G1", 8),
             ("D", "F", 3), ("D", "H", 8), ("E", "H", 6), ("F", "G1", 4), ("H", "G2", 6), ("E", "G2", 4)]
    g = Graph(nodes, edges, "S", ["G1", "G2"])
    rb, rd, ru, rg, ra = graph_search_question(E, g, r"Consider the undirected graph below with initial state $S$ and \textbf{two} goal states "
                                                     r"$G_1$, $G_2$; a search stops at whichever goal satisfies its goal test first. ")
    chk = check_h(g)
    E.sub(r"With several goals, what must an admissible heuristic estimate? Is $h$ admissible and consistent?",
          r"The cost to the \emph{nearest} goal. $h^*$: " + ", ".join(r"%s$=%s$" % (k, fmt(v)) for k, v in chk["hstar"].items())
          + r"; $h\le h^*$ (admissible) and $h(u)\le c(u,v)+h(v)$ on every edge (consistent).", 1.6, label="(d)")
    E.sub(r"Which goal does each strategy reach? Why does greedy best-first search end at a different goal from A*?",
          ", ".join(r"%s$\to$%s" % (a, r["path"][-1]) for a, r in zip(["BFS", "UCS", "DFS", "GBFS", "A*"], (rb, ru, rd, rg, ra)))
          + r". GBFS only follows $h$: after the tie $A/B$ ($h=5$) and then $B/D$ (alphabetical), it expands $B$, whose child $E$ leads straight to $G_2$ "
            r"(cost %s). A* also counts the cost already paid and finds the cheaper route to $G_1$ (cost %s)." % (fmt(g.path_cost(rg["path"])), fmt(ra["cost"])),
          1.8, label="(e)")

    # Q3 ------------------------------------------------------------------ hill climbing
    E.newpage("exam")
    hill8_question(E, (1, 2, 5, 3, 0, 4, 6, 7, 8), (0, 1, 2, 3, 4, 5, 6, 7, 8))

    # Q4 ------------------------------------------------------------------ minimax + right-to-left
    E.newpage("exam")
    vals = iter([26, 2, 27, 8, 17, 15, 5, 18, 34, 29, 14, 28, 31, 40, 10, 36, 30, 20])
    t1 = build_tree([[[next(vals), next(vals)] for _ in range(3)] for _ in range(3)], "max")
    ab1 = minimax_question(E, t1, r"Consider the following game tree (MAX at the root).", dx=0.85, rotate=False)
    ab1r = alphabeta(t1, reverse=True)
    E.sub(r"Run alpha-beta again, this time visiting the children of every node from \textbf{right to left}. Which leaves are pruned now? Explain the "
          r"difference.",
          center(tikz_gtree(t1, "ab", ab=ab1r, dx=0.85, leaf_index=True)) + ab_prune_text(ab1r)
          + r"Pruned leaves: %s (%d) instead of %d. Going right to left, MAX first explores %s, the best child (value %s), so $\alpha$ is high at once "
            r"and the other MIN nodes are cut as soon as a child is $\le\alpha$: good move ordering is what makes alpha-beta efficient."
          % (", ".join("\\#" + l.name for l in ab1r["pruned_leaves"]), len(ab1r["pruned_leaves"]), len(ab1["pruned_leaves"]),
             t1.children[-1].name, fmt(t1.children[-1].mm)),
          4.0)

    # Q5 ------------------------------------------------------------------ MIN root
    E.newpage("exam")
    v2 = iter([24, 25, 9, 7, 4, 1, 30, 27, 11, 26, 6, 13, 39])
    t2 = build_tree([[[next(v2), next(v2)], [next(v2), next(v2)], [next(v2), next(v2)]],
                     [[next(v2), next(v2)], [next(v2), next(v2), next(v2)], [next(v2), next(v2)]]], "min")
    alphabeta_question(E, t2, r"Consider the game tree below, in which \textbf{MIN moves first}.", dx=0.9, who="MIN")

    # Q6 ------------------------------------------------------------------ multiplayer
    mt = [[[(1, 2, 6), (4, 2, 3)], [(6, 1, 2), (7, 4, 1)]], [[(5, 1, 1), (5, 5, 5)], [(7, 7, 1), (2, 3, 4)]]]
    ms = solve_multi(mt)
    E.question(r"Three players A, B, C move in turn. Each leaf gives the utility vector $(u_A,u_B,u_C)$ and every player maximises its own component."
               + center(multiplayer_tikz(mt)))
    E.sub(r"Back up the utility vectors to every node. Which move does A make?",
          center(multiplayer_tikz(mt, ms)) + r"Root $=(%s)$: A moves to the right subtree (A gets %d instead of %d)." % (",".join(map(str, ms[()])), ms[()][0], ms[(0,)][0]),
          1.4)
    E.sub(r"The game is not zero-sum. Explain, using this tree, why alliances may form and why they may be broken.",
          r"$(5,5,5)$ is good for everybody, so A and B both prefer the right subtree: collaboration can arise. But each player keeps an alliance only "
          r"while it serves its own utility: at the right-most C node, C prefers $(2,3,4)$ to $(7,7,1)$, which A and B would both like.", 1.8)

    # Q7 ------------------------------------------------------------------ MCTS
    E.newpage("exam")
    em = {"R": ["A", "B"]}
    for a in "AB":
        em[a] = [a + str(i) for i in (1, 2, 3)]
        for i in (1, 2, 3):
            em[a + str(i)] = [a + str(i) + str(j) for j in (1, 2)]
            for j in (1, 2):
                em[a + str(i) + str(j)] = [a + str(i) + str(j) + str(k) for k in (1, 2)]
    root = MNode("R")
    mcts_run(root, em, [4, 4, 9, 2, 4, 3, 7, 7, 5], 2, "2")
    given = clone_mcts(root)
    q = [0, 1, 10]
    log = mcts_run(root, em, q, 2, "2")
    E.question(r"Consider the MCTS tree below; rewards are scores in $[0,10]$ for the root player. Use $\mathrm{UCB1}=\bar V_i+C\sqrt{\ln N/n_i}$ "
               r"with $C=2$ (unvisited $=\infty$, ties to the left; a never-visited leaf is rolled out directly, otherwise all its children are added and "
               r"the rollout starts at the first). Expansion: $A\to A_1,A_2,A_3$; $B\to B_1,B_2,B_3$; $X_i\to X_{i1},X_{i2}$; $X_{ij}\to X_{ij1},X_{ij2}$."
               + center(tikz_mcts(given, scale=0.85, dx=1.8)))
    E.sub(r"Perform three iterations whose rollouts return $%s$ (in order). Give the UCB1 values at every selection step and draw the final tree."
          % r",\ ".join(map(str, q)),
          mcts_log_tex(log) + r"\par Final tree:" + center(tikz_mcts(root, scale=0.75, dx=1.55)), 9.0)
    N = root.n

    def lcb(c):
        return c.t / c.n - 2 * math.sqrt(math.log(N) / c.n)
    mx = max(root.children, key=lambda c: c.t / c.n)
    rb_ = max(root.children, key=lambda c: c.n)
    sc_ = max(root.children, key=lambda c: lcb(c))
    E.sub(r"Which root action is chosen by the \emph{max child}, \emph{robust child} and \emph{secure child} rules (secure: maximise "
          r"$\bar V_i-C\sqrt{\ln N/n_i}$, $C=2$)? What does \emph{max-robust child} recommend?",
          r"Averages " + ", ".join(r"%s: %.2f" % (mname(c.name), c.t / c.n) for c in root.children) + r" $\Rightarrow$ max child \textbf{%s}; " % mname(mx.name)
          + r"visits " + ", ".join(r"%s: %d" % (mname(c.name), c.n) for c in root.children) + r" $\Rightarrow$ robust child \textbf{%s}; " % mname(rb_.name)
          + r"lower bounds " + ", ".join(r"%s: %.2f" % (mname(c.name), lcb(c)) for c in root.children) + r" $\Rightarrow$ secure child \textbf{%s}. " % mname(sc_.name)
          + r"Max and robust disagree, so max-robust says to keep searching until one child is best in both.", 1.8)

    # Q8 ------------------------------------------------------------------ map colouring
    E.newpage("exam")
    pos = {"A": (0, 1.1), "B": (1.6, 2.2), "C": (1.6, 0), "D": (3.2, 1.1), "E": (3.2, -1.0), "F": (4.8, 0.1)}
    map_coloring_question(E, pos, [("A", "B"), ("A", "C"), ("A", "D"), ("B", "C"), ("C", "D"), ("C", "E"), ("D", "E"), ("D", "F"), ("E", "F")])

    # Q9 ------------------------------------------------------------------ 4-queens FC
    E.newpage("exam")
    V = ["Q1", "Q2", "Q3", "Q4"]
    csp = CSP(V, {v: [1, 2, 3, 4] for v in V})
    for i in range(4):
        for j in range(i + 1, 4):
            csp.add(V[i], V[j], (lambda d: (lambda a, b: a != b and abs(a - b) != d))(j - i))
    sol, tr = backtrack_fc(csp, "static", "given", "fc")
    E.question(r"4-queens as a CSP: variable $Q_i$ is the row of the queen in column $i$, with domain $\{1,2,3,4\}$.")
    E.sub(r"Write the constraints.", r"For all $i<j$: $Q_i\ne Q_j$ and $|Q_i-Q_j|\ne j-i$ (columns are distinct by construction).", 1.0)
    E.sub(r"Solve with backtracking and \emph{forward checking}, variables in the order $Q_1,\dots,Q_4$, values in increasing order. Give the domains "
          r"after every assignment and draw the search tree, marking the wipe-outs.",
          bt_table(csp, tr) + center(bt_search_tree_tikz(tr, scale=1.0, dx=2.1))
          + r"Solution: " + ", ".join(r"$Q_%s=%d$" % (k[1], sol[k]) for k in V) + r" (its mirror image $(3,1,4,2)$ is the other solution).", 7.5)

    # Q10 ----------------------------------------------------------------- AC vs FC
    cg = {"A": (0, 1.2), "B": (1.6, 2.2), "C": (1.6, 0.2), "F": (-1.6, 1.2), "D": (3.3, 2.2), "E": (3.3, 0.2)}
    ce = [("A", "B"), ("A", "C"), ("A", "F"), ("B", "C"), ("B", "D"), ("C", "E"), ("D", "E")]
    adj = {v: set() for v in cg}
    for a, b in ce:
        adj[a].add(b)
        adj[b].add(a)
    E.question(r"The constraint graph below has only binary constraints and no variable is assigned initially. For each independent scenario, list "
               r"every variable whose domain \emph{might} change." + center(tikz_cgraph(cg, ce, scale=0.85)))
    E.sub(r"A value is assigned to A and forward checking is run for A.", r"Neighbours of A: \textbf{%s}." % ", ".join(sorted(adj["A"])), 0.8)
    E.sub(r"A is assigned and forward checking is run; then B is assigned and forward checking is run for B.",
          r"Unassigned neighbours of B: \textbf{%s}." % ", ".join(sorted(adj["B"] - {"A"})), 0.8)
    E.sub(r"A is assigned and arc consistency is enforced.",
          r"Propagation reaches the whole connected component: \textbf{%s}." % ", ".join(sorted(reachable_avoiding(adj, "A", set()))), 0.8)
    E.sub(r"A is assigned and arc consistency is enforced; then B is assigned and arc consistency is enforced again.",
          r"\textbf{%s}: propagation from B continues through unassigned variables only. F is reachable only through A, whose single value is already "
          r"consistent, so A cannot change and no arc into F is re-examined." % ", ".join(sorted(reachable_avoiding(adj, "B", {"A"}))), 1.2)

    # Q11 ----------------------------------------------------------------- theory
    E.newpage("exam")
    E.question(r"Answer the following questions briefly.")
    E.sub(r"Describe the ``laws of thought'' approach with a syllogism, and give the two obstacles the lecture mentions.",
          r"Irrefutable reasoning: \emph{All men are mortal; Socrates is a man; so Socrates is mortal}. Obstacles: not all intelligent behaviour is "
          r"mediated by logic, and solving a problem ``in principle'' differs from solving it in practice (intractability).", 2.0)
    E.sub(r"On a 4-connected grid, compare the number of leaves of a depth-20 search tree with the number of distinct states within 20 steps "
          r"(about $2d^2$). What does this say about tree-search vs graph-search?",
          r"$4^{20}\approx10^{12}$ leaves vs $\approx800$ states: almost all nodes are redundant paths, so graph-search (remembering reached states) "
          r"turns an intractable search into an easy one.", 1.8)
    ps = [(t, math.exp(-3.0 / t)) for t in (10, 3, 1)]
    E.sub(r"In simulated annealing a successor is $\Delta E=-3$ worse than the current state. Compute its acceptance probability at $T=10$, $3$, $1$. "
          r"Why is simulated annealing better than plain hill climbing?",
          ", ".join(r"$T=%d$: $e^{-3/%d}=%.3f$" % (t, t, p) for t, p in ps)
          + r". Early random downhill moves let it escape local maxima; as $T$ decreases it behaves like hill climbing.", 1.8)
    E.sub(r"With perfect move ordering, how many nodes does alpha-beta examine? Evaluate the effective branching factor for chess ($b\approx35$) "
          r"and name two move-ordering techniques.",
          r"$O(b^{m/2})$, effective branching factor $\sqrt{35}\approx5.9$. Killer-move heuristic; transposition tables.", 1.6)

    # Q12 ----------------------------------------------------------------- true / false
    E.question(r"True or false?")
    tf_block(E, [
        (r"In graph search the frontier separates the expanded (interior) region from the unreached (exterior) region.", True,
         r"Graph-search separation property: every path to an unreached state passes through the frontier."),
        (r"For BFS, memory is a bigger problem than execution time.", True, r"All generated nodes are kept: $O(b^d)$ memory runs out first."),
        (r"A* graph search with a consistent heuristic never needs to re-expand a state.", True,
         r"The first time a state is expanded it is on an optimal path, so no cheaper path is found later."),
        (r"A* with an inadmissible heuristic can never return an optimal solution.", False,
         r"It may, e.g.\ if all nodes on an optimal path have admissible $h$ values."),
        (r"For the 8-puzzle, $h=\max\{2,h_{\text{Manhattan}}\}$ is admissible.", False, r"At the goal $h=2>0$."),
        (r"For the 8-puzzle, $h=\min\{2,h_{\text{Manhattan}}\}$ is admissible.", True, r"$h\le h_{\text{Manhattan}}\le h^*$."),
        (r"Pruning in expectimax is possible only if the leaf values are known to lie in a bounded range.", True,
         r"Otherwise an unseen outcome could always raise the average above any bound."),
        (r"In UCB1, increasing $C$ makes MCTS more exploratory.", True, r"$C$ scales the exploration term $\sqrt{\ln N/n_i}$."),
        (r"The least-constraining-value heuristic tries first the value that rules out the most choices for the neighbours.", False,
         r"It prefers the value ruling out the \emph{fewest} (fail-last)."),
        (r"Any constraint over more than two variables can be transformed into binary constraints.", True,
         r"As stated in the lecture (e.g.\ by introducing auxiliary variables)."),
    ])
    return E
