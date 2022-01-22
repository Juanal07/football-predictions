from pyspark.sql import SparkSession

# import pandas as pd

spark = SparkSession.builder.master("local[*]").getOrCreate()

players = spark.read.csv(
    "./data/FootballDataFromTransfermarkt/players.csv",
    header=True,
    inferSchema=True,
    sep=",",
)
players.createOrReplaceTempView("players")
appearances = spark.read.csv(
    "./data/FootballDataFromTransfermarkt/appearances.csv",
    header=True,
    inferSchema=True,
    sep=",",
)
appearances.createOrReplaceTempView("appearances")
games = spark.read.csv(
    "./data/FootballDataFromTransfermarkt/games.csv",
    header=True,
    inferSchema=True,
    sep=",",
)
games.createOrReplaceTempView("games")

df = spark.sql(
    """SELECT player_id, pretty_name, date_of_birth,country_of_citizenship,
    position,sub_position, foot,height_in_cm,
    market_value_in_gbp,highest_market_value_in_gbp
    FROM players"""
)
df.createOrReplaceTempView("df")
result = spark.sql(
    """SELECT player_id, total_goals, total_goals/games as `g/g`, yellow_cards/games as `y/g`, red_cards/games as `r/g`,
    minutes_played/games as `m/g`,assists as total_assists, assists/games as `a/g`,games from
    (select player_id, sum(goals) as total_goals, count(game_id) as games, sum(yellow_cards) as yellow_cards,
    sum(red_cards) as red_cards, sum(minutes_played) as minutes_played, sum(assists) as assists
    FROM appearances GROUP BY player_id)"""
)
result.createOrReplaceTempView("result")
result2 = spark.sql(
    """select player_id, count(distinct season) as seasons from (SELECT player_id, season
    FROM appearances JOIN games ON appearances.game_id=games.game_id) group by player_id order by seasons desc
    """
)
result2.createOrReplaceTempView("result2")
df = spark.sql(
    """SELECT df.player_id, pretty_name, date_of_birth,country_of_citizenship,
    position, sub_position,
    foot,height_in_cm, market_value_in_gbp,highest_market_value_in_gbp,
    total_goals,`g/g`,
    `y/g`,`r/g`,`m/g`,total_assists, `a/g`, games/seasons as `g/s`
    FROM df JOIN result ON df.player_id=result.player_id JOIN result2 ON df.player_id=result2.player_id"""
)
# df.createOrReplaceTempView("df")
df.show()
print("Número de rows: ", df.count())
name = "prediction_df"
df.toPandas().to_csv("output/{}.csv".format(name))
