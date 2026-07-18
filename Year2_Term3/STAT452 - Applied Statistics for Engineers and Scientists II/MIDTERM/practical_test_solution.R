# STAT452 practical midterm: complete solution using R
#
# Required files in R_training/midterm:
#   seatpos.csv
#   newdata.csv
#
# Required package:
#   install.packages("glmnet")

options(digits = 6)

section <- function(title) {
  cat("\n", paste(rep("=", 78), collapse = ""), "\n", sep = "")
  cat(title, "\n")
  cat(paste(rep("=", 78), collapse = ""), "\n", sep = "")
}

find_exam_file <- function(filename) {
  candidates <- c(filename, file.path("R_training", "midterm", filename))
  existing <- candidates[file.exists(candidates)]
  if (length(existing) == 0L) {
    stop("Cannot find ", filename,
         ". Run from the repository root or R_training/midterm.")
  }
  existing[1L]
}

# -----------------------------------------------------------------------------
# Setup and data checks
# -----------------------------------------------------------------------------
section("Setup and data checks")

seatpos <- read.csv(find_exam_file("seatpos.csv"))
newdata <- read.csv(find_exam_file("newdata.csv"))

stopifnot(nrow(seatpos) == 38L, ncol(seatpos) == 9L)
stopifnot(identical(names(newdata), setdiff(names(seatpos), "hipcenter")))

str(seatpos)
print(summary(seatpos))
cat("Missing values by variable:\n")
print(colSums(is.na(seatpos)))

# -----------------------------------------------------------------------------
# (a) Full OLS model and residual analysis
# -----------------------------------------------------------------------------
section("(a) Full OLS model and residual analysis")

full_ols <- lm(hipcenter ~ ., data = seatpos)
print(summary(full_ols))
cat("95% confidence intervals:\n")
print(confint(full_ols))

# Run the standard diagnostic plots when the script is used in RStudio.
if (interactive()) {
  old_par <- par(mfrow = c(2, 2))
  plot(full_ols)
  par(old_par)
}

cat("Shapiro-Wilk test for residual normality:\n")
print(shapiro.test(resid(full_ols)))

# Base-R Breusch-Pagan LM test. Regress squared residuals on all predictors.
bp_auxiliary <- lm(
  I(resid(full_ols)^2) ~ .,
  data = seatpos[setdiff(names(seatpos), "hipcenter")]
)
bp_statistic <- nrow(seatpos) * summary(bp_auxiliary)$r.squared
bp_df <- length(coef(full_ols)) - 1L
bp_p_value <- pchisq(bp_statistic, df = bp_df, lower.tail = FALSE)
cat("Breusch-Pagan statistic =", bp_statistic,
    "df =", bp_df, "p-value =", bp_p_value, "\n")

# Influence diagnostics.
influence_table <- data.frame(
  row = seq_len(nrow(seatpos)),
  fitted = fitted(full_ols),
  residual = resid(full_ols),
  studentized_residual = rstudent(full_ols),
  leverage = hatvalues(full_ols),
  cooks_distance = cooks.distance(full_ols)
)
influence_table <- influence_table[
  order(influence_table$cooks_distance, decreasing = TRUE),
]
cat("Five most influential rows by Cook's distance:\n")
print(head(influence_table, 5L), row.names = FALSE)

# Variance inflation factors using only base R.
predictor_names <- setdiff(names(seatpos), "hipcenter")
vif <- vapply(predictor_names, function(variable) {
  other_variables <- setdiff(predictor_names, variable)
  auxiliary_model <- lm(
    reformulate(other_variables, response = variable),
    data = seatpos
  )
  1 / (1 - summary(auxiliary_model)$r.squared)
}, numeric(1))
cat("Variance inflation factors:\n")
print(sort(vif, decreasing = TRUE))

cat("Condition number of standardized predictors:\n")
print(kappa(scale(seatpos[predictor_names]), exact = TRUE))

# -----------------------------------------------------------------------------
# (b) Full model versus the intercept-only model
# -----------------------------------------------------------------------------
section("(b) Full OLS model versus intercept-only model")

