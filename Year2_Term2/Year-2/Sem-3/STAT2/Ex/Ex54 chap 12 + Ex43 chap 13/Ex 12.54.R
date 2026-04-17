library(Devore7)
x <- c(22.5, 22.8, 22.8, 23.3, 23.3, 24.4, 25.0, 25.0, 25.0, 25.0, 26.0, 26.0, 26.8, 28.2)
y <- c(158, 155, 156, 160, 161, 162, 164, 166, 167, 170, 166, 173, 178, 174)
model <- lm(y~x)
summary(model)
s_xx <- 36.463571
s_xy <- 137.60
B_1 <- s_xy/s_xx
B_1
sum_x <- 346.1
sum_y <- 2310
n <- 14
x_bar <- sum_x/n
y_bar <- sum_y/n
B_0 <- y_bar - B_0*x_bar
B_0

s_yy <- 626.00
SSE <- s_yy - B_1*s_xy
SSE
R_square <- 1-SSE/s_yy
R_square
summary(model)
anova(model)

x0 <- 23
s_y_hat <- sqrt(1/n+(x0-x_bar)^2/s_xx)
t <- qt(0.025,n-2,lower.tail = FALSE)
y_hat <- B_0 + B_1*x0
se_residual <- sqrt(SSE/(n-2))
s_y_hat <- se_residual*sqrt(1/n + (x0-x_bar)^2/s_xx)
PI <- c(y_hat-t*sqrt(s_y_hat^2+se_residual^2),y_hat+t*sqrt(s_y_hat^2+se_residual^2))
PI

x0 <- 25
s_y_hat <- sqrt(1/n+(x0-x_bar)^2/s_xx)
t <- qt(0.025,n-2,lower.tail = FALSE)
y_hat <- B_0 + B_1*x0
se_residual <- sqrt(SSE/(n-2))
s_y_hat <- se_residual*sqrt(1/n + (x0-x_bar)^2/s_xx)
PI <- c(y_hat-t*sqrt(s_y_hat^2+se_residual^2),y_hat+t*sqrt(s_y_hat^2+se_residual^2))
PI
