# 역화살표 표기법

import math

input_str = input() # ex: 2 <- 2 <- 2

X = [int(x.strip()) for x in input_str.split('<-')]
n = len(X)

x_r = [0] * n
current_power = X[-1]
x_r[-1] = current_power

for i in range(n - 2, -1, -1):
    current_power = X[i] ** current_power
    x_r[i] = current_power

x_d = [math.ceil(val / 2) for val in x_r]

r_xd = x_d[-1]
for i in range(n - 2, -1, -1):
    r_xd = x_d[i] ** r_xd

r_xr = x_r[0]
final_result = r_xr + r_xd

print("X:", X)
print("x_result:", x_r)
print("x_divide:", x_d)
print("R(x_r):", r_xr)
print("R(x_d):", r_xd)
print("Result:", final_result)