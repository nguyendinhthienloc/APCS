# STAT452 R Syntax Reference

A practical syntax reference for the four training topics in this course.

## 0. Basic R syntax

```r
# Comment
x <- 5                         # Assignment
x == 5                        # Equality test
c(1, 2, 3)                     # Create a vector
seq(0, 10, by = 2)             # Sequence
rep(1:3, times = 2)            # Repeat values
length(x)                      # Number of elements
class(x)                       # Object class
typeof(x)                      # Storage type
is.na(x)                       # Missing-value indicator
x[!is.na(x)]                   # Remove missing values
?mean                          # Open help
help(lm)
getwd()                        # Current folder
setwd("path/to/folder")        # Change folder
set.seed(452)                  # Reproducible random results
```

Use `<-` for assignment. Use `=` mainly for function arguments. Use `==` to test equality.

## 1. Objects, vectors, matrices, and data frames

```r
v <- c(2, 4, 6, 8)
v[1]                           # First element
v[2:4]                         # Elements 2 through 4
v[-1]                          # Every element except the first
v[v > 4]                       # Logical filtering

M <- matrix(1:6, nrow = 2, byrow = TRUE)
M[1, 2]                        # Row 1, column 2
t(M)                           # Transpose
dim(M)                         # Dimensions
nrow(M); ncol(M)

d <- data.frame(
  y = c(10, 12, 15),
  x = c(1, 2, 3),
  group = factor(c("A", "A", "B"))
)
d$y                            # Select a column
d[, c("y", "x")]               # Select columns
d[1:2, ]                       # Select rows
subset(d, x > 1)               # Filter rows
d$new_variable <- d$x^2        # Add a column
names(d); str(d); head(d)
summary(d)
```

## 2. Importing, exporting, and preparing data

```r
data(mtcars)                   # Load a built-in dataset
cars <- mtcars
read.csv("data.csv")
write.csv(cars, "cars.csv", row.names = FALSE)

na.omit(d)                     # Remove rows with missing values
complete.cases(d)
d[complete.cases(d), ]

factor(c("No", "Yes"), levels = c("No", "Yes"))
factor(x, labels = c("automatic", "manual"))
droplevels(d)

mean(x)
mean(x, na.rm = TRUE)
median(x, na.rm = TRUE)
sd(x, na.rm = TRUE)
var(x, na.rm = TRUE)
min(x); max(x); range(x)
quantile(x, probs = c(.25, .5, .75), na.rm = TRUE)
sum(x); length(x)
table(d$group)
prop.table(table(d$group))
scale(x)                       # Standardize: mean 0, standard deviation 1
```

## 3. Graphics and model visualization

```r
plot(x, y)
plot(y ~ x, data = d)
hist(x, breaks = 10)
boxplot(y ~ group, data = d)
pairs(d[, c("y", "x1", "x2")])
cor(d[, c("x1", "x2", "x3")], use = "complete.obs")

plot(x, y, pch = 19, col = "navy",
     main = "Response versus predictor",
     xlab = "Predictor", ylab = "Response")

abline(lm(y ~ x, data = d), col = "red", lwd = 2)

curve(predict(fit, newdata = data.frame(x = x)),
      add = TRUE, col = "blue", lwd = 2)

par(mfrow = c(2, 2))            # Four plots on one page
plot(fit)
par(mfrow = c(1, 1))            # Reset layout
legend("topright", legend = c("Observed", "Fitted"),
       col = c("black", "blue"), pch = c(19, NA), lty = c(NA, 1))
```

## 4. Multiple linear regression

### Fit and inspect a model

```r
fit <- lm(mpg ~ wt + hp, data = mtcars)
fit
summary(fit)
coef(fit)
coefficients(fit)
confint(fit)
vcov(fit)
formula(fit)
model.frame(fit)
model.matrix(fit)
```

The formula syntax is:

