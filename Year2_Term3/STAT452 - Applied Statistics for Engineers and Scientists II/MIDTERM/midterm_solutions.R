# STAT452 Midterm: complete reproducible R solutions
#
# Files expected in this folder:
#   seatpos.csv  - 38 training observations
#   newdata.csv  - 6 observations to predict
#
# Only glmnet is needed beyond base R. Install it once with:
# install.packages("glmnet")

options(digits = 6)

section <- function(title) {
  cat("\n", paste(rep("=", 78), collapse = ""), "\n", sep = "")
  cat(title, "\n")
  cat(paste(rep("=", 78), collapse = ""), "\n", sep = "")
}

find_exam_file <- function(filename) {
  candidates <- c(
    filename,
    file.path("R_training", "midterm", filename)
  )
  existing <- candidates[file.exists(candidates)]
  if (length(existing) == 0L) {
    stop("Cannot find ", filename,
         ". Run this script from the repository root or R_training/midterm.")
  }
  existing[1L]
}

# =============================================================================
# WRITTEN MIDTERM
# =============================================================================

section("Written Problem 1: multiple linear regression")

study <- data.frame(
  x1 = c(5, 9, 7, 9, 3),
  x2 = c(1, 0, 7, 7, 8),
  y  = c(5.0, 6.0, 9.5, 10.0, 7.5)
)

study_full <- lm(y ~ x1 + x2, data = study)
study_reduced <- lm(y ~ x1, data = study)

X_study <- model.matrix(study_full)
y_study <- matrix(study$y, ncol = 1)
beta_manual <- solve(crossprod(X_study), crossprod(X_study, y_study))

cat("X'X:\n")
print(crossprod(X_study))
cat("X'y:\n")
print(crossprod(X_study, y_study))
cat("beta-hat = (X'X)^(-1)X'y:\n")
print(beta_manual)

study_sse <- sum(resid(study_full)^2)
study_sst <- sum((study$y - mean(study$y))^2)
study_r2 <- 1 - study_sse / study_sst
cat("SSE =", study_sse, " SST =", study_sst, " R-squared =", study_r2, "\n")

cat("Nested-model comparison (computed in R):\n")
print(anova(study_reduced, study_full))

study_new <- data.frame(x1 = 5, x2 = 6)
cat("Prediction at x1=5, x2=6:\n")
print(predict(study_full, newdata = study_new))

section("Written Problem 2: exponential regression")

population <- data.frame(
  x = 1:4,
  y = c(2.98, 4.65, 5.00, 6.50)
)
population$log_y <- log(population$y)
population_model <- lm(log_y ~ x, data = population)

print(population)
cat("Model on the log scale: log(y) = beta0 + beta1*x + error\n")
print(coef(population_model))
cat("Equivalent median model: y = exp(beta0)*exp(beta1)^x\n")
cat("exp(beta0) =", exp(coef(population_model)[1]),
    " exp(beta1) =", exp(coef(population_model)[2]), "\n")
cat("Year-5 plug-in prediction:\n")
print(exp(predict(population_model, newdata = data.frame(x = 5))))

section("Written Problem 3: logistic regression")

logistic_beta <- c(
  intercept = -3.449548,
  x1 = 0.002294,
  x2 = 0.777014,
  x3 = -0.560031
)
logistic_new <- data.frame(
  x1 = c(640, 600, 700, 620),
  x2 = c(3.35, 3.62, 3.56, 3.17),
  x3 = c(3, 3, 1, 2)
)
logistic_eta <- drop(cbind(1, as.matrix(logistic_new)) %*% logistic_beta)
logistic_probability <- plogis(logistic_eta)
logistic_class <- as.integer(logistic_probability >= 0.5)
print(cbind(
  logistic_new,
  log_odds = logistic_eta,
  probability_class_1 = logistic_probability,
  predicted_class = logistic_class
))

