#!/usr/bin/env python3
"""Compute noun-to-word ratio from an existing augmented CSV.

Usage: python compute_ratio_from_csv.py [input_csv]
If no input CSV is provided it will use
`human_vs_ai_essays_with_wordcount_nouncount.csv` in the cwd.
"""
import sys
import os
import pandas as pd
import numpy as np


def main(argv):
    default = "human_vs_ai_essays_with_wordcount_nouncount.csv"
    path = argv[1] if len(argv) > 1 else default
    if not os.path.exists(path):
        print(f"Input file not found: {path}")
        return 2

    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows from: {path}")

    # Choose noun column: prefer 'noun_count' when it contains non-zero values,
    # otherwise fall back to 'noun_count_estimate' if present.
    noun_col = None
    if 'noun_count' in df.columns and df['noun_count'].sum() > 0:
        noun_col = 'noun_count'
    elif 'noun_count_estimate' in df.columns:
        noun_col = 'noun_count_estimate'
    else:
        # Try to detect any column with 'noun' in the name
        for c in df.columns:
            if 'noun' in c.lower():
                noun_col = c
                break

    if noun_col is None:
        print("No noun-count column found in input CSV. Please provide a file with a noun_count or noun_count_estimate column.")
        return 3

    if 'word_count' not in df.columns:
        print("No 'word_count' column found in input CSV. Please add word counts first.")
        return 4

    # Compute ratio safely
    df['noun_word_ratio'] = df[noun_col] / df['word_count'].replace({0: np.nan})
    df['noun_word_ratio'] = df['noun_word_ratio'].fillna(0.0)

    out_csv = 'human_vs_ai_noun_word_ratio.csv'
    cols = []
    # include text if present and not excessively large; always include label/word/noun/ratio
    if 'text' in df.columns:
        cols.append('text')
    # try to include a label-like column
    label_col = None
    for c in ['label', 'generated', 'target', 'class']:
        if c in df.columns:
            label_col = c
            break
    if label_col is None:
        # try to find an integer-like column with few unique values
        for c in df.columns:
            if pd.api.types.is_integer_dtype(df[c]) and df[c].nunique() <= 10:
                label_col = c
                break
    if label_col:
        cols.append(label_col)

    cols.extend(['word_count', noun_col, 'noun_word_ratio'])

    df.to_csv(out_csv, columns=cols, index=False)
    print(f"Saved noun/word ratio CSV using '{noun_col}' as noun column: {out_csv}")
    print("Summary stats:")
    print(df['noun_word_ratio'].describe())
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
