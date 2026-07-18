# STAT452 Midterm Tests: Comprehensive Solutions and R Guide

This guide covers both papers in this folder:

- `MidTerm_STAT452_23TT2.pdf` - written midterm
- `Midterm_Practical.pdf` - R practical midterm

The companion script `midterm_solutions.R` reproduces all numerical results. The
two linked datasets from the practical paper are saved as `seatpos.csv` and
`newdata.csv`.

## Quick answer sheet

| Item | Main result |
|---|---|
| Written 1(a) | `y_hat = 1.819205 + 0.486520 x1 + 0.558644 x2`; R-squared = 0.984959 |
| Written 1(b) | Add `x2`; partial F = 117.42, p = 0.008409 |
| Written 1(c) | Predicted score = 7.603669 |
| Written 2(a) | `log(y_hat) = 0.924456 + 0.241221 x` |
| Written 2(b) | Year-5 plug-in prediction = 8.419576 million |
| Written 3(a) | `logit(p_hat) = -3.449548 + 0.002294 x1 + 0.777014 x2 - 0.560031 x3` |
| Written 3(b) | Predicted classes: 0, 0, 1, 0 |
| Practical OLS | R-squared = 0.687; adjusted R-squared = 0.600; overall p = 1.31e-5 |
| Practical ridge | With the fixed folds in the script, lambda.min = 36.521 |
| Practical LASSO | lambda.min = 5.748; nonzero predictors are Age, Ht, and Leg |

---

# Part I - Written Midterm

## Problem 1 - Multiple linear regression

### Core idea

Multiple regression chooses the plane that minimizes the sum of squared vertical
residuals. Here the plane uses both self-study time (`x1`) and tutoring time
(`x2`) to predict the score `y`.

The model is

```text
y_i = beta_0 + beta_1 x1_i + beta_2 x2_i + error_i.
```

### 1(a) Estimate the coefficients and R-squared

Write the model in matrix form as `y = X beta + error`, where the first column
of `X` is a column of ones:

```text
X = [1  5  1]       y = [ 5.0]
    [1  9  0]           [ 6.0]
    [1  7  7]           [ 9.5]
    [1  9  7]           [10.0]
    [1  3  8]           [ 7.5]
```

The least-squares estimator is

```text
beta_hat = (X'X)^(-1) X'y.
```

For these data,

```text
X'X = [  5   33   23]       X'y = [ 38.0]
       [ 33  245  141]              [258.0]
       [ 23  141  163]              [201.5]
```

Solving the normal equations gives

```text
beta_0_hat = 1.819205
beta_1_hat = 0.486520
beta_2_hat = 0.558644
```

Therefore,

```text
y_hat = 1.819205 + 0.486520 x1 + 0.558644 x2.
```

Interpretation, always holding the other predictor fixed:

- One additional hour of self-study is associated with an estimated 0.4865-point
  increase in score.
- One additional hour of tutoring is associated with an estimated 0.5586-point
  increase in score.
- The intercept is the fitted score at `x1 = x2 = 0`. It is mathematically needed,
  but the dataset contains no student near that combination, so it should not be
  given a strong practical interpretation.

The fitted residual sum of squares and total sum of squares are

```text
SSE = sum((y_i - y_hat_i)^2) = 0.281267
SST = sum((y_i - y_bar)^2)   = 18.700000
```

Thus,

```text
R-squared = 1 - SSE/SST
          = 1 - 0.281267/18.7
          = 0.984959.
```

About 98.50% of the observed score variation in these five students is explained
by the fitted model. This is an in-sample description, not proof that study hours
cause higher scores, and the sample is extremely small.

R verification:

```r
d <- data.frame(
  x1 = c(5, 9, 7, 9, 3),
  x2 = c(1, 0, 7, 7, 8),
  y  = c(5, 6, 9.5, 10, 7.5)
)
fit <- lm(y ~ x1 + x2, data = d)
coef(fit)
summary(fit)$r.squared
```

### 1(b) Compare `y ~ x1` with `y ~ x1 + x2`

The reduced model is nested inside the full model. The partial F test asks:

```text
H0: beta_2 = 0  (x2 adds no linear information after x1)
H1: beta_2 != 0.
```

From the supplied ANOVA table,

