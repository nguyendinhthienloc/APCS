"""Build the practice midterms:  python build.py [1 2 3 4] [--no-pdf]

Writes ../exams/ExamK.tex and ../solutions/ExamK_Solutions.tex and compiles them
with pdflatex (run twice for the page count)."""
import importlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from common import write  # noqa: E402

OVERFULL = {}


def compile_tex(folder, name):
    for _ in range(2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", name + ".tex"],
                           cwd=folder, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            log = r.stdout
            i = log.find("\n!")
            print(log[i:i + 1500] if i >= 0 else log[-2500:])
            raise SystemExit("LaTeX failed for %s" % name)
    log = open(os.path.join(folder, name + ".log"), encoding="utf-8", errors="replace").read()
    import re
    bad = re.findall(r"(Overfull \\[hv]box \(([\d.]+)pt too (?:wide|high)\)[^\n]*\n?[^\n]*)", log)
    bad = [b for b in bad if float(b[1]) > 0.5]
    OVERFULL[name] = [b[0].replace("\n", " ")[:160] for b in bad]
    for ext in (".aux", ".log", ".out"):
        p = os.path.join(folder, name + ext)
        if os.path.exists(p):
            os.remove(p)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    nums = [int(a) for a in args] or [1, 2, 3, 4]
    pdf = "--no-pdf" not in sys.argv
    ed = os.path.join(ROOT, "exams")
    sd = os.path.join(ROOT, "solutions")
    os.makedirs(ed, exist_ok=True)
    os.makedirs(sd, exist_ok=True)
    for k in nums:
        mod = importlib.import_module("exam%d" % k)
        E = mod.build()
        write(os.path.join(ed, "Exam%d.tex" % k), E.render(False))
        write(os.path.join(sd, "Exam%d_Solutions.tex" % k), E.render(True))
        if pdf:
            compile_tex(ed, "Exam%d" % k)
            compile_tex(sd, "Exam%d_Solutions" % k)
        print("Exam %d done" % k)
    for nm, lst in OVERFULL.items():
        print("%-20s overfull boxes > 0.5pt: %d" % (nm, len(lst)))
        for l in lst:
            print("    ", l)


if __name__ == "__main__":
    main()
