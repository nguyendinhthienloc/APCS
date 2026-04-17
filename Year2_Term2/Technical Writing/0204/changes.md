# changes.md — Full Revision Log

## Overview
Full upgrade of manuscript for Q1 journal submission. All changes target increased information density, methodological rigour, and space efficiency.

---

## 1. Global Changes

| Change | Rationale |
|--------|-----------|
| Removed all `\newpage` commands (intro_back.tex L1, end.tex L254) | Eliminated unnecessary page breaks wasting space |
| Removed all `\clearpage` commands (results.tex L134) | Prevented forced page breaks disrupting layout flow |
| Switched to `twocolumn` layout with 10pt font | Standard Q1 journal format; ~40% space savings |
| Added `geometry` package with 2cm margins | Tighter margins for increased text area |
| Added `enumitem` with `nosep` | Compact list spacing throughout |
| Added `caption` package with small font, 4pt skip | Reduced caption vertical footprint |
| Reduced `\textfloatsep`, `\floatsep`, `\intextsep` | Eliminated excessive whitespace around floats |
| Changed all `\begin{figure}[H]` to `[htbp]` | Better float placement; avoids forced positioning |
| Changed `\includegraphics` widths from `0.85\linewidth` to `\columnwidth` | Proper sizing for twocolumn layout |

---

## 2. Section-by-Section Changes

### main.tex
- **Abstract rewritten** (Q1 style): Added explicit novelty claim ("first systematic cross-domain co-occurrence analysis"); tightened phrasing; ~15% shorter
- Added packages: `multicol`, `enumitem`, `caption`, `xcolor`, `geometry`
- Space optimisation parameters added to preamble

### intro_back.tex (Introduction + Background)
- **`\newpage` removed** from line 1
- Introduction compressed ~20%: merged redundant sentences, tightened phrasing
- **Contributions list strengthened**: Each contribution now explicitly states novelty:
  - Contribution 1: "to our knowledge, the first such analysis spanning multiple clinical domains"
  - Contribution 2: "distinguishing it from purely conceptual prior frameworks"
  - Contribution 3: "parsimonious five-metric framework"
- Background compressed ~15%: removed repeated phrasing, merged short paragraphs

### related_work.tex
- Compressed ~20%: merged five paragraphs into four; eliminated filler phrases
- All 25+ citations preserved
- Positioning statement at end sharpened

### methodology.tex
- **[ADDED] Corpus Justification paragraph** (§4.1): Explains why n=52 is sufficient for the study's analytical objectives; cites cross-domain coverage (5 sub-domains, 28 venues), statistical power for binary correlation, and breadth of evaluation designs
- Phase 1 inclusion/exclusion criteria reformatted as inline list (saves ~8 lines)
- PRISMA flow tightened with arrow notation
- Formal definitions kept intact (all 6 equations preserved)
- Phase 3 statistical approach compressed
- Phase 4 taxonomy construction compressed ~15%

### results.tex
- **`\clearpage` removed** from line 134
- All figure references use `[htbp]` instead of `[H]`
- Figure widths changed to `\columnwidth` for twocolumn
- **[ADDED] Reference to Figure~8 (evaluation_gap)** in taxonomy validation subsection
- Domain footnote compressed

### end.tex
- **`\newpage` removed** from line 254
- **[ADDED] §6.2 Metric Redundancy and Complementarity**: Interprets AOPC–PF correlation ($\rho=0.51$) as methodological overlap vs. conceptual redundancy; explains AOPC–IROF as shared paradigm but complementary (semantic segments vs. features); interprets Sufficiency isolation as evidence of non-redundant evaluative dimension
- **[ADDED] §6.3 Minimal Evaluation Framework with Table~V**: Compact LaTeX table with columns: Metric, Layer, Role, Required/Optional, Rationale
- **[ADDED] §6.4 Clinical Implications**: Two explicit risk paragraphs — risk of missing Sufficiency (acting on correlated but not causally sufficient features); risk of missing Robustness (explanation instability under distributional shift in multi-site deployment)
- **[ADDED] Figure~6 reference** (fig6_minimal_framework.png): Three-layer framework diagram
- **[ADDED] Figure~7 reference** (fig7_metric_correlation_network.png): Metric correlation network with redundancy cluster highlighted
- Discussion §6.1 compressed ~10%
- Conclusion rewritten with explicit novelty claims
- Threats to Validity and Limitations kept intact but compressed

