from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[*]").getOrCreate()

players = spark.read.csv(
    "./data/FootballDatabase/players.csv",
    header=True,
    inferSchema=True,
    sep=",",
)
players.createOrReplaceTempView("players1")

players = spark.read.csv(
    "./data/FootballDataFromTransfermarkt/players.csv",
    header=True,
    inferSchema=True,
    sep=",",
)
players.createOrReplaceTempView("players2")

players = spark.read.csv(
    "./data/FootballPlayersMarketValuePrediction/Final.csv",
    header=True,
    inferSchema=True,
    sep=";",
)
players.createOrReplaceTempView("players3")

# spark.sql("""select * from players1""").show()
# spark.sql("""select * from players2""").show()
# spark.sql("""select * from players3""").show()

result = spark.sql(
    """SELECT players1.playerID, players1.name, players2.country_of_birth,players2.date_of_birth, year(now())-year(date_of_birth) as age, position, foot, `Market Value` 
    FROM players1 INNER JOIN players2 ON players1.name=players2.pretty_name FULL OUTER JOIN players3 ON players1.name=players3.Player ORDER BY players1.playerID ASC"""
)
# TODO:
# normalizar csv,codificacion
# que no se añadan jugadores del 2o dataset
# eliminar repetidos usando la edad

print("Número de rows: ", result.count())
result.show()


name = "result"
result.toPandas().to_csv("output/{}.csv".format(name))