```r
y ~ x                           # Intercept plus x
y ~ x1 + x2                    # Intercept plus two predictors
y ~ .                           # Every other column as predictor
y ~ x - 1                      # Remove the intercept
y ~ 0 + x                      # Remove the intercept
y ~ x1 * x2                    # x1 + x2 + x1:x2
y ~ x1:x2                      # Interaction only
y ~ x + factor(group)          # Numeric and categorical predictor
```

### Coefficients and interpretations

```r
coef(fit)["wt"]
coef(summary(fit))
summary(fit)$coefficients
summary(fit)$sigma
summary(fit)$r.squared
summary(fit)$adj.r.squared
df.residual(fit)
```

For `mpg ~ wt + hp`, the coefficient of `wt` is interpreted as the expected change in mpg for a one-unit increase in weight while holding horsepower fixed.

### Fitted values and residuals

```r
y_hat <- fitted(fit)
y_hat <- fit$fitted.values
e <- resid(fit)
e <- residuals(fit)

head(data.frame(
  observed = mtcars$mpg,
  fitted = y_hat,
  residual = e
))

max(abs(mtcars$mpg - (y_hat + e)))
sum(e)
```

### Manual least-squares quantities

```r
x <- mtcars$wt
y <- mtcars$mpg
x_bar <- mean(x)
y_bar <- mean(y)

Sxx <- sum((x - x_bar)^2)
Sxy <- sum((x - x_bar) * (y - y_bar))
b1 <- Sxy / Sxx
b0 <- y_bar - b1 * x_bar

SSE <- sum(e^2)
SST <- sum((y - mean(y))^2)
SSR <- SST - SSE
MSE <- SSE / df.residual(fit)
RMSE <- sqrt(MSE)
R2 <- 1 - SSE / SST
c(SSE = SSE, SST = SST, SSR = SSR, MSE = MSE, RMSE = RMSE, R2 = R2)
```

### Matrix least squares

```r
X <- model.matrix(fit)
Y <- matrix(mtcars$mpg, ncol = 1)

t(X)                            # Transpose
t(X) %*% X                      # Matrix multiplication
solve(t(X) %*% X)               # Matrix inverse
beta_hat <- solve(t(X) %*% X, t(X) %*% Y)
beta_hat

drop(t(X) %*% matrix(resid(fit), ncol = 1))
```

Use `%*%` for matrix multiplication. Use `*` for element-by-element multiplication.

### Coefficient tests and confidence intervals

```r
tab <- coef(summary(fit))
estimate <- tab["hp", "Estimate"]
standard_error <- tab["hp", "Std. Error"]
t_value <- estimate / standard_error
df_error <- df.residual(fit)
p_value <- 2 * pt(abs(t_value), df = df_error, lower.tail = FALSE)

c(t = t_value, df = df_error, p = p_value)
confint(fit, "hp", level = 0.95)
```

### Prediction

```r
new_car <- data.frame(wt = 3, hp = 110)

predict(fit, newdata = new_car)
predict(fit, newdata = new_car,
        interval = "confidence", level = 0.95)
predict(fit, newdata = new_car,
        interval = "prediction", level = 0.95)
```

A confidence interval estimates the mean response. A prediction interval estimates one new individual response and is wider.

### Nested models and partial F-tests

```r
reduced <- lm(mpg ~ wt, data = mtcars)
full <- lm(mpg ~ wt + hp, data = mtcars)

anova(reduced, full)
anova(full)
drop1(full, test = "F")
```

### Diagnostics and influential observations

```r
plot(fit)

rstandard(fit)                  # Standardized residuals
rstudent(fit)                   # Studentized residuals
hatvalues(fit)                  # Leverage
cooks.distance(fit)             # Cook's distance
influence.measures(fit)
dfbetas(fit)
which.max(abs(rstandard(fit)))
which.max(cooks.distance(fit))
```

Interpret the four standard plots as checks for:

1. Linearity and changing spread.
2. Approximate normality of errors.
3. Constant error variance.
4. Leverage and influential observations.

## 5. Polynomial regression

### Polynomial terms

