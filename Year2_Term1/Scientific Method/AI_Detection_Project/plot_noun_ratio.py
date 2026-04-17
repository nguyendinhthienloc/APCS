"""Plot noun/word ratio by label.

Creates two PNGs in the working directory:
 - noun_ratio_boxplot.png      (boxplot of noun/word ratio by label)
 - noun_ratio_means.png        (mean ratio per label with 95% CI error bars)

Usage:
    python plot_noun_ratio.py --input human_vs_ai_noun_word_ratio.csv

If --show is passed the plots will be displayed interactively.
"""
import argparse
import os
import sys
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats


def find_label_column(df):
    for c in ['label', 'generated', 'target', 'class']:
        if c in df.columns:
            return c
    for c in df.columns:
        if pd.api.types.is_integer_dtype(df[c]) and df[c].nunique() <= 10:
            return c
    return None


def ensure_ratio(df):
    # Prefer existing ratio column, else compute from noun_count / word_count
    if 'noun_word_ratio' in df.columns:
        return df
    if 'noun_count' in df.columns and 'word_count' in df.columns:
        df['noun_word_ratio'] = df['noun_count'] / df['word_count'].replace({0: np.nan})
        df['noun_word_ratio'] = df['noun_word_ratio'].fillna(0.0)
        return df
    # try fallback noun_count_estimate
    if 'noun_count_estimate' in df.columns and 'word_count' in df.columns:
        df['noun_word_ratio'] = df['noun_count_estimate'] / df['word_count'].replace({0: np.nan})
        df['noun_word_ratio'] = df['noun_word_ratio'].fillna(0.0)
        return df
    raise RuntimeError('No noun_word_ratio or noun_count/word_count columns found')


def plot_boxplot(df, label_col, ratio_col, out_path):
    sns.set(style='whitegrid')
    plt.figure(figsize=(6, 5))
    ax = sns.boxplot(x=label_col, y=ratio_col, data=df, palette='pastel')
    ax.set_xlabel('Label')
    ax.set_ylabel('Noun / Word ratio')
    ax.set_title('Noun/Word Ratio by Label')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_means_with_ci(df, label_col, ratio_col, out_path):
    # group means and 95% CI (Welch-style per-group using t distribution)
    groups = df.groupby(label_col)[ratio_col]
    stats_list = []
    for name, series in groups:
        s = series.dropna()
        n = len(s)
        mean = s.mean()
        std = s.std(ddof=1)
        sem = std / np.sqrt(n) if n > 0 else 0.0
        # 95% CI using t-critical
        tcrit = stats.t.ppf(1 - 0.025, df=n - 1) if n > 1 else 0.0
        ci = sem * tcrit
        stats_list.append((name, n, mean, sem, ci))

    stats_df = pd.DataFrame(stats_list, columns=['label', 'n', 'mean', 'sem', 'ci']).sort_values('label')

    plt.figure(figsize=(6, 5))
    x = np.arange(len(stats_df))
    means = stats_df['mean'].values
    cis = stats_df['ci'].values
    labels = stats_df['label'].astype(str).tolist()

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.bar(x, means, yerr=cis, capsize=8, color=['#8fbfe0', '#f7a6b0'][:len(x)])
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel('Label')
    ax.set_ylabel('Mean noun/word ratio')
    ax.set_title('Mean Noun/Word Ratio by Label (95% CI)')
    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', default='human_vs_ai_noun_word_ratio.csv', help='Input CSV with noun_word_ratio')
    parser.add_argument('--outdir', '-o', default='.', help='Output directory for PNGs')
    parser.add_argument('--show', action='store_true', help='Show plots interactively')
    args = parser.parse_args(argv)

    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}")
        sys.exit(1)

    df = pd.read_csv(args.input)
    df = ensure_ratio(df)
    label_col = find_label_column(df)
    if label_col is None:
        print('Could not find label column (label/generated/target/class)')
        sys.exit(2)

    # optional: map labels to human/AI strings if 0/1
    if set(df[label_col].unique()) <= {0, 1}:
        df[label_col] = df[label_col].map({0: 'Human', 1: 'AI'})

    ratio_col = 'noun_word_ratio'

    # prepare out paths
    box_out = os.path.join(args.outdir, 'noun_ratio_boxplot.png')
    mean_out = os.path.join(args.outdir, 'noun_ratio_means.png')

    print('Creating boxplot ->', box_out)
    plot_boxplot(df, label_col, ratio_col, box_out)
    print('Creating mean+CI plot ->', mean_out)
    plot_means_with_ci(df, label_col, ratio_col, mean_out)

    if args.show:
        # quick inline show of both (recreate for display)
        sns.set(style='whitegrid')
        plt.figure(figsize=(6,5))
        sns.boxplot(x=label_col, y=ratio_col, data=df, palette='pastel')
        plt.show()

    print('Done. Files saved:')
    print(' -', box_out)
    print(' -', mean_out)


if __name__ == '__main__':
    main()