cat("Odds ratios for a one-unit increase, holding other predictors fixed:\n")
print(exp(logistic_beta[-1]))

# =============================================================================
# PRACTICAL MIDTERM
# =============================================================================

section("Practical setup")

seatpos <- read.csv(find_exam_file("seatpos.csv"))
newdata <- read.csv(find_exam_file("newdata.csv"))

stopifnot(nrow(seatpos) == 38L, ncol(seatpos) == 9L)
stopifnot(identical(names(newdata), setdiff(names(seatpos), "hipcenter")))

cat("Training dimensions:", nrow(seatpos), "rows x", ncol(seatpos), "columns\n")
cat("Prediction dimensions:", nrow(newdata), "rows x", ncol(newdata), "columns\n")
print(summary(seatpos))

section("Practical (a): full OLS model and residual analysis")

full_ols <- lm(hipcenter ~ ., data = seatpos)
print(summary(full_ols))
cat("95% coefficient confidence intervals:\n")
print(confint(full_ols))

# Diagnostic numbers that can be checked without plotting.
n_obs <- nrow(seatpos)
n_parameters <- length(coef(full_ols))
standardized_residuals <- rstandard(full_ols)
studentized_residuals <- rstudent(full_ols)
leverage <- hatvalues(full_ols)
cook <- cooks.distance(full_ols)

cat("Residual five-number summary:\n")
print(summary(resid(full_ols)))
cat("Shapiro-Wilk test of residual normality:\n")
print(shapiro.test(resid(full_ols)))

# Breusch-Pagan LM test, implemented with base R:
# regress squared OLS residuals on all predictors and use n*R^2 ~ chi-square(p).
bp_auxiliary <- lm(I(resid(full_ols)^2) ~ ., data = seatpos[, -9L])
bp_statistic <- n_obs * summary(bp_auxiliary)$r.squared
bp_df <- ncol(seatpos) - 1L
bp_p_value <- pchisq(bp_statistic, df = bp_df, lower.tail = FALSE)
cat("Breusch-Pagan LM statistic =", bp_statistic,
    " df =", bp_df, " p-value =", bp_p_value, "\n")

influence_table <- data.frame(
  row = seq_len(n_obs),
  standardized_residual = standardized_residuals,
  studentized_residual = studentized_residuals,
  leverage = leverage,
  cooks_distance = cook
)
influence_table <- influence_table[
  order(influence_table$cooks_distance, decreasing = TRUE),
]
cat("Five largest Cook's distances:\n")
print(head(influence_table, 5L), row.names = FALSE)
cat("Rules of thumb: |studentized residual| > 2, leverage >",
    2 * n_parameters / n_obs, ", Cook's D >", 4 / n_obs, "\n")

# Variance inflation factors, implemented with base R.
predictor_names <- setdiff(names(seatpos), "hipcenter")
vif <- vapply(predictor_names, function(variable) {
  others <- setdiff(predictor_names, variable)
  auxiliary_formula <- reformulate(others, response = variable)
  auxiliary_model <- lm(auxiliary_formula, data = seatpos)
  1 / (1 - summary(auxiliary_model)$r.squared)
}, numeric(1))
cat("Variance inflation factors:\n")
print(sort(vif, decreasing = TRUE))
cat("Condition number of the standardized predictor matrix:\n")
print(kappa(scale(seatpos[, predictor_names]), exact = TRUE))

cat("For the four standard diagnostic plots, run interactively:\n")
cat("  par(mfrow=c(2,2)); plot(full_ols); par(mfrow=c(1,1))\n")

section("Practical (b): full OLS model versus intercept-only model")

null_ols <- lm(hipcenter ~ 1, data = seatpos)
print(anova(null_ols, full_ols))
cat("The same overall F test appears at the bottom of summary(full_ols).\n")

section("Practical (c)-(f): ridge and LASSO with reproducible 10-fold CV")

