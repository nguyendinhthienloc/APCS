################################################################################
# Applied Statistics for Engineers and Scientists II - 24A02
# Lab 02 and Lab 03 Solutions
# Polynomial regression, transformations, ridge regression, and lasso
#
# Run this script from the folder containing:
#   Fish.csv, dummy.csv, prostate.csv, fat.csv
# Optional file for Lab 03 Problem 2:
#   abalone.csv
#
# Required packages:
#   tidyverse, MASS, glmnet
# Optional package:
#   olsrr
################################################################################

rm(list = ls())

required_packages <- c("tidyverse", "MASS", "glmnet")
missing_required <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_required) > 0) {
  stop(
    "Please install required package(s): ",
    paste(missing_required, collapse = ", "),
    "\nExample: install.packages(c(",
    paste(sprintf('"%s"', missing_required), collapse = ", "),
    "))"
  )
}

library(tidyverse)
library(MASS)
library(glmnet)

has_olsrr <- requireNamespace("olsrr", quietly = TRUE)

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

read_csv_here <- function(file) {
  if (!file.exists(file.path("data", file))) {
    stop("File not found: ", file, "\nCurrent working directory: ", getwd())
  }
  readr::read_csv(file.path("data", file), show_col_types = FALSE)
}

trainTestSplit <- function(data, seed, trainRatio = 0.8) {
  stopifnot(is.data.frame(data))
  stopifnot(is.numeric(trainRatio), trainRatio > 0, trainRatio < 1)
  set.seed(seed)
  n <- nrow(data)
  train_size <- floor(trainRatio * n)
  train_index <- sample(seq_len(n), size = train_size, replace = FALSE)
  list(
    train.data = data[train_index, , drop = FALSE],
    test.data = data[-train_index, , drop = FALSE],
    train.index = train_index
  )
}

mse_vec <- function(actual, predicted) {
  mean((actual - predicted)^2)
}

rss_vec <- function(actual, predicted) {
  sum((actual - predicted)^2)
}

safe_save_plot <- function(plot_obj, filename, width = 8, height = 5) {
  print(plot_obj)
  ggplot2::ggsave(filename, plot_obj, width = width, height = height, dpi = 300)
}

lm_diagnostics <- function(model, title = "linear model") {
  cat("\n================ Diagnostics:", title, "================\n")
  print(summary(model))
  cat("\nResidual summary:\n")
  print(summary(residuals(model)))
  cat("\nLargest absolute standardized residuals:\n")
  std_resid <- rstandard(model)
  print(head(sort(abs(std_resid), decreasing = TRUE), 10))
  cat("\nLargest Cook's distances:\n")
  cook <- cooks.distance(model)
  print(head(sort(cook, decreasing = TRUE), 10))
  invisible(tibble(
    index = seq_along(residuals(model)),
    fitted = fitted(model),
    residual = residuals(model),
    std_resid = std_resid,
    cooks_distance = cook,
    leverage = hatvalues(model)
  ))
}

plot_residuals_gg <- function(model, title_prefix = "Model") {
  diag_data <- tibble(
    index = seq_along(residuals(model)),
    fitted = fitted(model),
    residual = residuals(model),
    std_resid = rstandard(model),
    cooks_distance = cooks.distance(model)
  )

  p1 <- ggplot(diag_data, aes(index, residual)) +
    geom_hline(yintercept = 0, linetype = "dashed") +
    geom_point() +
    labs(
      title = paste(title_prefix, "residuals versus index"),
      x = "Observation index", y = "Residual"
    ) +
    theme_minimal()

  p2 <- ggplot(diag_data, aes(fitted, residual)) +
    geom_hline(yintercept = 0, linetype = "dashed") +
    geom_point() +
    labs(
      title = paste(title_prefix, "residuals versus fitted values"),
      x = "Fitted value", y = "Residual"
    ) +
    theme_minimal()

  p3 <- ggplot(diag_data, aes(sample = std_resid)) +
    stat_qq() +
    stat_qq_line() +
    labs(
      title = paste(title_prefix, "normal Q-Q plot of standardized residuals"),
      x = "Theoretical quantile", y = "Sample quantile"
    ) +
    theme_minimal()

  p4 <- ggplot(diag_data, aes(index, cooks_distance)) +
    geom_col() +
    geom_hline(yintercept = 4 / nrow(diag_data), linetype = "dashed") +
    labs(
      title = paste(title_prefix, "Cook's distance"),
      x = "Observation index", y = "Cook's distance"
    ) +
    theme_minimal()

  print(p1); print(p2); print(p3); print(p4)
  invisible(diag_data)
}

