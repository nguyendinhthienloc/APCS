"""Solver + TikZ renderer used to build the CS420 practice midterms.

Every numeric answer in the solution files (search orders, minimax / alpha-beta
values, MCTS statistics, CSP traces) is computed here, so exam and solution are
always consistent with each other and with the lecture conventions.
"""
import math

INF = float("inf")


# ----------------------------------------------------------------------------
# formatting helpers
# ----------------------------------------------------------------------------
def fmt(v, nd=2):
    if v == INF:
        return r"+\infty"
    if v == -INF:
        return r"-\infty"
    if isinstance(v, float):
        if abs(v - round(v)) < 1e-9:
            return str(int(round(v)))
        s = ("%." + str(nd) + "f") % v
        return s.rstrip("0").rstrip(".") if "." in s else s
    return str(v)


def m(s):
    return "$" + s + "$"


# ============================================================================
# GAME TREES: minimax, alpha-beta, expectimax
# ============================================================================
class GNode:
    def __init__(self, kind, value=None):
        self.kind = kind            # 'max' | 'min' | 'chance' | 'leaf'
        self.value = value
        self.children = []
        self.probs = None
        self.name = None
        self.id = None
        self.x = 0.0
        self.depth = 0
        self.mm = None              # minimax / expectimax value


def _other(kind):
    return {"max": "min", "min": "max"}[kind]


