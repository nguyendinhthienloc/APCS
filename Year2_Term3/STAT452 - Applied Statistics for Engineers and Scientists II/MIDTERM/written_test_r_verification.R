# STAT452 60-minute written test: R verification
# The paper solution contains the mathematical derivations. This script checks
# the numerical results using R.

options(digits = 7)

section <- function(title) {
  cat("\n", paste(rep("=", 72), collapse = ""), "\n", sep = "")
  cat(title, "\n")
  cat(paste(rep("=", 72), collapse = ""), "\n", sep = "")
}

# -----------------------------------------------------------------------------
# Problem 1: multiple linear regression
# -----------------------------------------------------------------------------
section("Problem 1: multiple linear regression")

study <- data.frame(
  x1 = c(5, 9, 7, 9, 3),
  x2 = c(1, 0, 7, 7, 8),
  y = c(5.0, 6.0, 9.5, 10.0, 7.5)
)

full_model <- lm(y ~ x1 + x2, data = study)
reduced_model <- lm(y ~ x1, data = study)

X <- model.matrix(full_model)
Y <- matrix(study$y, ncol = 1)

cat("X'X:\n")
print(crossprod(X))
cat("X'y:\n")
print(crossprod(X, Y))
cat("beta-hat = solve(X'X, X'y):\n")
print(solve(crossprod(X), crossprod(X, Y)))

SSE <- sum(resid(full_model)^2)
SST <- sum((study$y - mean(study$y))^2)
cat("SSE =", SSE, "\n")
cat("SST =", SST, "\n")
cat("R-squared =", 1 - SSE / SST, "\n")

cat("Partial F-test for adding x2:\n")
print(anova(reduced_model, full_model))

cat("Prediction at x1=5 and x2=6:\n")
print(predict(full_model, newdata = data.frame(x1 = 5, x2 = 6)))

# -----------------------------------------------------------------------------
# Problem 2: exponential regression after a log transformation
# -----------------------------------------------------------------------------
section("Problem 2: exponential regression")

population <- data.frame(
  year = 1:4,
  population = c(2.98, 4.65, 5.00, 6.50)
)

exponential_model <- lm(log(population) ~ year, data = population)
print(summary(exponential_model))
cat("Estimated coefficients on the log scale:\n")
print(coef(exponential_model))
cat("Multiplicative growth factor exp(beta_1):\n")
print(exp(coef(exponential_model)["year"]))
cat("Year-5 plug-in prediction on the original scale:\n")
print(exp(predict(exponential_model, newdata = data.frame(year = 5))))

# -----------------------------------------------------------------------------
# Problem 3: logistic regression calculations
# -----------------------------------------------------------------------------
section("Problem 3: logistic regression")

logistic_beta <- c(
  intercept = -3.449548,
  x1 = 0.002294,
  x2 = 0.777014,
  x3 = -0.560031
)

new_observations <- data.frame(
  x1 = c(640, 600, 700, 620),
  x2 = c(3.35, 3.62, 3.56, 3.17),
  x3 = c(3, 3, 1, 2)
)

eta <- drop(cbind(1, as.matrix(new_observations)) %*% logistic_beta)
probability <- plogis(eta)
predicted_class <- as.integer(probability >= 0.5)

print(cbind(
  new_observations,
  eta = eta,
  probability = probability,
  predicted_class = predicted_class
))

cat("One-unit odds ratios:\n")
print(exp(logistic_beta[-1]))

# -----------------------------------------------------------------------------
# Problem 4: numerical verification of the proved ridge formulas
# This problem penalizes both the intercept and slope, unlike glmnet's default.
# -----------------------------------------------------------------------------
section("Problem 4: numerical check of the ridge proof")

ridge_formula <- function(x, y, lambda) {
  n <- length(y)
  x_bar <- mean(x)
  y_bar <- mean(y)
  Sxx <- sum((x - x_bar)^2)
  Sxy <- sum((x - x_bar) * (y - y_bar))

  beta1 <- (
    Sxy + n * lambda * x_bar * y_bar / (n + lambda)
  ) / (
    Sxx + lambda * (1 + n * x_bar^2 / (n + lambda))
  )
  beta0 <- n * (y_bar - beta1 * x_bar) / (n + lambda)
  c(beta0 = beta0, beta1 = beta1)
}

x_check <- c(1, 2, 4, 5)
y_check <- c(2, 3, 7, 8)
lambda_check <- 2

X_check <- cbind(1, x_check)
matrix_solution <- drop(solve(
  crossprod(X_check) + lambda_check * diag(2),
  crossprod(X_check, y_check)
))

print(rbind(
  derived_formula = ridge_formula(x_check, y_check, lambda_check),
  matrix_solution = matrix_solution
))