flag_influential <- function(model, std_resid_cutoff = 3) {
  n <- nobs(model)
  cook_cutoff <- 4 / n
  out <- tibble(
    index = seq_len(n),
    std_resid = rstandard(model),
    cooks_distance = cooks.distance(model),
    leverage = hatvalues(model)
  ) |>
    mutate(flag = abs(std_resid) > std_resid_cutoff | cooks_distance > cook_cutoff)
  out |> filter(flag)
}

make_poly_x <- function(data, degree) {
  stats::model.matrix(y ~ poly(X, degree = degree, raw = TRUE), 
                      data = data)[, -1, drop = FALSE]
}

fit_poly_lm <- function(data, degree) {
  if (degree == 0) {
    lm(y ~ 1, data = data)
  } else {
    lm(y ~ poly(X, degree = degree, raw = TRUE), data = data)
  }
}

extract_nonzero_coefs <- function(coef_object, tol = 1e-8) {
  cf <- as.matrix(coef_object)
  tibble(
    term = rownames(cf),
    estimate = as.numeric(cf[, 1])
  ) |>
    filter(abs(estimate) > tol)
}

manual_best_subsets_aic <- function(data, response, predictors, max_size = length(predictors)) {
  results <- list()
  counter <- 1L

  # Include the intercept-only model.
  null_formula <- as.formula(paste(response, "~ 1"))
  null_fit <- lm(null_formula, data = data)
  results[[counter]] <- tibble(
    size = 0L,
    predictors = "(Intercept only)",
    AIC = AIC(null_fit),
    formula = deparse(null_formula)
  )
  counter <- counter + 1L

  for (k in seq_len(max_size)) {
    cmb <- combn(predictors, k, simplify = FALSE)
    for (pred_set in cmb) {
      form <- as.formula(paste(response, "~", paste(pred_set, collapse = " + ")))
      fit <- lm(form, data = data)
      results[[counter]] <- tibble(
        size = k,
        predictors = paste(pred_set, collapse = ", "),
        AIC = AIC(fit),
        formula = deparse(form)
      )
      counter <- counter + 1L
    }
  }

  bind_rows(results) |> arrange(AIC)
}

clean_abalone_names <- function(data) {
  out <- data
  names(out) <- names(out) |>
    stringr::str_replace_all("\\.", "_") |>
    stringr::str_replace_all("\\s+", "_") |>
    stringr::str_replace_all("-", "_") |>
    stringr::str_to_lower()
  out
}

# -----------------------------------------------------------------------------
# Lab 02. Problem 1: Polynomial regression and transformations with Fish.csv
# -----------------------------------------------------------------------------

cat("\n\n================ LAB 02: PROBLEM 1 ================\n")
fish <- read_csv_here("Fish.csv") |> drop_na()

p_fish_scatter <- ggplot(fish, aes(x = Width, y = Weight)) +
  geom_point() +
  geom_smooth(method = "lm", formula = y ~ x, se = FALSE, linetype = "dashed") +
  geom_smooth(method = "lm", formula = y ~ poly(x, 2, raw = TRUE), se = FALSE) +
  geom_smooth(method = "lm", formula = y ~ poly(x, 3, raw = TRUE), se = FALSE, linetype = "dotted") +
  labs(
    title = "Fish data: Weight versus Width",
    subtitle = "Dashed: linear; solid: quadratic; dotted: cubic",
    x = "Width", y = "Weight"
  ) +
  theme_minimal()
print(p_fish_scatter)

fish_quad <- lm(Weight ~ Width + I(Width^2), data = fish)
fish_cubic <- lm(Weight ~ Width + I(Width^2) + I(Width^3), data = fish)

cat("\nQuadratic model summary:\n")
print(summary(fish_quad))
cat("\nCubic model summary:\n")
print(summary(fish_cubic))
cat("\nNested model comparison: quadratic versus cubic:\n")
print(anova(fish_quad, fish_cubic))

