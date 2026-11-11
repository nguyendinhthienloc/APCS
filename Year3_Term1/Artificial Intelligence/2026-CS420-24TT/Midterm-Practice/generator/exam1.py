from qbank import *


def jug_space():
    start = (0, 0)
    seen = {start: None}
    q = [start]
    while q:
        x, y = q.pop(0)
        nxt = [(4, y), (x, 3), (0, y), (x, 0)]
        t = min(x, 3 - y)
        nxt.append((x - t, y + t))
        t = min(y, 4 - x)
        nxt.append((x + t, y - t))
        for s in nxt:
            if s not in seen:
                seen[s] = (x, y)
                q.append(s)
    goal = min((s for s in seen if s[0] == 2), key=lambda s: _depth(seen, s))
    path = [goal]
    while seen[path[-1]] is not None:
        path.append(seen[path[-1]])
    return len(seen), path[::-1]


def _depth(par, s):
    d = 0
    while par[s] is not None:
        s = par[s]
        d += 1
    return d


def build():
    E = Exam(1)

    # Q1 ------------------------------------------------------------------ formulation
    nreach, jp = jug_space()
    E.question(r"You have a 4-litre jug and a 3-litre jug, both initially empty, and a tap with unlimited water. You may fill a jug from the tap, "
               r"empty a jug onto the ground, or pour one jug into the other until the source is empty or the destination is full. The goal is to have "
               r"\emph{exactly 2 litres in the 4-litre jug}.", title="The two-jug problem")
    E.sub(r"Consider a state as a tuple of values. Which values should be included in the tuple?",
          r"$(x, y)$: litres in the 4-L jug ($x\in\{0,\dots,4\}$) and in the 3-L jug ($y\in\{0,\dots,3\}$).", 1.0)
    E.sub(r"Define the initial state and the goal state(s).", r"Initial $(0,0)$. Goal: any state with $x=2$, i.e.\ $(2,y)$ for $y=0..3$.", 1.0)
    E.sub(r"Define the action function (preconditions and effects of every action).",
          r"Fill4: $x<4 \Rightarrow (4,y)$; Fill3: $y<3\Rightarrow(x,3)$; Empty4: $x>0\Rightarrow(0,y)$; Empty3: $y>0\Rightarrow(x,0)$; "
          r"Pour4$\to$3: $x>0, y<3$, $t=\min(x,3-y)\Rightarrow(x-t,\,y+t)$; Pour3$\to$4: $y>0,x<4$, $t=\min(y,4-x)\Rightarrow(x+t,\,y-t)$.", 2.0)
    E.sub(r"What is the action cost?", r"Each action costs 1 (path cost = number of actions).", 0.8)
    E.sub(r"What is the maximum number of states in the state space? How many are reachable from the initial state? Give a shortest solution.",
          r"$5\times4=\mathbf{20}$ tuples. Reachable from $(0,0)$: \textbf{%d} (every reachable state has at least one jug empty or full). "
          r"Shortest solution (%d actions): %s." % (nreach, len(jp) - 1, r" $\to$ ".join("(%d,%d)" % s for s in jp)), 2.0)

    # Q2 ------------------------------------------------------------------ graph search
    nodes = {"S": (0, 0, 8, "left"), "A": (2, 1.6, 13, "above"), "B": (2, -1.6, 8, "below"),
             "C": (4.2, 2.3, 7, "above"), "D": (4.2, 0, 8, "below"), "E": (4.2, -2.3, 15, "below"),
             "F": (6.4, 1.3, 2, "above"), "H": (6.4, -1.3, 7, "below"), "G": (8.4, 0, 0, "right")}
    edges = [("S", "A", 6), ("S", "B", 1), ("A", "C", 6), ("A", "D", 7), ("B", "D", 1), ("B", "E", 8),
             ("C", "F", 5), ("D", "F", 9, "pos=0.4"), ("D", "H", 2), ("E", "H", 8), ("F", "G", 4), ("H", "G", 7), ("C", "D", 1)]
    g = Graph(nodes, edges, "S", ["G"])
    rb, rd, ru, rg, ra = graph_search_question(E, g, r"Consider the undirected graph below; $S$ is the initial state and $G$ the goal state. "
                                                     r"Step costs are written on the edges and the heuristic $h$ next to the vertices. ")
    chk = check_h(g)
    E.sub(r"Is $h$ admissible? Justify.",
          r"True costs $h^*$: " + ", ".join(r"%s$=%s$" % (k, fmt(v)) for k, v in chk["hstar"].items())
          + r". $h(n)\le h^*(n)$ for every $n$ $\Rightarrow$ \textbf{admissible}.", 1.5, label="(d)")
    E.sub(r"Is $h$ consistent? Justify.",
          r"$h(u)\le c(u,v)+h(v)$ holds on every edge in both directions (tight: "
          + ", ".join(r"$h(%s)=c(%s,%s)+h(%s)$" % (u, u, v, v) for u in g.adj for v, c in g.nbrs(u) if g.h(u) == c + g.h(v))
          + r") $\Rightarrow$ \textbf{consistent}.", 1.5, label="(e)")
    E.sub(r"Which of the five strategies returned an optimal path here, and which of them are guaranteed to do so?",
          r"Optimal cost %s. UCS and A* found it; BFS (cost %s), DFS (%s) and GBFS (%s) did not. UCS (positive costs) and A* with an admissible/"
          r"consistent heuristic are guaranteed optimal; BFS only when all step costs are equal; DFS and GBFS never."
          % (fmt(ru["cost"]), fmt(g.path_cost(rb["path"])), fmt(g.path_cost(rd["path"])), fmt(g.path_cost(rg["path"]))), 1.5, label="(f)")

    # Q3 ------------------------------------------------------------------ hill climbing
    E.newpage("exam")
    hill8_question(E, (1, 2, 3, 6, 0, 4, 8, 7, 5), (1, 2, 3, 8, 0, 4, 7, 6, 5))

    # Q4 ------------------------------------------------------------------ minimax / alpha-beta
    E.newpage("exam")
    t1 = build_tree([[[8, 16, 11], [21, 6]], [[24, 1], [30, 19], [25, 29]], [[12, 18], [26, 23, 7]]], "max")
    minimax_question(E, t1, r"Consider the following game tree. The root is a MAX node and the search always visits children left to right "
                            r"(small grey numbers are leaf indices).")

    # Q5 ------------------------------------------------------------------ deep cut-offs
    E.newpage("exam")
    t2 = build_tree([[[[22, 12], [9, 17]], [[16, 19], [10, 7]]], [[[2, 26], [24, 21]], [[4, 6], [14, 23]]]], "max")
    minimax(t2)
    ab2 = alphabeta(t2)
    deep = [p for p in ab2["prunes"] if p["deep"]]
    alphabeta_question(E, t2, r"Consider the following 4-ply game tree (MAX at the root).", dx=0.85,
                       extra_sol=r"\par\textbf{Deep cut-offs} at %s: the bound $\alpha=%s$ was set at the root A, several levels above, "
                                 r"while their own parents had not found anything yet." % (" and ".join(p["node"].name for p in deep), fmt(deep[0]["bound"])))
    E.sub(r"Which of the cut-offs are \emph{deep} cut-offs (the bound was set by an ancestor that is not the node's parent)?",
          r"%s (bound from A); the others (%s) use a bound set by the parent." % (", ".join(p["node"].name for p in deep),
                                                                              ", ".join(p["node"].name for p in ab2["prunes"] if not p["deep"])), 1.0)

    # Q6 ------------------------------------------------------------------ MCTS
    E.newpage("exam")
    em = {"S0": ["S1", "S2"], "S1": ["S3", "S4"], "S2": ["S5", "S6"], "S3": ["S7", "S8"],
          "S4": ["S9", "S10"], "S5": ["S11", "S12"], "S6": ["S13", "S14"]}
    rolls = [10, 7, 11, 4, 4, 3, 1]
    root = MNode("S0")
    log = mcts_run(root, em, rolls, 2, "2")
    E.question(r"Run Monte Carlo Tree Search from a tree that contains only the root $S_0$ ($t=0$, $n=0$), exactly as in the lecture walkthrough. "
               r"Use $\mathrm{UCB1}(S_i)=\bar V_i + C\sqrt{\ln N/n_i}$ with $C=2$ (an unvisited node has $\mathrm{UCB1}=\infty$; ties go to the left-most node). "
               r"A leaf that has never been visited is rolled out directly; otherwise all its children are added and the rollout starts at the first one. "
               r"Every state has two actions: $S_0\to S_1,S_2$; $S_1\to S_3,S_4$; $S_2\to S_5,S_6$; $S_3\to S_7,S_8$; $S_4\to S_9,S_{10}$; $S_5\to S_{11},S_{12}$. "
               r"The rollouts of iterations 1--7 return, in order: $%s$." % r",\ ".join(str(r) for r in rolls))
    E.sub(r"Perform the 7 iterations. Give the UCB1 values compared at every selection step and draw the final tree with $t$ and $n$ for every node.",
          mcts_log_tex(log) + r"\par Final tree:" + center(tikz_mcts(root, scale=0.85, dx=1.8)), 11.0)
    a, b = root.children
    E.sub(r"Which action is recommended at the root by the \emph{max child} rule, and which by the \emph{robust child} rule?",
          r"Averages: $S_1$: $%s/%d=%s$, $S_2$: $%s/%d=%s$ $\Rightarrow$ max child \textbf{$S_1$}. Visits: $S_1$: %d, $S_2$: %d $\Rightarrow$ robust child "
          r"\textbf{$S_2$}. The rules disagree, so max-robust would continue the search." % (fmt(a.t), a.n, fmt(a.t / a.n), fmt(b.t), b.n, fmt(b.t / b.n), a.n, b.n),
          1.2)

    # Q7 ------------------------------------------------------------------ map colouring
    E.newpage("exam")
    pos = {"A": (0, 1), "B": (1.6, 2.1), "C": (1.6, -0.1), "D": (3.2, 1.6), "E": (3.2, -0.6), "F": (4.8, 0.5)}
    map_coloring_question(E, pos, [("A", "B"), ("A", "C"), ("B", "C"), ("B", "D"), ("C", "D"), ("C", "E"), ("D", "E"), ("D", "F"), ("E", "F")])

    # Q8 ------------------------------------------------------------------ CSP formulation
    E.newpage("exam")
    dom = {"S": ["ai", "math", "phys"], "P": ["library", "cafe", "home"], "T": ["morning", "afternoon", "evening"], "F": ["pizza", "salad", "noodles"]}
    csp = CSP(["S", "P", "T", "F"], dom)
    csp.add("P", "T", lambda p, t: p != "library" or t in ("morning", "afternoon"))
    csp.add("S", "T", lambda s, t: s != "math" or t == "morning")
    csp.add("P", "F", lambda p, f: p != "library" or f != "pizza")
    csp.add("S", "P", lambda s, p: s != "ai" or p != "cafe")
    D0 = {k: list(v) for k, v in dom.items()}
    D0["T"] = ["evening"]
    okk, D, _ = ac3(csp, None, D0)
    sols = [(s, p, f) for s in D["S"] for p in D["P"] for f in D["F"]
            if csp.ok("S", s, "P", p) and csp.ok("P", p, "F", f) and csp.ok("S", s, "T", "evening") and csp.ok("P", p, "T", "evening")]
    E.question(r"You are planning a study session with four decisions: the (S)ubject, the (P)lace, the (T)ime and the (F)ood. The candidates are "
               r"S $\in\{$\emph{ai, math, phys}$\}$, P $\in\{$\emph{library, cafe, home}$\}$, T $\in\{$\emph{morning, afternoon, evening}$\}$, "
               r"F $\in\{$\emph{pizza, salad, noodles}$\}$, with the constraints: (1) the library is open only in the morning or afternoon; "
               r"(2) math must be studied in the morning; (3) pizza is not allowed in the library; (4) AI cannot be studied at the cafe (no sockets).",
               title="Planning a study session")
    E.sub(r"Formulate the problem as a CSP: variables, domains and binary constraints.",
          dom_row_table(["S", "P", "T", "F"], [", ".join(dom[v]) for v in "SPTF"])
          + r"Binary constraints: (1) between P and T, (2) between S and T, (3) between P and F, (4) between S and P.",
          dom_row_table(["S", "P", "T", "F"], ["", "", "", ""]) + r"Binary constraints:" + box(1.2))
    E.sub(r"Draw the constraint graph.", center(tikz_cgraph({"S": (0, 1.2), "T": (2, 1.2), "P": (1, 0), "F": (3, 0)},
                                                        [("S", "T"), ("S", "P"), ("P", "T"), ("P", "F")], scale=0.9)), 2.6)
    E.sub(r"You decide to study in the \emph{evening}. Cross out the eliminated values to show the domains after arc consistency has been enforced.",
          dom_row_table(["S", "P", "T", "F"], [strike_dom(dom[v], D[v], "evening" if v == "T" else None) for v in "SPTF"])
          + r"(1) removes \emph{library}; (2) removes \emph{math}; then no other arc can remove anything: \emph{ai} still has support "
            r"\emph{home}, and \emph{pizza} has support \emph{cafe}/\emph{home}.",
          dom_row_table(["S", "P", "T", "F"], [", ".join(dom[v]) for v in "SPTF"]))
    E.sub(r"Give one solution, or state that none exists.",
          r"For example S=%s, P=%s, T=evening, F=%s (there are %d solutions with T=evening)." % (sols[0][0], sols[0][1], sols[0][2], len(sols)), 0.8)

    # Q9 ------------------------------------------------------------------ theory
    E.newpage("exam")
    E.question(r"Answer the following questions briefly.")
    E.sub(r"Russell \& Norvig organise definitions of AI into four categories. Name them, state which one this course adopts and give two reasons.",
          r"Thinking humanly (cognitive modelling), thinking rationally (laws of thought), acting humanly (Turing test), acting rationally "
          r"(\textbf{rational agent} --- adopted). Reasons: it is more general than the laws-of-thought approach (correct inference is only one way to "
          r"act rationally; sometimes something must be done with no provably correct choice), and rationality is mathematically well defined, so it is "
          r"more amenable to scientific development than approaches based on human behaviour or thought.", 2.6)
    E.sub(r"Explain the difference between the state space and the search tree, and between tree-search and graph-search algorithms.",
          r"The state space is the graph of world states and actions (each state once). The search tree contains paths from the initial state; a "
          r"state may appear in many nodes. Tree-search does not check redundant paths; graph-search keeps a \emph{reached} table and only the best "
          r"path to each state. Tree-search suits formulations where redundant paths are rare, or when memory is too small for the reached table.", 2.6)
    E.sub(r"For a uniform tree with branching factor $b=5$ and the shallowest goal at depth $d=4$, how many nodes does BFS generate in the worst "
          r"case? Why is memory a bigger problem than time for BFS?",
          r"$b+b^2+b^3+b^4=5+25+125+625=\mathbf{780}$. All generated nodes stay in memory ($O(b^d)$ space as well as time), and memory is "
          r"exhausted long before the time limit (lecture table: terabytes needed at depth 10--12).", 1.8)
    E.sub(r"Name three landscape features on which hill climbing gets stuck. If one run succeeds with probability $p=0.14$, how many restarts "
          r"does random-restart hill climbing need on average?",
          r"Local maxima, ridges, plateaux (flat local maxima / shoulders). Expected restarts $1/p\approx\mathbf{7}$.", 1.5)
    E.sub(r"Why should variable selection in backtracking be fail-first while value selection is fail-last?",
          r"All variables must be assigned anyway, so a doomed branch should fail as early as possible (MRV/degree prune big subtrees). For values we "
          r"need only one solution, so we try the value most likely to succeed (LCV keeps the most options for the neighbours).", 1.8)

    # Q10 ----------------------------------------------------------------- true / false
    E.question(r"True or false?")
    tf_block(E, [
        (r"BFS is cost-optimal whenever all action costs are strictly positive.", False,
         r"BFS returns the shallowest goal; it is optimal only when all step costs are equal (e.g.\ $S\to G$ costing 10 vs $S\to A\to G$ costing 2)."),
        (r"Uniform-cost search applies the goal test when a node is generated.", False,
         r"It tests when the node is removed from the frontier; testing at generation could return a more expensive path."),
        (r"Every consistent heuristic is admissible.", True,
         r"Summing $h(n_i)\le c(n_i,n_{i+1})+h(n_{i+1})$ along an optimal path gives $h(n)\le h^*(n)$ since $h(\text{goal})=0$."),
        (r"If $h_1$ and $h_2$ are admissible, then $\max\{h_1,h_2\}$ is admissible and dominates both.", True,
         r"At each node it equals one of two lower bounds, and it is $\ge$ each of them by definition."),
        (r"Greedy best-first (graph) search is complete in infinite state spaces.", False,
         r"Only in finite spaces; in an infinite space it can follow an infinite path along which $h$ keeps decreasing."),
        (r"A poor move ordering may make alpha-beta return a different root value than minimax.", False,
         r"Alpha-beta prunes only branches that cannot affect the decision; ordering changes only how much is pruned."),
        (r"With perfect move ordering alpha-beta examines $O(b^{m/2})$ nodes.", True,
         r"The effective branching factor becomes $\sqrt b$, so it can search about twice as deep as minimax in the same time."),
        (r"In MCTS with UCB1, once a node has children, each of them is selected at least once before any of them is selected a second time.", True,
         r"An unvisited child has UCB1 $=\infty$."),
        (r"Forward checking detects every inconsistency that arc consistency detects.", False,
         r"FC only prunes neighbours of the variable just assigned; it misses conflicts between two unassigned variables, which AC propagates."),
        (r"In simulated annealing a worse move ($\Delta E<0$) is accepted with probability $e^{\Delta E/T}$, which decreases as $T$ decreases.", True,
         r"E.g.\ $\Delta E=-2$: $T=4\Rightarrow 0.61$, $T=1\Rightarrow0.14$."),
    ])
    return E