```text
F = 117.42, p = 0.008409.
```

At significance level 0.05, `p < 0.05`, so reject `H0`. The tutoring variable
significantly reduces RSS after self-study time has already been included. Among
the two proposed models, use the full model `y ~ x1 + x2`.

Do not compare the two models merely by noting that the full model has a smaller
RSS: adding a predictor can never increase training RSS. The F test determines
whether the reduction is large relative to the remaining error and degrees of
freedom.

### 1(c) Prediction

At `x1 = 5` and `x2 = 6`,

```text
y_hat = 1.819205 + 0.486520(5) + 0.558644(6)
      = 7.603669.
```

The predicted math score is approximately **7.60**.

R verification:

```r
predict(fit, newdata = data.frame(x1 = 5, x2 = 6))
```

### Casio fx-580VN X verification

The calculator does not have a direct two-predictor regression menu. Use matrix
mode to solve the three normal equations.

1. Open `MENU -> Matrix`.
2. Define `MatA` as the 3-by-3 matrix `X'X` shown above.
3. Define `MatB` as the 3-by-1 matrix `X'y` shown above.
4. Calculate `MatA^(-1) * MatB`.
5. The display should give approximately `(1.819205, 0.486520, 0.558644)'`.
6. In ordinary calculation mode, substitute the five fitted values, compute the
   five squared residuals, and add them to verify `SSE = 0.281267`.

Menu wording can differ slightly with calculator language and firmware.

---

## Problem 2 - Exponential regression

### Core idea

Taking logarithms turns multiplicative growth into an ordinary straight-line
regression.

The model is

```text
y = exp(beta_0 + beta_1 x + error).
```

Taking natural logarithms gives

```text
z = log(y) = beta_0 + beta_1 x + error,
```

where `z = log(y)`. The transformed observations are approximately

| x | y | log(y) |
|---:|---:|---:|
| 1 | 2.98 | 1.091923 |
| 2 | 4.65 | 1.536867 |
| 3 | 5.00 | 1.609438 |
| 4 | 6.50 | 1.871802 |

### 2(a) Estimate the transformed linear model

For simple linear regression,

```text
beta_1_hat = S_xz/S_xx,
beta_0_hat = z_bar - beta_1_hat x_bar.
```

Using the four transformed observations gives

```text
beta_1_hat = 0.241221
beta_0_hat = 0.924456.
```

Hence,

```text
log(y_hat) = 0.924456 + 0.241221 x.
```

Equivalently, on the original scale,

```text
y_hat = exp(0.924456) exp(0.241221)^x
      = 2.52050 (1.27280)^x.
```

The fitted population multiplies by about 1.2728 for each additional year, an
estimated 27.28% year-to-year increase under this model.

R verification:

```r
d <- data.frame(x = 1:4, y = c(2.98, 4.65, 5.00, 6.50))
fit_exp <- lm(log(y) ~ x, data = d)
coef(fit_exp)
```

### 2(b) Predict year 5

```text
log(y_hat_5) = 0.924456 + 0.241221(5) = 2.130559,
y_hat_5 = exp(2.130559) = 8.419576.
```

The exam-style prediction is approximately **8.42 million people**.

A technical nuance: because the error is normal on the log scale,
`exp(beta_0 + beta_1 x)` estimates the conditional median on the original scale.
The conditional mean would include the lognormal correction
`exp(sigma^2/2)`. The question asks for a prediction based on the fitted values,
so the usual expected answer is the plug-in value 8.4196.

### Casio fx-580VN X verification

1. Compute `ln(y)` for each of the four populations.
2. Open `MENU -> Statistics -> A+BX`.
3. Enter `x` in the first column and `ln(y)` in the second.
4. Open the regression calculation results and read the intercept `a` and slope
   `b`; they should be approximately `a = 0.924456`, `b = 0.241221`.
5. Evaluate `exp(a + 5b)` to obtain approximately `8.419576`.

---

## Problem 3 - Logistic regression

### Core idea

Logistic regression predicts a probability while keeping it between zero and
one. Its linear predictor describes log-odds rather than the probability itself.

Let `p(x) = P(y = 1 | x1, x2, x3)`. The estimated model is

```text
log(p_hat/(1-p_hat))
  = -3.449548 + 0.002294 x1 + 0.777014 x2 - 0.560031 x3.
```