def build_tree(spec, root_kind="max"):
    """spec: number = leaf; list = internal node (kind alternates);
    tuple (kind, [children]) or ('chance', [children], [probs]) = explicit kind."""
    counter = [0]

    def rec(sp, kind, depth):
        if isinstance(sp, (int, float, str)):
            n = GNode("leaf", sp)
        else:
            probs = None
            if isinstance(sp, tuple):
                kind = sp[0]
                kids = sp[1]
                if len(sp) > 2:
                    probs = sp[2]
            else:
                kids = sp
            n = GNode(kind)
            n.probs = probs
            ck = "max" if kind == "chance" else _other(kind)
            for k in kids:
                n.children.append(rec(k, ck, depth + 1))
        n.depth = depth
        n.id = counter[0]
        counter[0] += 1
        return n

    root = rec(spec, root_kind, 0)
    # level-order letters for internal nodes, left-to-right numbers for leaves
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    level = [root]
    li = 0
    leaves = []
    while level:
        nxt = []
        for n in level:
            if n.kind != "leaf":
                n.name = letters[li] if li < 26 else letters[li // 26 - 1] + letters[li % 26]
                li += 1
            nxt.extend(n.children)
        level = nxt
    # leaves numbered in DFS (left-to-right) order
    def dfs(n):
        if n.kind == "leaf":
            leaves.append(n)
            n.name = str(len(leaves))
        for c in n.children:
            dfs(c)
    dfs(root)
    root.leaves = leaves
    return root


def all_nodes(root):
    out = []
    def dfs(n):
        out.append(n)
        for c in n.children:
            dfs(c)
    dfs(root)
    return out


def minimax(n):
    if n.kind == "leaf":
        n.mm = n.value
    elif n.kind == "max":
        n.mm = max(minimax(c) for c in n.children)
    elif n.kind == "min":
        n.mm = min(minimax(c) for c in n.children)
    else:  # chance
        vals = [minimax(c) for c in n.children]
        probs = n.probs or [1.0 / len(vals)] * len(vals)
        n.mm = sum(p * v for p, v in zip(probs, vals))
    return n.mm


def alphabeta(root, reverse=False):
    """Alpha-beta exactly as in the lecture pseudo-code (fail-soft).
    Also records which node last set alpha / beta, so cut-offs can be explained."""
    order, prunes = [], []
    evaluated = []
    recs = {}
    parent = {}
    for n in all_nodes(root):
        for c in n.children:
            parent[c.id] = n

    def kids(n):
        return list(reversed(n.children)) if reverse else n.children

    def val(n, a, b, asrc, bsrc):
        if n.kind == "leaf":
            evaluated.append(n)
            return n.value
        rec = {"node": n, "entry": (a, b), "entry_src": (asrc, bsrc), "seen": [], "pruned": []}
        recs[n.id] = rec
        order.append(rec)
        ch = kids(n)
        if n.kind == "max":
            v = -INF
            for i, c in enumerate(ch):
                v2 = val(c, a, b, asrc, bsrc)
                rec["seen"].append((c, v2))
                if v2 > v:
                    v = v2
                if v > a:
                    a, asrc = v, n
                if v >= b:
                    rec["pruned"] = ch[i + 1:]
                    if rec["pruned"]:
                        prunes.append({"node": n, "after": c, "v": v, "bound": b, "src": bsrc,
                                       "deep": bsrc is not parent.get(n.id),
                                       "test": r"v=%s \ge \beta=%s" % (fmt(v), fmt(b)),
                                       "pruned": ch[i + 1:]})
                    break
        else:
            v = INF
            for i, c in enumerate(ch):
                v2 = val(c, a, b, asrc, bsrc)
                rec["seen"].append((c, v2))
                if v2 < v:
                    v = v2
                if v < b:
                    b, bsrc = v, n
                if v <= a:
                    rec["pruned"] = ch[i + 1:]
                    if rec["pruned"]:
                        prunes.append({"node": n, "after": c, "v": v, "bound": a, "src": asrc,
                                       "deep": asrc is not parent.get(n.id),
                                       "test": r"v=%s \le \alpha=%s" % (fmt(v), fmt(a)),
                                       "pruned": ch[i + 1:]})
                    break
        rec["ret"] = v
        rec["exit"] = (a, b)
        ea, eb = rec["entry"]
        if v <= ea:
            rec["bound"] = "le"
        elif v >= eb:
            rec["bound"] = "ge"
        else:
            rec["bound"] = None
        # show a bound only when it is genuinely a bound (node cut off, or value differs
        # from the true minimax value); otherwise the value returned is exact.
        if not rec["pruned"] and (n.mm is None or v == n.mm):
            rec["bound"] = None
        if rec["bound"] is None and n.mm is not None and v != n.mm:
            rec["bound"] = "le" if v <= ea else "ge"
        return v

    v = val(root, -INF, INF, None, None)
    best = None
    for c, cv in recs[root.id]["seen"]:
        if cv == v:
            best = c
            break
    pruned_leaves = [l for l in root.leaves if l not in evaluated]
    return {"value": v, "order": order, "prunes": prunes, "recs": recs,
            "evaluated": evaluated, "pruned_leaves": pruned_leaves, "best": best}


def subtree_nodes(n):
    return all_nodes(n)


# ---------------------------------------------------------------- tree tikz
TREE_STYLES = r"""
\tikzset{
  maxn/.style={draw, thick, regular polygon, regular polygon sides=3, minimum size=10.5mm, inner sep=0pt, font=\small},
  minn/.style={maxn, shape border rotate=180},
  chn/.style={draw, thick, circle, minimum size=9.5mm, inner sep=0pt, font=\small},
  leafn/.style={draw, rectangle, minimum width=5.5mm, minimum height=5.5mm, inner sep=1pt, font=\small},
  gone/.style={draw=black!25, text=black!35},
  cut/.style={red!80!black, very thick, dashed},
  sol/.style={text=blue!70!black, font=\small\bfseries},
}
"""


def layout_tree(root, dx=0.75):
    xs = {}
    i = [0]

    def rec(n):
        if n.kind == "leaf":
            n.x = i[0] * dx
            i[0] += 1
        else:
            for c in n.children:
                rec(c)
            n.x = (n.children[0].x + n.children[-1].x) / 2.0
    rec(root)


def tikz_tree(root, mode="blank", ab=None, dx=0.75, dy=1.55, scale=1.0,
              leaf_index=True, label_side="left"):
    """mode: 'blank' (exam), 'minimax' (all values), 'ab' (alpha-beta result)."""
    layout_tree(root, dx)
    gone = set()
    cut_edges = set()
    if mode == "ab":
        for p in ab["prunes"]:
            for c in p["pruned"]:
                cut_edges.add((p["node"].id, c.id))
                for d in all_nodes(c):
                    gone.add(d.id)
    L = []
    parent_of = {}
    for n in all_nodes(root):
        for c in n.children:
            parent_of[c.id] = n
    L.append(r"\begin{tikzpicture}[scale=%s, every node/.style={transform shape}]" % scale)
    for n in all_nodes(root):
        y = -n.depth * dy
        style = {"max": "maxn", "min": "minn", "chance": "chn", "leaf": "leafn"}[n.kind]
        txt = ""
        if n.kind == "leaf":
            txt = fmt(n.value)
        elif mode == "minimax":
            txt = r"\textcolor{blue!70!black}{\textbf{%s}}" % fmt(n.mm)
        elif mode == "ab" and n.id in ab["recs"]:
            r = ab["recs"][n.id]
            pre = {"le": r"\le", "ge": r"\ge", None: ""}[r["bound"]]
            txt = r"\textcolor{blue!70!black}{\textbf{$%s%s$}}" % (pre, fmt(r["ret"]))
        extra = ""
        if n.id in gone:
            extra = ", gone"
        lab = ""
        if n.kind != "leaf":
            par = parent_of.get(n.id)
            side = label_side
            if par is not None:
                side = "right" if par.x < n.x - 1e-9 else "left"
            lab = r", label={[font=\scriptsize\bfseries, inner sep=1pt, label distance=0.3mm]%s:%s}" % (side, n.name)
        elif leaf_index:
            lab = r", label={[font=\tiny, text=black!45, inner sep=1pt]below:%s}" % n.name
        yy = y
        if n.kind == "max":
            yy = y + 0.12
        if n.kind == "leaf":
            L.append(r"\node[%s%s%s] (n%d) at (%.3f,%.3f) {%s};" % (style, extra, lab, n.id, n.x, yy, txt))
        else:
            L.append(r"\node[%s%s%s] (n%d) at (%.3f,%.3f) {};" % (style, extra, lab, n.id, n.x, yy))
            if txt:
                dy_txt = -0.06 if n.kind == "max" else 0.06
                L.append(r"\node[font=\footnotesize, inner sep=0pt] at ($(n%d.center)+(0,%.2f)$) {%s};" % (n.id, dy_txt, txt))
    for n in all_nodes(root):
        for k, c in enumerate(n.children):
            if (n.id, c.id) in cut_edges:
                L.append(r"\draw[cut] (n%d) -- (n%d) node[midway, font=\small\bfseries, text=red!80!black]{$\times$};" % (n.id, c.id))
            elif c.id in gone:
                L.append(r"\draw[black!25] (n%d) -- (n%d);" % (n.id, c.id))
            else:
                edge = r"\draw (n%d) -- (n%d)" % (n.id, c.id)
                if n.kind == "chance" and n.probs:
                    side = "left" if k == 0 else "right"
                    edge += r" node[pos=0.62, %s, font=\scriptsize, inner sep=1pt]{%s}" % (side, prob_tex(n.probs[k]))
                L.append(edge + ";")
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


def prob_tex(p):
    from fractions import Fraction
    f = Fraction(p).limit_denominator(20)
    if f.denominator == 1:
        return "$%d$" % f.numerator
    return r"$%d/%d$" % (f.numerator, f.denominator)


def ab_table(ab):
    """Per-node trace table (visiting order)."""
    rows = []
    for r in ab["order"]:
        n = r["node"]
        ea, eb = r["entry"]
        seen = ", ".join(fmt(v) for _, v in r["seen"])
        pre = {"le": r"\le ", "ge": r"\ge ", None: ""}[r["bound"]]
        pr = ", ".join(_desc(c) for c in r["pruned"]) if r["pruned"] else "--"
        rows.append(r"%s & %s & $[%s,\ %s]$ & %s & $%s%s$ & %s \\" % (
            n.name, n.kind.upper(), fmt(ea), fmt(eb), seen, pre, fmt(r["ret"]), pr))
    head = (r"\begin{center}\small" "\n"
            r"\begin{tabularx}{\linewidth}{c c c >{\raggedright}p{2.7cm} c >{\raggedright\arraybackslash}X}" "\n" r"\toprule" "\n"
            r"Node & Type & $[\alpha,\beta]$ on entry & Values returned by children (in order) & Returned & Pruned children \\" "\n"
            r"\midrule")
    return head + "\n" + "\n".join(rows) + "\n" + r"\bottomrule\end{tabularx}\end{center}"


def _desc(c):
    if c.kind == "leaf":
        return "leaf \\#%s" % c.name
    lv = [l.name for l in all_nodes(c) if l.kind == "leaf"]
    return "%s (leaves \\#%s--\\#%s)" % (c.name, lv[0], lv[-1]) if len(lv) > 1 else "%s (leaf \\#%s)" % (c.name, lv[0])


def ab_prune_text(ab):
    if not ab["prunes"]:
        return "No pruning occurs."
    items = []
    for p in ab["prunes"]:
        n = p["node"]
        who = "MAX" if n.kind == "max" else "MIN"
        after = ("leaf \\#%s" % p["after"].name) if p["after"].kind == "leaf" else "child %s" % p["after"].name
        src = p["src"].name if p["src"] is not None else "?"
        if n.kind == "max":
            why = r"MIN at %s already has an alternative worth $\beta=%s$, so it will never let play reach %s" % (src, fmt(p["bound"]), n.name)
        else:
            why = r"MAX at %s already has an alternative worth $\alpha=%s$, so it will never let play reach %s" % (src, fmt(p["bound"]), n.name)
        deep = r" \textbf{Deep cut-off}: the bound comes from %s, %s levels above %s." % (src, n.depth - p["src"].depth, n.name) if p["deep"] else ""
        items.append(r"\item At %s node \textbf{%s}, after %s: $%s$ $\Rightarrow$ prune %s. (%s.)%s" % (
            who, n.name, after, p["test"], ", ".join(_desc(c) for c in p["pruned"]), why, deep))
    return "\\begin{itemize}[leftmargin=1.5em,itemsep=1pt]\n" + "\n".join(items) + "\n\\end{itemize}"


# ============================================================================
# GRAPH SEARCH
# ============================================================================
class Graph:
    def __init__(self, nodes, edges, start, goals, directed=False):
        """nodes: {name: (x, y, h, hpos)}; edges: [(u, v, cost, opts)]"""
        self.nodes = nodes
        self.edges = edges
        self.start = start
        self.goals = set(goals)
        self.directed = directed
        self.adj = {u: {} for u in nodes}
        for e in edges:
            u, v, c = e[0], e[1], e[2]
            self.adj[u][v] = c
            if not directed:
                self.adj[v][u] = c

    def h(self, u):
        return self.nodes[u][2]

    def nbrs(self, u):
        return sorted(self.adj[u].items())

    def path_cost(self, path):
        return sum(self.adj[a][b] for a, b in zip(path, path[1:]))


def _path(parent, s):
    p = [s]
    while parent.get(p[-1]) is not None:
        p.append(parent[p[-1]])
    return p[::-1]


def bfs(g):
    """Lecture BFS: graph search, FIFO, reached set, EARLY goal test.
    'order' lists the EXPANDED states only (the goal is generated, never expanded)."""
    s = g.start
    trace = []
    if s in g.goals:
        return {"order": [], "path": [s], "trace": trace, "final": []}
    frontier = [s]
    reached = {s}
    parent = {s: None}
    expanded = []
    while frontier:
        n = frontier.pop(0)
        expanded.append(n)
        for c, _ in g.nbrs(n):
            if c in g.goals:
                parent[c] = n
                trace.append((n, list(frontier), c))
                return {"order": expanded, "path": _path(parent, c), "trace": trace, "final": list(frontier)}
            if c not in reached:
                reached.add(c)
                parent[c] = n
                frontier.append(c)
        trace.append((n, list(frontier), None))
    return {"order": expanded, "path": None, "trace": trace, "final": []}


def dfs(g, early=True, limit=None):
    """Lecture DFS: tree search with cycle check along the current path, LIFO,
    early goal test by default. Alphabetically-earlier children are expanded first.
    With a depth limit, nodes at depth == limit are popped (listed) but not expanded."""
    trace = []
    stack = [[g.start]]
    expanded = []
    if early and g.start in g.goals:
        return {"order": [], "path": [g.start], "trace": trace, "final": []}
    while stack:
        path = stack.pop()
        n = path[-1]
        expanded.append(n)
        if not early and n in g.goals:
            trace.append((n, [p[-1] for p in stack[::-1]], None))
            return {"order": expanded, "path": path, "trace": trace, "final": [p[-1] for p in stack[::-1]]}
        if limit is not None and len(path) - 1 >= limit:
            trace.append((n, [p[-1] for p in stack[::-1]], None))
            continue
        kids = [c for c, _ in g.nbrs(n) if c not in path]
        if early:
            for c in kids:
                if c in g.goals:
                    trace.append((n, [p[-1] for p in stack[::-1]], c))
                    return {"order": expanded, "path": path + [c], "trace": trace,
                            "final": [p[-1] for p in stack[::-1]]}
        for c in reversed(kids):
            stack.append(path + [c])
        trace.append((n, [p[-1] for p in stack[::-1]], None))
    return {"order": expanded, "path": None, "trace": trace, "final": []}


def best_first(g, kind, early_goal=False):
    """BEST-FIRST-SEARCH from the lecture (graph search, late goal test).
    kind: 'ucs' f=g, 'gbfs' f=h, 'astar' f=g+h.  A cheaper path to a state in the
    frontier replaces its entry; ties on f are broken alphabetically."""
    def f(name, gc):
        if kind == "ucs":
            return gc
        if kind == "gbfs":
            return g.h(name)
        return gc + g.h(name)

    s = g.start
    frontier = {s: (f(s, 0), 0)}
    reached = {s: 0}
    parent = {s: None}
    expanded = []
    trace = []
    reopen = []
    updates = []
    ties = []
    expanded_set = set()
    while frontier:
        best = min(frontier.items(), key=lambda kv: (kv[1][0], kv[0]))
        fv = best[1][0]
        same = [k for k, v in frontier.items() if v[0] == fv]
        if len(same) > 1:
            ties.append((sorted(same), fv))
        n, (fn, gn) = best
        del frontier[n]
        expanded.append(n)
        if n in expanded_set:
            reopen.append(n)
        expanded_set.add(n)
        if n in g.goals:
            trace.append({"pop": (n, fn, gn), "frontier": _fr(frontier, g, kind), "goal": True})
            return {"order": expanded, "path": _path(parent, n), "cost": gn, "trace": trace,
                    "reopen": reopen, "updates": updates, "ties": ties,
                    "final": [k for k, _, _ in _fr(frontier, g, kind)]}
        for c, cost in g.nbrs(n):
            g2 = gn + cost
            if early_goal and c in g.goals:
                parent[c] = n
                trace.append({"pop": (n, fn, gn), "frontier": _fr(frontier, g, kind), "goal": False, "gen_goal": c})
                return {"order": expanded, "path": _path(parent, c), "cost": g2, "trace": trace,
                        "reopen": reopen, "updates": updates, "ties": ties,
                        "final": [k for k, _, _ in _fr(frontier, g, kind)]}
            if c not in reached or g2 < reached[c]:
                if c in frontier:
                    updates.append((c, frontier[c][1], g2, n))
                elif c in expanded_set:
                    reopen.append(("re-added", c))
                reached[c] = g2
                parent[c] = n
                frontier[c] = (f(c, g2), g2)
        trace.append({"pop": (n, fn, gn), "frontier": _fr(frontier, g, kind), "goal": False})
    return {"order": expanded, "path": None, "cost": None, "trace": trace,
            "reopen": reopen, "updates": updates, "ties": ties}


def _fr(frontier, g, kind):
    items = sorted(frontier.items(), key=lambda kv: (kv[1][0], kv[0]))
    return [(k, v[0], v[1]) for k, v in items]


def fr_tex(items, kind, g):
    out = []
    for name, fv, gv in items:
        if kind == "astar":
            out.append(r"%s$_{%s+%s=%s}$" % (name, fmt(gv), fmt(g.h(name)), fmt(fv)))
        else:
            out.append(r"%s$_{%s}$" % (name, fmt(fv)))
    return ", ".join(out) if out else r"$\emptyset$"


def bf_trace_table(res, kind, g):
    rows = []
    for i, t in enumerate(res["trace"], 1):
        n, fn, gn = t["pop"]
        if kind == "astar":
            pop = r"%s$_{%s+%s=%s}$" % (n, fmt(gn), fmt(g.h(n)), fmt(fn))
        else:
            pop = r"%s$_{%s}$" % (n, fmt(fn))
        if t["goal"]:
            fr = r"\textit{goal removed from the frontier -- stop}"
        elif t.get("gen_goal"):
            fr = r"generates goal \textbf{%s} $\Rightarrow$ stop; frontier: %s" % (t["gen_goal"], fr_tex(t["frontier"], kind, g))
        else:
            fr = fr_tex(t["frontier"], kind, g)
        rows.append(r"%d & %s & %s \\" % (i, pop, fr))
    sub = {"ucs": r"subscript $=g(n)$", "gbfs": r"subscript $=h(n)$",
           "astar": r"subscript $=g+h=f$"}[kind]
    return (r"\begin{center}\small\begin{tabularx}{\linewidth}{c l >{\raggedright\arraybackslash}X}\toprule" "\n"
            r"Step & Expanded & Frontier after the expansion, in priority order (%s) \\ \midrule" % sub + "\n"
            + "\n".join(rows) + "\n" r"\bottomrule\end{tabularx}\end{center}")


def queue_trace_table(res, what):
    rows = []
    for i, (n, fr, goal) in enumerate(res["trace"], 1):
        frs = ", ".join(fr) if fr else r"$\emptyset$"
        if goal:
            frs = r"generates goal \textbf{%s} $\Rightarrow$ stop; frontier: %s" % (goal, frs)
        rows.append(r"%d & %s & %s \\" % (i, n, frs))
    hdr = "Queue (front $\\rightarrow$ back)" if what == "bfs" else "Stack (top $\\rightarrow$ bottom)"
    return (r"\begin{center}\small\begin{tabularx}{\linewidth}{c c >{\raggedright\arraybackslash}X}\toprule" "\n"
            r"Step & Expanded & %s after the expansion \\ \midrule" % hdr + "\n"
            + "\n".join(rows) + "\n" r"\bottomrule\end{tabularx}\end{center}")


def tikz_graph(g, show_h=True, scale=1.0, node_size=7.5):
    L = [r"\begin{tikzpicture}[scale=%s, every node/.style={transform shape},"
         r" gn/.style={draw, thick, circle, minimum size=%smm, inner sep=0pt, font=\small\bfseries},"
         r" ec/.style={font=\scriptsize, fill=white, inner sep=1pt}]" % (scale, node_size)]
    for name, spec in g.nodes.items():
        x, y, h = spec[0], spec[1], spec[2]
        hpos = spec[3] if len(spec) > 3 else "above"
        extra = ""
        if name == g.start:
            extra = ", fill=green!15"
        if name in g.goals:
            extra = ", double, fill=orange!15"
        lab = ""
        if show_h:
            lab = r", label={[font=\scriptsize, text=blue!60!black, inner sep=1pt]%s:$h{=}%s$}" % (hpos, fmt(h))
        L.append(r"\node[gn%s%s] (%s) at (%.2f,%.2f) {%s};" % (extra, lab, name, x, y, name))
    arrow = "-{Stealth[length=2.2mm]}" if g.directed else ""
    for e in g.edges:
        u, v, c = e[0], e[1], e[2]
        opt = e[3] if len(e) > 3 else ""
        bend = ""
        lpos = "midway"
        if opt:
            parts = [p.strip() for p in opt.split(";")]
            for p in parts:
                if p.startswith("pos="):
                    lpos = p
                elif p:
                    bend = p
        L.append(r"\draw[thick%s] (%s) to[%s] node[ec, %s]{%s} (%s);" % (
            ("," + arrow) if arrow else "", u, bend, lpos, fmt(c), v))
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


def check_h(g):
    """Return (admissible, consistent, list of violations) using exact h*."""
    # h* via Dijkstra backwards (reverse edges for directed)
    import heapq
    rev = {u: {} for u in g.nodes}
    for u in g.adj:
        for v, c in g.adj[u].items():
            rev[v][u] = c
    dist = {u: INF for u in g.nodes}
    pq = []
    for t in g.goals:
        dist[t] = 0
        heapq.heappush(pq, (0, t))
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, c in rev[u].items():
            if d + c < dist[v]:
                dist[v] = d + c
                heapq.heappush(pq, (d + c, v))
    adm_viol = [(u, g.h(u), dist[u]) for u in g.nodes if g.h(u) > dist[u]]
    con_viol = []
    for u in g.adj:
        for v, c in g.adj[u].items():
            if g.h(u) > c + g.h(v):
                con_viol.append((u, v, g.h(u), c, g.h(v)))
    return {"hstar": dist, "adm": not adm_viol, "adm_viol": adm_viol,
            "con": not con_viol, "con_viol": con_viol}


# ============================================================================
# MCTS
# ============================================================================
class MNode:
    def __init__(self, name, t=0.0, n=0, parent=None):
        self.name = name
        self.t = t
        self.n = n
        self.parent = parent
        self.children = []

    def add(self, name, t=0.0, n=0):
        c = MNode(name, t, n, self)
        self.children.append(c)
        return c


def ucb(child, parent, C):
    if child.n == 0:
        return INF
    return child.t / child.n + C * math.sqrt(math.log(parent.n) / child.n)


def ucb_tex(child, parent, C, Ctex):
    if child.n == 0:
        return r"$\infty$ (unvisited)"
    val = ucb(child, parent, C)
    return r"$\frac{%s}{%s} + %s\sqrt{\frac{\ln %d}{%d}} = %s$" % (
        fmt(child.t), child.n, Ctex, parent.n, child.n, "%.3f" % val)


def mcts_run(root, expand_map, rollouts, C, Ctex):
    """Course convention: descend by max UCB1 (unvisited = inf, ties -> leftmost)
    while the node has children; at a leaf: if n == 0 roll out from it, otherwise
    expand all its children (expand_map) and roll out from the first new child."""
    log = []
    for it, val in enumerate(rollouts, 1):
        node = root
        path = [root]
        sel = []
        while node.children:
            scores = [(ucb(c, node, C), c) for c in node.children]
            bestv = max(s for s, _ in scores)
            chosen = next(c for s, c in scores if s == bestv)
            sel.append({"at": node.name, "N": node.n,
                        "scores": [(c.name, ucb_tex(c, node, C, Ctex), s) for s, c in scores],
                        "chosen": chosen.name})
            node = chosen
            path.append(node)
        expanded = []
        if node.n > 0 and node.name in expand_map:
            for nm in expand_map[node.name]:
                expanded.append(node.add(nm))
            node = node.children[0]
            path.append(node)
        for p in path:
            p.n += 1
            p.t += val
        log.append({"it": it, "sel": sel, "expanded": [e.name for e in expanded],
                    "rollout_from": node.name, "value": val,
                    "path": [p.name for p in path], "snapshot": snapshot(root)})
    return log


def snapshot(root):
    out = []
    def rec(n):
        out.append((n.name, n.t, n.n))
        for c in n.children:
            rec(c)
    rec(root)
    return out


def tikz_mcts(root, scale=1.0, dx=2.1, dy=1.7, highlight=None, blank=False):
    highlight = set(highlight or [])
    # layout: leaves evenly spaced
    pos = {}
    cnt = [0]

    def rec(n, d):
        if not n.children:
            pos[id(n)] = (cnt[0] * dx, -d * dy)
            cnt[0] += 1
        else:
            for c in n.children:
                rec(c, d + 1)
            xs = [pos[id(c)][0] for c in n.children]
            pos[id(n)] = ((xs[0] + xs[-1]) / 2.0, -d * dy)
    rec(root, 0)
    L = [r"\begin{tikzpicture}[scale=%s, every node/.style={transform shape},"
         r" mn/.style={draw, thick, circle, align=center, font=\footnotesize, inner sep=0.5pt, minimum size=13.5mm}]" % scale]
    ids = {}
    k = [0]

    def emit(n):
        k[0] += 1
        ids[id(n)] = "m%d" % k[0]
        x, y = pos[id(n)]
        st = ", fill=yellow!25" if n.name in highlight else ""
        if blank:
            body = r"\textbf{%s}\\ $t=\ \ \ \ $\\ $n=\ \ \ \ $" % mname(n.name)
        else:
            body = r"\textbf{%s}\\ $t=%s$\\ $n=%d$" % (mname(n.name), fmt(n.t), n.n)
        L.append(r"\node[mn%s] (%s) at (%.2f,%.2f) {%s};" % (st, ids[id(n)], x, y, body))
        for c in n.children:
            emit(c)
            L.append(r"\draw[thick] (%s) -- (%s);" % (ids[id(n)], ids[id(c)]))
    emit(root)
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


def clone_mcts(root):
    def rec(n, parent):
        c = MNode(n.name, n.t, n.n, parent)
        c.children = [rec(k, c) for k in n.children]
        return c
    return rec(root, None)


def mname(s):
    import re
    m_ = re.fullmatch(r"([A-Za-z]+)(\d+)", s)
    return "$%s_{%s}$" % (m_.group(1), m_.group(2)) if m_ else s


def mcts_log_tex(log):
    parts = []
    for e in log:
        s = [r"\textbf{Iteration %d.}" % e["it"]]
        items = []
        for st in e["sel"]:
            sc = "; ".join(r"%s: %s" % (mname(nm), tx) for nm, tx, _ in st["scores"])
            items.append(r"\item \emph{Selection} at %s ($N=%d$): %s $\Rightarrow$ go to \textbf{%s}." % (
                mname(st["at"]), st["N"], sc, mname(st["chosen"])))
        if not e["sel"]:
            items.append(r"\item \emph{Selection}: the root is the only node in the tree.")
        if e["expanded"]:
            items.append(r"\item \emph{Expansion}: %s was visited before ($n>0$) and has no children $\Rightarrow$ add %s; roll out from the first one, \textbf{%s}." % (
                mname(e["path"][-2]), ", ".join(mname(x) for x in e["expanded"]), mname(e["rollout_from"])))
        else:
            items.append(r"\item \emph{Expansion}: none --- \textbf{%s} has $n=0$, so we roll out directly from it." % mname(e["rollout_from"]))
        items.append(r"\item \emph{Simulation}: rollout from %s returns $%s$." % (mname(e["rollout_from"]), fmt(e["value"])))
        items.append(r"\item \emph{Backpropagation}: add $%s$ to $t$ and $1$ to $n$ for %s." % (
            fmt(e["value"]), r" $\to$ ".join(mname(x) for x in e["path"])))
        s.append("\\begin{itemize}[leftmargin=1.5em,itemsep=1pt]\n" + "\n".join(items) + "\n\\end{itemize}")
        snap = ", ".join(r"%s: %s/%d" % (mname(nm), fmt(t), n) for nm, t, n in e["snapshot"])
        s.append(r"\textit{Statistics ($t/n$) after iteration %d:} %s." % (e["it"], snap))
        parts.append("\n".join(s))
    return "\n\n\\smallskip\n".join(parts)


# ============================================================================
# CSP
# ============================================================================
class CSP:
    def __init__(self, variables, domains):
        self.vars = list(variables)
        self.dom = {v: list(domains[v]) for v in variables}
        self.cons = {}
        self.nb = {v: [] for v in variables}

    def add(self, x, y, pred):
        self.cons[(x, y)] = pred
        self.cons[(y, x)] = (lambda p: (lambda b, a: p(a, b)))(pred)
        if y not in self.nb[x]:
            self.nb[x].append(y)
        if x not in self.nb[y]:
            self.nb[y].append(x)

    def neq(self, pairs):
        for a, b in pairs:
            self.add(a, b, lambda u, v: u != v)

    def ok(self, x, vx, y, vy):
        p = self.cons.get((x, y))
        return True if p is None else p(vx, vy)


def ac3(csp, queue=None, domains=None):
    D = {v: list(d) for v, d in (domains or csp.dom).items()}
    if queue is None:
        queue = [(x, y) for (x, y) in csp.cons]
    queue = list(queue)
    trace = []
    while queue:
        xi, xj = queue.pop(0)
        removed = [x for x in D[xi] if not any(csp.ok(xi, x, xj, y) for y in D[xj])]
        added = []
        if removed:
            D[xi] = [x for x in D[xi] if x not in removed]
            if not D[xi]:
                trace.append({"arc": (xi, xj), "removed": removed, "added": [], "D": dict((k, list(v)) for k, v in D.items()), "fail": True})
                return False, D, trace
            for xk in csp.nb[xi]:
                if xk != xj and (xk, xi) not in queue:
                    queue.append((xk, xi))
                    added.append((xk, xi))
        trace.append({"arc": (xi, xj), "removed": removed, "added": added,
                      "D": dict((k, list(v)) for k, v in D.items()), "fail": False,
                      "qlen": len(queue)})
    return True, D, trace


def dom_tex(d):
    return r"\{" + ",".join(str(x) for x in d) + r"\}"


def ac3_table(trace, show_vars=None, only_changes=False):
    rows = []
    for i, t in enumerate(trace, 1):
        if only_changes and not t["removed"]:
            continue
        arc = r"$%s \to %s$" % t["arc"]
        rem = ", ".join(str(x) for x in t["removed"]) if t["removed"] else "--"
        add = ", ".join(r"$%s\to %s$" % a for a in t["added"]) if t["added"] else "--"
        dom = r"$D_{%s}=%s$" % (t["arc"][0], dom_tex(t["D"][t["arc"][0]])) if t["removed"] else ""
        if t.get("fail"):
            dom += r" \textbf{(empty: fail)}"
        rows.append(r"%d & %s & %s & %s & %s \\" % (i, arc, rem, dom, add))
    return (r"\begin{center}\small\begin{tabular}{c c c l p{5cm}}\toprule" "\n"
            r"\# & Arc popped & Removed from tail & New domain & Arcs appended to queue \\ \midrule" "\n"
            + "\n".join(rows) + "\n" r"\bottomrule\end{tabular}\end{center}")


def backtrack_fc(csp, var_order="mrv", value_order="lcv", inference="fc", static=None):
    """Backtracking search with MRV (+degree tie-break, then alphabetical/given order),
    LCV value ordering, and forward checking (or MAC). Returns trace."""
    trace = []
    assignment = {}
    order_index = {v: i for i, v in enumerate(static or csp.vars)}

    def select(D):
        un = [v for v in csp.vars if v not in assignment]
        if var_order == "static":
            return sorted(un, key=lambda v: order_index[v])[0], {}
        info = {}
        for v in un:
            deg = sum(1 for w in csp.nb[v] if w not in assignment)
            info[v] = (len(D[v]), -deg, order_index[v])
        best = min(un, key=lambda v: info[v])
        return best, info

    def lcv(var, D):
        scores = []
        for val in D[var]:
            ruled = 0
            for w in csp.nb[var]:
                if w in assignment:
                    continue
                ruled += sum(1 for y in D[w] if not csp.ok(var, val, w, y))
            scores.append((ruled, D[var].index(val), val))
        if value_order == "lcv":
            scores.sort()
        else:
            scores.sort(key=lambda s: s[1])
        return [(v, r) for r, _, v in scores]

    def infer(var, val, D):
        D2 = {k: list(v) for k, v in D.items()}
        D2[var] = [val]
        if inference == "fc":
            for w in csp.nb[var]:
                if w in assignment:
                    continue
                D2[w] = [y for y in D2[w] if csp.ok(var, val, w, y)]
                if not D2[w]:
                    return None, D2, w
            return D2, D2, None
        elif inference == "mac":
            q = [(w, var) for w in csp.nb[var] if w not in assignment]
            okk, D3, _ = ac3(csp, q, D2)
            if not okk:
                empty = [k for k, v in D3.items() if not v]
                return None, D3, empty[0] if empty else None
            return D3, D3, None
        return D2, D2, None

    def rec(D, depth):
        if len(assignment) == len(csp.vars):
            return dict(assignment)
        var, info = select(D)
        vals = lcv(var, D)
        trace.append({"type": "select", "var": var, "info": info, "vals": vals, "depth": depth,
                      "D": {k: list(v) for k, v in D.items()}})
        for val, _ in vals:
            consistent = all(csp.ok(var, val, w, assignment[w]) for w in csp.nb[var] if w in assignment)
            if not consistent:
                trace.append({"type": "inconsistent", "var": var, "val": val, "depth": depth})
                continue
            assignment[var] = val
            D2, Dshow, wipe = infer(var, val, D)
            trace.append({"type": "assign", "var": var, "val": val, "D": {k: list(v) for k, v in Dshow.items()},
                          "wipe": wipe, "depth": depth, "assigned": dict(assignment)})
            if D2 is not None:
                r = rec(D2, depth + 1)
                if r is not None:
                    return r
            del assignment[var]
            trace.append({"type": "undo", "var": var, "val": val, "depth": depth})
        trace.append({"type": "fail", "var": var, "depth": depth})
        return None

    sol = rec({k: list(v) for k, v in csp.dom.items()}, 0)
    return sol, trace


def bt_table(csp, trace, names=None):
    names = names or {}
    cols = csp.vars
    rows = []
    step = 0
    for t in trace:
        if t["type"] != "assign":
            if t["type"] == "undo":
                rows.append(r"\multicolumn{%d}{l}{\quad\textit{backtrack: undo %s=%s}} \\" % (
                    len(cols) + 2, t["var"], names.get(t["val"], t["val"])))
            continue
        step += 1
        cells = []
        for v in cols:
            d = t["D"][v]
            txt = "".join(str(names.get(x, x)) for x in d) if all(len(str(names.get(x, x))) == 1 for x in d) else ",".join(str(names.get(x, x)) for x in d)
            if v in t["assigned"]:
                txt = r"\textbf{%s}" % txt if v == t["var"] else r"\textit{%s}" % txt
            if not d:
                txt = r"\textcolor{red}{$\emptyset$}"
            cells.append(txt)
        note = ""
        if t["wipe"]:
            note = r"\textcolor{red}{$D_{%s}$ wiped out}" % t["wipe"]
        rows.append(r"%d & %s$=$%s & %s & %s \\" % (step, t["var"], names.get(t["val"], t["val"]), " & ".join(cells), note))
    head = (r"\begin{center}\small\begin{tabular}{c l %s l}\toprule" % ("c " * len(cols)) + "\n"
            + r"Step & Assign & " + " & ".join(cols) + r" & Note \\ \midrule")
    return head + "\n" + "\n".join(rows) + "\n" + r"\bottomrule\end{tabular}\end{center}"


# ============================================================================
# extra helpers
# ============================================================================
def ids(g, maxd=12):
    """IDS = DLS(0), DLS(1), ...; DLS is the lecture DFS (late goal test) in which
    nodes at depth == limit are goal-tested but not expanded."""
    its = []
    for l in range(maxd + 1):
        r = dfs(g, early=True, limit=l)
        its.append((l, r["order"], r["path"]))
        if r["path"]:
            break
    return its


def to_spec(n):
    if n.kind == "leaf":
        return n.value
    kids = [to_spec(c) for c in n.children]
    if n.kind == "chance":
        return ("chance", kids, n.probs)
    return (n.kind, kids)


def perfect_order_spec(n):
    """Children re-sorted best-first for the player to move (needs n.mm)."""
    if n.kind == "leaf":
        return n.value
    kids = list(n.children)
    if n.kind == "max":
        kids.sort(key=lambda c: -c.mm)
    elif n.kind == "min":
        kids.sort(key=lambda c: c.mm)
    return (n.kind, [perfect_order_spec(c) for c in kids])


def eff_branching(N, d):
    lo, hi = 1.0, float(N)
    for _ in range(200):
        mid = (lo + hi) / 2
        s = sum(mid ** i for i in range(d + 1))
        if s < N + 1:
            lo = mid
        else:
            hi = mid
    return lo


def puzzle_h(state, goal):
    pos = {v: (i // 3, i % 3) for i, v in enumerate(goal)}
    h1 = sum(1 for i, v in enumerate(state) if v != 0 and goal[i] != v)
    det = []
    for i, v in enumerate(state):
        if v == 0:
            continue
        r, c = i // 3, i % 3
        gr, gc = pos[v]
        det.append((v, abs(r - gr) + abs(c - gc)))
    det.sort()
    return h1, sum(d for _, d in det), det


def queens_attacks(rows):
    n = len(rows)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if rows[i] == rows[j] or abs(rows[i] - rows[j]) == abs(i - j):
                pairs.append((i + 1, j + 1))
    return pairs


def min_conflicts_board(rows):
    """conf[r][c] = #queens attacking square (row r, column c) when the queen of
    column c is moved there (others fixed). rows are 1-based rows per column."""
    n = len(rows)
    conf = [[0] * n for _ in range(n)]
    for c in range(n):
        for r in range(1, n + 1):
            k = 0
            for c2 in range(n):
                if c2 == c:
                    continue
                r2 = rows[c2]
                if r2 == r or abs(r2 - r) == abs(c2 - c):
                    k += 1
            conf[r - 1][c] = k
    return conf


# ---------------------------------------------------------------- CSP search tree
def bt_search_tree_tikz(trace, names=None, dx=1.9, dy=1.25, scale=1.0):
    names = names or {}

    class T:
        def __init__(s, label, fail=None):
            s.label = label
            s.fail = fail
            s.kids = []
            s.sol = False
    root = T(r"$\{\}$")
    stack = [root]
    for t in trace:
        if t["type"] == "assign":
            while len(stack) > t["depth"] + 1:
                stack.pop()
            nd = T(r"%s$=$%s" % (t["var"], names.get(t["val"], t["val"])),
                   fail=t["wipe"])
            stack[-1].kids.append(nd)
            stack.append(nd)
    # mark the solution path: the last chain in the stack
    if trace and trace[-1]["type"] == "assign" and not trace[-1]["wipe"]:
        for nd in stack[1:]:
            nd.sol = True
    pos = {}
    cnt = [0]

    def lay(n, d):
        if not n.kids:
            pos[id(n)] = (cnt[0] * dx, -d * dy)
            cnt[0] += 1
        else:
            for k in n.kids:
                lay(k, d + 1)
            xs = [pos[id(k)][0] for k in n.kids]
            pos[id(n)] = ((xs[0] + xs[-1]) / 2.0, -d * dy)
    lay(root, 0)
    L = [r"\begin{tikzpicture}[scale=%s, every node/.style={transform shape}, bn/.style={draw, rounded corners=2pt, font=\footnotesize, inner sep=2pt}]" % scale]
    k = [0]
    ids_ = {}

    def emit(n):
        k[0] += 1
        ids_[id(n)] = "b%d" % k[0]
        x, y = pos[id(n)]
        st = ""
        if n.sol:
            st = ", fill=green!20, very thick"
        if n.fail:
            st = ", fill=red!10, draw=red!70!black"
        L.append(r"\node[bn%s] (%s) at (%.2f,%.2f) {%s};" % (st, ids_[id(n)], x, y, n.label))
        if n.fail:
            L.append(r"\node[font=\scriptsize, text=red!70!black, below=1pt of %s] {$\times$ $D_{%s}=\emptyset$};" % (ids_[id(n)], n.fail))
        for kd in n.kids:
            emit(kd)
            L.append(r"\draw (%s) -- (%s);" % (ids_[id(n)], ids_[id(kd)]))
    emit(root)
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


def tikz_cgraph(nodes, edges, scale=1.0, size=8):
    """Plain constraint graph. nodes: {name: (x, y)}; edges: [(u, v[, opts])]."""
    L = [r"\begin{tikzpicture}[scale=%s, every node/.style={transform shape}, cv/.style={draw, thick, circle, minimum size=%smm, inner sep=0pt, font=\small\bfseries}]" % (scale, size)]
    for nm, (x, y) in nodes.items():
        L.append(r"\node[cv] (%s) at (%.2f,%.2f) {%s};" % (nm, x, y, nm))
    for e in edges:
        opt = e[2] if len(e) > 2 else ""
        L.append(r"\draw[thick] (%s) to[%s] (%s);" % (e[0], opt, e[1]))
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


def reachable_avoiding(adj, start, blocked):
    seen = {start}
    st = [start]
    while st:
        u = st.pop()
        for v in adj[u]:
            if v not in seen and v not in blocked:
                seen.add(v)
                st.append(v)
    return seen - {start}
