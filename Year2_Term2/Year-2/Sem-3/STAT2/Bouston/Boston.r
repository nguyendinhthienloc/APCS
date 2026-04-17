setwd('D:/STAT/Bouston')
getwd()
# Load necessary libraries
library(ggplot2)
library(car)
library(leaps)

# Read the dataset
data <- read.csv("Bouston.csv", header = TRUE)
attach(data)

# Fit a basic linear model
initial_model <- lm(medv ~ ., data = data)

# Check for normality of residuals using Shapiro-Wilk test
shapiro_test <- shapiro.test(residuals(initial_model))
print(shapiro_test)

# Draw boxplots for all columns to visualize outliers
par(mfrow=c(2,4))
for(i in 1:ncol(data)){
  boxplot(data[,i], main=names(data)[i])
}

# Calculate Cook's distance
cooksD <- cooks.distance(initial_model)

# Identify influential observations
influential <- cooksD[(cooksD > (4/length(cooksD)))]

# Extract the indices of influential observations
outliers <- as.numeric(names(influential))

# Remove influential observations to clean the data
clean_data <- data[-outliers, ]

# Draw boxplots for all columns to visualize outliers
par(mfrow=c(2,4))
for(i in 1:ncol(clean_data)){
  boxplot(data[,i], main=names(clean_data)[i])
}

(dim(data)[1]-dim(clean_data)[1])/(dim(data)[1])*100

# Fit a linear model on the cleaned data to check for normality again
clean_model <- lm(medv ~ ., data = clean_data)
shapiro_test_cleaned <- shapiro.test(residuals(clean_model))
print(shapiro_test_cleaned)


# Calculate VIF values
vif_values <- vif(clean_model)
print(vif_values)

taxModel <- lm(tax~. -medv,data=clean_data)
summary(taxModel)

simplified_model <- lm(medv ~. -tax,data=clean_data)
vif_values <- vif(simplified_model)
print(vif_values)


# Use step wise

modFull = lm(medv ~ . -tax, data = clean_data)
modZero = lm(medv ~ 1, data = clean_data)
modInter = lm(medv ~ crim + zn + indus + chas + nox + rm + age)

modBest1A = MASS::stepAIC(modFull, direction = "backward", scope = list(lower = modZero, upper = modFull), k = 2)

modBest1B = MASS::stepAIC(modFull, direction = "backward", scope = list(lower = modZero, upper = modFull), k = log(nrow(clean_data)))

modBest2 = MASS::stepAIC(modZero, direction = "forward", scope = list(lower = modZero, upper = modFull), k = log(nrow(clean_data)))

modBest3 = MASS::stepAIC(modInter, direction = "both", scope = list(lower = modZero, upper = modFull), k = log(nrow(clean_data)))

# Fisher-partial test
anova(modBest2, modBest1A)
anova(modBest1A, modBest2)
alias()
# Calculate R-squared and Adjusted R-squared
r_squared_modBest2 <- summary(modBest2)$r.squared
adj_r_squared_modBest2 <- summary(modBest2)$adj.r.squared
r_squared_modBest1A <- summary(modBest1A)$r.squared
adj_r_squared_modBest1A <- summary(modBest1A)$adj.r.squared

# Calculate AIC and BIC
aic_modBest2 <- AIC(modBest2)
bic_modBest2 <- BIC(modBest2)
aic_modBest1A <- AIC(modBest1A)
bic_modBest1A <- BIC(modBest1A)

# Calculate Residual Standard Error
rse_modBest2 <- summary(modBest2)$sigma
rse_modBest1A <- summary(modBest1A)$sigma
