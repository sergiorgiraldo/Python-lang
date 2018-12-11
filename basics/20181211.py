# -*- coding: utf-8 -*-
"""
Created on Tue Dec 11 13:37:17 2018

@author: sgiraldo

knn - classification problem

https://stackabuse.com/k-nearest-neighbors-algorithm-in-python-and-scikit-learn/
https://www.kaggle.com/lalitharajesh/iris-dataset-exploratory-data-analysis
"""

import numpy as np  
import matplotlib.pyplot as plt  
import pandas as pd 
from sklearn.datasets import load_iris

#get data
iris = load_iris()

#plot
# The indices of the features that we are plotting
x_index = 0
y_index = 1

# this formatter will label the colorbar with the correct target names
formatter = plt.FuncFormatter(lambda i, *args: iris.target_names[int(i)])

plt.figure(figsize=(5, 4))
plt.scatter(iris.data[:, x_index], iris.data[:, y_index], c=iris.target)
plt.colorbar(ticks=[0, 1, 2], format=formatter)
plt.xlabel(iris.feature_names[x_index])
plt.ylabel(iris.feature_names[y_index])

plt.tight_layout()
plt.show()
#**********************************

#Preprocessing, tranasforma to panda and split our dataset into its attributes and labels
dataset = pd.DataFrame(iris.data)
dataset.columns = iris.feature_names
dataset['CLASS'] = iris.target
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
