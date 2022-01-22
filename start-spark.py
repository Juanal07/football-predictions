from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.functions import col, abs


# import pandas as pd

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

# Turn Strings into indexes
indexers = [StringIndexer(inputCol=column, outputCol=column + "_index").fit(players) for column in list(set([
    'country_of_birth',
    'country_of_citizenship',
    'date_of_birth',
    'position',
    'sub_position',
    'foot',
    'height_in_cm']))]

# apply to df
pipeline = Pipeline(stages=indexers)
clean = players.dropna()
df_r = pipeline.fit(clean).transform(clean)

# vectorize features
vectorAssembler = VectorAssembler(inputCols = [
    'country_of_birth_index',
    'country_of_citizenship_index',
    'date_of_birth_index',
    'position_index',
    'sub_position_index',
    'foot_index',
    'height_in_cm_index'], outputCol = 'features')
df_vec = vectorAssembler.transform(df_r)
df_vec.select(['features', 'highest_market_value_in_gbp']).show(3)

splits = df_vec.randomSplit([0.7, 0.3])
train_df = splits[0]
test_df = splits[1]

# Train LinearRegression
lr = LinearRegression(featuresCol = 'features', labelCol='highest_market_value_in_gbp')
lr_model = lr.fit(train_df)
print("Coefficients: " + str(lr_model.coefficients))
print("Intercept: " + str(lr_model.intercept))

print("--- Training ---")
trainingSummary = lr_model.summary
print("RMSE: %f" % trainingSummary.rootMeanSquaredError)
print("r2: %f" % trainingSummary.r2)

print("--- Test ---")
lr_predictions = lr_model.transform(test_df)
lr_predictions = lr_predictions.withColumn("difference", abs(col("highest_market_value_in_gbp") - col("prediction")))
lr_predictions.select("pretty_name", "prediction","highest_market_value_in_gbp", "difference","features").show(5)
lr_evaluator = RegressionEvaluator(predictionCol="prediction", \
                 labelCol="highest_market_value_in_gbp",metricName="r2")
print("R Squared (R2) on test data = %g" % lr_evaluator.evaluate(lr_predictions))

test_result = lr_model.evaluate(test_df)
print("Root Mean Squared Error (RMSE) on test data = %g" % test_result.rootMeanSquaredError)

lr_predictions.agg({'difference': 'mean'}).show()

quit()

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
