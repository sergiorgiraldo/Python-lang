# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 09:22:10 2018

@author: sgiraldo
"""

import numpy as np

x = np.array([3,2])
y = np.array([5,1])
z = x + y
print(z)
x = np.array([1,2,3])
y = np.array([-7,8,9])
dot = np.dot(x,y)
print(np.dot(x,y))
x_modulus = np.sqrt((x*x).sum())
y_modulus = np.sqrt((y*y).sum())
cos_angle = dot / x_modulus / y_modulus # cosine of angle between x and y
angle = np.arccos(cos_angle)
print(angle)
angleDg = angle * 360 / 2 / np.pi # angle in degrees
print(angleDg)
x = np.array( ((2,3), (3, 5)) )
y = np.array( ((1,2), (5, -1)) )
x * y
x = np.matrix( ((2,3), (3, 5)) )
y = np.matrix( ((1,2), (5, -1)) )
x * y
x = np.array( ((2,3), (3, 5)) )
y = np.matrix( ((1,2), (5, -1)) )
np.dot(x,y)
np.mat(x) * np.mat(y)
x = np.array([0,0,1])
y = np.array([0,1,0])
np.cross(x,y)
np.cross(y,x)

"""
Let's assume there are four people, and we call them Lucas, Mia, Leon and Hannah. 
Each of them has bought chocolates out of a choice of three. 
The brand are A, B and C, not very marketable, we have to admit. 
Lucas bought 100 g of brand A, 175 g of brand B and 210 of C. Mia choose 90 g of A, 160 g of B and 150 g of C. 
Leon bought 200 g of A, 50 of B and 100 g of C. 
Hannah apparently didn't like brand B, because she hadn't bought any of those. 
But she she seems to be a real fan of brand C, because she bought 310 g of them. Furthermore she bought 120 g of A.

So, what's the price in Euro of these chocolates: A costs 2.98 per 100 g, B costs 3.90 and C only 1.99 Euro.
"""

NumPersons = np.array([[100,175,210],[90,160,150],[200,50,100],[120,0,310]])
Price_per_100_g = np.array([2.98,3.90,1.99])
Price_in_Cent = np.dot(NumPersons,Price_per_100_g)
Price_in_  Euro = Price_in_Cent / np.array([100,100,100,100])
Price_in_Euro

