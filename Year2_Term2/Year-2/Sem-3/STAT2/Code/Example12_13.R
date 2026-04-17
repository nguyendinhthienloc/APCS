# Load dataset from Devore7 library
library(Devore7)
data("xmp12.13")
attach(xmp12.13)
dim(xmp12.13)
head(xmp12.13)
x

#y=xmp12.13$y # strength (MPa) 
#x=xmp12.13$x #carbonation depth (mm)

plot(x,y, xlab="carbonation depth (mm)", ylab="strength (MPa)")

mod13=lm(y~x)
summary(mod13)
anova(mod13)

#####confidence intervals for β_0 and β_1
confint(mod13)
confint(mod13, level = 0.96)
#confint(stop_dist_model, level = 0.99)

#####Confidence interval for the mean response
new_x = data.frame(x= 52)
predict(mod13, newdata = new_x,interval = c("confidence"))

 new_x = data.frame(x = c(45, 35))
 predict(mod13, newdata = new_x,interval = c("confidence"))
 #predict(mod13, newdata = new_x,interval = c("confidence"), level = 0.99)

#####Prediction Interval for New Observations
predict(mod13, newdata = new_x,  interval = c("prediction"))

#####Confidence and Prediction Bands
depth = seq(min(x), max(x), by = 0.01)
strength_CI_band = predict(mod13, 
                       newdata = data.frame(x = depth), 
                       interval = "confidence", level = 0.95)
strength_PI_band = predict(mod13, 
                       newdata = data.frame(x = depth), 
                       interval = "prediction", level = 0.95) 
plot(y ~ x, data = xmp12.13,
     xlab = "carbonation depth (mm)", 
     ylab = "strength (MPa)",
     main = "Y= 27.18294 - 0.29756x with R^2=76.56% ",
     pch  = 20,cex  = 2,col  = "grey",
     ylim = c(min(strength_PI_band), max(strength_PI_band)))
abline(mod13, lwd = 3, col = "darkorange")
lines(depth, strength_CI_band[,"lwr"], col = "dodgerblue", lwd = 3, lty = 1)
lines(depth, strength_CI_band[,"upr"], col = "dodgerblue", lwd = 3, lty = 1)
lines(depth, strength_PI_band[,"lwr"], col = "dodgerblue", lwd = 3, lty = 3)
lines(depth, strength_PI_band[,"upr"], col = "dodgerblue", lwd = 3, lty = 3)
points(mean(x), mean(y), pch = "*", cex = 2, col="red")
legend(51, 33, legend=c("Regression", "95% CI","95% PI"),
       col=c("darkorange", "dodgerblue", "dodgerblue"), lty=c(1,1,3), cex=0.7)


