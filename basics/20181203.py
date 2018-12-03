# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 15:20:22 2018

@author: sgiraldo
"""

import pandas as pd
import numpy as np

def v(what):
    print(what)
    print("\n")

url = 'https://raw.github.com/pandas-dev/pandas/master/pandas/tests/data/tips.csv'
tips = pd.read_csv(url)

v(tips.head())

# SELECT total_bill, tip, smoker, time
# FROM tips
# LIMIT 5;
v(tips[['total_bill', 'tip', 'smoker', 'time']].head(5))

#SELECT *
#FROM tips
#WHERE time = 'Dinner'
#LIMIT 5;
v(tips[tips['time'] == 'Dinner'].head(5))

is_dinner = tips['time'] == 'Dinner'
v(is_dinner.value_counts())
v(tips[is_dinner].head(5))
v(tips[~is_dinner].head(5)) #negate in pandas

#SELECT *
#FROM tips
#WHERE time = 'Dinner' AND tip > 5.00;
v(tips[(tips['time'] == 'Dinner') & (tips['tip'] > 5.00)].head(5))
v(tips[(is_dinner) & (tips['tip'] > 5.00)].head(5))

#SELECT *
#FROM tips
#WHERE size >= 5 OR total_bill > 45;
v(tips[(tips['size'] >= 5) | (tips['total_bill'] > 45)])

#SELECT sex, count(*)
#FROM tips
#GROUP BY sex;
v(tips.groupby('sex').size())
v(tips.groupby('sex').count())
v(tips.groupby('sex')['total_bill'].count())

#SELECT day, AVG(tip), COUNT(*)
#FROM tips
#GROUP BY day;
v(tips.groupby('day').agg({'tip': np.mean, 'day': np.size}))

#SELECT smoker, day, COUNT(*), AVG(tip)
#FROM tips
#GROUP BY smoker, day;
tips.groupby(['smoker', 'day']).agg({'tip': [np.size, np.mean]})

#SELECT * FROM tips
#ORDER BY tip DESC
#LIMIT 10 OFFSET 5;
v(tips.nlargest(10+5, columns='tip').tail(10))

#SELECT * FROM (
#  SELECT
#    t.*,
#    ROW_NUMBER() OVER(PARTITION BY day ORDER BY total_bill DESC) AS rn
#  FROM tips t
#)
#WHERE rn < 3
#ORDER BY day, rn;
v(tips.assign(rn=tips.sort_values(['total_bill'], ascending=False).groupby(['day']).cumcount() + 1).query('rn < 3').sort_values(['day','rn']))
v(tips.assign(rnk=tips.groupby(['day'])['total_bill'].rank(method='first', ascending=False)).query('rnk < 3').sort_values(['day','rnk']))    

#SELECT * FROM (
#  SELECT
#    t.*,
#    RANK() OVER(PARTITION BY sex ORDER BY tip) AS rnk
#  FROM tips t
#  WHERE tip < 2
#)
#WHERE rnk < 3
#ORDER BY sex, rnk;
v(tips[tips['tip'] < 2].assign(rnk_min=tips.groupby(['sex'])['tip'].rank(method='min')).query('rnk_min < 3').sort_values(['sex','rnk_min']))

#management

#UPDATE tips
#SET tip = tip*2
#WHERE tip < 2;
tips.loc[tips['tip'] < 2, 'tip'] *= 2

#DELETE FROM tips
#WHERE tip > 9;

tips = tips.loc[tips['tip'] <= 9] #notice the 'less than', we select what will remain

#joins
df1 = pd.DataFrame({'key': ['A', 'B', 'C', 'D'], 'value': np.random.randn(4)})
df2 = pd.DataFrame({'key': ['B', 'D', 'D', 'E'], 'value': np.random.randn(4)})

#INNER JOIN
#SELECT *
#FROM df1
#INNER JOIN df2
#  ON df1.key = df2.key;
v(pd.merge(df1, df2, on='key'))
indexed_df2 = df2.set_index('key')
v(pd.merge(df1, indexed_df2, left_on='key', right_index=True))  

#LEFT JOIN
#SELECT *
#FROM df1
#LEFT OUTER JOIN df2
#  ON df1.key = df2.key;
v(df1)
v(df2)
v(pd.merge(df1, df2, on='key', how='left'))

#RIGHT JOIN
#SELECT *
#FROM df1
#RIGHT OUTER JOIN df2
#  ON df1.key = df2.key;
v(df1)
v(df2)
v(pd.merge(df1, df2, on='key', how='right'))

#FULL JOIN
#SELECT *
#FROM df1
#FULL OUTER JOIN df2
#  ON df1.key = df2.key;
v(df1)
v(df2)
v(pd.merge(df1, df2, on='key', how='outer'))

#UNION
df1 = pd.DataFrame({'city': ['Chicago', 'San Francisco', 'New York City'],'rank': range(1, 4)})
df2 = pd.DataFrame({'city': ['Chicago', 'Boston', 'Los Angeles'],'rank': [1, 4, 5]})

#SELECT city, rank
#FROM df1
#UNION ALL
#SELECT city, rank
#FROM df2;
v(df1)
v(df2)
v(pd.concat([df1, df2]))

#SELECT city, rank
#FROM df1
#UNION
#SELECT city, rank
#FROM df2;
v(pd.concat([df1, df2]).drop_duplicates())

#null checking
frame = pd.DataFrame({'col1': ['A', 'B', np.NaN, 'C', 'D'], 'col2': ['F', np.NaN, 'G', 'H', 'I']})
v(frame)

#SELECT *
#FROM frame
#WHERE col2 IS NULL;
v(frame[frame['col2'].isna()])

#SELECT *
#FROM frame
#WHERE col1 IS NOT NULL;
frame[frame['col1'].notna()]