fish_cubic_diag <- lm_diagnostics(fish_cubic, "Fish cubic model")
plot_residuals_gg(fish_cubic, "Fish cubic model")

fish_flagged <- flag_influential(fish_cubic)
cat("\nObservations flagged by |standardized residual| > 3 or Cook's distance > 4/n:\n")
print(fish_flagged)

if (nrow(fish_flagged) > 0) {
  fish_clean <- fish[-fish_flagged$index, , drop = FALSE]
} else {
  fish_clean <- fish
}

fish_cubic_clean <- lm(Weight ~ Width + I(Width^2) + I(Width^3), data = fish_clean)
cat("\nCubic model after removing flagged observations, if any:\n")
print(summary(fish_cubic_clean))
plot_residuals_gg(fish_cubic_clean, "Fish cubic model after removal")

fish_sqrt <- fish_clean |> mutate(sqrt_Weight = sqrt(Weight))
fish_sqrt_model <- lm(sqrt_Weight ~ Width, data = fish_sqrt)

p_fish_sqrt <- ggplot(fish_sqrt, aes(x = Width, y = sqrt_Weight)) +
  geom_point() +
  geom_smooth(method = "lm", se = FALSE) +
  labs(
    title = "Fish data after square-root transformation",
    x = "Width", y = expression(sqrt(Weight))
  ) +
  theme_minimal()
print(p_fish_sqrt)

cat("\nSquare-root transformed model summary:\n")
print(summary(fish_sqrt_model))
plot_residuals_gg(fish_sqrt_model, "sqrt(Weight) ~ Width")

# -----------------------------------------------------------------------------
# Lab 02. Problem 2: Interactions with iris
# -----------------------------------------------------------------------------

cat("\n\n================ LAB 02: PROBLEM 2 ================\n")
iris_tbl <- as_tibble(iris)

p_iris <- ggplot(iris_tbl, aes(x = Sepal.Width, y = Sepal.Length, color = Species)) +
  geom_point() +
  geom_smooth(method = "lm", se = FALSE) +
  labs(
    title = "Iris data: Sepal.Length versus Sepal.Width by species",
    x = "Sepal.Width", y = "Sepal.Length"
  ) +
  theme_minimal()
print(p_iris)

iris_simple <- lm(Sepal.Length ~ Sepal.Width, data = iris_tbl)
iris_interaction <- lm(Sepal.Length ~ Sepal.Width + Sepal.Width:Species, data = iris_tbl)

cat("\nSimple model summary:\n")
print(summary(iris_simple))
cat("\nInteraction-only model summary, following the lab formula:\n")
print(summary(iris_interaction))
cat("\nNested comparison: simple model versus interaction-only model:\n")
print(anova(iris_simple, iris_interaction))
plot_residuals_gg(iris_interaction, "Iris interaction-only model")

# A model with both species main effects and interactions is often more natural.
iris_full_interaction <- lm(Sepal.Length ~ Sepal.Width * Species, data = iris_tbl)
cat("\nFull interaction model with different intercepts and slopes, for comparison:\n")
print(summary(iris_full_interaction))
print(anova(iris_simple, iris_full_interaction))

# -----------------------------------------------------------------------------
# Lab 02. Problem 3: Box-Cox transformations
# -----------------------------------------------------------------------------

cat("\n\n================ LAB 02: PROBLEM 3 ================\n")
boxcox_grid <- seq(-2, 2, by = 0.01)
boxcox_profile <- MASS::boxcox(iris_interaction, lambda = boxcox_grid, plotit = TRUE)
lambda_hat <- boxcox_profile$x[which.max(boxcox_profile$y)]
cat("\nBox-Cox lambda maximizing the profile log-likelihood:", lambda_hat, "\n")

boxcox_transform <- function(y, lambda) {
  if (any(y <= 0, na.rm = TRUE)) {
    stop("Box-Cox transformation requires strictly positive response values.")
  }
  if (abs(lambda) < 1e-8) {
    log(y)
  } else {
    (y^lambda - 1) / lambda
  }
}

iris_bc <- iris_tbl |>
  mutate(Sepal_Length_bc = boxcox_transform(Sepal.Length, lambda_hat))

