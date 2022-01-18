from pyspark.sql import SparkSession

# import pandas as pd

spark = SparkSession.builder.master("local[*]").getOrCreate()

# players = spark.read.csv(
#     "./data/FootballDatabase/players.csv",
#     header=True,
#     inferSchema=True,
#     sep=",",
# )
# players.createOrReplaceTempView("players")
#
# name = "players"
# players.toPandas().to_csv("output/{}.csv".format(name))
