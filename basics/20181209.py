# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 10:43:24 2018

@author: Sergio

pearson for correlation in continuous variables, 
cramer for correlation in categorical variables
"""

from scipy import stats
import numpy as np
import matplotlib.pyplot as plt 

#PEARSON

def plot(a,b):
    gradient, intercept, r_value, p_value, std_err = stats.linregress(a,b)
    mn=np.min(a)
    mx=np.max(a)
    a1=np.linspace(mn,mx,500)
    b1=gradient*a1+intercept
    plt.plot(a,b,'ob')
    plt.plot(a1,b1,'-r')
    plt.show()

a = [3,4,5,6,7,8]
b = [9,10,11,12,13,14]
print(stats.pearsonr(a,b)) 
plot(a,b)

a = [3,4,5,6,7,8]
b = np.random.rand(6)
print(stats.pearsonr(a,b)) 
plot(a,b)

a = np.random.rand(100)
b = np.random.rand(100)
print(stats.pearsonr(a,b)) 
plot(a,b)

a = [3,4,5,6,7,8]
b = [12,11,27,31,39,51]
print(stats.pearsonr(a,b)) 
plot(a,b)

a = [3,4,5,6,7,8]
b = [121,32,82,9,-15,-33]
print(stats.pearsonr(a,b)) 
plot(a,b)

#CRAMER
import statsmodels.api as sm
anes96 = sm.datasets.anes96
df_anes96 = anes96.load_pandas().data
df_anes96.head()
print(anes96.DESCRLONG)
print(anes96.NOTE)

df_anes96.corr()
df_anes96["selfLR"].corr(df_anes96["educ"])

