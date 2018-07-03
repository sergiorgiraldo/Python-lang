# Import libraries
import pandas as pd
import numpy as np
from sklearn import linear_model
from scipy import stats
import matplotlib.pyplot as plt

# Get training data from 2011-2015 to train the logistic regression model

# Initialize arrays to hold training data
train_num_hits = np.empty([0, 1])
train_win_label = np.empty([0, 1])

# Loop
for year in range(2011, 2016):
    # Construct log file name
    log_file = "GL" + str(year) + ".TXT"

    # Read log into a dataframe
    df = pd.read_table(log_file, sep=",", header=None)

    # Rename columns for readability
    df.rename(columns = {6: 'Home Team', 9: 'Runs Visitor', 10: 'Runs Home', 50: 'Hits Home'}, inplace=True)

    # Add new columns to indicate whether home team or visiting team won the game
    df['Home Win'] = (df['Runs Home'] > df['Runs Visitor'])

    # Add to training set
    train_num_hits = np.vstack([train_num_hits, df['Hits Home'].values.reshape([-1, 1])])
    train_win_label = np.vstack([train_win_label, df['Home Win'].values.reshape([-1, 1])])

# Instantiate logistic regression object
log_regr = linear_model.LogisticRegression()

# Fit model to training data
log_regr.fit(train_num_hits, train_win_label.ravel())

print("Slope = ", float(log_regr.coef_), " Intercept = ", float(log_regr.intercept_))

#Get performance score
log_regr_score_train = log_regr.score(train_num_hits, train_win_label.ravel())
print("Percentage correct on training set = ", 100. * log_regr_score_train, "%")

# Estimate the probability of home team winning the game as a function of number
# of hits from the training data
hits_range = np.arange(np.min(train_num_hits), np.max(train_num_hits))
prob_est_train_data = np.zeros([len(hits_range), 1])
for hits in hits_range:
    index = np.where(train_num_hits == hits)
    if len(index[0]) > 0:
        prob_est_train_data[int(hits - np.min(train_num_hits))] = np.sum(train_win_label[index[0]]) / len(index[0])

# Get the probabilities as estimated by the model
prob_est_model = log_regr.predict_proba(train_num_hits)

# Plot and visualize input and estimated probabilities
plt.plot(hits_range, prob_est_train_data, 'bs', label="Training data")
plt.plot(train_num_hits, prob_est_model[:, 1], 'ro', label="Model fit")
plt.plot([0, 30], [0.5, 0.5], "k--")
plt.plot([7.89, 7.89], [-0.1, 1.1], "k--")
plt.ylim([-0.1, 1.1])
plt.legend(loc="lower right")
plt.xlabel("Number of hits")
plt.ylabel("Probability of win for home team")
plt.show()
