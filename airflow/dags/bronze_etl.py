from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, input_file_name, regexp_extract

RAW_PATH = "s3a://brandeis-grants/*/"
BRONZE_PATH = "s3a://brandeis-grants-bronze/"

spark = (SparkSession.builder
         .appName("BronzeETL")
         .master("local[*]")
         .config("spark.hadoop.fs.s3a.aws.credentials.provider",
                 "com.amazonaws.auth.EnvironmentVariableCredentialsProvider")
         .getOrCreate())

df = (spark.read
      .format("xml")
      .option("rowTag", "grant")
      .load(RAW_PATH))

df = (df
      .withColumn("ingest_ts", current_timestamp())
      .withColumn("source_file", input_file_name())
      .withColumn(
            "funder_folder",
            regexp_extract(input_file_name(), "brandeis-grants/([^/]+)/", 1)
      )
     )

df.write.format("delta").mode("overwrite").save(BRONZE_PATH)

print("Bronze ETL Complete")

spark.stop()
