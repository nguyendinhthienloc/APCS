"""Reusable question builders in the review-sheet format."""
from common import *


# ---------------------------------------------------------------- minimax / alpha-beta
def minimax_question(E, root, intro, dx=0.8, rotate=True, who="MAX"):
    minimax(root)
    ab = alphabeta(root)
    E.question(intro + center(tikz_gtree(root, "blank", dx=dx, leaf_index=True)))
    E.sub(r"Compute the final backed-up value of every node using the minimax algorithm (no alpha-beta pruning at this step). "
          r"Which move should %s make at the root?" % who,
          value_table(root, [("Minimax", mm_values(root))]) + center(tikz_gtree(root, "minimax", dx=dx, leaf_index=True))
          + r"Root value $=%s$; %s moves to \textbf{%s}." % (fmt(root.mm), who, ab["best"].name),
          value_table(root, [("Minimax", None)]) + box(0.8))
    E.sub(r"Run alpha-beta pruning (children visited left to right). Give the value computed at every node (mark \textbf{X} if the node is "
          r"never visited), cross out the pruned branches on the tree and briefly explain each case.",
          value_table(root, [(r"$\alpha$-$\beta$", ab_values(root, ab))])
          + r"($\le v$ / $\ge v$: the node was cut off, so only this bound is known; writing the returned number $v$ is also accepted.)"
          + center(tikz_gtree(root, "ab", ab=ab, dx=dx, leaf_index=True))
          + r"$\alpha$ and $\beta$ at every visited node:" + ab_window_table(ab) + ab_prune_text(ab)
          + r"Leaves evaluated: %d of %d." % (len(ab["evaluated"]), len(root.leaves)),
          value_table(root, [(r"$\alpha$-$\beta$", None)]) + box(4.0))
    if rotate:
        rp = build_tree(perfect_order_spec(root), root.kind)
        # keep the original letters on the rotated tree
        orig = {}
        _match_names(root, rp)
        minimax(rp)
        abp = alphabeta(rp)
        E.sub(r"Using the minimax values from (a), and without performing any alpha-beta calculation, rotate the children of each node at every "
              r"level so that alpha-beta prunes as much as possible. Draw the new tree (keep the node letters).",
              r"Best child first for the player to move (MAX: largest value first, MIN: smallest first):"
              + center(tikz_gtree(rp, "ab", ab=abp, dx=dx))
              + r"With this ordering alpha-beta evaluates only \textbf{%d} leaves (instead of %d)." % (len(abp["evaluated"]), len(ab["evaluated"])),
              5.5)
    return ab


def _match_names(orig, rot):
    """rotated tree is built from values only; copy letters by matching subtrees."""
    def sig(n):
        if n.kind == "leaf":
            return ("L", n.value)
        return (n.kind, tuple(sorted(sig(c) for c in n.children)))
    pool = {}
    for n in all_nodes(orig):
        if n.kind != "leaf":
            pool.setdefault(sig(n), []).append(n.name)
    for n in all_nodes(rot):
        if n.kind != "leaf":
            n.name = pool[sig(n)].pop(0)


def alphabeta_question(E, root, intro, dx=0.8, who="MAX", extra_sol=""):
    minimax(root)
    ab = alphabeta(root)
    E.question(intro + center(tikz_gtree(root, "blank", dx=dx, leaf_index=True)))
    E.sub(r"Note the minimax value of every node (no pruning).",
          value_table(root, [("Minimax", mm_values(root))]) + r"Root value $=%s$; %s moves to \textbf{%s}." % (fmt(root.mm), who, ab["best"].name),
          value_table(root, [("Minimax", None)]))
    E.sub(r"Show where alpha-beta pruning occurs (left to right) by crossing out the corresponding branches, and briefly explain each case.",
          center(tikz_gtree(root, "ab", ab=ab, dx=dx, leaf_index=True)) + ab_window_table(ab) + ab_prune_text(ab)
          + r"Leaves evaluated: %d of %d; never evaluated: %s." % (len(ab["evaluated"]), len(root.leaves),
                                                                   ", ".join("\\#" + l.name for l in ab["pruned_leaves"]) or "none") + extra_sol,
          4.5)
    return ab


