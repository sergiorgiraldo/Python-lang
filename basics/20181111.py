import os
import urllib.request
import pandas as pd

# use `urllib` download files from Earth Lab figshare repository

# download .csv containing monthly average precipitation for Boulder, CO
urllib.request.urlretrieve(url = "https://ndownloader.figshare.com/files/12710618",
                            filename = "avg-precip-months-seasons.csv")

# print message that data downloads were successful
print("datasets downloaded successfully")

avg_precip = pd.read_csv("avg-precip-months-seasons.csv")

# print the type for the pandas dataframe
print(type(avg_precip))

# print the values in the pandas dataframe
print(avg_precip)