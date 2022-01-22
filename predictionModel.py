from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.functions import col, abs

from pyspark.ml.regression import DecisionTreeRegressor
from pyspark.ml.feature import VectorIndexer

spark = SparkSession.builder.master("local[*]").getOrCreate()

players = spark.read.csv(
    "./output/prediction_df.csv",
    header=True,
    inferSchema=True,
    sep=",",
)
rows = [
    'country_of_citizenship',
    'date_of_birth',
    'position',
    'sub_position',
    'foot',
    'height_in_cm',
    "total_goals",
    "g/g",
    "y/g",
    "r/g",
    "m/g",
    "total_assists",
    "a/g",
    "g/s",]
players.createOrReplaceTempView("players2")
no_marketvalue = players.filter(players.market_value_in_gbp.isNull())
have_marketvalue = players.filter(players.market_value_in_gbp.isNotNull())
# players.select("pretty_name", "market_value_in_gbp", "highest_market_value_in_gbp").show()
# no_marketvalue.select("pretty_name", "market_value_in_gbp", "highest_market_value_in_gbp").show()
# have_marketvalue.select("pretty_name", "market_value_in_gbp", "highest_market_value_in_gbp").show()
# clean = players.dropna()
clean = have_marketvalue.dropna()
print(have_marketvalue.count())
print(clean.count())

# Turn Strings into indexes
indexers = [StringIndexer(inputCol=column, outputCol=column + "_index").fit(players) for column in list(set([
    'country_of_citizenship',
    'date_of_birth',
    'position',
    'sub_position',
    'foot']))]

# apply to df
pipeline = Pipeline(stages=indexers)
df_r = pipeline.fit(clean).transform(clean)

# vectorize features
vectorAssembler = VectorAssembler(inputCols = [
    'country_of_citizenship_index',
    'date_of_birth_index',
    'position_index',
    'sub_position_index',
    'foot_index',
    'height_in_cm',
    "total_goals",
    "g/g",
    "y/g",
    "r/g",
    "m/g",
    "total_assists",
    "a/g",
    "g/s"], outputCol = 'features')
df_vec = vectorAssembler.transform(df_r)
df_vec.select(['features', 'market_value_in_gbp']).show(3)

splits = df_vec.randomSplit([0.9, 0.1])
train_df = splits[0]
test_df = splits[1]

# Train LinearRegression
lr = LinearRegression(featuresCol = 'features', labelCol='market_value_in_gbp')
lr_model = lr.fit(train_df)
print("Coefficients: " + str(lr_model.coefficients))
print("Intercept: " + str(lr_model.intercept))

print("--- Training ---")
trainingSummary = lr_model.summary
print("RMSE: %f" % trainingSummary.rootMeanSquaredError)
print("r2: %f" % trainingSummary.r2)

print("--- Test ---")
lr_predictions = lr_model.transform(test_df)
lr_predictions = lr_predictions.withColumn("difference", abs(col("market_value_in_gbp") - col("prediction")))
lr_predictions.select("pretty_name", "prediction","market_value_in_gbp", "difference","features").show(5)
lr_evaluator = RegressionEvaluator(predictionCol="prediction", \
                 labelCol="market_value_in_gbp",metricName="r2")
print("R Squared (R2) on test data = %g" % lr_evaluator.evaluate(lr_predictions))

test_result = lr_model.evaluate(test_df)
print("Root Mean Squared Error (RMSE) on test data = %g" % test_result.rootMeanSquaredError)

lr_predictions.describe(["difference"]).show()

lr_predictions.agg({'difference': 'mean'}).show()
quantiles = lr_predictions.approxQuantile("difference", [0.25, 0.5, 0.75], 0.2)
print(quantiles)

# clean_players = players.dropna(subset=rows)
# clean_players_index = pipeline.fit(clean_players).transform(clean_players)
# clean_players_vec = vectorAssembler.transform(clean_players_index)
# players2withPredictions = lr_model.transform(clean_players_vec)
# players2withPredictions.toPandas().to_csv("output/{}.csv".format("players2_predicted"), index=False)