iris_bc_model <- lm(Sepal_Length_bc ~ Sepal.Width + Sepal.Width:Species, data = iris_bc)
cat("\nBox-Cox transformed interaction model summary:\n")
print(summary(iris_bc_model))
plot_residuals_gg(iris_bc_model, "Box-Cox transformed iris model")

# -----------------------------------------------------------------------------
# Lab 02. Problem 4: Train/test split and polynomial model selection
# -----------------------------------------------------------------------------

cat("\n\n================ LAB 02: PROBLEM 4 ================\n")
dummy <- read_csv_here("dummy.csv") |> drop_na()

split_dummy <- trainTestSplit(dummy, seed = 0, trainRatio = 0.8)
train.data <- split_dummy$train.data
test.data <- split_dummy$test.data

p_dummy_train <- ggplot(train.data, aes(x = X, y = y)) +
  geom_point() +
  labs(title = "Training data from dummy.csv", x = "X", y = "y") +
  theme_minimal()
print(p_dummy_train)

poly_results <- map_dfr(0:5, function(deg) {
  fit <- fit_poly_lm(train.data, deg)
  pred_test <- predict(fit, newdata = test.data)
  tibble(
    degree = deg,
    train_RSS = rss_vec(train.data$y, fitted(fit)),
    test_RSS = rss_vec(test.data$y, pred_test),
    test_MSE = mse_vec(test.data$y, pred_test),
    adj_R2 = summary(fit)$adj.r.squared
  )
})

cat("\nPolynomial models degree 0 to 5: train RSS and test RSS/MSE:\n")
print(poly_results)

best_degree <- poly_results$degree[which.min(poly_results$test_RSS)]
cat("\nBest degree by test RSS:", best_degree, "\n")
best_poly_lm <- fit_poly_lm(train.data, best_degree)
cat("\nBest polynomial model summary:\n")
print(summary(best_poly_lm))
plot_residuals_gg(best_poly_lm, paste0("Best dummy polynomial, degree ", best_degree))

# -----------------------------------------------------------------------------
# Lab 03. Problem 1: Ridge and LASSO regression on dummy.csv
# -----------------------------------------------------------------------------

cat("\n\n================ LAB 03: PROBLEM 1 ================\n")
# Reuse train.data and test.data from Lab 02 Problem 4, as requested by the lab.

ols_degree5 <- lm(y ~ poly(X, degree = 5, raw = TRUE), data = train.data)
ols_degree5_pred <- predict(ols_degree5, newdata = test.data)
cat("\nOLS degree-5 polynomial coefficients:\n")
print(coef(ols_degree5))
cat("\nOLS degree-5 test MSE:", mse_vec(test.data$y, ols_degree5_pred), "\n")

x_train_poly5 <- make_poly_x(train.data, degree = 5)
y_train <- train.data$y
x_test_poly5 <- make_poly_x(test.data, degree = 5)
y_test <- test.data$y
lambda_grid <- exp(seq(-5, 5, by = 0.01))

set.seed(0)
cv_ridge_dummy <- cv.glmnet(
  x = x_train_poly5,
  y = y_train,
  alpha = 0,
  lambda = lambda_grid,
  standardize = TRUE,
  intercept = TRUE,
  nfolds = 10
)
plot(cv_ridge_dummy)

ridge_lambda_min <- cv_ridge_dummy$lambda.min
ridge_coef_dummy <- coef(cv_ridge_dummy, s = "lambda.min")
ridge_pred_dummy <- predict(cv_ridge_dummy, newx = x_test_poly5, s = "lambda.min")

cat("\nRidge optimal lambda by CV:", ridge_lambda_min, "\n")
cat("\nRidge coefficients at lambda.min:\n")
print(ridge_coef_dummy)
cat("\nRidge test MSE:", mse_vec(y_test, as.numeric(ridge_pred_dummy)), "\n")

set.seed(0)
cv_lasso_dummy <- cv.glmnet(
  x = x_train_poly5,
  y = y_train,
  alpha = 1,
  lambda = lambda_grid,
  standardize = TRUE,
  intercept = TRUE,
  nfolds = 10
)
plot(cv_lasso_dummy)

lasso_lambda_min <- cv_lasso_dummy$lambda.min
lasso_coef_dummy <- coef(cv_lasso_dummy, s = "lambda.min")
lasso_pred_dummy <- predict(cv_lasso_dummy, newx = x_test_poly5, s = "lambda.min")

