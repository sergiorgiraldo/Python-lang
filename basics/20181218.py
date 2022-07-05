# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 13:44:37 2018

@author: sgiraldo

keras

"""

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
import numpy
import pandas as pd

# fix random seed for reproducibility
numpy.random.seed(7)
# load pima indians dataset
dataset = numpy.loadtxt("pima-indians-diabetes.csv", delimiter=",", skiprows=1)

# split into input (X) and output (Y) variables
X = dataset[:,0:8]
Y = dataset[:,8]

# create model
model = Sequential()
model.add(Dense(8, input_dim=8, activation='relu'))
model.add(Dense(8, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# Compile model
model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
# Fit the model
model.fit(X, Y, epochs=200, batch_size=10, verbose=2)
# evaluate the model
scores = model.evaluate(X, Y)

# calculate predictions
predictions = model.predict(X, verbose=2)
# round predictions
rounded = [round(x[0]) for x in predictions]

#summary
print("\n**********EVALUATION**********")
print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))

print("**********PREDICTION**********")
print(rounded)
