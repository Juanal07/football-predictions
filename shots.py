from pyspark.sql import SparkSession
import sys

# import pandas as pd

spark = SparkSession.builder.master("local[*]").getOrCreate()

shots = spark.read.csv(
    "./data/FootballDatabase/shots.csv", header=True, inferSchema=True, sep=","
)
players = spark.read.csv(
    "./data/FootballDatabase/players.csv", header=True, inferSchema=True, sep=","
)
players.createOrReplaceTempView("players")
games = spark.read.csv(
    "./data/FootballDatabase/games.csv", header=True, inferSchema=True, sep=","
)
games.createOrReplaceTempView("games")

shooterID = sys.argv[1]  # Messi
print(shooterID)
# shooterID = 447  # De Bruyne
# shooterID = 564
# shooterID = 629  # Rooney
# shotType = "Head"
shotResult = "Goal"

result = shots.filter(shots["shooterID"] == shooterID)
# result = result.filter(shots["shotType"] == shotType)
result = result.filter(shots["shotResult"] == shotResult)
result.createOrReplaceTempView("shots")

result = spark.sql(
    """SELECT name, shooterID,date, shotResult, shotType, positionX, positionY FROM shots JOIN players on players.playerID=shots.shooterID JOIN games on games.gameID==shots.gameID"""
)

result.show()

name = "goals-test"
result.toPandas().to_csv("output/{}.csv".format(name))
