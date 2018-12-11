# -*- coding: utf-8 -*-
"""
Created on Tue Dec 11 13:37:17 2018

@author: sgiraldo

knn - classification problem

https://stackabuse.com/k-nearest-neighbors-algorithm-in-python-and-scikit-learn/
"""

import numpy as np  
import matplotlib.pyplot as plt  
import pandas as pd 

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"

# Assign colum names to the dataset
names = ['sepal-length', 'sepal-width', 'petal-length', 'petal-width', 'Class']

# Read dataset to pandas dataframe
dataset = pd.read_csv(url, names=names)  

#Preprocessing, split our dataset into its attributes and labels
X = dataset.iloc[:, :-1].values  
y = dataset.iloc[:, 4].values  

#split dataset
from sklearn.model_selection import train_test_split  
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)  

#feature scaling: scale the features so that all of them can be uniformly evaluated
from sklearn.preprocessing import StandardScaler  
scaler = StandardScaler()  
scaler.fit(X_train)

X_train = scaler.transform(X_train)  
X_test = scaler.transform(X_test)  

#training and prediction
from sklearn.neighbors import KNeighborsClassifier  
classifier = KNeighborsClassifier(n_neighbors=5)  
classifier.fit(X_train, y_train)  
y_pred = classifier.predict(X_test)  

#evaluate
from sklearn.metrics import classification_report, confusion_matrix  
print(confusion_matrix(y_test, y_pred))  #true negatives, false negatives, true positives
print(classification_report(y_test, y_pred))  

##plotting the mean error for the predicted values of test set for all the K values between 1 and 40.
error = []

# Calculating error for K values between 1 and 40
for i in range(1, 40):  
    knn = KNeighborsClassifier(n_neighbors=i)
    knn.fit(X_train, y_train)
    pred_i = knn.predict(X_test)
    #sanitycheck
    if (i == 10):
        print(pred_i)
        print(y_test)
    error.append(np.mean(pred_i != y_test))

print(error) #sanitycheck
    
plt.figure(figsize=(12, 6))  
plt.plot(range(1, 40), error, color='red', linestyle='dashed', marker='o',  
         markerfacecolor='blue', markersize=10)
plt.title('Error Rate K Value')  
plt.xlabel('K Value')  
plt.ylabel('Mean Error')  
