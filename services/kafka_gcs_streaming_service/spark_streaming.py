import os
from glob import glob

from pyspark import SparkConf, SparkFiles
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    coalesce,
    col,
    create_map,
    dayofmonth,
    from_json,
    lit,
    month,
    struct,
    to_json,
    year,
)
from pyspark.sql.streaming import StreamingQueryListener

from utils.logger import Logger


class KafkaToGcsStreaming:
    """
    Streaming data from Kafka Topics and push to Google Cloud Storage (GCS)
    using Spark Streaming.

    """

    def __init__(self, config: dict, logger: Logger) -> None:
        self.config = config
        self.logger = logger

    def _init_spark_job(self) -> None:
        """
        Initialize Spark Session for Streaming Task.
        """
        jars_file = self._get_jar_files(self.config["SPARK"]["JARS_FOLDER_PATH"])
        conf = (
            SparkConf()
            .setAppName("Kafka_To_GCS_Streaming")
            .setMaster(f"spark://{self.config['SPARK']['HOSTNAME']}")
            .set("spark.executor.instances", "4")
            .set("spark.executor.cores", "8")
            .set("spark.executor.memory", "8g")
            .set("spark.cores.max", "8")
            .set("spark.submit.deployMode", "client")
        )
        self.spark = (
            SparkSession.builder.config(conf=conf)
            # .config(
            #     "spark.jars.packages",
            #     "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.4",
            # )
            .config("spark.jars", jars_file)
            # Config GCS connector
            .config("spark.hadoop.fs.gs.auth.type", "SERVICE_ACCOUNT_JSON_KEYFILE")
            .config(
                "spark.hadoop.fs.gs.auth.service.account.json.keyfile",
                self.config["GCS"]["SERVICES_ACCOUNT_PATH"],
            )
            .config(
                "spark.hadoop.fs.gs.impl",
                "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
            )
            .config(
                "spark.hadoop.fs.AbstractFileSystem.gs.impl",
                "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
            )
            .config(
                "spark.hadoop.mapreduce.fileoutputcommitter.marksuccessfuljobs", "false"
            )
            .getOrCreate()
        )

    def _get_jar_files(self, jars_folder: str) -> str:
        """
        Get all dependency JARs files for the Spark Streaming pipeline.

        Parameters:
            jars_folder (str): The path to the folder containing all JAR files.

        Returns:
            str: A string containing the paths of all dependency JAR files,
        """
        jar_files = ",".join(glob(f"{os.getcwd()}/{jars_folder}/*.jar"))
        return jar_files

    def _write_minibatch_to_gcs(self, batch_df: DataFrame, batch_id: str) -> None:
        """
        Write each mini-batch to GCS using gcs-connector.
        """
        gcs_path = self.config["GCS"]["BUCKET_PATH"]

        batch_df.write.mode("append").format("parquet").option(
            "compression", "snappy"
        ).partitionBy("platform", "year", "month", "day", "topic").save(gcs_path)

        self.logger.info(f"Batch ID: {batch_id} | Writing data to GCS successful.")

    def start_streaming(self, listener: StreamingQueryListener = None) -> None:
        """
        Start the streaming pipeline that consume data from Kafka Topics and push
        data to Google Cloud Storage (GCS).
        """
        self._init_spark_job()

        if listener:
            self.spark.streams.addListener(listener)

        # Define Source Data (Kafka Topics)
        kafka_topics = ",".join(self.config["KAFKA"]["TOPIC"])
        kafka_stream = (
            self.spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", self.config["KAFKA"]["BROKERS"])
            .option("subscribe", kafka_topics)
            .option("startingOffsets", "earliest")
            .option("maxOffsetsPerTrigger", "2000")  # Number of messages per batch
            .load()
        )

        # Transform Source Data
        mapping_platform_page = {
            "stack_over_flow": "stack_exchange_data",
            "ai_stack_exchange": "stack_exchange_data",
            "ask_ubuntu_stack_exchange": "stack_exchange_data",
            "devops_stack_exchange": "stack_exchange_data",
            "software_engineering_stack_exchange": "stack_exchange_data",
            "data_science_stack_exchange": "stack_exchange_data",
            "security_stack_exchange": "stack_exchange_data",
            "database_administrator_stack_exchange": "stack_exchange_data",
            "super_user_stack_exchange": "stack_exchange_data",
            "reddit_futurology": "reddit_data",
            "reddit_science": "reddit_data",
            "reddit_technology": "reddit_data",
        }

        kafka_df = kafka_stream.selectExpr(
            "CAST(key AS STRING)",
            "CAST(value AS STRING)",
            "topic",
            "partition",
            "offset",
            "timestamp",
        )

        # Mapping Platform Page for partition data
        mapping_expr = create_map(
            [lit(x) for pair in mapping_platform_page.items() for x in pair]
        )
        kafka_df = kafka_df.withColumn(
            "platform",
            coalesce(mapping_expr[col("topic")], lit("unknow_topic")),
        )

        kafka_df = (
            kafka_df.withColumn("year", year("timestamp"))
            .withColumn("month", month("timestamp"))
            .withColumn("day", dayofmonth("timestamp"))
        )
        kafka_df = kafka_df.withColumnRenamed("timestamp", "timestamp_utc")

        # Write data to GCS
        query = (
            kafka_df.writeStream.foreachBatch(self._write_minibatch_to_gcs)
            .option(
                "checkpointLocation",
                f"file://{os.getcwd()}/{self.config['SPARK']['CHECKPOINT_PATH']}",
            )
            .trigger(processingTime="10 minute")
            .start()
        )
        # Keep the stream running
        query.awaitTermination()
