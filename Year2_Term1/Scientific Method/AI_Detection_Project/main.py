# full_analysis_human_vs_ai.py
"""
Full dataset exploration + noun counting + basic plots for
'Human vs AI Generated Essays' (Kaggle).
Outputs:
 - human_vs_ai_essays_with_wordcount_nouncount.csv
 - figure_wordcount.png
 - figure_nouncount.png
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Attempt to import NLTK; if missing, give user instructions
try:
    import nltk
    from nltk import word_tokenize, pos_tag
except Exception as e:
    print("NLTK is required but not installed or not available.")
    print("Install with: pip install nltk")
    print("Then run once: python -c \"import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')\"")
    raise

# Ensure required NLTK data is present (safe to call multiple times)
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# -------------------------
# Helper: find CSV in cwd
# -------------------------
def find_csv(candidates=None):
    if candidates is None:
        candidates = []
    for name in candidates:
        if os.path.exists(name):
            return name
    for fname in os.listdir(os.getcwd()):
        if fname.lower().endswith('.csv'):
            return fname
    return None

# Candidate filenames commonly used
possible = [
    "human_vs_ai_essays.csv",
    "human_vs_ai_essays_with_wordcount.csv",
    "balanced_ai_human_prompts.csv",
    "balanced_ai_human_prompts_0.csv",
    "essays.csv",
    "data.csv",
]

csv_path = find_csv(possible)
if csv_path is None:
    print("No CSV found in the current directory. Please place the dataset CSV here.")
    print("Files here:")
    for f in os.listdir(os.getcwd()):
        print(" -", f)
    sys.exit(1)

print(f"Using dataset file: {csv_path}\n")

# -------------------------
# Load CSV into DataFrame
# -------------------------
df = pd.read_csv(csv_path)
print("First 5 rows:")
print(df.head(5))

print("\nDataFrame info:")
print(df.info())

print("\nColumns:", list(df.columns))

# -------------------------
# Standardize column names: find text and label columns
# -------------------------
text_col = None
label_col = None

possible_text_cols = ['text', 'essay', 'content', 'body']
possible_label_cols = ['label', 'generated', 'target', 'class']

for c in df.columns:
    cl = c.lower()
    if cl in possible_text_cols:
        text_col = c
    if cl in possible_label_cols:
        label_col = c

# fallback heuristics
if text_col is None:
    # choose the longest string column if any
    str_cols = [c for c in df.columns if df[c].dtype == object]
    if len(str_cols) == 1:
        text_col = str_cols[0]
    elif len(str_cols) > 1:
        # pick the column with longest average string length
        avg_lens = {c: df[c].astype(str).map(len).mean() for c in str_cols}
        text_col = max(avg_lens, key=avg_lens.get)

if label_col is None:
    # try numeric columns with small number of unique values (0/1)
    for c in df.columns:
        if pd.api.types.is_integer_dtype(df[c]) or pd.api.types.is_float_dtype(df[c]):
            if df[c].nunique() <= 5:
                label_col = c
                break

if text_col is None or label_col is None:
    print("\nCould not confidently identify text and/or label columns automatically.")
    print("Please edit the script and set `text_col` and `label_col` variables to the correct column names.")
    print("Detected columns:", list(df.columns))
    sys.exit(1)

print(f"\nDetected text column: '{text_col}'")
print(f"Detected label column: '{label_col}'")

# -------------------------
# Basic stats & counts
# -------------------------
n_rows = len(df)
print(f"\nNumber of rows: {n_rows}")

print("\nLabel value counts:")
print(df[label_col].value_counts(dropna=False))

# Add word_count (if not present)
if 'word_count' not in df.columns:
    df['word_count'] = df[text_col].astype(str).apply(lambda x: len(x.split()))
print("\nAverage words per essay:", round(df['word_count'].mean(), 2))

# -------------------------
# Noun counting function
# -------------------------
def count_nouns(text):
    """
    Count tokens tagged as nouns by NLTK POS tagger.
    Tags that start with 'NN' are considered nouns (NN, NNS, NNP, NNPS).
    """
    try:
        tokens = word_tokenize(str(text))
        tagged = pos_tag(tokens)
        noun_count = sum(1 for _, tag in tagged if tag.startswith('NN'))
        return noun_count
    except Exception:
        return 0

# Add noun_count column (this may take time for large datasets)
if 'noun_count' not in df.columns:
    print("\nCounting nouns across all essays (this may take a while depending on dataset size)...")
    df['noun_count'] = df[text_col].astype(str).apply(count_nouns)
    print("Noun counting completed.")

# -------------------------
# Grouped statistics
# -------------------------
grouped = df.groupby(label_col).agg(
    count=('word_count', 'count'),
    avg_word_count=('word_count', 'mean'),
    avg_noun_count=('noun_count', 'mean'),
    median_noun_count=('noun_count', 'median'),
).reset_index()

print("\nGrouped summary statistics:")
print(grouped)

# Save augmented CSV
out_csv = "human_vs_ai_essays_with_wordcount_nouncount.csv"
df.to_csv(out_csv, index=False)
print(f"\nSaved augmented data to: {out_csv}")

# -------------------------
# Noun-to-word ratio and separate CSV
# -------------------------
if 'noun_count' in df.columns and 'word_count' in df.columns:
    # avoid division-by-zero
    df['noun_word_ratio'] = df['noun_count'] / df['word_count'].replace({0: np.nan})
    df['noun_word_ratio'] = df['noun_word_ratio'].fillna(0.0)

    # choose columns to export (include text for context)
    out_cols = [text_col, label_col, 'word_count', 'noun_count', 'noun_word_ratio']
    ratio_csv = "human_vs_ai_noun_word_ratio.csv"
    df.loc[:, out_cols].to_csv(ratio_csv, index=False)
    print(f"Saved noun/word ratio per-essay CSV: {ratio_csv}")
else:
    print("Could not compute noun/word ratio — noun_count or word_count missing.")

# -------------------------
# Plotting: Average word_count and noun_count per label
# -------------------------
# Prepare plotting labels
labels = grouped[label_col].astype(str).tolist()
avg_words = grouped['avg_word_count'].tolist()
avg_nouns = grouped['avg_noun_count'].tolist()

# Bar chart - average word count
plt.figure(figsize=(6,4))
plt.bar(labels, avg_words)
plt.title("Average Essay Length (words) by Label")
plt.xlabel("Label (0=Human, 1=AI) -- detected column: " + str(label_col))
plt.ylabel("Average Word Count")
plt.tight_layout()
wc_fig = "figure_wordcount.png"
plt.savefig(wc_fig, dpi=150)
plt.close()
print(f"Saved figure: {wc_fig}")

# Bar chart - average noun count
plt.figure(figsize=(6,4))
plt.bar(labels, avg_nouns)
plt.title("Average Noun Count by Label")
plt.xlabel("Label (0=Human, 1=AI) -- detected column: " + str(label_col))
plt.ylabel("Average Noun Count")
plt.tight_layout()
nc_fig = "figure_nouncount.png"
plt.savefig(nc_fig, dpi=150)
plt.close()
print(f"Saved figure: {nc_fig}")

# Also print some example essays for illustration
print("\n--- Example essays (for demonstration) ---")
for lab in df[label_col].unique()[:2]:
    sample = df[df[label_col] == lab][text_col].astype(str).iloc[0]
    wc = df[df[label_col] == lab]['word_count'].iloc[0]
    nc = df[df[label_col] == lab]['noun_count'].iloc[0]
    print(f"\nLabel={lab} | word_count={wc} | noun_count={nc}")
    print("Sample text (first 300 chars):")
    print(sample[:300].replace("\n", " "))

print("\nAll done. You can embed the saved PNG figures and the augmented CSV into your report.")