# ---------------------------------------------------------------- map colouring (review Q6 format)
def map_coloring_question(E, pos, edges, intro_extra=""):
    V = sorted(pos)
    full = ["R", "G", "B"]

    def mk():
        c = CSP(V, {v: list(full) for v in V})
        c.neq(edges)
        return c
    csp = mk()
    E.question(r"This problem is about map colouring. Each region must be coloured Red (R), Green (G) or Blue (B), and neighbouring regions "
               r"must have different colours. The constraint graph is shown below. The following questions are mutually independent." + intro_extra
               + center(tikz_cgraph(pos, edges, scale=0.95)))
    # (a) forward checking after B = R
    fc = fc_after(csp, [("B", "R")])
    blank = [r"R\ G\ B" if v != "B" else r"\textbf{R}" for v in V]
    E.sub(r"\textbf{Cross out} all values that would be eliminated by \emph{forward checking} after variable B has been assigned as shown."
          + dom_row_table(V, blank),
          dom_row_table(V, [strike_dom(full, fc[v], "R" if v == "B" else None) for v in V])
          + r"Only the neighbours of B (%s) lose R." % ", ".join(sorted(csp.nb["B"])),
          "")
    # (b) AC-3 after A=R, B=G
    okk, ac, _ = ac_after(csp, [("A", "R"), ("B", "G")])
    blank = [r"\textbf{R}" if v == "A" else (r"\textbf{G}" if v == "B" else r"R\ G\ B") for v in V]
    E.sub(r"A and B have been assigned as shown, but no constraint propagation has been done yet. \textbf{Cross out} all values that would be "
          r"eliminated by \emph{arc consistency} (AC-3)." + dom_row_table(V, blank),
          dom_row_table(V, [strike_dom(full, ac[v], {"A": "R", "B": "G"}.get(v)) for v in V])
          + r"Propagation continues through the graph (unlike forward checking): every arc $X_i\to X_j$ is revised until no domain changes. "
          + ("Here arc consistency even leaves a single value for every variable." if all(len(d) == 1 for d in ac.values()) else ""),
          "")
    # (c), (d) MRV / degree after A = R with propagation
    fa = fc_after(csp, [("A", "R")])
    un = [v for v in V if v != "A"]
    m_ = min(len(fa[v]) for v in un)
    mrv = [v for v in un if len(fa[v]) == m_]
    deg = {v: sum(1 for w in csp.nb[v] if w != "A") for v in un}
    md = max(deg.values())
    dh = [v for v in un if deg[v] == md]
    cells = [r"\textbf{R}" if v == "A" else r"\ ".join(fa[v]) for v in V]
    E.sub(r"Variable A is already assigned and constraint propagation has been done. \textbf{Circle} all unassigned variables that might be "
          r"selected by the \emph{Minimum-Remaining-Values} (MRV) heuristic." + dom_row_table(V, cells),
          r"Remaining values: " + ", ".join("%s: %d" % (v, len(fa[v])) for v in un) + r" $\Rightarrow$ MRV may select \textbf{%s}." % ", ".join(mrv),
          "")
    E.sub(r"Same situation. \textbf{Circle} all unassigned variables that might be selected by the \emph{Degree Heuristic}." + dom_row_table(V, cells),
          r"Degree = number of constraints with other \emph{unassigned} variables: " + ", ".join("%s: %d" % (v, deg[v]) for v in un)
          + r" $\Rightarrow$ the degree heuristic may select \textbf{%s}." % ", ".join(dh),
          "")
    # (e) full solve
    steps, sol = mrv_dh_steps(mk())
    ex = []
    so = []
    for k, st in enumerate(steps, 1):
        if k < len(steps):
            ex.append(r"\underline{Step %d}\par\begin{center}\small %s\end{center}Assign to the variable \rule{2.5cm}{0.3pt} with the value \rule{2.5cm}{0.3pt}\par" % (k, mrv_step_table(V)))
        else:
            ex.append(r"\underline{Step %d}\par Assign to the variable \rule{2.5cm}{0.3pt} with the value \rule{2.5cm}{0.3pt}\par" % k)
        why = "unique minimum MRV" if not st["dh"] else ("tie on MRV broken by DH" if list(st["dh"].values()).count(max(st["dh"].values())) == 1
                                                          else "tie on MRV and DH, broken alphabetically")
        so.append(r"\underline{Step %d}\par\begin{center}\small %s\end{center}Assign to the variable \textbf{%s} with the value \textbf{%s} (%s). "
                  r"Domains before this step: %s.\par" % (k, mrv_step_table(V, st), st["var"], st["val"], why,
                                                          ", ".join("%s=%s" % (v, "".join(st["D"][v])) for v in V)))
    E.sub(r"Assume no variable has been assigned yet. Solve the CSP using backtracking with \emph{forward checking}, choosing variables with MRV, "
          r"then the degree heuristic (DH), and finally alphabetical order; try values in the order R, G, B. For every step give the MRV value of "
          r"every region not yet coloured, and the DH values of the regions tied on the minimum MRV.",
          "\\par " + "\n".join(so) + r"Solution: " + ", ".join("%s=%s" % (v, sol[v]) for v in V) + ". No backtracking is needed.",
          "\\par " + "\n".join(ex))
    return csp


# ---------------------------------------------------------------- 8-puzzle hill climbing (review Q3 format)
def hill8_question(E, start, goal, intro=""):
    levels, res, _ = hill_climb_8(start, goal)
    assert res == "goal"

    def grid(s):
        return r"\begin{tabular}{|c|c|c|}\hline " + r"\\\hline ".join(" & ".join(str(v) if v else r"--" for v in s[i * 3:i * 3 + 3]) for i in range(3)) + r"\\\hline\end{tabular}"
    E.question(intro + r"Consider the 8-puzzle. Apply \emph{steepest-descent hill climbing} with the Manhattan-distance heuristic $h$ to the "
               r"following pair of initial and goal states."
               + r"\begin{center}Initial state\quad %s\qquad\qquad Goal state\quad %s\end{center}" % (grid(start), grid(goal))
               + r"Your work should: draw the search tree including all successors of every expanded state (moves of the blank in the order Up, Down, "
                 r"Left, Right; do not regenerate the parent state), write the heuristic value of every node, and mark the path found.")
    E.sub("", center(hill_tree_tikz(start, goal, [l[:3] for l in levels]))
          + r"Each level keeps the successor with the smallest $h$ (green). $h$ decreases %s and the goal is reached after %d moves: %s."
          % (r"$\to$".join(str(manhattan(x, goal)) for x in [start] + [l[1][l[2]][1] for l in levels]), len(levels),
             ", ".join(l[1][l[2]][0] for l in levels)),
          12.0, label="")
