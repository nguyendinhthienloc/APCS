# STAT452 Chapter 3: Ridge, LASSO, Cross-Validation, and Variable Selection
# Built-in mtcars data; base R and MASS are used.

data(mtcars)
cars <- mtcars
X <- scale(as.matrix(cars[, c("wt","hp","qsec","disp","drat","gear")]))
y <- cars$mpg

# 1. OLS baseline and collinearity.
ols <- lm(mpg ~ wt + hp + qsec + disp + drat + gear, data=cars)
summary(ols)
cor(cars[, c("wt","hp","qsec","disp","drat","gear")])

# 2. Ridge regression. MASS::lm.ridge uses standardized predictors.
library(MASS)
lambda_grid <- seq(0, 30, length.out=100)
ridge_path <- lm.ridge(mpg ~ wt + hp + qsec + disp + drat + gear,
                       data=cars, lambda=lambda_grid)
matplot(lambda_grid, t(ridge_path$coef), type="l", lty=1,
        xlab="lambda", ylab="standardized coefficient")
select_lambda <- lambda_grid[which.min(ridge_path$GCV)]
select_lambda
coef(ridge_path)[which.min(ridge_path$GCV), ]

# 3. A small from-scratch LASSO coordinate-descent solver.
lasso_cd <- function(X, y, lambda, maxit=5000, tol=1e-8) {
  X <- scale(X); y <- as.numeric(scale(y))
  beta <- numeric(ncol(X))
  soft <- function(z, g) sign(z)*max(abs(z)-g, 0)
  for (iter in seq_len(maxit)) {
    old <- beta
    for (j in seq_along(beta)) {
      r <- y - X %*% beta + X[,j] * beta[j]
      beta[j] <- soft(sum(X[,j] * r) / nrow(X), lambda)
    }
    if (max(abs(beta-old)) < tol) break
  }
  beta
}
lasso_grid <- seq(0.01, 0.8, length.out=80)
lasso_coefs <- sapply(lasso_grid, function(lam) lasso_cd(X, y, lam))
matplot(lasso_grid, t(lasso_coefs), type="l", lty=1,
        xlab="lambda", ylab="standardized coefficient")

# 4. Compare subset models with AIC and BIC.
full <- lm(mpg ~ wt + hp + qsec + disp + drat + gear, data=cars)
aic_model <- step(full, direction="both", trace=0)
bic_model <- step(full, direction="both", k=log(nrow(cars)), trace=0)
formula(aic_model); formula(bic_model)

# 5. Five-fold cross-validation.
set.seed(452)
fold <- sample(rep(1:5, length.out=nrow(cars)))
cv_mse <- function(formula, data, fold) {
  mean(sapply(sort(unique(fold)), function(k) {
    fit <- lm(formula, data=data[fold != k,])
    mean((data$mpg[fold == k] - predict(fit, data[fold == k,]))^2)
  }))
}
cv_mse(mpg ~ wt, cars, fold)
cv_mse(mpg ~ wt + hp + qsec + disp + drat + gear, cars, fold)

