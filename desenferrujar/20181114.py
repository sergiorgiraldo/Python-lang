import pandas as pd
import urllib.request
import zipfile
from pathlib import Path
from os import path

homeDir = str(Path.home())

#read file (from 20181113 recipe)
dataFilename = path.join(homeDir, 'gl2017.txt')
df = pd.read_table(dataFilename, sep=",", header=None)
df.rename(
        columns={3: 'Visiting Team',
                 4: 'Visiting Team League',
                 6: 'Home Team',
                 7: 'Home Team League',
                 9: 'Runs Visitor',
                 10: 'Runs Home'}, inplace=True)

#who won more, national or american league?
