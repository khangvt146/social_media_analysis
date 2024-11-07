import json
import threading

import praw
from kafka import KafkaProducer
from kafka.producer.future import FutureRecordMetadata

from services.reddit_streaming_service import RedditPost
from utils.logger import Logger


class RedditStreamingService:
    """
    Class for streaming subreddit data and publishing to Kafka Brokers.
    """

    def __init__(self, config: dict, logger: Logger) -> None:
        self.config = config
        self.logger = logger

        # Create a Reddit instance with credentials
        self.reddit = praw.Reddit(
            client_id=self.config["REDDIT"]["CLIENT_ID"],
            client_secret=self.config["REDDIT"]["CLIENT_SECRET"],
            user_agent=self.config["REDDIT"]["APP_NAME"],
        )

        # Initialize Kafka Producer
        self.producer = KafkaProducer(
            bootstrap_servers=self.config["KAFKA"]["BROKER_URL"],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            retries=3,
            acks="all",  # Ensure all replicas acknowledge to increase reliability
            linger_ms=1000,  # Batch messages for a short interval
            compression_type="gzip",  # Compress to reduce network usage
        )

    def _on_send_success(self, metadata: FutureRecordMetadata, msg: str) -> None:
        # Handle successful message send
        self.logger.info(
            f"Topic: {metadata.topic} | Partition: {metadata.partition} | Offset: {metadata.offset} | Messages: {msg}"
        )

    def _on_send_error(self, exc):
        # Handle error in sending message
        self.logger.error(f"Failed to send message: {exc}")

    def _publish_message(self, data: dict, topic: str) -> None:
        """
        Publish data retrieved from API to the Kafka Broker.

        Parameters:
            - data (dict): The extracted data in dictionary format.
            - topic (str): The name of Kafka Topic to be published data.
        """
        record: FutureRecordMetadata = self.producer.send(topic=topic, value=data)
        record.add_callback(self._on_send_success, msg=data["title"])
        record.add_errback(self._on_send_error)
        self.producer.flush()

    def _streaming_subreddit(self, subreddit_name: str, topic: str) -> None:
        """
        Stream data from a specified subreddit by creating a WebSocket using the PRAW API.

        Paramerters:
            - subreddit_name (str): The subreddit name to retrieve data.
            - topic (str): The name of Kafka topic
        """
        self.logger.info(f"Start streaming process from subreddit {subreddit_name}")

        stream_subreddit = self.reddit.subreddit(subreddit_name)
        try:
            for post in stream_subreddit.stream.submissions(skip_existing=True):
                # Print basic information about each post
                author = post.author
                author_name = author.name if author else None
                try:
                    reddit_post = RedditPost(
                        id=post.id,
                        name=post.name,
                        author=author_name,
                        title=post.title,
                        created_utc=post.created_utc,
                        selftext=post.selftext,
                        permalink=post.permalink,
                        url=post.url,
                        is_original_content=post.is_original_content,
                        is_self=post.is_self,
                        is_spoiler=post.spoiler,
                        is_locked=post.locked,
                        is_stickied=post.stickied,
                        is_over_18=post.over_18,
                        # link_flair_template_id=post.link_flair_template_id,
                        link_flair_text=post.link_flair_text,
                        num_comments=post.num_comments,
                        num_crossposts=post.num_crossposts,
                        num_reports=post.num_reports,
                        score=post.score,
                        ups=post.ups,
                        downs=post.downs,
                        upvote_ratio=post.upvote_ratio,
                    )
                    self._publish_message(reddit_post.to_dict(), topic)
                except Exception as e:
                    self.logger.error(
                        f"An error occurs in process submission data. Details: {e}"
                    )
                    continue
        except Exception as e:
            self.logger.error(f"An error occurred in streaming sockets: {e}")
            self.producer.close()
            raise Exception(e)

        self.producer.close()

    def run_streaming(self, req_subreddit: list) -> None:
        """
        Start streaming subreddit process.

        """
        threads = []
        for subreddit_info in req_subreddit:
            thread = threading.Thread(
                target=self._streaming_subreddit,
                args=(
                    subreddit_info["NAME"],
                    subreddit_info["TOPIC"],
                ),
            )
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()