```r
linear <- lm(mpg ~ wt, data = mtcars)
quadratic <- lm(mpg ~ wt + I(wt^2), data = mtcars)
cubic <- lm(mpg ~ wt + I(wt^2) + I(wt^3), data = mtcars)

summary(quadratic)
anova(linear, quadratic, cubic)
AIC(linear, quadratic, cubic)
BIC(linear, quadratic, cubic)
```

Use `I()` to make R evaluate the arithmetic expression inside a formula.

### Orthogonal polynomials

```r
orthogonal_fit <- lm(mpg ~ poly(wt, degree = 2), data = mtcars)
raw_fit <- lm(mpg ~ poly(wt, degree = 2, raw = TRUE), data = mtcars)
summary(orthogonal_fit)
summary(raw_fit)
```

`poly(wt, 2)` uses orthogonal polynomial bases by default. Use `raw = TRUE` for the ordinary `wt` and `wt^2` terms.

### Centering and stationary points

```r
mtcars$wt_c <- mtcars$wt - mean(mtcars$wt)
centered_fit <- lm(mpg ~ wt_c + I(wt_c^2), data = mtcars)

b <- coef(centered_fit)
turning_point_centered <- -b["wt_c"] / (2 * b["I(wt_c^2)"])
turning_point_original <- turning_point_centered + mean(mtcars$wt)
```

### Polynomial predictions and plots

```r
grid <- data.frame(
  wt = seq(min(mtcars$wt), max(mtcars$wt), length.out = 100)
)
grid$fit <- predict(quadratic, newdata = grid)

plot(mpg ~ wt, data = mtcars, pch = 19)
lines(grid$wt, grid$fit, col = "blue", lwd = 2)
```

Be cautious when predicting outside the observed predictor range:

```r
predict(quadratic, newdata = data.frame(wt = c(1, 3, 6)))
range(mtcars$wt)
```

### Transformations

```r
log_y_fit <- lm(log(mpg) ~ wt, data = mtcars)
log_x_fit <- lm(mpg ~ log(wt), data = mtcars)
log_log_fit <- lm(log(mpg) ~ log(wt), data = mtcars)

sqrt_fit <- lm(sqrt(mpg) ~ wt, data = mtcars)
inverse_fit <- lm(mpg ~ I(1 / wt), data = mtcars)
power_fit <- lm(mpg ~ I(wt^0.5), data = mtcars)

summary(log_log_fit)
plot(log_log_fit)
```

Common transformations:

```r
log(x)
sqrt(x)
x^2
1 / x
exp(x)
```

## 6. Ridge regression

Ridge regression uses an L2 penalty:

```r
library(MASS)

ridge_grid <- seq(0, 30, length.out = 100)

ridge_fit <- lm.ridge(
  mpg ~ wt + hp + qsec + disp + drat + gear,
  data = mtcars,
  lambda = ridge_grid
)

ridge_fit$coef
ridge_fit$GCV
which.min(ridge_fit$GCV)
ridge_grid[which.min(ridge_fit$GCV)]

plot(ridge_fit)
select(ridge_fit)
```

Ridge coefficients are shrunk toward zero but normally do not become exactly zero.

### Standardization

```r
predictors <- mtcars[, c("wt", "hp", "qsec", "disp", "drat", "gear")]
X_standardized <- scale(predictors)
center_values <- attr(X_standardized, "scaled:center")
scale_values <- attr(X_standardized, "scaled:scale")
```

### Ridge coefficient paths

```r
matplot(
  ridge_grid,
  t(ridge_fit$coef),
  type = "l",
  lty = 1,
  xlab = "lambda",
  ylab = "Coefficient"
)
```

## 7. LASSO regression

If the `glmnet` package is available:

```r
library(glmnet)

x <- model.matrix(
  mpg ~ wt + hp + qsec + disp + drat + gear,
  data = mtcars
)[, -1]
y <- mtcars$mpg

lasso_fit <- glmnet(x, y, alpha = 1)
plot(lasso_fit, xvar = "lambda")

cv_lasso <- cv.glmnet(x, y, alpha = 1, nfolds = 5)
plot(cv_lasso)
cv_lasso$lambda.min
cv_lasso$lambda.1se

coef(cv_lasso, s = "lambda.min")
predict(cv_lasso, newx = x, s = "lambda.min")
```

