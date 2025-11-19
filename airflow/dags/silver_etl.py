from pyspark.sql import SparkSession
from delta import *

BRONZE_PATH = "s3a://brandeis-grants-bronze/"
SILVER_PATH = "s3a://brandeis-grants-silver/"

spark = (SparkSession.builder
         .appName("SilverETL")
         .master("local[*]")
         .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
         .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
         .getOrCreate())

bronze = spark.read.format("delta").load(BRONZE_PATH)

# Basic dedupe logic — keep the row with the highest award_amount
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, col

window = Window.partitionBy("award_id").orderBy(col("award_amount").desc())

silver = (bronze
          .withColumn("rn", row_number().over(window))
          .filter("rn = 1")
          .drop("rn"))

silver.write.format("delta").mode("overwrite").save(SILVER_PATH)

print("Silver ETL Complete")

spark.stop()
