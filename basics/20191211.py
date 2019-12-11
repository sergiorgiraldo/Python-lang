# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 11:19:39 2019

@author: sgiraldo
"""

dict = {0: [0, 0, 0, 1, 4, 1, 0, 0, 4],
             1: [0, 1, 0, 1, 1, 4, 1, 1, 4],
             2: [2, 2, 2, 2, 2, 3, 3, 2],
             3: [3, 3, 2, 3, 2, 3, 3, 3],
             4: [0, 1, 4, 4, 4, 0, 1, 4, 4]}
y = []
for x in dict.values():
    if set(x) not in y:
        y.append(set(x))
print(y)