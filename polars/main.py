import pandas as pd
import polars as pl
import time

# download parquet from https://www.kaggle.com/datasets/chaudharypriyanshu/polars-20-vs-pandas-dataset-for-comparison?resource=download

print("\n# Loading Data Comparison")

start_time = time.time()
train_pd=pd.read_parquet('train.parquet') #Pandas dataframe
print("pandas df--- %s seconds ---" % (time.time() - start_time))

start_time = time.time()
train_pl=pl.read_parquet('train.parquet')
print("polars df--- %s seconds ---" % (time.time() - start_time))

print("\n# Aggregation Comparison- All columns- All Operation Together")

start_time = time.time()
nums=['num_7','num_8', 'num_9', 'num_10', 'num_11', 'num_12', 'num_13', 'num_14','num_15']
cats=['cat_1', 'cat_2', 'cat_3', 'cat_4', 'cat_5', 'cat_6']
train_pd[nums].agg(['min','max','mean','median','std'])
train_pd[cats].agg(['nunique'])
print("pandas --- %s seconds ---" % (time.time() - start_time))

start_time = time.time()
nums=['num_7','num_8', 'num_9', 'num_10', 'num_11', 'num_12', 'num_13', 'num_14','num_15']
cats=['cat_1', 'cat_2', 'cat_3', 'cat_4', 'cat_5', 'cat_6']
train_pl.select(
    [pl.col(col).min().alias(f"{col}_min") for col in nums] +
    [pl.col(col).max().alias(f"{col}_max") for col in nums] +
    [pl.col(col).mean().alias(f"{col}_mean") for col in nums] +
    [pl.col(col).median().alias(f"{col}_median") for col in nums] +
    [pl.col(col).std().alias(f"{col}_std") for col in nums]
)
train_pl.select(
    [pl.col(col).n_unique().alias(f"{col}_nunique") for col in cats]
)
print("polars --- %s seconds ---" % (time.time() - start_time))

print("\n# Comparing Min calculation time taken- single columns")

start_time = time.time()
print(train_pd['num_7'].agg(['min']))
print("pandas "+str((time.time() - start_time)))

start_time = time.time()
print(train_pl.select(pl.min("num_7")))
print("polars "+str((time.time() - start_time)))

print("\n# Comparing Median calculation time taken- single columns¶")

start_time = time.time()
print(train_pd['num_7'].agg(['median']))
print("pandas "+str((time.time() - start_time)))

start_time = time.time()
print(train_pl.select(pl.median("num_7")))
print("polars "+str((time.time() - start_time)))

print("\n# Comparing Mean calculation time taken- single columns¶")

start_time = time.time()
print(train_pd['num_7'].agg(['mean']))
print("pandas "+str((time.time() - start_time)))

start_time = time.time()
print(train_pl.select(pl.mean("num_7")))
print("polars "+str((time.time() - start_time)))

print("\n# Comparing Std calculation time taken- single columns¶")

start_time = time.time()
print(train_pd['num_7'].agg(['std']))
print("pandas "+str((time.time() - start_time)))

start_time = time.time()
print(train_pl.select(pl.std("num_7")))
print("polars "+str((time.time() - start_time)))

print("\n# Comparing Nunique calculation time taken- single columns¶")

start_time = time.time()
print(train_pd['cat_1'].agg(['nunique']))
print("pandas "+str((time.time() - start_time)))

start_time = time.time()
print(train_pl.select(pl.n_unique("cat_1")))
print("polars "+str((time.time() - start_time)))

print("\n# Comparing Min calculation time taken- many columns at once¶")

start_time = time.time()
print(train_pd[nums].agg(['min']))
print("pandas "+str((time.time() - start_time)))

start_time = time.time()
print(train_pl.select(pl.min(nums)))
print("polars "+str((time.time() - start_time)))

print("\n# Comparing Median calculation time taken- many columns at once¶")