For ridge with `glmnet`, use `alpha = 0`:

```r
ridge_glmnet <- glmnet(x, y, alpha = 0)
cv_ridge <- cv.glmnet(x, y, alpha = 0, nfolds = 5)
```

LASSO can set coefficients exactly to zero. This makes it useful for sparse variable selection.

### Coordinate descent concepts

```r
soft_threshold <- function(z, gamma) {
  sign(z) * max(abs(z) - gamma, 0)
}
```

The soft-thresholding operation is the key update used in a simple coordinate-descent LASSO implementation.

## 8. Variable selection

### Full and reduced models

```r
full <- lm(mpg ~ wt + hp + qsec + disp + drat + gear, data = mtcars)
reduced <- lm(mpg ~ wt + hp, data = mtcars)

AIC(full, reduced)
BIC(full, reduced)
anova(reduced, full)
```

### Stepwise selection

```r
step(full, direction = "forward", trace = 0)
step(full, direction = "backward", trace = 0)
step(full, direction = "both", trace = 0)

bic_model <- step(
  full,
  direction = "both",
  k = log(nrow(mtcars)),
  trace = 0
)
formula(bic_model)
```

AIC uses `k = 2`. BIC is approximated with `k = log(n)`.

### Manual subset comparison

```r
candidate_1 <- lm(mpg ~ wt, data = mtcars)
candidate_2 <- lm(mpg ~ wt + hp, data = mtcars)
candidate_3 <- lm(mpg ~ wt + hp + qsec, data = mtcars)

AIC(candidate_1, candidate_2, candidate_3)
BIC(candidate_1, candidate_2, candidate_3)
```

Do not select variables from p-values alone. Consider subject-matter meaning, collinearity, prediction error, AIC/BIC, and validation performance.

### Cross-validation

```r
set.seed(452)
fold <- sample(rep(1:5, length.out = nrow(mtcars)))

cv_mse <- function(formula, data, fold) {
  mean(sapply(sort(unique(fold)), function(k) {
    train <- data[fold != k, ]
    test <- data[fold == k, ]
    fit <- lm(formula, data = train)
    mean((test$mpg - predict(fit, newdata = test))^2)
  }))
}

cv_mse(mpg ~ wt, mtcars, fold)
cv_mse(mpg ~ wt + hp + qsec + disp + drat + gear, mtcars, fold)
```

### Leave-one-out cross-validation

```r
library(boot)

loocv <- cv.glm(
  data = mtcars,
  glmfit = glm(mpg ~ wt + hp, data = mtcars),
  K = nrow(mtcars)
)
loocv$delta
```

## 9. Logistic regression

### Prepare a binary response

```r
data(mtcars)

cars <- transform(
  mtcars,
  transmission = factor(
    am,
    levels = c(0, 1),
    labels = c("automatic", "manual")
  )
)
table(cars$transmission)
```

### Fit a logistic model

```r
logit_fit <- glm(
  transmission ~ wt + hp,
  data = cars,
  family = binomial(link = "logit")
)

summary(logit_fit)
coef(logit_fit)
confint.default(logit_fit)
```

The model is:

```r
log odds = beta_0 + beta_1 * wt + beta_2 * hp
```

### Odds ratios

```r
odds_ratios <- exp(coef(logit_fit))
odds_ratios

odds_ratio_intervals <- exp(confint.default(logit_fit))
odds_ratio_intervals

# Effect of a 10-unit increase in horsepower:
exp(10 * coef(logit_fit)["hp"])
```

Interpret `exp(beta_j)` as the multiplicative change in odds for a one-unit increase in predictor `x_j), holding other predictors constant.

### Predicted probabilities

```r
prob_manual <- predict(logit_fit, type = "response")
linear_predictor <- predict(logit_fit, type = "link")

head(prob_manual)
range(prob_manual)

