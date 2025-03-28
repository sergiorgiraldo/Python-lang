# Create your first MLP in Keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
import numpy
# fix random seed for reproducibility
numpy.random.seed(7)
# load pima indians dataset
dataset = numpy.loadtxt("pima-indians-diabetes.csv", delimiter=",")
# split into input (X) and output (Y) variables
X = dataset[:,0:8]
Y = dataset[:,8]

# create model
model = Sequential()
model.add(Dense(12, input_dim=8, activation='relu'))
model.add(Dense(8, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# Compile model
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
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