Equivalently,

```text
p_hat = exp(eta_hat)/(1 + exp(eta_hat)),
```

where `eta_hat` is the right-hand side of the logit equation.

### 3(a) Interpret the coefficients

Each coefficient is a change in log-odds when that predictor rises by one unit,
holding the other predictors fixed. Exponentiating gives the easier odds-ratio
interpretation.

| Term | Estimate | Odds ratio | Interpretation |
|---|---:|---:|---|
| `x1` | 0.002294 | 1.002297 | A one-unit increase multiplies the odds of class 1 by 1.0023, about a 0.23% increase. |
| `x2` | 0.777014 | 2.174968 | A one-unit increase multiplies the odds by about 2.175, a 117.5% increase. |
| `x3` | -0.560031 | 0.571191 | A one-unit increase multiplies the odds by 0.571, about a 42.9% decrease. |

For `x1`, one unit may be too small to communicate well. A 100-unit increase
multiplies the odds by `exp(100 * 0.002294)`, approximately 1.258.

The p-values for `x1`, `x2`, and `x3` are all below 0.05, so each is statistically
significant at the 5% level in the fitted model. Significance does not by itself
prove causation.

### 3(b) Classify the four observations

Use the standard cutoff 0.5: predict class 1 when `p_hat >= 0.5`, equivalently
when `eta_hat >= 0`.

| Row | eta_hat | p_hat | Predicted class |
|---:|---:|---:|---:|
| 1 | -1.058484 | 0.257599 | 0 |
| 2 | -0.940450 | 0.280809 | 0 |
| 3 | 0.362391 | 0.589619 | 1 |
| 4 | -0.684196 | 0.335326 | 0 |

Thus the predicted classes are **0, 0, 1, 0**.

R verification:

```r
b <- c(-3.449548, 0.002294, 0.777014, -0.560031)
new <- data.frame(
  x1 = c(640, 600, 700, 620),
  x2 = c(3.35, 3.62, 3.56, 3.17),
  x3 = c(3, 3, 1, 2)
)
eta <- drop(cbind(1, as.matrix(new)) %*% b)
p <- plogis(eta)
cbind(new, eta, p, class = as.integer(p >= 0.5))
```

### Casio fx-580VN X verification

For each row, use ordinary calculation mode:

1. Compute `eta = -3.449548 + 0.002294*x1 + 0.777014*x2 - 0.560031*x3`.
2. Compute `1/(1 + exp(-eta))`.
3. Compare the result with 0.5.

For the first row the display should give `eta` about -1.05848 and probability
about 0.25760, so the class is 0.

---

## Problem 4 - Ridge estimator when the intercept is penalized

### What we are trying to show

We want to minimize

```text
L = sum((y_k - beta_0 - beta_1 x_k)^2) + lambda(beta_0^2 + beta_1^2)
```

and derive the two formulas printed in the question.

The strategy is to differentiate with respect to both coefficients, solve the
first normal equation for `beta_0`, and substitute it into the second.

### Step 1: Differentiate with respect to beta_0

Set the derivative equal to zero:

```text
-2 sum(y_k - beta_0 - beta_1 x_k) + 2 lambda beta_0 = 0.
```

Using `sum(y_k) = n y_bar` and `sum(x_k) = n x_bar` gives

```text
(n + lambda) beta_0 + n x_bar beta_1 = n y_bar.
```

Therefore,

```text
beta_0_hat = n/(n + lambda) (y_bar - beta_1_hat x_bar).
```

This differs from ordinary least squares because the question penalizes the
intercept. Without an intercept penalty, the familiar result would be
`beta_0_hat = y_bar - beta_1_hat x_bar`.

### Step 2: Differentiate with respect to beta_1

Set the second derivative equation to zero:

```text
-2 sum[x_k(y_k - beta_0 - beta_1 x_k)] + 2 lambda beta_1 = 0,
```

so

```text
sum(x_k y_k) = n x_bar beta_0 + beta_1[sum(x_k^2) + lambda].
```

Substitute the expression for `beta_0`:

```text
sum(x_k y_k)
 = n x_bar * n/(n+lambda)(y_bar - beta_1 x_bar)
   + beta_1[sum(x_k^2) + lambda].
```

