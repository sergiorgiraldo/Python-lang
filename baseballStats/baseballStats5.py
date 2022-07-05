# Import libraries
import pandas as pd
import numpy as np
from sklearn import linear_model
from scipy import stats
import matplotlib.pyplot as plt

# Read log into a dataframe
df = pd.read_table("GL2015.TXT", sep=",", header=None)

# Rename columns for readability
# Input type: dataframe
# Output type: dataframe
def rename_cols(df):
    df.rename(columns = {7: 'Home League', 9: 'Runs Visitor', 10: 'Runs Home'}, inplace=True)
    return df

# Invoke function to rename columns
df = rename_cols(df)

# Compute total runs per game
# Input type: dataframe
# Output type: dataframe
def compute_runs_per_game(df):
    df['Total Runs'] = (df['Runs Visitor'] + df['Runs Home'])
    return df

# Invoke function to compute runs per game
df = compute_runs_per_game(df)

# Compute means runs/game by league (for the entire season)
# Input type: dataframe
# Output type: series
def compute_mean_runs_per_game(df):
    mean_per_league = df.groupby(df['Home League'])['Total Runs'].mean()
    return mean_per_league

# Invoke function to compute mean runs/game by league
mean_runs_by_league = compute_mean_runs_per_game(df)

# Extract runs for AL and NL
# Input type: dataframe
# Output type: series, series
def get_runs_by_league(df):
    index_NL = np.where(df['Home League'] == "NL")
    runs_NL = df.iloc[index_NL[0]]['Total Runs'].values.reshape([len(index_NL[0]), 1])
    index_AL = np.where(df['Home League'] == "AL")
    runs_AL = df.iloc[index_AL[0]]['Total Runs'].values.reshape([len(index_AL[0]), 1])
    return runs_AL, runs_NL

# Invoke function to get runs by league on a game by game basis
runs_per_game_AL, runs_per_game_NL = get_runs_by_league(df)

# Calculate number of runs per game for AL and NL

# Initialize
runs_NL = np.empty([0, 1])
runs_AL = np.empty([0, 1])
mean_NL = np.empty([0, 1])
mean_AL = np.empty([0, 1])

# Loop over seasons
for year in range(2011, 2017):
    # Construct log file name
    log_file = "GL" + str(year) + ".TXT"

    # Read log into a dataframe
    df = pd.read_table(log_file, sep=",", header=None)

    # Rename columns for readability
    df = rename_cols(df)

    # Compute total runs per game
    df = compute_runs_per_game(df)

    # Compute runs/game for each league for the entire season
    mean_per_league = compute_mean_runs_per_game(df)
    mean_AL = np.append(mean_AL, mean_per_league[0])
    mean_NL = np.append(mean_NL, mean_per_league[1])

    # Extract runs for NL and AL on a game-by-game basis
    runs_per_game_AL, runs_per_game_NL = get_runs_by_league(df)
    runs_AL = np.append(runs_AL, runs_per_game_AL)
    runs_NL = np.append(runs_NL, runs_per_game_NL)

print("Mean and std. dev. runs/game NL (2011-2016): ", np.mean(runs_NL), " ", np.std(runs_NL))
print("Mean and std. dev. runs/game AL (2011-2016): ", np.mean(runs_AL), " ", np.std(runs_AL))

# Plot seasonal means by league
plt.plot(range(2011, 2017), mean_AL, 'r-o', label="AL")
plt.plot(range(2011, 2017), mean_NL, 'b-o', label="NL")
plt.xlabel("Year")
plt.ylabel("Runs / game")
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)
plt.legend()
plt.show()

# Run Mann-Whitney U test
mwu_output = stats.mannwhitneyu(runs_NL, runs_AL)
print("p-value = ", mwu_output.pvalue, " U = ", mwu_output.statistic)