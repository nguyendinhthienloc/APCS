getwd()
setwd('D:/STAT/Lab/Lab 4-20240610')
getwd()
data <- read.csv("Admission_Predict.csv",header = TRUE)
data
head(data) # print first 6 lines
attach(data)
plot(CGPA,Chance.of.Admit)
cor(CGPA,Chance.of.Admit)

model <- lm(Chance.of.Admit~CGPA)
model
summary(model) # y = Bo + B1x + error[i] 
               # error[i] ~ N(0,sigma^2)
               # sigma^2 = MSE
               # MSE = SSE/(n-2) (n-2):degree of freedom

# CI co hai loai: + E(Y|X0) du bao gia tri trung binh cua Y khi co X0 moi
#                 + Y|X0 du doan Y se nam trong khoang gia tri

# Tim CI 95% cho beta1,beta0
confint(model1, level = 0.95)
# test. H0: beta1 = 0.1 ; beta1 # 0.1
# Tinh T0, so sanh |T0| < t(n-2,1-alpha/2) -> Reject H0
# CGPA = 9.35, tim y_hat, CI. mu_Y, I alpha = 0.95
n <- nrow(data)
n
sumx <- sum(CGPA)
sumx
sumy <- sum(Chance.of.Admit)
sumy
sumxy <- sum(CGPA*Chance.of.Admit)
sumxy
sumx2 <- sum(CGPA^2)
sumx2
sumy2 <- sum(Chance.of.Admit^2)
sumy2
Sxx <- sumx2 - (sumx)^2/n
Sxy <- sumxy - sumx*sumy/n
B1_hat <- Sxy/Sxx
B1_hat
xbar <- mean(CGPA)
xbar
ybar <- mean(Chance.of.Admit)
ybar
B0_hat <- ybar - B1_hat*xbar
B0_hat
###
x_new <- data.frame(CGPA = 9.35)
prediction_interval <- predict(model, newdata = x_new, interval = "prediction", level = 0.95)
prediction_interval # predict Y_hat
confidence_interval <- predict(model, newdata = x_new, interval = "confidence", level = 0.95)
confidence_interval # predict mu_Y
###
auto <- read.csv("Auto.csv", header = TRUE)
attach(auto)
head(auto)
model2 <- lm(mpg~horsepower)
summary(model2)
# tuong quan, <2e-16 < alpha -> Reject H0 -> b1 # 0 -> co tuong quan
# tuong quan strong
# tuong quan negative
predict(model2,newdata = data.frame(horsepower=98),interval = "prediction",level = 0.95)
plot(horsepower,mpg)
abline(model2)
hist(model2$residuals,breaks=40)
qqnorm(model2$residuals)
