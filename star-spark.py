from pyspark.sql import SparkSession

# import pandas as pd

spark = SparkSession.builder.master("local[*]").getOrCreate()
