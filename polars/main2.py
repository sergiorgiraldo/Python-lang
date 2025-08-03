import polars as pl
train = pl.read_parquet("train.parquet")
train2 = pl.read_parquet("train.parquet")
train3 = pl.read_parquet("train.parquet")

result = (train
    .join(train2, on="user", how="inner")
    # .join(train3, on="user", how="inner")
    .select([
        pl.col("cat_2").alias("train.cat_2"),
        pl.col("cat_2_right").alias("train2.cat_2"),
        # pl.col("cat_2_right_right").alias("train3.cat_2")
    ])
)

print(result)