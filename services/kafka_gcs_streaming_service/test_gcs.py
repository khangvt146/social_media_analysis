import os

from pyspark import SparkConf
from pyspark.sql import DataFrame, SparkSession

conf = (
    SparkConf()
    .setAppName("Social_Media_Analysis")
    .setMaster("spark://172.29.15.3:7077")
    .set("spark.executor.instances", "4")
    .set("spark.executor.cores", "4")
    .set("spark.executor.memory", "16g")
    .set("spark.cores.max", "8")
)
spark = (
    SparkSession.builder.config(conf=conf)
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.4",
    )
    .config(
        "spark.jars",
        "https://repo1.maven.org/maven2/com/google/cloud/bigdataoss/gcs-connector/3.0.0/gcs-connector-3.0.0-shaded.jar",
    )
    .config("spark.hadoop.google.cloud.auth.service.account.enable", "true")
    .config(
        "spark.hadoop.google.cloud.auth.service.account.json.keyfile",
        "/home/hduser/Khang/social_media/configs/khang_vo_services_account.json",
    )
    .config(
        "fs.gs.impl",
        "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
    )
    .config(
        "fs.AbstractFileSystem.gs.impl",
        "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
    )
    .config("fs.gs.auth.type", "SERVICE_ACCOUNT_JSON_KEYFILE")
    .config("spark.hadoop.mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")
    .getOrCreate()
)
sc = spark.sparkContext
# Example DataFrame
# data = [("Alice", 1), ("Bob", 2), ("Carol", 3)]
# columns = ["Name", "ID"]
# df = spark.createDataFrame(data, columns)
df = spark.read.format("parquet").load("file:///home/hduser/Khang/social_media/tmpfb6geh2x")

# Specify the GCS bucket path
output_path = "gs://khangvt16_data_bucket/test_data"

# Write DataFrame to GCS
# df.coalesce(1).write.mode("append").format("parquet").option(
#     "compression", "snappy"
# ).save(output_path)
df.write.mode("append").format("parquet").partitionBy(
    "platform", "year", "month", "day", "topic"
).save(output_path)

# Stop Spark session
spark.stop()
