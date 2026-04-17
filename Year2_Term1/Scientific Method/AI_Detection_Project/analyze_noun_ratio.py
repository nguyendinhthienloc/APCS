import pandas as pd
import numpy as np
from scipy import stats


def find_label_column(df):
    for c in ['label', 'generated', 'target', 'class']:
        if c in df.columns:
            return c
    # fallback: integer-like with 2 unique values
    for c in df.columns:
        if pd.api.types.is_integer_dtype(df[c]) and df[c].nunique() <= 5:
            return c
    return None


def cohen_d(x, y):
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    pooled_std = np.sqrt(((nx - 1) * x.std(ddof=1) ** 2 + (ny - 1) * y.std(ddof=1) ** 2) / dof)
    if pooled_std == 0:
        return 0.0
    return (x.mean() - y.mean()) / pooled_std


def main():
    path = 'human_vs_ai_noun_word_ratio.csv'
    df = pd.read_csv(path)
    print(f'Loaded {len(df)} rows from {path}')

    label_col = find_label_column(df)
    if label_col is None:
        raise SystemExit('Could not find a label column in CSV')
    print(f'Using label column: {label_col}')

    ratio_col = 'noun_word_ratio'
    if ratio_col not in df.columns:
        raise SystemExit(f"Column '{ratio_col}' not found in CSV")

    # Ensure label values are 0/1 (map if necessary)
    labels = df[label_col].unique()
    print('Label values present:', labels)

    group0 = df[df[label_col] == 0][ratio_col].dropna()
    group1 = df[df[label_col] == 1][ratio_col].dropna()

    def stats_for(s):
        return dict(n=len(s), mean=float(s.mean()), std=float(s.std(ddof=1)), median=float(s.median()))

    s0 = stats_for(group0)
    s1 = stats_for(group1)

    print('\nGroup 0 (likely human) stats:', s0)
    print('Group 1 (likely AI) stats:', s1)

    # t-test (Welch)
    tstat, pval = stats.ttest_ind(group1, group0, equal_var=False)
    d = cohen_d(group1, group0)

    print(f"\nWelch t-test: t = {tstat:.4f}, p = {pval:.4e}")
    print(f"Cohen's d (group1 - group0): {d:.4f}")

    # Simple interpretation
    mean_diff = s1['mean'] - s0['mean']
    print(f"\nMean noun/word ratio: AI = {s1['mean']:.4f}, Human = {s0['mean']:.4f}, difference = {mean_diff:.4f}")

    # Check distribution shape
    print('\nQuick distribution info:')
    print('AI ratio: min,25%,50%,75%,max ->', group1.quantile([0, .25, .5, .75, 1.0]).tolist())
    print('Human ratio: min,25%,50%,75%,max ->', group0.quantile([0, .25, .5, .75, 1.0]).tolist())

    # Save a tiny summary CSV
    summary = pd.DataFrame([{
        'label': 0,
        'n': s0['n'],
        'mean_ratio': s0['mean'],
        'std_ratio': s0['std'],
        'median_ratio': s0['median']
    }, {
        'label': 1,
        'n': s1['n'],
        'mean_ratio': s1['mean'],
        'std_ratio': s1['std'],
        'median_ratio': s1['median']
    }])
    summary.to_csv('noun_word_ratio_summary_by_label.csv', index=False)
    print('\nWrote summary to noun_word_ratio_summary_by_label.csv')


if __name__ == '__main__':
    main()
