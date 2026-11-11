"""Review-exercise style renderers and solvers (format of the CS420 review sheets)."""
from engine import *


# ============================================================================
# Game trees: circles with letters inside, MAX/MIN row labels on the left
# ============================================================================
def tikz_gtree(root, mode="blank", ab=None, dx=0.8, dy=1.25, scale=1.0, leaf_index=False):
    """mode: 'blank' | 'minimax' (values in red beside nodes) | 'ab' (alpha-beta result:
    returned values in red, pruned edges marked //, unvisited nodes grey)."""
    layout_tree(root, dx)
    nodes = all_nodes(root)
    parent_of = {}
    for n in nodes:
        for c in n.children:
            parent_of[c.id] = n
    gone, cut = set(), set()
    if mode == "ab":
        for p in ab["prunes"]:
            for c in p["pruned"]:
                cut.add((p["node"].id, c.id))
                for d in all_nodes(c):
                    gone.add(d.id)
    xmin = min(n.x for n in nodes)
    L = [r"\begin{tikzpicture}[scale=%s, every node/.style={transform shape},"
         r" gc/.style={draw, thick, circle, minimum size=6.6mm, inner sep=0pt, font=\small},"
         r" gl/.style={draw, rectangle, minimum width=5mm, minimum height=4.6mm, inner sep=1pt, font=\small},"
         r" gx/.style={draw=black!25, text=black!35}, val/.style={font=\footnotesize\bfseries, text=red!80!black, inner sep=1pt}]" % scale]
    # row labels
    depths = {}
    for n in nodes:
        if n.kind != "leaf":
            depths.setdefault(n.depth, set()).add(n.kind)
    for d, kinds in sorted(depths.items()):
        lab = "/".join(sorted(k.upper() for k in kinds))
        L.append(r"\node[font=\footnotesize, anchor=east] at (%.2f,%.2f) {%s};" % (xmin - 0.55, -d * dy, lab))
    for n in nodes:
        y = -n.depth * dy
        st = ", gx" if n.id in gone else ""
        if n.kind == "leaf":
            lab = ""
            if leaf_index:
                lab = r", label={[font=\tiny, text=black!45, inner sep=1pt]below:%s}" % n.name
            L.append(r"\node[gl%s%s] (n%d) at (%.3f,%.3f) {%s};" % (st, lab, n.id, n.x, y, fmt(n.value)))
            continue
        txt = ""
        if mode == "minimax":
            txt = fmt(n.mm)
        elif mode == "ab" and n.id in ab["recs"]:
            r = ab["recs"][n.id]
            pre = {"le": r"\le", "ge": r"\ge", None: ""}[r["bound"]]
            txt = "$%s%s$" % (pre, fmt(r["ret"]))
        side = "left"
        par = parent_of.get(n.id)
        if par is not None and par.x < n.x - 1e-9:
            side = "right"
        lab = (r", label={[val]%s:%s}" % (side, txt)) if txt else ""
        L.append(r"\node[gc%s%s] (n%d) at (%.3f,%.3f) {%s};" % (st, lab, n.id, n.x, y, n.name))
    for n in nodes:
        for k, c in enumerate(n.children):
            if (n.id, c.id) in cut:
                L.append(r"\draw (n%d) -- (n%d) node[midway, sloped, text=red!80!black, font=\small\bfseries, inner sep=0pt]{/\!/};" % (n.id, c.id))
            elif c.id in gone:
                L.append(r"\draw[black!25] (n%d) -- (n%d);" % (n.id, c.id))
            else:
                e = r"\draw (n%d) -- (n%d)" % (n.id, c.id)
                if n.kind == "chance" and n.probs:
                    e += r" node[pos=0.55, %s, font=\scriptsize, inner sep=1pt]{%s}" % ("left" if k == 0 else "right", prob_tex(n.probs[k]))
                L.append(e + ";")
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


def internal_names(root):
    return sorted([n for n in all_nodes(root) if n.kind != "leaf"], key=lambda n: (len(n.name), n.name))


