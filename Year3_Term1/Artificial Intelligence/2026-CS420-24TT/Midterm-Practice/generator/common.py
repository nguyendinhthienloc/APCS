"""Document builder: layout of the CS420 review-exercise sheets
("Question N." blocks, sub-questions, empty answer boxes / tables to fill)."""
from engine import *
from rv import *

PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=1.9cm, top=2.1cm, bottom=2.0cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb}
\usepackage{enumitem,booktabs,array,tabularx,multirow}
\usepackage[normalem]{ulem}
\usepackage{adjustbox}
\usepackage{xcolor}
\usepackage{fancyhdr,lastpage}
\usepackage[most]{tcolorbox}
\usepackage{tikz}
\usetikzlibrary{shapes.geometric,arrows.meta,positioning,calc}
\usepackage[hidelinks]{hyperref}
\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt}
\renewcommand{\arraystretch}{1.25}
\emergencystretch=2em
\pagestyle{fancy}\fancyhf{}
\lhead{\small\textit{Course: CS420 -- Artificial Intelligence}}
\rhead{\small @@KIND@@}
\cfoot{\small Page \thepage\ of \pageref{LastPage}}
\renewcommand{\headrulewidth}{0.4pt}
% empty answer box (exam) / filled box (solution)
\newtcolorbox{ansbox}[1][]{enhanced, breakable, colback=white, colframe=black!55, boxrule=0.5pt, arc=0pt,
  left=5pt, right=5pt, top=3pt, bottom=3pt, before skip=3pt, after skip=6pt, #1}
\newtcolorbox{solbox}{enhanced, breakable, colback=blue!2!white, colframe=blue!50!black, boxrule=0.6pt, arc=0pt,
  left=6pt, right=6pt, top=4pt, bottom=4pt, before skip=3pt, after skip=8pt,
  fontupper=\color{black}}
\newcommand{\question}[1]{\par\medskip\noindent\textbf{Question #1.}\ }
\newcommand{\subq}[1]{\par\smallskip\noindent\textbf{#1}\ }
\newcommand{\T}{\textbf{\textcolor{green!45!black}{TRUE}}}
\newcommand{\F}{\textbf{\textcolor{red!70!black}{FALSE}}}
@@TREESTYLES@@
\begin{document}
"""


def lines(n):
    """kept for compatibility: an empty answer box of n 'lines' height"""
    return box(0.75 * n)


def box(height_cm):
    return r"\begin{ansbox}[height=%.1fcm]\end{ansbox}" % height_cm


class Exam:
    def __init__(self, num, duration="120 minutes", dfs_goal="early"):
        self.num = num
        self.duration = duration
        self.blocks = []
        self.qn = 0
        self.sub_i = 0

    # --- structure ---------------------------------------------------------
    def question(self, text, title=None):
        self.qn += 1
        self.sub_i = 0
        t = (r"\textit{%s.} " % title) if title else ""
        self.blocks.append(("raw", r"\question{%d}" % self.qn + t + text, None, None))
        return self.qn

    def sub(self, text, sol, space=None, label=None):
        """A sub-question (a), (b), ...  `space` = exam answer area (cm number or tex)."""
        if label is None:
            label = "(%s)" % "abcdefghijklmnop"[self.sub_i]
            self.sub_i += 1
        if space is None:
            space = 2.2
        if isinstance(space, (int, float)):
            space = box(space)
        self.blocks.append(("sub", label, text, sol, space))

    def raw(self, both="", exam=None, sol=None):
        self.blocks.append(("raw", both, exam, sol))

    def newpage(self, which="both"):
        self.blocks.append(("np", which))

    # legacy helpers used by older code
    def part(self, *a, **k):
        pass

    def q(self, label, pts, text, sol, space=""):
        self.sub(text, sol, space if space != "" else 2.2, label="")

    # --- rendering -----------------------------------------------------------
    def render(self, solution):
        kind = ("Practice Test %d -- Solution" if solution else "Practice Test %d") % self.num
        out = [PREAMBLE.replace("@@KIND@@", kind).replace("@@TREESTYLES@@", TREE_STYLES)]
        out.append(r"""
{\large\textbf{\textit{Course: CS420 -- Artificial Intelligence}}}\par
{\textbf{\textit{Midterm examination review -- Lectures 0 to 3}}}\par
\begin{center}{\Large\bfseries PRACTICE MIDTERM EXAMINATION -- TEST %d%s}\\[3pt]
{\small Duration: %s \quad$\cdot$\quad Closed book \quad$\cdot$\quad Calculator allowed}\end{center}
\noindent\rule{\linewidth}{0.6pt}
""" % (self.num, r"\\[2pt]\textcolor{blue!55!black}{SOLUTION}" if solution else "", self.duration))
        if not solution:
            out.append(r"\noindent Full name: \rule{6.5cm}{0.3pt}\hfill Student ID: \rule{4cm}{0.3pt}\par\smallskip")
        out.append(r"{\small\textit{Unless a question says otherwise, ties are broken in alphabetical order (left-to-right in trees), and "
                   r"successors are generated in alphabetical order.}}\par")
        for b in self.blocks:
            if b[0] == "raw":
                _, both, ex, so = b
                out.append(both)
                if solution and so:
                    out.append(so)
                if not solution and ex:
                    out.append(ex)
            elif b[0] == "sub":
                _, label, text, sol, space = b
                out.append((r"\subq{%s}" % label if label else r"\par\smallskip\noindent ") + text)
                if solution:
                    out.append("\\begin{solbox}\n" + sol + "\n\\end{solbox}")
                else:
                    out.append(space)
            elif b[0] == "np":
                if b[1] == "both" or (b[1] == "exam" and not solution) or (b[1] == "sol" and solution):
                    out.append(r"\clearpage")
        out.append(r"\end{document}")
        import re
        txt = "\n".join(out)
        # guard: control words glued to following letters (e.g. "\parSolution")
        txt = re.sub(r"\\(par|hline|medskip|smallskip|noindent|centering)(?=[A-Z])",r"\\\1 ", txt)
        return txt


# ---------------------------------------------------------------- shared blocks
def tf_block(E, items):
    E.raw(r"For each statement, circle \textbf{T} or \textbf{F} and justify your answer in one or two sentences "
          r"(an answer without a correct justification earns no credit).")
    for k, (st, truth, why) in enumerate(items, 1):
        E.sub(st + r" \hfill \textbf{T \quad F}", (r"\T" if truth else r"\F") + r". " + why, 1.5, label="%d." % k)


def center(s):
    if "tikzpicture" in s and "tabular" not in s:
        # never wider than the current line (exam page or solution box)
        s = "\\begin{adjustbox}{max width=\\linewidth}\n" + s + "\n\\end{adjustbox}"
    return "\\begin{center}\n" + s + "\n\\end{center}"


def seq(lst):
    return " ".join(lst) if lst else "--"


def pth(lst):
    return " ".join(lst) if lst else "failure"


def fset(lst):
    return r"$\{$ " + ", ".join(lst) + r" $\}$" if lst else r"$\{\ \}$"


def write(path, txt):
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)


# ---------------------------------------------------------------- graph-search question
def graph_search_question(E, g, intro, show_h_note=True, extra=None):
    """Review-sheet format: list of expanded states, path, final frontier."""
    rb, rd = bfs(g), dfs(g, early=True)
    ru = best_first(g, "ucs")
    rg = best_first(g, "gbfs", early_goal=True)
    ra = best_first(g, "astar")
    E.question(intro + center(tikz_graph(g)) +
               r"For each search strategy, (a) list, in order, the states \textbf{expanded}, (b) give the path found and (c) give the final content "
               r"of the frontier (a state is expanded when it is removed from the frontier). Conventions: BFS, DFS and greedy best-first search "
               r"test a state for the goal when it is \emph{generated} (so the goal is not expanded); UCS and A* test it when it is \emph{removed} "
               r"from the frontier (graph search; a cheaper path to a frontier state replaces its entry). DFS avoids loops by remembering the "
               r"states on the current path only. The path returned will not be accepted if the list of expanded states is wrong.")
    rows = [("Breadth-first search", rb, True), ("Uniform-cost search", ru, True), ("Depth-first search", rd, False),
            ("Greedy best-first search", rg, True), ("Graph-search A*", ra, True)]

    def table(sol):
        lines_ = [r"\begin{center}\small\begin{tabularx}{\linewidth}{|>{\raggedright}p{2.6cm}|>{\raggedright}X|>{\raggedright}p{3.6cm}|>{\raggedright\arraybackslash}p{2.6cm}|}\hline",
                  r"\textbf{Algorithm} & \textbf{List of expanded states} & \textbf{Path returned} & \textbf{Final frontier}\\ \hline"]
        for name, r, fr in rows:
            if sol:
                frs = fset(r.get("final", [])) if fr else "(not asked)"
                lines_.append(r"%s & \textcolor{blue!60!black}{%s} & \textcolor{blue!60!black}{%s} (cost %s) & \textcolor{blue!60!black}{%s}\\ \hline"
                              % (name, seq(r["order"]), pth(r["path"]), fmt(g.path_cost(r["path"])), frs))
            else:
                lines_.append(r"%s & & & %s\\[8mm] \hline" % (name, "" if fr else r"\textit{(not asked)}"))
        lines_.append(r"\end{tabularx}\end{center}")
        return "\n".join(lines_)

    details = (r"\textbf{BFS} (queue after each expansion):" + queue_trace_table(rb, "bfs")
               + r"\textbf{DFS} (stack after each expansion):" + queue_trace_table(rd, "dfs")
               + r"\textbf{UCS:}" + bf_trace_table(ru, "ucs", g)
               + r"\textbf{Greedy best-first:}" + bf_trace_table(rg, "gbfs", g)
               + r"\textbf{A*:}" + bf_trace_table(ra, "astar", g))
    E.raw(exam=table(False), sol="\\begin{solbox}\n" + table(True) + details + "\n\\end{solbox}")
    return rb, rd, ru, rg, ra