cat("\nLasso optimal lambda by CV:", lasso_lambda_min, "\n")
cat("\nLasso coefficients at lambda.min:\n")
print(lasso_coef_dummy)
cat("\nLasso nonzero coefficients at lambda.min:\n")
print(extract_nonzero_coefs(lasso_coef_dummy))
cat("\nLasso test MSE:", mse_vec(y_test, as.numeric(lasso_pred_dummy)), "\n")

cat("\nComparison comment:\n")
cat("Ridge usually keeps all polynomial terms but shrinks them. Lasso may set high-order terms\n")
cat("to zero. If the 4th and 5th order coefficients are zero or close to zero under lasso,\n")
cat("then lasso is selecting a model closer to the cubic polynomial.\n")

# -----------------------------------------------------------------------------
# Lab 03. Problem 2: Abalone dataset
# -----------------------------------------------------------------------------

cat("\n\n================ LAB 03: PROBLEM 2 ================\n")
if (!file.exists("abalone.csv")) {
  cat("\nThe file abalone.csv is not present in the working directory.\n")
  cat("Place abalone.csv in the working directory and rerun this block.\n")
} else {
  abalone_raw <- read_csv_here("abalone.csv") |> drop_na()
  abalone <- clean_abalone_names(abalone_raw)

  # Expected names after cleaning:
  # whole_weight, length, diameter, height, shucked_weight, viscera_weight, shell_weight
  required_abalone <- c(
    "whole_weight", "length", "diameter", "height",
    "shucked_weight", "viscera_weight", "shell_weight"
  )
  missing_abalone <- setdiff(required_abalone, names(abalone))
  if (length(missing_abalone) > 0) {
    stop("The abalone file is missing required columns after name cleaning: ",
         paste(missing_abalone, collapse = ", "),
         "\nAvailable columns: ", paste(names(abalone), collapse = ", "))
  }

  split_abalone <- trainTestSplit(abalone, seed = 0, trainRatio = 0.8)
  ab_train <- split_abalone$train.data
  ab_test <- split_abalone$test.data

  ab_predictors <- c("length", "diameter", "height", "shucked_weight", "viscera_weight", "shell_weight")
  ab_formula <- as.formula(paste("whole_weight ~", paste(ab_predictors, collapse = " + ")))
  ab_full_lm <- lm(ab_formula, data = ab_train)
  cat("\nAbalone full OLS model summary:\n")
  print(summary(ab_full_lm))

  ab_x_train <- model.matrix(ab_formula, data = ab_train)[, -1, drop = FALSE]
  ab_y_train <- ab_train$whole_weight
  ab_x_test <- model.matrix(ab_formula, data = ab_test)[, -1, drop = FALSE]
  ab_y_test <- ab_test$whole_weight

  set.seed(0)
  cv_lasso_abalone <- cv.glmnet(
    x = ab_x_train,
    y = ab_y_train,
    alpha = 1,
    standardize = TRUE,
    intercept = TRUE,
    nfolds = 10
  )
  plot(cv_lasso_abalone)
  ab_lasso_coef <- coef(cv_lasso_abalone, s = "lambda.min")
  cat("\nAbalone lasso lambda.min:", cv_lasso_abalone$lambda.min, "\n")
  cat("\nAbalone lasso nonzero coefficients:\n")
  print(extract_nonzero_coefs(ab_lasso_coef))
  ab_lasso_pred <- predict(cv_lasso_abalone, newx = ab_x_test, s = "lambda.min")
  cat("\nAbalone lasso test MSE:", mse_vec(ab_y_test, as.numeric(ab_lasso_pred)), "\n")

  cat("\nNumber of possible submodels using 6 candidate predictors:\n")
  cat("Including the intercept-only model: 2^6 =", 2^6, "\n")
  cat("Excluding the intercept-only model:", 2^6 - 1, "\n")

  ab_aic_all <- manual_best_subsets_aic(ab_train, "whole_weight", ab_predictors)
  cat("\nBest abalone subsets by AIC from manual exhaustive search:\n")
  print(head(ab_aic_all, 10))

  p_ab_aic <- ggplot(ab_aic_all, aes(x = size, y = AIC)) +
    geom_point(alpha = 0.6) +
    geom_line(data = ab_aic_all |> group_by(size) |> slice_min(AIC, n = 1), aes(x = size, y = AIC)) +
    labs(title = "Abalone all-subsets search: subset size versus AIC", x = "Subset size", y = "AIC") +
    theme_minimal()
  print(p_ab_aic)

  ab_backward <- step(ab_full_lm, direction = "backward", trace = FALSE)
  ab_null_lm <- lm(whole_weight ~ 1, data = ab_train)
  ab_forward <- step(ab_null_lm, scope = list(lower = whole_weight ~ 1, upper = ab_formula),
                     direction = "forward", trace = FALSE)
  cat("\nAbalone backward stepwise model:\n")
  print(summary(ab_backward))
  cat("\nAbalone forward stepwise model:\n")
  print(summary(ab_forward))

  if (has_olsrr) {
    cat("\nRunning olsrr best subset tools as optional confirmation.\n")
    ab_ols_all <- olsrr::ols_step_all_possible(ab_full_lm)
    print(ab_ols_all)
    ab_ols_best <- olsrr::ols_step_best_subset(ab_full_lm, metric = "aic")
    print(ab_ols_best)
  } else {
    cat("\nPackage olsrr is not installed. Manual AIC search and base R step() were used instead.\n")
  }
}

