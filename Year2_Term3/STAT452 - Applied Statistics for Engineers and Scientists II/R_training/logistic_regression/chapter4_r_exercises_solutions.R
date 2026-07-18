# STAT452 Chapter 4: Logistic Regression and Classification
# Dataset: mtcars. Response am is automatic (0) or manual (1).

data(mtcars)
cars <- transform(mtcars, transmission=factor(am, levels=c(0,1),
                                      labels=c("automatic","manual")))

# 1. Why not linear regression for a binary response?
linear_binary <- lm(am ~ wt + hp, data=cars)
range(predict(linear_binary))
plot(cars$wt, cars$am, pch=19, ylab="am (0=automatic, 1=manual)", xlab="wt")

# 2. Fit logistic regression by maximum likelihood.
logit_fit <- glm(transmission ~ wt + hp, data=cars,
                 family=binomial(link="logit"))
summary(logit_fit)
exp(coef(logit_fit))                 # odds ratios
confint.default(logit_fit)           # Wald intervals

# 3. Convert log-odds to probabilities and classify.
prob_manual <- predict(logit_fit, type="response")
predicted <- ifelse(prob_manual >= 0.5, "manual", "automatic")
table(observed=cars$transmission, predicted=predicted)
mean(predicted == cars$transmission)

# 4. Thresholds and confusion-matrix measures.
classification_metrics <- function(prob, truth, threshold=0.5) {
  pred <- factor(ifelse(prob >= threshold, "manual", "automatic"),
                 levels=levels(truth))
  tab <- table(observed=truth, predicted=pred)
  accuracy <- sum(diag(tab))/sum(tab)
  sensitivity <- tab["manual","manual"] / sum(tab["manual",])
  specificity <- tab["automatic","automatic"] / sum(tab["automatic",])
  c(accuracy=accuracy, sensitivity=sensitivity, specificity=specificity)
}
classification_metrics(prob_manual, cars$transmission, 0.5)
classification_metrics(prob_manual, cars$transmission, 0.3)

# 5. Training/test split and threshold sweep.
set.seed(452)
test <- sample(seq_len(nrow(cars)), 8)
train_fit <- glm(transmission ~ wt + hp, data=cars[-test,], family=binomial)
test_prob <- predict(train_fit, newdata=cars[test,], type="response")
classification_metrics(test_prob, cars$transmission[test], 0.5)
thresholds <- seq(0.05, 0.95, by=0.05)
metrics <- t(sapply(thresholds, function(th)
  classification_metrics(prob_manual, cars$transmission, th)))
plot(1-metrics[,"specificity"], metrics[,"sensitivity"], type="b",
     xlab="False-positive rate", ylab="True-positive rate")

# 6. Compare nested logistic models.
null_fit <- glm(transmission ~ 1, data=cars, family=binomial)
anova(null_fit, logit_fit, test="Chisq")
AIC(null_fit, logit_fit)

