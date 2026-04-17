# Load dataset from Devore7 library
library(Devore7)

data("xmp12.06")
attach(xmp12.06)
head(xmp12.06)
dim(xmp12.06)

xmp12.06

plot(filtrate,moistcon)
# linear model
mod = lm(moistcon ~ filtrate)
names(mod)
mod$coefficients
summary(mod)
anova(mod)
##return the coefficients
coef(mod) #  mod$coefficients

# return  residuals, and fitted values
Residual = mod$residuals # Residual = resid(mod)
(fit=fitted(mod) )#fit = predict(mod)

### s2_e  = sum(e^2) / (n - 2)
data =xmp12.06
fit=round(fit,digits=3)
Residual=round(Residual,digits=3)
restab=data.frame(data,fit, Residual)
restab

#add the fitted line to the scatterplot
plot(moistcon ~ filtrate,
     xlab = "filtration rate",
     ylab = "moisture content",
     main = "moisture content = y = 72.96 + 0.041 filtration rate  ",
     pch  = 20,
     cex  = 2,
     col  = "cadetblue2")
abline(mod, lwd = 3, col = "red")