# -----------------------------------------------------------------------------
# Lab 03. Problem 3: Prostate dataset
# -----------------------------------------------------------------------------

cat("\n\n================ LAB 03: PROBLEM 3 ================\n")
prostate <- read_csv_here("prostate.csv") |> drop_na()
split_prostate <- trainTestSplit(prostate, seed = 0, trainRatio = 0.8)
pros_train <- split_prostate$train.data
pros_test <- split_prostate$test.data

pros_full_lm <- lm(lpsa ~ ., data = pros_train)
pros_null_lm <- lm(lpsa ~ 1, data = pros_train)
cat("\nFull prostate OLS model summary:\n")
print(summary(pros_full_lm))
cat("\nNested F-test: null model versus full model:\n")
print(anova(pros_null_lm, pros_full_lm))

pros_formula <- lpsa ~ .
pros_x_train <- model.matrix(pros_formula, data = pros_train)[, -1, drop = FALSE]
pros_y_train <- pros_train$lpsa
pros_x_test <- model.matrix(pros_formula, data = pros_test)[, -1, drop = FALSE]
pros_y_test <- pros_test$lpsa
pros_lambda_grid <- exp(seq(-5, 5, by = 0.01))

set.seed(0)
cv_ridge_prostate <- cv.glmnet(
  x = pros_x_train,
  y = pros_y_train,
  alpha = 0,
  lambda = pros_lambda_grid,
  standardize = TRUE,
  intercept = TRUE,
  nfolds = 10
)
plot(cv_ridge_prostate)
pros_ridge_coef <- coef(cv_ridge_prostate, s = "lambda.min")
pros_ridge_pred <- predict(cv_ridge_prostate, newx = pros_x_test, s = "lambda.min")
cat("\nProstate ridge lambda.min:", cv_ridge_prostate$lambda.min, "\n")
cat("\nProstate ridge coefficients:\n")
print(pros_ridge_coef)
cat("\nProstate ridge test MSE:", mse_vec(pros_y_test, as.numeric(pros_ridge_pred)), "\n")
cat("\nRidge does not perform exact variable deletion. Variables with very small absolute coefficients\n")
cat("can be considered weak, but ridge itself keeps all variables in the prediction rule.\n")

set.seed(0)
cv_lasso_prostate <- cv.glmnet(
  x = pros_x_train,
  y = pros_y_train,
  alpha = 1,
  lambda = pros_lambda_grid,
  standardize = TRUE,
  intercept = TRUE,
  nfolds = 10
)
plot(cv_lasso_prostate)
pros_lasso_coef <- coef(cv_lasso_prostate, s = "lambda.min")
pros_lasso_pred <- predict(cv_lasso_prostate, newx = pros_x_test, s = "lambda.min")
cat("\nProstate lasso lambda.min:", cv_lasso_prostate$lambda.min, "\n")
cat("\nProstate lasso nonzero coefficients:\n")
print(extract_nonzero_coefs(pros_lasso_coef))
cat("\nProstate lasso test MSE:", mse_vec(pros_y_test, as.numeric(pros_lasso_pred)), "\n")

