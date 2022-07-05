# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 14:48:47 2019

@author: sgiraldo
"""
print("##SIMPLE########################")
# simple scikit-learn k-fold cross-validation
from numpy import array
from sklearn.model_selection import KFold
# data sample
data = array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2])
# prepare cross validation
kfold = KFold(3, True, 1)
# enumerate splits
for train, test in kfold.split(data):
	print('train: %s, test: %s' % (data[train], data[test]))
    
print("##STRATIFIED########################")
#stratified cross-validation for regression
from sklearn.model_selection import StratifiedKFold 
from sklearn.model_selection import StratifiedKFold
import numpy as np

n_splits = 3

X = np.ones(10)
y = np.arange(1,11,dtype=float)
print(X)
print(y)

# binning to make StratifiedKFold work
yc = np.outer(y[::n_splits],np.ones(n_splits)).flatten()[:len(y)]
print(yc)
yc[-n_splits:]=yc[-n_splits]*np.ones(n_splits)

skf = StratifiedKFold(n_splits=n_splits)
for train, test in skf.split(X, yc):
    print("train: %s test: %s" % (train, test))   