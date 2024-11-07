from services.reddit_streaming_service import RedditStreamingService
from utils.file import File
from utils.logger import Logger

config = File.read_yaml_file("configs/reddit_config.yml")
logger = Logger("reddit_streaming", None)

subreddit_info = [
    {"NAME": "technology", "TOPIC": "reddit_technology"},
    {"NAME": "science", "TOPIC": "reddit_science"},
    {"NAME": "futurology", "TOPIC": "reddit_futurology"},
]
reddit_streaming = RedditStreamingService(config, logger)
reddit_streaming.run_streaming(subreddit_info)