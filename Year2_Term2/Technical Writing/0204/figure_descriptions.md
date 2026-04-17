# New Figure Specifications

## Figure 6: fig6_minimal_framework.png
**Filename:** `figures/fig6_minimal_framework.png`
**Type:** Single-column figure (`\columnwidth`)

### Layout
- Three horizontal rectangular layers stacked vertically, connected by downward arrows
- Each layer has a coloured background and rounded corners
- Consistent colour scheme with Fig. 5 (taxonomy diagram)

### Elements
**Layer 1 (Blue background, top):**
- Title: "Layer 1: Mathematical Faithfulness"
- Four boxes inside: "Faithfulness (Req.)", "Perturbation: AOPC/PF/IROF (Req.)", "Sensitivity (Req.†)", "Sufficiency (Req.†)"
- Coverage badge: "90.4% of corpus"

**Layer 2 (Orange background, middle):**
- Title: "Layer 2: System Robustness"
- Label: "Partially addressed by Sensitivity"
- Dashed arrow from Sensitivity box in Layer 1 to this layer (cross-layer bridging)
- Coverage badge: "34.6% of corpus"

**Layer 3 (Green background, bottom):**
- Title: "Layer 3: Human-Centred Trust"
- Three sub-boxes: "Clinician Trust", "Cognitive Load", "Decision Accuracy"
- Label: "(Req.) — at least one measure"
- Coverage badge: "13.5% of corpus"

**Footer:** "† = may be omitted under resource constraints if explicitly justified"

### LaTeX Insertion
```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.9\columnwidth]{figures/fig6_minimal_framework}
  \caption{Proposed minimal evaluation framework organised by taxonomy layer.
  Layer~1 requires Faithfulness, one perturbation metric, Sensitivity, and
  Sufficiency. Layer~2 is partially addressed by Sensitivity. Layer~3
  requires at least one clinician-facing measure. Arrows indicate cross-layer
  bridging.}
  \label{fig:minimal_framework}
\end{figure}
```

---

## Figure 7: fig7_metric_correlation_network.png
**Filename:** `figures/fig7_metric_correlation_network.png`
**Type:** Single-column figure (`0.9\columnwidth`)

### Layout
- Network/graph visualisation with 6 nodes arranged roughly circular
- Clean white background

### Elements
**Nodes (6 total):**
- Faithfulness (large node, warm red) — size proportional to frequency (47/52)
- Sensitivity (large node, coral) — 34/52
- AOPC/MoRF (medium node, light blue) — 13/52
- Pixel Flipping (medium node, medium blue) — 14/52
- IROF (small node, teal) — 4/52
- Sufficiency (small node, dark blue) — 4/52; positioned separately/isolated

**Edges (only statistically significant ones):**
- Faithfulness ↔ Sensitivity: thin line, ρ=0.33* label
- AOPC/MoRF ↔ Pixel Flipping: thick line, ρ=0.51*** label
- AOPC/MoRF ↔ IROF: medium line, ρ=0.37** label

**Redundancy cluster:**
- Dashed grey boundary enclosing AOPC/MoRF, Pixel Flipping, IROF
- Label: "Perturbation cluster"

**Sufficiency:**
- No connecting edges (all correlations non-significant)
- Positioned at bottom or right, visually isolated
- Optional label: "Isolated (all ρ < 0, n.s.)"

### LaTeX Insertion
```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.9\columnwidth]{figures/fig7_metric_correlation_network}
  \caption{Metric correlation network derived from Spearman's $\rho$ across
  the 52-study corpus. Node size encodes metric frequency; edge thickness
  encodes correlation strength. The dashed boundary highlights the
  perturbation-based redundancy cluster. Sufficiency is isolated with no
  significant correlations. Only edges with $p < 0.05$ are shown.}
  \label{fig:correlation_network}
\end{figure}
```

---

## Figure 8: fig8_evaluation_gap.png
**Filename:** `figures/fig8_evaluation_gap.png`
**Type:** Single-column figure (`0.9\columnwidth`)

### Layout
- Three horizontal bars (or vertical bars) showing coverage percentages
- Clean, minimal design with high data-to-ink ratio

### Elements
**Bar 1 (Blue):**
- Label: "Layer 1: Mathematical Faithfulness"
- Value: 90.4% (47/52 studies)
- Bar nearly full-width

**Bar 2 (Orange):**
- Label: "Layer 2: System Robustness"
- Value: 34.6% (18/52 studies)
- Bar roughly one-third width

**Bar 3 (Green):**
- Label: "Layer 3: Human-Centred Trust"
- Value: 13.5% (7/52 studies)
- Bar roughly one-seventh width

**Annotations:**
- Percentage labels displayed on or next to each bar
- Study counts (n=47, n=18, n=7) shown alongside
- Optional: gap arrows or brackets indicating the disparity

### LaTeX Insertion
```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.9\columnwidth]{figures/fig8_evaluation_gap}
  \caption{Evaluation coverage gap across the three taxonomy layers.
  Layer~1 is addressed by 90.4\% of studies, whereas Layer~2 and Layer~3
  are covered by only 34.6\% and 13.5\%, respectively---quantifying the
  structural imbalance in medical XAI evaluation.}
  \label{fig:evaluation_gap}
\end{figure>
```
