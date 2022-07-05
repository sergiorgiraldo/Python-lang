# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 19:55:46 2018

@author: Sergio
"""

def v(what):
    print(what, "\n")

import numpy as np
import pylab
import matplotlib.pyplot as plt

#3x + y = 7
#x + 2y = 4


#2x+y+z=7
#3x-4y +5z=-8
#x+y+z=6
c = np.array([[2,1,1], [3,-4,5], [1,1,1]])
d = np.array([7,-8, 6])
e = np.linalg.solve(c, d)
v(e)

#4x^3+3x^2−2x+10=0
ppar = [4, 3, -2, 10]
v(np.roots(ppar))

#y = 3x^2 + 1
p = np.poly1d([3, 0, 1]) #coefs from ax^2 + bx + c
derivative = np.polyder(p)
v(derivative)
integral = np.polyint(p)
v(integral)
pylab.plot(p)

xvals = np.arange(-2, 1, 0.01) # Grid of 0.01 spacing from -2 to 10
newyvals = 1 - 0.5 * xvals**2 # Evaluate quadratic approximation on xvals
plt.plot(xvals, newyvals, 'r--') # Create line plot with red dashed line
plt.xlabel('Input')
plt.ylabel('Function values')
plt.show() # Show the figure (remove the previous instance)

xvals = np.arange(-5, 5, 0.1) # Grid of 0.1 spacing from -5 to 5
newyvals = -8 - 2 * xvals + xvals**2 # Evaluate quadratic approximation on xvals
fig, ax = plt.subplots()
ax.plot(xvals, newyvals, 'r--') # Create line plot with red dashed line
ax.spines['left'].set_position('zero')
ax.spines['bottom'].set_position('zero')
ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')

xvals = np.arange(-8, 8, 1) 
newyvals = 2 * xvals + 4 
fig, ax = plt.subplots()
ax.plot(xvals, newyvals, 'r--') # Create line plot with red dashed line
ax.spines['left'].set_position('zero')
ax.spines['bottom'].set_position('zero')
ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
