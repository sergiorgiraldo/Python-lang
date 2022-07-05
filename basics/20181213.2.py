# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 09:37:24 2018

@author: sgiraldo

naive bayes from scikit learn
https://www.kaggle.com/baiazid/pima-indians-diabetes-na-ve-bayes

"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.feature_selection import VarianceThreshold
import matplotlib.pyplot as plt
import seaborn as sns
%matplotlib inline

dataset = pd.read_csv('pima-indians-diabetes.csv')
dataset.columns = [
    "NumTimesPrg", "PlGlcConc", "BloodP",
    "SkinThick", "TwoHourSerIns", "BMI",
    "DiPedFunc", "Age", "HasDiabetes"]
print(dataset.describe())

# Check the shape of the data: we have 768 rows and 9 columns:
# the first 8 columns are features while the last one
# is the supervised label (1 = has diabetes, 0 = no diabetes)
dataset.shape

# Visualise a table with the first rows of the dataset, to
# better understand the data format
dataset.head()

#visualizations
corr = dataset.corr()
corr
sns.heatmap(corr, annot = True)

dataset.hist(bins=50, figsize=(20, 15))
plt.show()

#data cleaning and transformation

#check columns with zero values
dataset.columns[(dataset == 0).any()] #'NumTimesPrg', 'PlGlcConc', 'BloodP', 'SkinThick', 'TwoHourSerIns','BMI'

#check columns with null values
dataset.columns[(dataset.isnull()).any()] #none

# Calculate the median value for BMI
median_bmi = dataset['BMI'].median()
# Substitute it in the BMI column of the
# dataset where values are 0
dataset['BMI'] = dataset['BMI'].replace(
    to_replace=0, value=median_bmi)

# Calculate the median value for BloodP
median_bloodp = dataset['BloodP'].median()
# Substitute it in the BloodP column of the
# dataset where values are 0
dataset['BloodP'] = dataset['BloodP'].replace(
    to_replace=0, value=median_bloodp)

# Calculate the median value for PlGlcConc
median_plglcconc = dataset['PlGlcConc'].median()
# Substitute it in the PlGlcConc column of the
# dataset where values are 0
dataset['PlGlcConc'] = dataset['PlGlcConc'].replace(
    to_replace=0, value=median_plglcconc)

# Calculate the median value for SkinThick
median_skinthick = dataset['SkinThick'].median()
# Substitute it in the SkinThick column of the
# dataset where values are 0
dataset['SkinThick'] = dataset['SkinThick'].replace(
    to_replace=0, value=median_skinthick)

# Calculate the median value for TwoHourSerIns
median_twohourserins = dataset['TwoHourSerIns'].median()
# Substitute it in the TwoHourSerIns column of the
# dataset where values are 0
dataset['TwoHourSerIns'] = dataset['TwoHourSerIns'].replace(
    to_replace=0, value=median_twohourserins)

#split the dataset in 80% / 20%
train_set, test_set = train_test_split(
    dataset, test_size=0.2, random_state=42)

# Separate labels from the rest of the dataset
train_set_labels = train_set["HasDiabetes"].copy()
train_set = train_set.drop("HasDiabetes", axis=1)

test_set_labels = test_set["HasDiabetes"].copy()
test_set = test_set.drop("HasDiabetes", axis=1)

# Apply a scaler
scaler = StandardScaler()
scaler.fit(train_set)
train_set_scaled = scaler.transform(train_set)
test_set_scaled = scaler.transform(test_set)

df = pd.DataFrame(data=train_set_scaled)
df.head()

# Prepare the configuration to run the test
seed = 7

classifier = GaussianNB()
classifier.fit(train_set_scaled, train_set_labels)

#predict
test_set_pred = classifier.predict(test_set_scaled)

#evaluate
cm = confusion_matrix(test_set_labels, test_set_pred)
print (cm)
print("F1: {:.2%}".format(f1_score(test_set_labels, test_set_pred)))
print("Accuracy: {:.2%}".format(accuracy_score(test_set_labels, test_set_pred)))