def value_table(root, rows, per_line=13):
    """rows: list of (row label, {node_id: text} or None for blank).  Splits wide tables."""
    names = internal_names(root)
    import math as _m
    k = _m.ceil(len(names) / 15.0)
    per_line = _m.ceil(len(names) / float(k))
    chunks = [names[i:i + per_line] for i in range(0, len(names), per_line)]
    out = []
    for ch in chunks:
        spec = "|l|" + "c|" * len(ch)
        lines_ = [r"\begin{tabular}{%s}\hline" % spec,
                  r"\textbf{Node} & " + " & ".join(r"\textbf{%s}" % n.name for n in ch) + r"\\ \hline"]
        for lab, vals in rows:
            cells = []
            for n in ch:
                cells.append((vals.get(n.id, "") if vals else r"\phantom{00}"))
            lines_.append(lab + " & " + " & ".join(cells) + r"\\[1.5mm] \hline")
        lines_.append(r"\end{tabular}")
        out.append("\n".join(lines_))
    return r"\begin{center}\small " + r"\\[2mm]".join(out) + r"\end{center}"


def mm_values(root):
    return {n.id: r"\textcolor{blue!60!black}{%s}" % fmt(n.mm) for n in all_nodes(root) if n.kind != "leaf"}


def ab_values(root, ab):
    out = {}
    for n in all_nodes(root):
        if n.kind == "leaf":
            continue
        if n.id in ab["recs"]:
            r = ab["recs"][n.id]
            pre = {"le": r"\le ", "ge": r"\ge ", None: ""}[r["bound"]]
            out[n.id] = r"\textcolor{blue!60!black}{$%s%s$}" % (pre, fmt(r["ret"]))
        else:
            out[n.id] = r"\textcolor{red!70!black}{\textbf{X}}"
    return out


def ab_window_table(ab):
    rows = []
    for r in ab["order"]:
        n = r["node"]
        ea, eb = r["entry"]
        xa, xb = r["exit"]
        pre = {"le": r"\le ", "ge": r"\ge ", None: ""}[r["bound"]]
        rows.append(r"%s & %s & $\alpha=%s,\ \beta=%s$ & $\alpha=%s,\ \beta=%s$ & $%s%s$ \\" % (
            n.name, n.kind.upper(), fmt(ea), fmt(eb), fmt(xa), fmt(xb), pre, fmt(r["ret"])))
    return (r"\begin{center}\small\begin{tabular}{c c c c c}\toprule Node & Type & On entry & When it returns & Value returned\\\midrule "
            + "\n".join(rows) + r"\bottomrule\end{tabular}\end{center}")