Collect the terms involving `beta_1`:

```text
beta_1 * [sum(x_k^2) + lambda - n^2 x_bar^2/(n+lambda)]
 = sum(x_k y_k) - n^2 x_bar y_bar/(n+lambda).
```

### Step 3: Convert to centered sums

Use

```text
sum(x_k y_k) = S_xy + n x_bar y_bar,
sum(x_k^2)   = S_xx + n x_bar^2.
```

The numerator becomes

```text
S_xy + n x_bar y_bar - n^2 x_bar y_bar/(n+lambda)
= S_xy + [n lambda/(n+lambda)] x_bar y_bar.
```

The denominator becomes

```text
S_xx + n x_bar^2 + lambda - n^2 x_bar^2/(n+lambda)
= S_xx + lambda + [n lambda/(n+lambda)] x_bar^2
= S_xx + lambda[1 + n x_bar^2/(n+lambda)].
```

Hence,

```text
beta_1_hat =
  {S_xy + [n lambda/(n+lambda)] x_bar y_bar}
  --------------------------------------------------
  {S_xx + lambda[1 + n x_bar^2/(n+lambda)]},
```

and

```text
beta_0_hat = n/(n+lambda)(y_bar - beta_1_hat x_bar),
```

which are exactly the required formulas.

### Important distinction from `glmnet`

The theoretical problem explicitly adds `lambda * beta_0^2`, so it penalizes the
intercept. By default, `glmnet` does **not** penalize the intercept. Do not expect
the practical ridge intercept to follow this written-problem formula.

There is no useful direct calculator shortcut for this symbolic derivation. The
exam expects the normal-equation argument above.

---

# Part II - Practical Midterm

## Reproducible setup

The training file has 38 rows and these columns:

```text
Age Weight HtShoes Ht Seated Arm Thigh Leg hipcenter
```

Run the complete analysis from the repository root with:

```powershell
Rscript R_training/midterm/midterm_solutions.R
```

Or, in RStudio:

```r
source("R_training/midterm/midterm_solutions.R")
```

Only `glmnet` is required beyond base R.

## Practical (a) - Full OLS model and residual analysis

The estimated model is

```text
hipcenter_hat = 436.4321
  + 0.7757 Age
  + 0.0263 Weight
  - 2.6924 HtShoes
  + 0.6013 Ht
  + 0.5338 Seated
  - 1.3281 Arm
  - 1.1431 Thigh
  - 6.4390 Leg.
```

Every slope is interpreted while all seven other variables are held fixed. For
example, one additional year of age is associated with a 0.776 mm increase in
the fitted `hipcenter` coordinate at the same weight and body dimensions. A
one-centimeter increase in lower-leg length is associated with a 6.439 mm
decrease in the fitted coordinate, holding the remaining measurements fixed.

Be cautious: holding `Ht` fixed while changing `HtShoes`, or vice versa, is nearly
an impossible comparison. The coefficient table reflects severe collinearity.

### Model fit

```text
Residual standard error = 37.7 mm on 29 df
R-squared              = 0.687
Adjusted R-squared     = 0.600
Overall F(8,29)        = 7.94
Overall p-value        = 1.31e-5
```

The model explains about 68.7% of the observed training variation, or 60.0% after
the adjusted-R-squared penalty for eight predictors.

### Individual coefficients

None of the eight slopes has an individual p-value below 0.05. This does not
contradict the highly significant overall F test. The predictors can be useful
collectively while their individual standard errors are inflated by
multicollinearity.

The clearest evidence is:

```text
VIF(Ht)      = 333.14
VIF(HtShoes) = 307.43
standardized-predictor condition number = 59.77
```

`Ht` and `HtShoes` measure almost the same physical quantity. Their OLS
coefficients can therefore become large, unstable, and even change sign while
their combined fitted contribution remains useful. This is exactly the setting
where ridge or LASSO can help.

### Residual checks

1. **Centering and shape.** The residual median is -3.68 mm and the residual range
   is about -73.83 to 62.34 mm. OLS residuals sum to zero by construction.
2. **Normality.** Shapiro-Wilk gives `W = 0.9715`, `p = 0.434`. At 5%, there is no
   evidence against normal residuals. This is not proof of exact normality.
