# Import libraries
import pandas as pd
import numpy as np
from sklearn import linear_model
from scipy import stats
import matplotlib.pyplot as plt

#datasets: http://www.retrosheet.org/gamelogs/index.html
#labels for the data set: http://www.retrosheet.org/gamelogs/glfields.txt
'''
Field(s)  Meaning
    1     Date in the form "yyyymmdd"
    2     Number of game:
             "0" -- a single game
             "1" -- the first game of a double (or triple) header
                    including seperate admission doubleheaders
             "2" -- the second game of a double (or triple) header
                    including seperate admission doubleheaders
             "3" -- the third game of a triple-header
             "A" -- the first game of a double-header involving 3 teams
             "B" -- the second game of a double-header involving 3 teams
    3     Day of week  ("Sun","Mon","Tue","Wed","Thu","Fri","Sat")
  4-5     Visiting team and league
    6     Visiting team game number
          For this and the home team game number, ties are counted as
          games and suspended games are counted from the starting
          rather than the ending date.
  7-8     Home team and league
    9     Home team game number
10-11     Visiting and home team score (unquoted)
   12     Length of game in outs (unquoted).  A full 9-inning game would
          have a 54 in this field.  If the home team won without batting
          in the bottom of the ninth, this field would contain a 51.
   13     Day/night indicator ("D" or "N")
   14     Completion information.  If the game was completed at a
          later date (either due to a suspension or an upheld protest)
          this field will include:
             "yyyymmdd,park,vs,hs,len" Where
          yyyymmdd -- the date the game was completed
          park -- the park ID where the game was completed
          vs -- the visitor score at the time of interruption
          hs -- the home score at the time of interruption
          len -- the length of the game in outs at time of interruption
          All the rest of the information in the record refers to the
          entire game.
   15     Forfeit information:
             "V" -- the game was forfeited to the visiting team
             "H" -- the game was forfeited to the home team
             "T" -- the game was ruled a no-decision
   16     Protest information:
             "P" -- the game was protested by an unidentified team
             "V" -- a disallowed protest was made by the visiting team
             "H" -- a disallowed protest was made by the home team
             "X" -- an upheld protest was made by the visiting team
             "Y" -- an upheld protest was made by the home team
          Note: two of these last four codes can appear in the field
          (if both teams protested the game).
   17     Park ID
   18     Attendance (unquoted)
   19     Time of game in minutes (unquoted)
20-21     Visiting and home line scores.  For example:
             "010000(10)0x"
          Would indicate a game where the home team scored a run in
          the second inning, ten in the seventh and didn't bat in the
          bottom of the ninth.
22-38     Visiting team offensive statistics (unquoted) (in order):
             at-bats
             hits
             doubles
             triples
             homeruns
             RBI
             sacrifice hits.  This may include sacrifice flies for years
                prior to 1954 when sacrifice flies were allowed.
             sacrifice flies (since 1954)
             hit-by-pitch
             walks
             intentional walks
             strikeouts
             stolen bases
             caught stealing
             grounded into double plays
             awarded first on catcher's interference
             left on base
39-43     Visiting team pitching statistics (unquoted)(in order):
             pitchers used ( 1 means it was a complete game )
             individual earned runs
             team earned runs
             wild pitches
             balks
44-49     Visiting team defensive statistics (unquoted) (in order):
             putouts.  Note: prior to 1931, this may not equal 3 times
                the number of innings pitched.  Prior to that, no
                putout was awarded when a runner was declared out for
                being hit by a batted ball.
             assists
             errors
             passed balls
             double plays
             triple plays
50-66     Home team offensive statistics
67-71     Home team pitching statistics
72-77     Home team defensive statistics
78-79     Home plate umpire ID and name
80-81     1B umpire ID and name
82-83     2B umpire ID and name
84-85     3B umpire ID and name
86-87     LF umpire ID and name
88-89     RF umpire ID and name
          If any umpire positions were not filled for a particular game
          the fields will be "","(none)".
90-91     Visiting team manager ID and name
92-93     Home team manager ID and name
94-95     Winning pitcher ID and name
96-97     Losing pitcher ID and name
98-99     Saving pitcher ID and name--"","(none)" if none awarded
100-101   Game Winning RBI batter ID and name--"","(none)" if none
          awarded
102-103   Visiting starting pitcher ID and name
104-105   Home starting pitcher ID and name
106-132   Visiting starting players ID, name and defensive position,
          listed in the order (1-9) they appeared in the batting order.
133-159   Home starting players ID, name and defensive position
          listed in the order (1-9) they appeared in the batting order.
  160     Additional information.  This is a grab-bag of informational
          items that might not warrant a field on their own.  The field 
          is alpha-numeric. Some items are represented by tokens such as:
             "HTBF" -- home team batted first.
             Note: if "HTBF" is specified it would be possible to see
             something like "01002000x" in the visitor's line score.
          Changes in umpire positions during a game will also appear in 
          this field.  These will be in the form:
             umpchange,inning,umpPosition,umpid with the latter three
             repeated for each umpire.
          These changes occur with umpire injuries, late arrival of 
          umpires or changes from completion of suspended games. Details
          of suspended games are in field 14.
  161     Acquisition information:
             "Y" -- we have the complete game
             "N" -- we don't have any portion of the game
             "D" -- the game was derived from box score and game story
             "P" -- we have some portion of the game.  We may be missing
                    innings at the beginning, middle and end of the game.
 
Missing fields will be NULL.
'''

