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

result = spark.sql(
    """SELECT player_id, pretty_name, date_of_birth, position, foot,height_in_cm,
    market_value_in_gbp,highest_market_value_in_gbp
    FROM players"""
)

print("Número de rows: ", result.count())
result.show()

training = result.filter(result.market_value_in_gbp.isNotNull())
print("Número de rows: ", training.count())
training.show()

test = result.filter(result.market_value_in_gbp.isNull())
print("Número de rows: ", test.count())
test.show()

from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.feature import IndexToString, StringIndexer, VectorIndexer
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# Load and parse the data file, converting it to a DataFrame.
data = result

# Index labels, adding metadata to the label column.
# Fit on whole dataset to include all labels in index.
labelIndexer = StringIndexer(
    inputCol="market_value_in_gbp", outputCol="market_value_in_gbp_prediction"
).fit(data)

# Automatically identify categorical features, and index them.
# Set maxCategories so features with > 4 distinct values are treated as continuous.
featureIndexer = VectorIndexer(
    inputCol="features", outputCol="indexedFeatures", maxCategories=4
).fit(data)

# Split the data into training and test sets (30% held out for testing)
(trainingData, testData) = data.randomSplit([0.7, 0.3])

# Train a RandomForest model.
rf = RandomForestClassifier(
    labelCol="indexedLabel", featuresCol="indexedFeatures", numTrees=10
)

# Convert indexed labels back to original labels.
labelConverter = IndexToString(
    inputCol="prediction", outputCol="predictedLabel", labels=labelIndexer.labels
)

# Chain indexers and forest in a Pipeline
pipeline = Pipeline(stages=[labelIndexer, featureIndexer, rf, labelConverter])

# Train model.  This also runs the indexers.
model = pipeline.fit(trainingData)

# Make predictions.
predictions = model.transform(testData)

# Select example rows to display.
predictions.select("predictedLabel", "label", "features").show(5)

# Select (prediction, true label) and compute test error
evaluator = MulticlassClassificationEvaluator(
    labelCol="indexedLabel", predictionCol="prediction", metricName="accuracy"
)
accuracy = evaluator.evaluate(predictions)
print("Test Error = %g" % (1.0 - accuracy))

rfModel = model.stages[2]
print(rfModel)  # summary only