3. **Constant variance.** The base-R Breusch-Pagan calculation gives
   `LM = 14.037`, `df = 8`, `p = 0.0808`. At 5%, there is no statistically
   significant evidence of heteroscedasticity, although the p-value is close
   enough to justify checking the scale-location plot.
4. **Influence.** Row 31 has Cook's distance 0.695 and leverage 0.560. It exceeds
   both rough thresholds `4/n = 0.105` and `2k/n = 0.474`, so it deserves data
   verification and a sensitivity refit. Rows 23 and 35 also have Cook's
   distances above `4/n`.
5. **Linearity.** Inspect the residuals-versus-fitted plot. A random cloud around
   zero supports the linear mean structure; curvature suggests transformations
   or nonlinear terms.

Interactive diagnostic plots:

```r
par(mfrow = c(2, 2))
plot(full_ols)
par(mfrow = c(1, 1))
```

Do not delete an influential row only because Cook's distance is large. First
check for a recording error, understand why it is unusual, and report whether the
scientific conclusion changes when it is included or excluded.

## Practical (b) - Full model versus noise-only model

The hypotheses are

```text
H0: beta_Age = beta_Weight = ... = beta_Leg = 0
H1: at least one slope is nonzero.
```

The nested-model ANOVA gives

```text
RSS(null) = 131639
RSS(full) =  41262
F(8,29)  = 7.94
p        = 1.31e-5.
```

Because `p < 0.05`, reject `H0`. The full set of anthropometric predictors gives
a statistically significant improvement over an intercept-only model.

R code:

```r
null_ols <- lm(hipcenter ~ 1, data = seatpos)
full_ols <- lm(hipcenter ~ ., data = seatpos)
anova(null_ols, full_ols)
```

## Practical (c) - Ridge regression with cross-validation

Ridge minimizes squared error plus an L2 penalty:

```text
SSE + lambda * sum(beta_j^2).
```

It shrinks correlated coefficients toward zero but normally keeps all of them
nonzero. The script uses:

- `alpha = 0` for ridge;
- the exam grid `seq(1e-3, 50, by = 1e-3)`;
- 10-fold CV;
- `set.seed(452)` and explicit fold IDs;
- `type.measure = "mse"`;
- `standardize = TRUE`, the `glmnet` default.

With those fixed folds:

```text
lambda.min = 36.521
lambda.1se = 50.000
```

`lambda.min` minimizes estimated cross-validation MSE. `lambda.1se` is the
largest penalty whose error is within one standard error of the minimum and is a
reasonable more-regularized alternative. Because `lambda.1se` hits the upper
edge 50, a real analysis using the 1-SE rule should expand the grid above 50.

Ridge coefficients at `lambda.min`:

| Term | Ridge estimate |
|---|---:|
| Intercept | 399.992503 |
| Age | 0.473581 |
| Weight | -0.106186 |
| HtShoes | -0.738541 |
| Ht | -0.737116 |
| Seated | -1.203317 |
| Arm | -1.354624 |
| Thigh | -1.304223 |
| Leg | -3.109081 |

Compared with OLS, the unstable height coefficients and other slopes have been
pulled toward a more balanced set of values. Ridge is especially appropriate
when prediction is more important than choosing a small subset of variables.

`glmnet` standardizes predictors internally when fitting, does not penalize the
intercept, and transforms the displayed coefficients back to the original units.

## Practical (d) - Ridge predictions

Using `lambda.min = 36.521`:

| New row | Ridge prediction (mm) |
|---:|---:|
| 1 | -139.711 |
| 2 | -112.954 |
| 3 | -219.990 |
| 4 | -149.057 |
| 5 | -228.157 |
| 6 | -102.596 |

R code:

```r
predict(ridge_cv, newx = X_new, s = "lambda.min")
```

Use `model.matrix` for both training and new data so that columns and encoding
match exactly.

## Practical (e) - LASSO and comparison with OLS

LASSO uses an L1 penalty:

```text
SSE + lambda * sum(abs(beta_j)).
```

The corners of the L1 constraint allow some estimated slopes to be exactly zero,
so LASSO performs shrinkage and variable selection at the same time.

With the same fixed folds:

```text
lambda.min = 5.748
lambda.1se = 20.288
```

