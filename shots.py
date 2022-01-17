from pyspark.sql import SparkSession
import pandas as pd

spark = SparkSession.builder.master("local[*]").getOrCreate()

shots = spark.read.csv(
    "./FootballDatabase/shots.csv", header=True, inferSchema=True, sep=","
)
players = spark.read.csv(
    "./FootballDatabase/players.csv", header=True, inferSchema=True, sep=","
)
players.createOrReplaceTempView("players")

shooterID = 2097
shotType = "Head"
shotResult = "Goal"

result = shots.filter(shots["shooterID"] == shooterID)
result = result.filter(shots["shotType"] == shotType)
result = result.filter(shots["shotResult"] == shotResult)
result.createOrReplaceTempView("shots")

result = spark.sql(
    """SELECT name, shooterID, shotResult, shotType, positionX, positionY FROM shots JOIN players on players.playerID=shots.shooterID"""
)

result.show()

name = "goles-messi"
result.toPandas().to_csv("output/{}.csv".format(name))