null_ols <- lm(hipcenter ~ 1, data = seatpos)
print(anova(null_ols, full_ols))

# -----------------------------------------------------------------------------
# (c)-(f) Ridge and LASSO with the same reproducible 10-fold split
# -----------------------------------------------------------------------------
section("(c)-(f) Ridge and LASSO")

if (!requireNamespace("glmnet", quietly = TRUE)) {
  stop("Package 'glmnet' is required. Run install.packages('glmnet') once.")
}

X <- model.matrix(hipcenter ~ ., data = seatpos)[, -1L, drop = FALSE]
y <- seatpos$hipcenter
X_new <- model.matrix(~ ., data = newdata)[, -1L, drop = FALSE]

lambda_grid <- seq(1e-3, 50, by = 1e-3)
set.seed(452)
fold_id <- sample(rep(seq_len(10L), length.out = nrow(X)))

# (c) Ridge: alpha = 0. The dense exam grid can cause glmnet to warn when it
# reaches extremely small penalties. The selected lambda lies safely before
# that numerical path limit, so the warning is suppressed here.
ridge_cv <- suppressWarnings(glmnet::cv.glmnet(
  x = X,
  y = y,
  alpha = 0,
  lambda = lambda_grid,
  foldid = fold_id,
  type.measure = "mse",
  standardize = TRUE
))

cat("Ridge lambda.min =", ridge_cv$lambda.min, "\n")
cat("Ridge lambda.1se =", ridge_cv$lambda.1se, "\n")
ridge_coefficients <- as.matrix(coef(ridge_cv, s = "lambda.min"))
print(ridge_coefficients)

if (interactive()) {
  plot(ridge_cv)
  abline(v = log(ridge_cv$lambda.min), col = "red", lty = 2)
}

# (d) Ridge predictions.
ridge_predictions <- drop(predict(
  ridge_cv,
  newx = X_new,
  s = "lambda.min"
))
cat("Ridge predictions:\n")
print(ridge_predictions)

# (e) LASSO: alpha = 1, using exactly the same folds and lambda grid.
lasso_cv <- glmnet::cv.glmnet(
  x = X,
  y = y,
  alpha = 1,
  lambda = lambda_grid,
  foldid = fold_id,
  type.measure = "mse",
  standardize = TRUE
)

cat("LASSO lambda.min =", lasso_cv$lambda.min, "\n")
cat("LASSO lambda.1se =", lasso_cv$lambda.1se, "\n")
lasso_coefficients <- as.matrix(coef(lasso_cv, s = "lambda.min"))
print(lasso_coefficients)

nonzero_lasso <- rownames(lasso_coefficients)[
  lasso_coefficients[, 1L] != 0 &
    rownames(lasso_coefficients) != "(Intercept)"
]
cat("Nonzero LASSO predictors at lambda.min:\n")
print(nonzero_lasso)

if (interactive()) {
  plot(lasso_cv)
  abline(v = log(lasso_cv$lambda.min), col = "red", lty = 2)
}

# Compare OLS, ridge, and LASSO on the original predictor scales.
coefficient_comparison <- data.frame(
  term = rownames(lasso_coefficients),
  OLS = coef(full_ols)[rownames(lasso_coefficients)],
  ridge = ridge_coefficients[rownames(lasso_coefficients), 1L],
  LASSO = lasso_coefficients[, 1L],
  row.names = NULL
)
cat("Coefficient comparison:\n")
print(coefficient_comparison)

# Optional post-LASSO OLS refit for comparison only.
post_lasso_ols <- lm(
  reformulate(nonzero_lasso, response = "hipcenter"),
  data = seatpos
)
cat("OLS refit using the LASSO-selected variables:\n")
print(summary(post_lasso_ols))

# (f) Compare predictions.
lasso_predictions <- drop(predict(
  lasso_cv,
  newx = X_new,
  s = "lambda.min"
))

prediction_comparison <- cbind(
  newdata,
  ridge_prediction = ridge_predictions,
  lasso_prediction = lasso_predictions,
  ridge_minus_lasso = ridge_predictions - lasso_predictions
)
cat("Ridge and LASSO predictions for newdata.csv:\n")
print(prediction_comparison)