if (!requireNamespace("glmnet", quietly = TRUE)) {
  stop("Package 'glmnet' is required. Run install.packages('glmnet') once.")
}

X <- model.matrix(hipcenter ~ ., data = seatpos)[, -1L, drop = FALSE]
y <- seatpos$hipcenter
X_new <- model.matrix(~ ., data = newdata)[, -1L, drop = FALSE]

# The exam specifies this dense search grid. Fixed fold IDs make the answers
# reproducible; changing the folds can slightly change the selected lambda.
lambda_grid <- seq(1e-3, 50, by = 1e-3)
set.seed(452)
fold_id <- sample(rep(seq_len(10L), length.out = nrow(X)))

ridge_cv <- glmnet::cv.glmnet(
  x = X,
  y = y,
  alpha = 0,
  lambda = lambda_grid,
  foldid = fold_id,
  type.measure = "mse",
  standardize = TRUE
)
ridge_lambda_min <- ridge_cv$lambda.min
ridge_lambda_1se <- ridge_cv$lambda.1se
cat("Ridge lambda.min =", ridge_lambda_min,
    " lambda.1se =", ridge_lambda_1se, "\n")

ridge_coefficients <- as.matrix(coef(ridge_cv, s = "lambda.min"))
cat("Ridge coefficients at lambda.min (reported on original predictor scales):\n")
print(ridge_coefficients)

ridge_predictions <- drop(predict(ridge_cv, newx = X_new, s = "lambda.min"))

lasso_cv <- glmnet::cv.glmnet(
  x = X,
  y = y,
  alpha = 1,
  lambda = lambda_grid,
  foldid = fold_id,
  type.measure = "mse",
  standardize = TRUE
)
lasso_lambda_min <- lasso_cv$lambda.min
lasso_lambda_1se <- lasso_cv$lambda.1se
cat("LASSO lambda.min =", lasso_lambda_min,
    " lambda.1se =", lasso_lambda_1se, "\n")

lasso_coefficients <- as.matrix(coef(lasso_cv, s = "lambda.min"))
cat("LASSO coefficients at lambda.min (reported on original predictor scales):\n")
print(lasso_coefficients)

nonzero_lasso <- rownames(lasso_coefficients)[
  lasso_coefficients[, 1L] != 0 & rownames(lasso_coefficients) != "(Intercept)"
]
cat("Nonzero LASSO predictors at lambda.min:\n")
print(nonzero_lasso)

# Compare penalized estimates with the full OLS estimates.
coefficient_comparison <- data.frame(
  term = rownames(lasso_coefficients),
  OLS = coef(full_ols)[rownames(lasso_coefficients)],
  ridge = ridge_coefficients[rownames(lasso_coefficients), 1L],
  LASSO = lasso_coefficients[, 1L],
  row.names = NULL
)
cat("Coefficient comparison (all on original predictor scales):\n")
print(coefficient_comparison)

# A post-LASSO OLS refit is useful for interpretation, but it is a different
# estimator and should not be presented as the LASSO model itself.
if (length(nonzero_lasso) > 0L) {
  post_lasso_formula <- reformulate(nonzero_lasso, response = "hipcenter")
  post_lasso_ols <- lm(post_lasso_formula, data = seatpos)
  cat("OLS refit using only variables selected by LASSO:\n")
  print(summary(post_lasso_ols))
}

lasso_predictions <- drop(predict(lasso_cv, newx = X_new, s = "lambda.min"))
prediction_comparison <- cbind(
  newdata,
  ridge_prediction = ridge_predictions,
  lasso_prediction = lasso_predictions,
  ridge_minus_lasso = ridge_predictions - lasso_predictions
)
cat("Predictions for newdata.csv:\n")
print(prediction_comparison)

cat("\nImportant glmnet detail: predictors are standardized internally by default,\n")
cat("the intercept is not penalized, and coef() returns coefficients transformed\n")
cat("back to the variables' original units.\n")

