import json

from kafka import KafkaProducer
from kafka.producer.future import FutureRecordMetadata

from utils.logger import Logger


class StackExchangeKafkaProducer:
    """
    Class for publish data to Kafka Brokers.
    """

    def __init__(self, config: dict, logger: Logger) -> None:
        self.logger = logger
        self.config = config

        # Initialize Kafka Producer
        self.producer = KafkaProducer(
            bootstrap_servers=self.config["KAFKA"]["BROKER_URL"],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            retries=3,
            acks="all",  # Ensure all replicas acknowledge to increase reliability
            linger_ms=1000,  # Batch messages for a short interval
            compression_type="gzip",  # Compress to reduce network usage
            batch_size=131072,  # 128KB
        )

    def _on_send_success(self, metadata: FutureRecordMetadata, msg: str) -> None:
        # Handle successful message send
        self.logger.info(
            f"Topic: {metadata.topic} | Partition: {metadata.partition} | Offset: {metadata.offset} | Messages: {msg}"
        )

    def _on_send_error(self, exc):
        # Handle error in sending message
        self.logger.error(f"Failed to send message: {exc}")

    def publish_message(self, data_list: list, topic: str) -> None:
        """
        Publish data retrieved from API to the Kafka Broker.

        Parameters:
            - data_list (list): The extracted data in list format.
            - topic (str): The name of Kafka Topic to be published data.

        """
        for item in data_list:
            try:
                record: FutureRecordMetadata = self.producer.send(
                    topic=topic, value=item
                )
                record.add_callback(self._on_send_success, msg=item["title"])
                record.add_errback(self._on_send_error)

            except Exception as e:
                self.logger.error(f"Error in publish message to Kafka. Details: {e}")
                continue

        self.producer.flush()
        self.producer.close()
