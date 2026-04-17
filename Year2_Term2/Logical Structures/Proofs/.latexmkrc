# .latexmkrc — latexmk configuration for this proofs project
#
# Usage:
#   latexmk              → compile once
#   latexmk -pvc         → watch for changes and recompile automatically
#   latexmk -C           → clean all generated files

# Use pdflatex to produce a PDF directly
$pdf_mode = 1;

# Non-stop mode so compilation doesn't hang on errors
$pdflatex = 'pdflatex -interaction=nonstopmode -synctex=1 %O %S';

# Extra extensions to clean up with 'latexmk -C'
$clean_ext = 'synctex.gz synctex.gz(busy) fdb_latexmk fls aux log out toc';
