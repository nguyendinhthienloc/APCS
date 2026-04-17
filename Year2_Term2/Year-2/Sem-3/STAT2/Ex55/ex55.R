
# 55.
# Input the data
x1 <- c(0.93, 1.11, 0.93, 1.11, 0.93, 1.11, 0.93, 1.11, 1.02, 1.02, 1.02, 1.02)
x2 <- c(1, 1, 1, 1, 1.4, 1.4, 1.4, 1.4, 1.18, 1.18, 1.18, 1.18)
x3 <- c(0.2, 0.2, 0.5, 0.5, 0.2, 0.2, 0.5, 0.5, 0.31, 0.31, 0.31, 0.31)
y <- c(32.95, 38.72, 35.2, 38.72, 32.27, 39.71, 33.67, 38.72, 35.2, 33.67, 36.02, 32.27)

# Transform the variables using natural logarithms
ln_x1 <- log(x1)
ln_x2 <- log(x2)
ln_x3 <- log(x3)
ln_y <- log(y)

# Create a data frame
data <- data.frame(ln_x1, ln_x2, ln_x3, ln_y)

# Fit the linear regression model
model <- lm(ln_y ~ ln_x1 + ln_x2 + ln_x3, data = data)

# Display the summary of the model
summary(model)

alpha = 0.05

## b.
model2 = lm(ln_y~ln_x1 + ln_x3)
summary(model2)

## c.
model3 = lm(ln_y~ln_x1)
summary(model3)

## d.
# Calculate standardized residuals
standardized_residuals <- rstandard(model3)

# Display the standardized residuals
standardized_residuals

# Create a data frame for plotting
plot_data <- data.frame(ln_x1 = ln_x1, standardized_residuals = standardized_residuals)

# Plot standardized residuals against ln_x1
plot(plot_data$ln_x1, plot_data$standardized_residuals, 
     xlab = "ln(x1)", ylab = "Standardized Residuals", 
     main = "Standardized Residuals vs. ln(x1)", 
     pch = 16, col = "blue")

# Add a horizontal line at y = 0 for reference
abline(h = 0, col = "red", lty = 2)
## e.
model4 = lm(ln_y ~ ln_x1 + I(ln_x1^2))
model4
summary(model4)

PI = predict(model4, newdata = data.frame(ln_x1 = 0), interval = "prediction", level = 0.95)
lower_bound_prediction = exp(PI[2])
upper_bound_prediction = exp(PI[3])
lower_bound_prediction
upper_bound_prediction


