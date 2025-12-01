from pyspark.sql import SparkSession
from datetime import datetime

SILVER_PATH = "s3a://brandeis-grants-silver/"
GOLD_PATH = "s3a://brandeis-grants-gold/output.xml"



spark = (SparkSession.builder
         .appName("GoldETL")
         .master("local[*]")
         .getOrCreate())

df = spark.read.format("delta").load(SILVER_PATH)

# Convert rows to XML inside a <grants> wrapper
xml = df.toPandas().to_xml(root_name="grants", row_name="grant", index=False)

import boto3
s3 = boto3.client("s3")

bucket = "brandeis-grants-gold"

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
key = f"output_{ts}.xml"


s3.put_object(Bucket=bucket, Key=key, Body=xml)

print("Gold ETL Complete")

spark.stop()
