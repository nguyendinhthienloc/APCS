# Set seed for reproducibility
set.seed(1)

# (a) Using the rnorm() function, create a vector, x, containing 100 observations drawn 
# from a N(0; 1) distribution. This represents a feature, X.
x <- rnorm(100, mean = 0, sd = 1)

# (b) Using the rnorm() function, create a vector, eps, containing 100 observations drawn 
# from a N(0; 0:25) distribution|a normal distribution with mean zero and variance 0:25.
eps <- rnorm(100, mean = 0, sd = 0.25)

# (c) Using x and eps, generate a vector y according to the model Y = −1 + 0:5X + : (3.39)
# What is the length of the vector y? What are the values of β0 and β1 in this linear model?
y <- -1 + 0.5 * x + eps
length_y <- length(y)
print(paste("Length of vector y:", length(y)))
print(paste("Beta_0:", -1))
print(paste("Beta_1:", 0.5))

# (d) Create a scatterplot displaying the relationship between x and y. Comment on what 
# you observe.
plot(x, y, main = "Relationship between x and y", xlab = "X", ylab = "Y", pch = 19, col = "blue")
# Comment:
# There is a postive linear relation ship.

# (e) Fit a least squares linear model to predict y using x. Comment on the model obtained. 
# How do β^0 and β^1 compare to β0 and β1?
model <- lm(y ~ x)
summary(model)
# Comment: 
# The linear regression model accurately estimates the coefficients close to the true
# values and shows significant statistical relevance. The R-squared value of 46.74%
# indicates a reasonable fit.
# The estimated coefficients from the linear regression model, B_hat_0 and B_hat_1
# compare very closely to the true values B_0 and B_1
# These estimates are highly accurate, confirming that the model effectively
# captures the underlying relationship between x and y

# (f) Display the least squares line on the scatterplot obtained in (d)
abline(model, col = "red", lwd = 2)  # Least squares line
abline(a = -1, b = 0.5, col = "green", lwd = 2, lty = 2)  # Population line, dashed
legend("topright", legend = c("Least Squares Line", "Population Line"),
       col = c("red", "green"), lwd = 2, lty = c(1, 2), cex = 0.8)

# (g) Now fit a polynomial regression model that predicts y using x and x2. Is there 
# evidence that the quadratic term improves the model fit? Explain your answer.
model_poly <- lm(y ~ x + I(x^2))
summary(model_poly)

# There is a small increase in the R-squared, moreover, the p-value of term x^2 quite large
# So x^2 does not have meaningful in explanation relation ship between x and y

# (h) Repeat (a)–(f) after modifying the data generation process in such a way
# that there is less noise in the data. The model (3.39) should remain the same.
# You can do this by decreasing the variance of the normal distribution used to
# generate the error term ϵ in (b). Describe your results.
x_less <- rnorm(100, mean = 0, sd = 1)
eps_less <- rnorm(100, mean = 0, sd = 0.25)
y_less <- -1 + 0.5 * x_less + eps_less
model_less <- lm(y_less~x_less)
summary(model_less)
plot(x_less, y_less, main = "Scatterplot of x vs y with Reduced Noise", xlab = "X", ylab = "Y", pch = 19, col = "blue")
abline(model_less, col = "red", lwd = 2)
abline(a = -1, b = 0.5, col = "green", lwd = 2, lty = 2)
legend("topright", legend = c("Least Squares Line", "Population Line"),
       col = c("red", "green"), lwd = 2, lty = c(1, 2), cex = 0.8)
# When the standard deviations of the error terms are small, that means
# the predictors will vary less from the response giving the model a better accuracy.

# (i) Repeat (a)–(f) after modifying the data generation process in such
# a way that there is more noise in the data. The model (3.39) should remain
# the same. You can do this by increasing the variance of the normal distribution used to generate the error term ϵ in (b).
# Describe your results.

x_large <- rnorm(100, mean = 0, sd = 1)
eps_large <- rnorm(100, mean = 0, sd = 1)
y_large <- -1 + 0.5 * x_large + eps_large
model_large <- lm(y_large ~ x_large)
summary(model_large)
plot(x_large, y_large, main = "Scatterplot of x vs y with Increased Noise", xlab = "X", ylab = "Y", pch = 19, col = "blue")
abline(model_large, col = "red", lwd = 2)
abline(a = -1, b = 0.5, col = "green", lwd = 2, lty = 2)
legend("topright", legend = c("Least Squares Line", "Population Line"),
       col = c("red", "green"), lwd = 2, lty = c(1, 2), cex = 0.8)

# When the standard deviations of the error terms are huge, the predictors will
# vary a lot from the response giving the model a harder time to statistically
# identify what value it will be.

# (j) What are the confidence intervals for β0 and β1 based on the original data set, the 
# noisier data set, and the less noisy data set? Comment on your results.

confint(model)
confint(model_less)
confint(model_large)

# Comment: The higher the standard deviation of the error terms,
# the less confident the model has in predicting a value.