start_time = time.time()
print(train_pd[nums].agg(['median']))
print("pandas "+str((time.time() - start_time)))

start_time = time.time()
print(train_pl.select(pl.median(nums)))
print("polars "+str((time.time() - start_time)))

print("\n# Comparing Mean calculation time taken- many columns at once¶")

start_time = time.time()
print(train_pd[nums].agg(['mean']))
print("pandas "+str((time.time() - start_time)))

start_time = time.time()
print(train_pl.select(pl.mean(nums)))
print("polars "+str((time.time() - start_time)))

print("\n# Comparing Std calculation time taken- many columns at once¶")

start_time = time.time()
print(train_pd[nums].agg(['std']))
print("pandas "+str((time.time() - start_time)))

start_time = time.time()
t=train_pl.select(pl.std(nums))
print(t)
print("polars "+str((time.time() - start_time)))

print("\n# Comparing Nunique calculation time taken- many columns at once¶")

start_time = time.time()
print(train_pd[cats].agg(['nunique']))
print("pandas "+str((time.time() - start_time)))

start_time = time.time()
print(train_pl.select(pl.n_unique(cats)))
print("polars "+str((time.time() - start_time)))

print("\n# Filtering and Selection operations¶")

start_time = time.time()
train_pd[train_pd['num_8']<=10][cats].nunique()
print("pandas "+str((time.time() - start_time)))

start_time = time.time()
train_pl.filter(pl.col("num_8") <= 10).select(pl.col(cats).n_unique())
print("polars "+str((time.time() - start_time)))

start_time = time.time()
train_pd[train_pd['cat_1']==1][nums].mean()
print("pandas "+str((time.time() - start_time)))

start_time = time.time()
train_pl.filter(pl.col("cat_1") == 1).select(pl.col(nums).mean())
print("polars "+str((time.time() - start_time)))

print("\n# Grouping Operations Comparison¶")
nums=['num_7','num_8', 'num_9', 'num_10', 'num_11', 'num_12', 'num_13', 'num_14','num_15']
cats=['cat_1', 'cat_2', 'cat_3', 'cat_4', 'cat_5', 'cat_6']

print("\n# Pandas numpy Functions")
start_time = time.time()
Function_1= train_pd.groupby(['user'])['cat_1'].agg('count')   #Function 1
print("pandas "+str((time.time() - start_time)))
start_time = time.time()
Function_2= train_pd.groupby(['user'])['num_7'].agg('mean')    #Function 2
print("pandas "+str((time.time() - start_time)))
start_time = time.time()
Function_3= train_pd.groupby(['user'])[nums].agg('mean')       #Function 3
print("pandas "+str((time.time() - start_time)))
start_time = time.time()
Function_4= train_pd.groupby(['user'])[cats].agg('count')      #Function 4
print("pandas "+str((time.time() - start_time)))

print("\n# Polars Functions")

start_time = time.time()
Function_1= train_pl.groupby('user').agg(pl.col('cat_1').count()) #Function 1
print("polars "+str((time.time() - start_time)))
start_time = time.time()
Function_2= train_pl.groupby('user').agg(pl.col('num_7').mean())  #Function 2
print("polars "+str((time.time() - start_time)))
start_time = time.time()
Function_3= train_pl.groupby('user').agg(pl.col(nums).mean())     #Function 3
print("polars "+str((time.time() - start_time)))
start_time = time.time()
Function_4= train_pl.groupby('user').agg(pl.col(cats).count())    #Function 4
print("polars "+str((time.time() - start_time)))

print("\n# Sorting Operation Comparison¶")

cols=['user','num_8'] # columns to be used for sorting

start_time = time.time()
train_pd.sort_values(by=cols,ascending=True)
print("pandas "+str((time.time() - start_time)))

start_time = time.time()
train_pl.sort(cols,descending=False)
print("polars "+str((time.time() - start_time)))