new_car <- data.frame(wt = 3, hp = 110)
predict(logit_fit, newdata = new_car, type = "response")
predict(logit_fit, newdata = new_car, type = "link")
```

### Classification

```r
threshold <- 0.5
predicted_class <- ifelse(
  prob_manual >= threshold,
  "manual",
  "automatic"
)

predicted_class <- factor(
  predicted_class,
  levels = levels(cars$transmission)
)

table(
  observed = cars$transmission,
  predicted = predicted_class
)

mean(predicted_class == cars$transmission)
```

### Confusion-matrix metrics

```r
confusion <- table(
  observed = cars$transmission,
  predicted = predicted_class
)

true_positive <- confusion["manual", "manual"]
true_negative <- confusion["automatic", "automatic"]
false_positive <- confusion["automatic", "manual"]
false_negative <- confusion["manual", "automatic"]

accuracy <- (true_positive + true_negative) / sum(confusion)
sensitivity <- true_positive / (true_positive + false_negative)
specificity <- true_negative / (true_negative + false_positive)
precision <- true_positive / (true_positive + false_positive)

c(
  accuracy = accuracy,
  sensitivity = sensitivity,
  specificity = specificity,
  precision = precision
)
```

Sensitivity is also called the true-positive rate. Specificity is the true-negative rate.

### Threshold comparison

```r
classify_at <- function(probability, truth, threshold = 0.5) {
  prediction <- factor(
    ifelse(probability >= threshold, "manual", "automatic"),
    levels = levels(truth)
  )
  table(observed = truth, predicted = prediction)
}

classify_at(prob_manual, cars$transmission, threshold = 0.3)
classify_at(prob_manual, cars$transmission, threshold = 0.5)
classify_at(prob_manual, cars$transmission, threshold = 0.7)
```

Lowering the threshold usually increases sensitivity and decreases specificity.

### Deviance and nested logistic models

```r
null_fit <- glm(
  transmission ~ 1,
  data = cars,
  family = binomial
)

anova(null_fit, logit_fit, test = "Chisq")
AIC(null_fit, logit_fit)
BIC(null_fit, logit_fit)
deviance(logit_fit)
logLik(logit_fit)
```

### Logistic diagnostic plots

```r
plot(logit_fit)
residuals(logit_fit, type = "deviance")
residuals(logit_fit, type = "pearson")
hatvalues(logit_fit)
cooks.distance(logit_fit)
```

Watch for fitted probabilities near 0 or 1, complete/quasi-complete separation, influential observations, and poor calibration.

## 10. Training/test validation

```r
set.seed(452)
test_index <- sample(seq_len(nrow(cars)), size = 8)

train <- cars[-test_index, ]
test <- cars[test_index, ]

train_fit <- glm(
  transmission ~ wt + hp,
  data = train,
  family = binomial
)

test_probability <- predict(
  train_fit,
  newdata = test,
  type = "response"
)

test_prediction <- ifelse(
  test_probability >= 0.5,
  "manual",
  "automatic"
)

mean(test_prediction == test$transmission)
table(observed = test$transmission, predicted = test_prediction)
```

Training accuracy is usually optimistic because the model was fitted on those observations. Test or cross-validation performance is more informative about generalization.

## 11. Common mistakes

```r
# Correct:
fit <- lm(y ~ x1 + x2, data = d)

# Common mistakes:
# fit <- lm(y = x1 + x2, data = d)   # Wrong formula syntax
# fit <- lm(y ~ x1 * x2, data = d)    # Includes interaction; not just addition
# fit <- predict(fit, newdata = data.frame(X1 = 3))  # Names must match
```

- Use `~` to define a model formula.
- Use `I(x^2)` or `poly(x, 2)` for polynomial terms.
- Use `%*%`, not `*`, for matrix multiplication.
- Keep predictors standardized for ridge/LASSO.
- Use `type = "response"` for logistic probabilities.
- Match factor levels and predictor names between training and new data.
- Do not interpret a multiple-regression coefficient without saying “holding other predictors fixed.”
- Do not use p-values as the only criterion for variable selection.
- Do not delete influential observations automatically.
- Do not extrapolate polynomial models casually.