input_df = pd.read_table("GL2015.TXT", sep=",", header=None)

# Method to rename columns of an input dataframe (for readability)
# Input type: dataframe
# Output type: dataframe
def rename_cols(input_df):
    input_df.rename(columns = {3: 'Visiting Team', 6: 'Home Team', 9: 'Runs Visitor', 10: 'Runs Home'}, inplace=True)
    return input_df

# Invoke function to rename columns
input_df = rename_cols(input_df)

# Method to add new columns to indicate whether home team or visiting team won the game
# Input type: dataframe
# Output type: dataframe
def add_new_cols(input_df):
    input_df['Home Win'] = (input_df['Runs Home'] > input_df['Runs Visitor'])
    input_df['Visitor Win'] = (input_df['Runs Visitor'] > input_df['Runs Home'])
    return input_df

# Method to group data by home team and compute relevant statistics
# Input type: dataframe
# Output type: dataframe (with stats grouped by home team)
def proc_home_team_data(input_df):

    # Group by home team
    home_group = input_df.groupby(input_df['Home Team'])

    # Compute stats: Number of games, runs scored, runs conceded, wins, run differential
    home_df = home_group[['Runs Visitor', 'Runs Home', 'Home Win']].apply(sum)
    home_df['Home Games'] = home_group['Home Win'].count()
    home_df.rename(columns = {'Runs Visitor': 'Runs by Visitor', 'Runs Home': 'Runs at Home', 'Home Win': 'Wins at Home'}, inplace=True)
    home_df['RD at Home'] = home_df['Runs at Home'] - home_df['Runs by Visitor']
    home_df.index.rename('Team', inplace=True)
    home_df.reset_index(inplace=True)

    return home_df

# Method to group data by visiting team and compute relevant statistics
# Input type: dataframe
# Output type: dataframe (with stats grouped by visiting team)
def proc_visiting_team_data(input_df):

    # Group by visiting team
    visit_group = input_df.groupby(input_df['Visiting Team'])

    # Compute stats: Number of games, runs scored, runs conceded, wins, run differential
    visit_df = visit_group[['Runs Visitor', 'Runs Home', 'Visitor Win']].apply(sum)
    visit_df['Road Games'] = visit_group['Visitor Win'].count()
    visit_df.rename(columns = {'Runs Visitor': 'Runs as Visitor', 'Runs Home': 'Runs by Home', 
                                 'Visitor Win': 'Wins as Visitor'}, inplace=True)
    visit_df['RD as Visitor'] = visit_df['Runs as Visitor'] - visit_df['Runs by Home']
    visit_df.index.rename('Team', inplace=True)
    visit_df.reset_index(inplace=True)

    return visit_df

