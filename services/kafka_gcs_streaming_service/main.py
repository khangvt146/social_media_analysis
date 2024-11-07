from services.kafka_gcs_streaming_service import (
    KafkaToGcsQueryListener,
    KafkaToGcsStreaming,
)
from utils.file import File
from utils.logger import Logger

config = File.read_yaml_file("configs/kafka_gcs_streaming.yml")
logger = Logger("kafka_gcs_streaming", None)

listener = KafkaToGcsQueryListener(logger)

spark_streaming = KafkaToGcsStreaming(config, logger)
spark_streaming.start_streaming(listener)