# ============================================================================
# 8-puzzle steepest-descent hill climbing (Manhattan distance)
# ============================================================================
def p8_moves(s):
    i = s.index(0)
    r, c = divmod(i, 3)
    out = []
    for name, dr, dc in (("Up", -1, 0), ("Down", 1, 0), ("Left", 0, -1), ("Right", 0, 1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < 3 and 0 <= cc < 3:
            j = rr * 3 + cc
            t = list(s)
            t[i], t[j] = t[j], t[i]
            out.append((name, tuple(t)))
    return out


def manhattan(s, goal):
    return puzzle_h(list(s), list(goal))[1]


def hill_climb_8(start, goal):
    """Steepest descent on h = Manhattan distance; successors exclude the parent
    state; blank moves generated in the order Up, Down, Left, Right.  Returns levels:
    [(parent, [(move, state, h)], chosen_index or None)]."""
    cur, prev = tuple(start), None
    levels = []
    hc = manhattan(cur, goal)
    while True:
        kids = [(mv, st, manhattan(st, goal)) for mv, st in p8_moves(cur) if st != prev]
        best = min(k[2] for k in kids)
        idx = [i for i, k in enumerate(kids) if k[2] == best]
        if best >= hc:
            levels.append((cur, kids, None))
            return levels, "stuck", idx
        levels.append((cur, kids, idx[0]))
        if len(idx) > 1:
            levels[-1] = (cur, kids, idx[0], "tie")
        prev, cur, hc = cur, kids[idx[0]][1], best
        if best == 0:
            return levels, "goal", idx


def board_tikz(s, at, name, h=None, hl=False, size=0.42):
    x0, y0 = at
    L = []
    st = "very thick, draw=green!50!black" if hl else "thick"
    L.append(r"\draw[%s] (%.2f,%.2f) rectangle (%.2f,%.2f);" % (st, x0, y0, x0 + 3 * size, y0 - 3 * size))
    for k in (1, 2):
        L.append(r"\draw[black!50] (%.2f,%.2f) -- (%.2f,%.2f);" % (x0 + k * size, y0, x0 + k * size, y0 - 3 * size))
        L.append(r"\draw[black!50] (%.2f,%.2f) -- (%.2f,%.2f);" % (x0, y0 - k * size, x0 + 3 * size, y0 - k * size))
    for i, v in enumerate(s):
        r, c = divmod(i, 3)
        if v:
            L.append(r"\node[font=\scriptsize] at (%.2f,%.2f) {%d};" % (x0 + (c + 0.5) * size, y0 - (r + 0.5) * size, v))
    L.append(r"\coordinate (%s-top) at (%.2f,%.2f);" % (name, x0 + 1.5 * size, y0))
    L.append(r"\coordinate (%s-bot) at (%.2f,%.2f);" % (name, x0 + 1.5 * size, y0 - 3 * size))
    if h is not None:
        L.append(r"\node[font=\scriptsize\bfseries, text=red!75!black, anchor=west] at (%.2f,%.2f) {h=%d};" % (x0 + 3 * size + 0.04, y0 - 1.5 * size, h))
    return "\n".join(L)


def hill_tree_tikz(start, goal, levels, size=0.42, gap=2.6, vgap=2.05):
    W = 3 * size
    L = [r"\begin{tikzpicture}"]
    L.append(board_tikz(start, (-W / 2, 0), "r0", manhattan(start, goal)))
    pname = "r0"
    y = -vgap
    for li, lev in enumerate(levels):
        _, kids, ch = lev[0], lev[1], lev[2]
        k = len(kids)
        xs = [(i - (k - 1) / 2) * gap - W / 2 for i in range(k)]
        for i, (mv, stt, h) in enumerate(kids):
            nm = "b%d_%d" % (li, i)
            L.append(board_tikz(stt, (xs[i], y), nm, h, hl=(ch == i)))
            L.append(r"\draw (%s-bot) -- node[font=\tiny, fill=white, inner sep=0.5pt]{%s} (%s-top);" % (pname, mv, nm))
        if ch is None:
            break
        pname = "b%d_%d" % (li, ch)
        y -= vgap
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


# ============================================================================
# n-queens / n-bishops boards
# ============================================================================
def queens_board_tikz(rows, numbers=None, piece=r"$\mathbb{Q}$", size=0.55, hl=None):
    n = len(rows)
    L = [r"\begin{tikzpicture}"]
    for c in range(n):
        for r in range(n):
            shade = "black!8" if (r + c) % 2 else "white"
            L.append(r"\fill[%s] (%.2f,%.2f) rectangle +(%.2f,%.2f);" % (shade, c * size, -r * size, size, -size))
    L.append(r"\draw[thick] (0,0) rectangle (%.2f,%.2f);" % (n * size, -n * size))
    for k in range(1, n):
        L.append(r"\draw[black!40] (%.2f,0) -- (%.2f,%.2f);" % (k * size, k * size, -n * size))
        L.append(r"\draw[black!40] (0,%.2f) -- (%.2f,%.2f);" % (-k * size, n * size, -k * size))
    for c, r in enumerate(rows):
        L.append(r"\node[font=\small\bfseries] at (%.2f,%.2f) {%s};" % ((c + 0.5) * size, -(r - 0.5) * size, piece))
    if numbers:
        for r in range(n):
            for c in range(n):
                if rows[c] != r + 1:
                    bold = hl is not None and (r + 1, c + 1) == hl
                    L.append(r"\node[font=\scriptsize%s, text=%s] at (%.2f,%.2f) {%d};" % (
                        r"\bfseries" if bold else "", "red!75!black" if bold else "blue!60!black", (c + 0.5) * size, -(r + 0.5) * size, numbers[r][c]))
    for c in range(n):
        L.append(r"\node[font=\tiny] at (%.2f,%.2f) {%d};" % ((c + 0.5) * size, 0.2, c + 1))
    for r in range(n):
        L.append(r"\node[font=\tiny] at (%.2f,%.2f) {%d};" % (-0.2, -(r + 0.5) * size, r + 1))
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


def queens_h(rows):
    return len(queens_attacks(list(rows)))


def queens_hboard(rows):
    """h of every successor: hb[r][c] = attacking pairs if queen of column c+1 moves to row r+1."""
    n = len(rows)
    hb = [[0] * n for _ in range(n)]
    for c in range(n):
        for r in range(1, n + 1):
            t = list(rows)
            t[c] = r
            hb[r - 1][c] = queens_h(t)
    return hb


def bishops_attacks(rows):
    n = len(rows)
    return [(i + 1, j + 1) for i in range(n) for j in range(i + 1, n) if abs(rows[i] - rows[j]) == abs(i - j)]


# ============================================================================
# CSP helpers in the review format
# ============================================================================
def strike_dom(full, kept, assigned=None):
    """Render a domain with eliminated values struck out (solutions) ."""
    out = []
    for v in full:
        if assigned is not None:
            out.append(r"\textbf{%s}" % v if v == assigned else r"\textcolor{red!70!black}{\sout{%s}}" % v)
        elif v in kept:
            out.append(str(v))
        else:
            out.append(r"\textcolor{red!70!black}{\sout{%s}}" % v)
    return r"\ ".join(out)


def dom_row_table(vars_, cells, header="Variables"):
    spec = "|l|" + "c|" * len(vars_)
    return (r"\begin{center}\small\begin{tabular}{%s}\hline %s & " % (spec, header) + " & ".join(r"\textbf{%s}" % v for v in vars_)
            + r"\\ \hline Domains & " + " & ".join(cells) + r"\\ \hline\end{tabular}\end{center}")


def fc_after(csp, assign):
    """Forward checking after the assignments in `assign` (applied in order)."""
    D = {v: list(d) for v, d in csp.dom.items()}
    for var, val in assign:
        D[var] = [val]
        for w in csp.nb[var]:
            if w in dict(assign) and w != var:
                continue
            D[w] = [y for y in D[w] if csp.ok(var, val, w, y)]
    return D


def ac_after(csp, assign):
    D = {v: list(d) for v, d in csp.dom.items()}
    for var, val in assign:
        D[var] = [val]
    okk, D2, tr = ac3(csp, None, D)
    return okk, D2, tr


def mrv_dh_steps(csp, value_order=None):
    """Backtracking + FC with MRV, then degree, then alphabetical; values in domain order.
    Returns the list of steps (no backtracking expected)."""
    assignment = {}
    D = {v: list(d) for v, d in csp.dom.items()}
    steps = []
    while len(assignment) < len(csp.vars):
        un = [v for v in csp.vars if v not in assignment]
        mrv = {v: len(D[v]) for v in un}
        m_ = min(mrv.values())
        tied = [v for v in un if mrv[v] == m_]
        dh = {}
        if len(tied) > 1:
            for v in tied:
                dh[v] = sum(1 for w in csp.nb[v] if w not in assignment)
            mx = max(dh.values())
            cand = [v for v in tied if dh[v] == mx]
        else:
            cand = tied
        var = sorted(cand)[0]
        val = None
        for x in D[var]:
            if all(csp.ok(var, x, w, assignment[w]) for w in csp.nb[var] if w in assignment):
                # forward-check feasibility
                okk = True
                for w in csp.nb[var]:
                    if w not in assignment and not [y for y in D[w] if csp.ok(var, x, w, y)]:
                        okk = False
                if okk:
                    val = x
                    break
        assert val is not None, "would need backtracking"
        steps.append({"mrv": mrv, "dh": dh, "var": var, "val": val, "D": {k: list(v) for k, v in D.items()}})
        assignment[var] = val
        D[var] = [val]
        for w in csp.nb[var]:
            if w not in assignment:
                D[w] = [y for y in D[w] if csp.ok(var, val, w, y)]
    return steps, assignment


def mrv_step_table(vars_, step=None, assigned=()):
    spec = "|l|" + "c|" * len(vars_)
    head = r"\begin{tabular}{%s}\hline Variables & " % spec + " & ".join(r"\textbf{%s}" % v for v in vars_) + r"\\ \hline"
    if step is None:
        return head + " MRV & " + " & ".join(r"\phantom{0}" for _ in vars_) + r"\\[1mm]\hline DH & " + \
            " & ".join(r"\phantom{0}" for _ in vars_) + r"\\[1mm]\hline\end{tabular}"
    mrv = " & ".join((r"\textcolor{blue!60!black}{%d}" % step["mrv"][v]) if v in step["mrv"] else "--" for v in vars_)
    dh = " & ".join((r"\textcolor{blue!60!black}{%d}" % step["dh"][v]) if v in step["dh"] else "" for v in vars_)
    return head + " MRV & " + mrv + r"\\ \hline DH & " + dh + r"\\ \hline\end{tabular}"