---

## 3. Table Optimisation

| Table | Change | Savings |
|-------|--------|---------|
| Table I (corpus) | Switched from `\hline` to `booktabs`; abbreviated domain names; shortened notes; added `\small` | ~30% height reduction |
| Table II (sensitivity) | Switched to booktabs; shortened descriptions | ~20% height reduction |
| Table III (faithfulness) | Removed `\setcounter`; switched to booktabs; shortened | ~20% height reduction |
| Table IV (perturbation) | Removed `\setcounter`; switched to booktabs; shortened | ~20% height reduction |
| **Table V (NEW)** | Minimal evaluation framework table with 5 rows × 5 columns | New addition |

---

## 4. Figures

### Existing Figures (resized for twocolumn)
| Figure | File | Change |
|--------|------|--------|
| Fig. 1 | fig1_metric_frequency.png | Width → `\columnwidth` |
| Fig. 2 | fig2_cooccurrence_heatmap.png | Width → `\columnwidth` |
| Fig. 3 | fig3_pairwise_cooccurrence.png | Width → `\columnwidth` |
| Fig. 4 | fig4_spearman_correlation.png | Width → `\columnwidth` |
| Fig. 5 | fig5_taxonomy_diagram.png | Width → `\columnwidth` |

### New Figures (to be created)

#### Figure 6: fig6_minimal_framework.png
- **Layout**: Three horizontal layers stacked vertically with connecting arrows
- **Layer 1 (blue box)**: Contains four metric boxes: "Faithfulness", "Perturbation (AOPC/PF/IROF)", "Sensitivity", "Sufficiency"
- **Layer 2 (orange box)**: Contains "System Robustness" label; dashed arrow from Sensitivity indicating cross-layer bridging
- **Layer 3 (green box)**: Contains "Human-Centred Trust" with sub-elements: "Clinician Trust", "Cognitive Load", "Decision Accuracy"
- **Labels**: Each layer shows corpus coverage percentage (90.4%, 34.6%, 13.5%)
- **Arrows**: Downward arrows between layers; bidirectional dashed arrow from Sensitivity to Layer 2

#### Figure 7: fig7_metric_correlation_network.png
- **Layout**: Network graph with 6 nodes arranged in a circular layout
- **Nodes**: Each node represents a metric (Faithfulness, Sensitivity, AOPC/MoRF, Pixel Flipping, IROF, Sufficiency); node size proportional to corpus frequency
- **Edges**: Weighted by Spearman $\rho$; thickness and colour intensity encode correlation strength
- **Redundancy cluster**: Dashed boundary enclosing AOPC/MoRF, Pixel Flipping, and IROF (perturbation cluster)
- **Sufficiency**: Positioned separately with no connecting edges (all correlations non-significant)
- **Significant edges**: Faithfulness–Sensitivity ($\rho=0.33^*$), AOPC–PF ($\rho=0.51^{***}$), AOPC–IROF ($\rho=0.37^{**}$)

#### Figure 8: fig8_evaluation_gap.png
- **Layout**: Three vertical bars or stacked horizontal bars
- **Bars**: Layer 1 = 90.4%, Layer 2 = 34.6%, Layer 3 = 13.5%
- **Colour coding**: Consistent with taxonomy diagram (blue/orange/green)
- **Labels**: Percentage values displayed on bars; layer names below

---

## 5. Content Additions Summary

| Addition | Section | Purpose |
|----------|---------|---------|
| Cross-domain novelty claim | Abstract, §1, §7 | Explicitly state first-of-its-kind analysis |
| Corpus justification | §4.1 | Justify n=52 with coverage and power arguments |
| Metric redundancy interpretation | §6.2 | Interpret AOPC–PF as methodological overlap; Sufficiency as non-redundant |
| Minimal framework table | §6.3 (Table V) | Compact actionable reference for researchers |
| Clinical implications | §6.4 | Explicit risk statements for missing Sufficiency and Robustness |
| Figure 6 (framework diagram) | §6.3 | Visual summary of three-layer framework |
| Figure 7 (correlation network) | §6.2 | Visual redundancy/complementarity map |
| Figure 8 (evaluation gap) | §5.4 | Visual quantification of layer coverage disparity |