# Method to merge dataframes with statistics grouped by home and visiting teams
# and to explicitly compute explanatory and response variables
# Input type: dataframe, dataframe
# Output type: dataframe
def merge_data_frames(home_df, visit_df):
    # Compute explanatory and response variables
    overall_df = home_df.merge(visit_df, how='outer', left_on='Team', right_on='Team')
    overall_df['RD'] = overall_df['RD at Home'] + overall_df['RD as Visitor']
    overall_df['Win Pct'] = (overall_df['Wins at Home'] + overall_df['Wins as Visitor']) / (overall_df['Home Games'] + overall_df['Road Games'])
    overall_df['Pythagorean expectation'] = 162 * (1 / (1 + np.power(
        (overall_df['Runs by Visitor'] + overall_df['Runs by Home'])/
        (overall_df['Runs as Visitor'] + overall_df['Runs at Home']), 1.83)))

    # Return dataframe with explanatory and response variables
    return overall_df

# Method to collate all data preprocessing steps
# Input type: dataframe
# Output type: dataframe
def extract_linear_reg_inputs(input_df):
    # Rename columns
    input_df = rename_cols(input_df)

    # Add new columns
    input_df = add_new_cols(input_df)

    # Group and process data by home team
    home_df = proc_home_team_data(input_df)

    # Group and process data by visiting team
    visit_df = proc_visiting_team_data(input_df)

    # Merge home and visitor dataframes
    overall_df = merge_data_frames(home_df, visit_df)

    return overall_df

# Get training data from 2011-2015 to train the linear regression model

# Initialize arrays to hold training data
train_run_diff = np.empty([0, 1])
train_win_pct = np.empty([0, 1])

# Loop
for year in range(2011, 2016):
    # Construct log file name
    log_file = "GL" + str(year) + ".TXT"

    # Read log into a dataframe
    df = pd.read_table(log_file, sep=",", header=None)

    # Extract relevant stats into another dataframe
    df_proc = extract_linear_reg_inputs(df)

    # Add to training set
    train_run_diff = np.vstack([train_run_diff, df_proc['RD'].values.reshape([-1, 1])])
    train_win_pct = np.vstack([train_win_pct, df_proc['Win Pct'].values.reshape([-1, 1])])    

 # Instantiate an object
lin_regr = linear_model.LinearRegression(fit_intercept=True)

# Compute model parameters with training data
lin_regr.fit(train_run_diff, train_win_pct)

# Access and display model parameters
print("Slope (a) = ", float(lin_regr.coef_), " Intercept (b) = ", float(lin_regr.intercept_))

# Get regression score (R-squared)
r_squared = lin_regr.score(train_run_diff, train_win_pct)
print("R-squared for linear fit = ", r_squared)

# Visualize
x_ax = np.array(range(int(np.min(train_run_diff)), int(np.max(train_run_diff)))).reshape(-1, 1)
y_ax = lin_regr.coef_ * x_ax + lin_regr.intercept_
plt.plot(train_run_diff, train_win_pct, 'bo', label="training_data")
plt.plot(x_ax, y_ax, 'r', label="model_fit")
plt.plot([-300, 300], [0.5, 0.5], "k--")
plt.plot([0, 0], [0.30, 0.65], "k--")
plt.ylim([0.30, 0.65])
plt.xlabel("Run differential")
plt.ylabel("Win percentage")
plt.legend(loc="lower right")
plt.show()

# Construct test dataset
log_file = "GL2016.TXT"
df = pd.read_table(log_file, sep=",", header=None)
df_proc = extract_linear_reg_inputs(df)
test_run_diff = df_proc['RD'].values.reshape([-1, 1])
test_win_pct = df_proc['Win Pct'].values.reshape([-1, 1])

# Predict outcomes using regression model
predict_win_pct = lin_regr.predict(test_run_diff)

# Compute percentage error for linear regression model on test set
mean_abs_error_test = np.mean(np.abs(predict_win_pct - test_win_pct))
print("Percentage error on test set = ", 100. * mean_abs_error_test, "%")

# Compute percentage error for linear regression model on training set
model_fit_train = lin_regr.predict(train_run_diff)
mean_abs_error_training = np.mean(np.abs(model_fit_train - train_win_pct))
print("Percentage error on training set ", 100. * mean_abs_error_training, "%")

# Visualize
plt.plot(test_win_pct, predict_win_pct, 'bo')
plt.plot([0.35, 0.7], [0.35, 0.7], 'r')
plt.xlabel("Actual win percentage")
plt.ylabel("Predicted win percentage")
plt.title("MLB 2016 season")
plt.show()