At `lambda.min`, the nonzero predictors are **Age, Ht, and Leg**.

| Term | Full OLS | Ridge | LASSO |
|---|---:|---:|---:|
| Intercept | 436.432128 | 399.992503 | 397.696648 |
| Age | 0.775716 | 0.473581 | 0.221804 |
| Weight | 0.026313 | -0.106186 | 0 |
| HtShoes | -2.692408 | -0.738541 | 0 |
| Ht | 0.601345 | -0.737116 | -2.200605 |
| Seated | 0.533752 | -1.203317 | 0 |
| Arm | -1.328069 | -1.354624 | 0 |
| Thigh | -1.143119 | -1.304223 | 0 |
| Leg | -6.439046 | -3.109081 | -5.468787 |

The LASSO model is therefore

```text
hipcenter_hat = 397.696648
  + 0.221804 Age
  - 2.200605 Ht
  - 5.468787 Leg.
```

If ordinary least squares is refitted using only these three selected variables,
the estimates are approximately

```text
Intercept = 452.198
Age       =   0.581
Ht        =  -2.325
Leg       =  -6.739
```

The post-LASSO OLS values are less shrunken because that refit has no penalty.
It is useful as a comparison, but it is not the LASSO estimator and naive OLS
p-values after data-driven variable selection should not be treated as ordinary
pre-specified inference.

Selection among highly correlated measurements can be unstable: another fold
split may choose `HtShoes` instead of `Ht`, or slightly change the optimal lambda.
Report the seed and folds, and focus on predictive validation rather than treating
one selected set as a scientific law.

## Practical (f) - Ridge versus LASSO predictions

| Row | Ridge | LASSO | Ridge - LASSO |
|---:|---:|---:|---:|
| 1 | -139.711 | -130.368 | -9.344 |
| 2 | -112.954 | -112.470 | -0.485 |
| 3 | -219.990 | -218.053 | -1.937 |
| 4 | -149.057 | -151.148 | 2.091 |
| 5 | -228.157 | -229.846 | 1.689 |
| 6 | -102.596 | -100.072 | -2.524 |

The two regularized models give similar predictions for five of the six rows.
Row 1 differs by about 9.34 mm. Without observed `hipcenter` values for these six
rows, the table compares predictions but cannot determine which model predicts
better. That requires held-out outcomes or repeated cross-validation error.

---

# Practical Exam Workflow

Use this order under time pressure:

1. Read the CSV files and immediately check `dim`, `names`, `str`, and missing
   values.
2. Fit `lm(hipcenter ~ ., data = seatpos)` and save the model object.
3. Interpret slopes with the phrase “holding all other predictors fixed.”
4. Report R-squared, adjusted R-squared, residual standard error, and the overall
   F test.
5. Inspect residual plots, normality, constant variance, leverage, Cook's
   distance, and multicollinearity.
6. Compare the null and full OLS models with `anova(null_ols, full_ols)`.
7. Construct `X` with `model.matrix` and remove only its intercept column.
8. Fix the random seed and fold IDs before fitting both ridge and LASSO.
9. Use the same folds for a fair comparison.
10. State whether `lambda.min` or `lambda.1se` is used for coefficients and
    predictions.
11. Build `X_new` with the same column construction as `X`.
12. Compare predictions numerically; do not claim a winner without actual test
    outcomes.

## Common mistakes

- Interpreting a logistic coefficient as a direct change in probability.
- Forgetting to back-transform the exponential model with `exp()`.
- Claiming that high R-squared proves causation.
- Saying the full OLS model is useless because no individual slope is significant,
  despite a significant overall F test and severe collinearity.
- Passing a data frame directly to `glmnet`; it needs a numeric matrix.
- Leaving the intercept column in `X` when `glmnet` already fits an intercept.
- Using different CV folds for ridge and LASSO when comparing them.
- Reporting an optimal lambda without a seed or fold definition.
- Treating the LASSO-selected variables as stable when predictors are highly
  correlated.
- Comparing ridge and LASSO predictions without observed outcomes and declaring
  one model more accurate.

## One-line summary

The written test checks whether you can translate models into estimators and
interpretations; the practical test shows why regularization is valuable when a
small dataset contains strongly correlated predictors.

