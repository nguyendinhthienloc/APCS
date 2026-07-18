# STAT452 Chapter 1: Simple R Exercises for Multiple Linear Regression
# Dataset: mtcars (built into R; no packages are needed)
# Run one exercise at a time. Lines beginning with # are notes, not commands.

data(mtcars)
cars <- mtcars

# -----------------------------------------------------------------------------
# Exercise 1: Inspect a data frame
# Math question: What are n (observations) and the candidate variables?
# Syntax: object <- value assigns a value; function(object) calls a function.
# -----------------------------------------------------------------------------
head(cars)
dim(cars)
names(cars)
str(cars)

# -----------------------------------------------------------------------------
# Exercise 2: Compute simple sample summaries
# Treat mpg as Y and wt as X. Compute x-bar, y-bar, s_x, and s_y.
# Syntax: cars$wt selects the wt column; mean() and sd() summarize a vector.
# -----------------------------------------------------------------------------
x <- cars$wt
y <- cars$mpg
x_bar <- mean(x)
y_bar <- mean(y)
s_x <- sd(x)
s_y <- sd(y)
c(x_bar = x_bar, y_bar = y_bar, s_x = s_x, s_y = s_y)

# Compute centered sums Sxx and Sxy, then the simple-regression coefficients.
Sxx <- sum((x - x_bar)^2)
Sxy <- sum((x - x_bar) * (y - y_bar))
b1_manual <- Sxy / Sxx
b0_manual <- y_bar - b1_manual * x_bar
c(Sxx = Sxx, Sxy = Sxy, b0 = b0_manual, b1 = b1_manual)

# -----------------------------------------------------------------------------
# Exercise 3: Fit and interpret a simple linear regression
# Math: mpg_i = beta_0 + beta_1 wt_i + epsilon_i.
# Syntax: response ~ predictor describes the model; lm() fits least squares.
# -----------------------------------------------------------------------------
simple_model <- lm(mpg ~ wt, data = cars)
coef(simple_model)
summary(simple_model)
all.equal(unname(coef(simple_model)), c(b0_manual, b1_manual))

# -----------------------------------------------------------------------------
# Exercise 4: Fit a multiple linear regression
# Math: mpg_i = beta_0 + beta_1 wt_i + beta_2 hp_i + epsilon_i.
# A coefficient is interpreted while holding the other predictor fixed.
# -----------------------------------------------------------------------------
full_model <- lm(mpg ~ wt + hp, data = cars)
coef(full_model)
summary(full_model)

# Compare the wt slope before and after hp is included.
c(simple_wt = coef(simple_model)["wt"], multiple_wt = coef(full_model)["wt"])

# -----------------------------------------------------------------------------
# Exercise 5: Work with fitted values and residuals
# Math: e_i = y_i - yhat_i, so y_i = yhat_i + e_i.
# For least squares with an intercept: sum(e_i)=0 and X^T e=0.
# -----------------------------------------------------------------------------
y_hat <- fitted(full_model)
e <- resid(full_model)
head(data.frame(observed = y, fitted = y_hat, residual = e))
max(abs(y - (y_hat + e)))
sum(e)
sum(cars$wt * e)
sum(cars$hp * e)

# -----------------------------------------------------------------------------
# Exercise 6: Reproduce lm() with the matrix least-squares formula
# Math: beta_hat = (X^T X)^(-1) X^T y.
# Syntax: model.matrix() constructs X; t() transposes; %*% multiplies matrices;
# solve(A) computes A^(-1), although solve(A, b) is usually numerically better.
# -----------------------------------------------------------------------------
X <- model.matrix(full_model)
Y <- matrix(cars$mpg, ncol = 1)
beta_matrix <- solve(t(X) %*% X, t(X) %*% Y)
beta_matrix
coef(full_model)

# Check the matrix normal equations X^T e = 0.
drop(t(X) %*% matrix(e, ncol = 1))

# -----------------------------------------------------------------------------
# Exercise 7: Calculate SSE, MSE, and R-squared manually
# Math: SSE=sum(e_i^2), MSE=SSE/(n-p-1), R^2=1-SSE/SST.
# Here p=2 predictors, while the intercept is counted separately.
# -----------------------------------------------------------------------------
n <- nrow(cars)
p <- 2
SSE <- sum(e^2)
MSE <- SSE / (n - p - 1)
SST <- sum((y - mean(y))^2)
R2 <- 1 - SSE / SST
c(SSE = SSE, MSE = MSE, residual_SE = sqrt(MSE), R2 = R2)
c(summary_sigma = summary(full_model)$sigma,
  summary_R2 = summary(full_model)$r.squared,
  adjusted_R2 = summary(full_model)$adj.r.squared)

# -----------------------------------------------------------------------------
# Exercise 8: Test a coefficient and form a confidence interval
# Test H0: beta_hp = 0 against H1: beta_hp != 0.
# Math: t = beta_hat_hp / SE(beta_hat_hp), with df=n-p-1.
# -----------------------------------------------------------------------------
coefficient_table <- coef(summary(full_model))
coefficient_table
t_hp <- coefficient_table["hp", "Estimate"] /
        coefficient_table["hp", "Std. Error"]
df_error <- df.residual(full_model)
p_hp <- 2 * pt(abs(t_hp), df = df_error, lower.tail = FALSE)
c(t_hp = t_hp, df = df_error, p_value = p_hp)
confint(full_model, "hp", level = 0.95)

# -----------------------------------------------------------------------------
# Exercise 9: Estimate a mean response and predict a new response
# New car: wt=3 (3000 lb) and hp=110.
# confidence interval: uncertainty in the mean E[Y|X=x0]
# prediction interval: uncertainty for one new individual Y_new.
# -----------------------------------------------------------------------------
new_car <- data.frame(wt = 3, hp = 110)
predict(full_model, newdata = new_car, interval = "confidence", level = 0.95)
predict(full_model, newdata = new_car, interval = "prediction", level = 0.95)

# -----------------------------------------------------------------------------
# Exercise 10: Compare nested models and check diagnostics
# Reduced: mpg ~ wt. Full: mpg ~ wt + hp.
# anova(reduced, full) conducts the partial F-test for adding hp.
# -----------------------------------------------------------------------------
reduced_model <- lm(mpg ~ wt, data = cars)
anova(reduced_model, full_model)

# Diagnostic quantities available without plotting:
which.max(abs(rstandard(full_model)))
which.max(cooks.distance(full_model))

# Run these plotting commands interactively in RStudio:
# par(mfrow = c(2, 2))
# plot(full_model)
# par(mfrow = c(1, 1))

# Main diagnostic meanings:
# Residuals vs Fitted: linearity and constant variance.
# Normal Q-Q: approximate normality of errors.
# Scale-Location: constant variance.
# Residuals vs Leverage: influential observations.
