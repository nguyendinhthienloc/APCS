# STAT452 Chapter 2: Polynomial Regression and Transformations
# Dataset: mtcars; no packages or downloads are needed.

data(mtcars)
cars <- mtcars

# 1. Inspect the response and predictor.
head(cars)
plot(cars$wt, cars$mpg, pch=19, main="Fuel efficiency versus weight",
     xlab="Weight (1000 lb)", ylab="Miles per gallon")

# 2. Compare linear, quadratic, and cubic models.
linear <- lm(mpg ~ wt, data=cars)
quadratic <- lm(mpg ~ wt + I(wt^2), data=cars)
cubic <- lm(mpg ~ wt + I(wt^2) + I(wt^3), data=cars)
summary(linear)
summary(quadratic)
summary(cubic)
anova(linear, quadratic, cubic)
AIC(linear, quadratic, cubic)
BIC(linear, quadratic, cubic)

# 3. Interpret curvature and preserve hierarchy.
coef(quadratic)
beta <- coef(quadratic)
turning_point <- -beta["wt"] / (2 * beta["I(wt^2)"])
turning_point
predict(quadratic, newdata=data.frame(wt=c(min(cars$wt), max(cars$wt))))

# 4. Centering reduces polynomial collinearity.
cars$wt_c <- cars$wt - mean(cars$wt)
quadratic_centered <- lm(mpg ~ wt_c + I(wt_c^2), data=cars)
condition_number <- function(X) max(svd(X)$d) / min(svd(X)$d)
condition_number(model.matrix(quadratic))
condition_number(model.matrix(quadratic_centered))

# 5. Transformations and residual diagnostics.
log_model <- lm(log(mpg) ~ log(wt), data=cars)
summary(log_model)
par(mfrow=c(2,2)); plot(quadratic); par(mfrow=c(1,1))
in_range <- seq(min(cars$wt), max(cars$wt), length.out=100)
lines(in_range, predict(quadratic, data.frame(wt=in_range)), col="blue", lwd=2)

# Never trust polynomial extrapolation without scientific justification.
predict(quadratic, newdata=data.frame(wt=c(1, 6)))