pros_backward <- step(pros_full_lm, direction = "backward", trace = FALSE)
pros_forward <- step(pros_null_lm, scope = list(lower = lpsa ~ 1, upper = pros_formula),
                     direction = "forward", trace = FALSE)
cat("\nProstate backward stepwise model:\n")
print(summary(pros_backward))
cat("\nProstate forward stepwise model:\n")
print(summary(pros_forward))

pros_predictors <- setdiff(names(prostate), "lpsa")
pros_best3 <- manual_best_subsets_aic(pros_train, "lpsa", pros_predictors, max_size = 3) |>
  filter(size == 3) |>
  arrange(AIC)
cat("\nBest 3-variable prostate models by AIC:\n")
print(head(pros_best3, 10))

# -----------------------------------------------------------------------------
# Lab 03. Problem 4: Fat dataset practice
# -----------------------------------------------------------------------------

cat("\n\n================ LAB 03: PROBLEM 4 ================\n")
fat <- read_csv_here("fat.csv") |> drop_na()

# The variables siri and density are direct formula-based relatives of brozek.
# For a realistic prediction exercise from body measurements, exclude siri and density.
# For a purely mechanical exercise, one may include them, but the prediction problem then
# becomes nearly deterministic and less instructive.
fat_predictors <- setdiff(names(fat), c("brozek", "siri", "density"))
fat_formula <- as.formula(paste("brozek ~", paste(fat_predictors, collapse = " + ")))

split_fat <- trainTestSplit(fat, seed = 0, trainRatio = 0.8)
fat_train <- split_fat$train.data
fat_test <- split_fat$test.data

fat_full_lm <- lm(fat_formula, data = fat_train)
cat("\nFat OLS model using anthropometric predictors only:\n")
print(summary(fat_full_lm))
fat_ols_pred <- predict(fat_full_lm, newdata = fat_test)
cat("\nFat OLS test MSE:", mse_vec(fat_test$brozek, fat_ols_pred), "\n")

fat_x_train <- model.matrix(fat_formula, data = fat_train)[, -1, drop = FALSE]
fat_y_train <- fat_train$brozek
fat_x_test <- model.matrix(fat_formula, data = fat_test)[, -1, drop = FALSE]
fat_y_test <- fat_test$brozek

set.seed(0)
cv_ridge_fat <- cv.glmnet(
  x = fat_x_train,
  y = fat_y_train,
  alpha = 0,
  standardize = TRUE,
  intercept = TRUE,
  nfolds = 10
)
plot(cv_ridge_fat)
fat_ridge_pred <- predict(cv_ridge_fat, newx = fat_x_test, s = "lambda.min")
cat("\nFat ridge lambda.min:", cv_ridge_fat$lambda.min, "\n")
cat("\nFat ridge test MSE:", mse_vec(fat_y_test, as.numeric(fat_ridge_pred)), "\n")
print(coef(cv_ridge_fat, s = "lambda.min"))

set.seed(0)
cv_lasso_fat <- cv.glmnet(
  x = fat_x_train,
  y = fat_y_train,
  alpha = 1,
  standardize = TRUE,
  intercept = TRUE,
  nfolds = 10
)
plot(cv_lasso_fat)
fat_lasso_pred <- predict(cv_lasso_fat, newx = fat_x_test, s = "lambda.min")
fat_lasso_coef <- coef(cv_lasso_fat, s = "lambda.min")
cat("\nFat lasso lambda.min:", cv_lasso_fat$lambda.min, "\n")
cat("\nFat lasso nonzero coefficients:\n")
print(extract_nonzero_coefs(fat_lasso_coef))
cat("\nFat lasso test MSE:", mse_vec(fat_y_test, as.numeric(fat_lasso_pred)), "\n")

fat_backward <- step(fat_full_lm, direction = "backward", trace = FALSE)
fat_forward <- step(lm(brozek ~ 1, data = fat_train),
                    scope = list(lower = brozek ~ 1, upper = fat_formula),
                    direction = "forward", trace = FALSE)
cat("\nFat backward stepwise model:\n")
print(summary(fat_backward))
cat("\nFat forward stepwise model:\n")
print(summary(fat_forward))