import numpy as np
#3x + y = 9
#x + 2y = 8
a = np.array([[3,1], [1,2]])
b = np.array([9,8])
x = np.linalg.solve(a, b)
print(x)

#2x+y+z=7
#3x-4y +5z=-8
#x+y+z=6
a = np.array([[2,1,1], [3,-4,5], [1,1,1]])
b = np.array([7,-8, 6])
x = np.linalg.solve(a, b)
print(x)

#4x^3+3x^2−2x+10=0
ppar = [4, 3, -2, 10]
print(np.roots(ppar))

#y = 3x^2 + 1
p = np.poly1d([3, 0, 1]) #coefs from ax^2 + bx + c
derivative = np.polyder(p)
print(derivative)
integral = np.polyint(p)
print(integral)

