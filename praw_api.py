import json
import time
from typing import List

import praw
from praw.models.reddit.submission import Submission
from tqdm import tqdm

from data_models import RedditPost
from utils.file import File

config = File.read_yaml_file("configs/config.yml")

MAX_POST = 1500
# SUB_REDDIT_DOMAIN = ["technology", "science"]
SUB_REDDIT_DOMAIN = ["science"]

# Create a Reddit instance with your credentials
reddit = praw.Reddit(
    client_id=config["CLIENT_ID"],
    client_secret=config["CLIENT_SECRET"],
    user_agent=config["APP_NAME"],
)


def get_subreddit_posts(subreddit: List[Submission]) -> List:
    total_post_data = []
    for post in tqdm(subreddit):
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
        except Exception as e:
            print(f"Error occurs. Details: {e}")
        total_post_data.append(reddit_post.to_dict())

    return total_post_data


for domain in SUB_REDDIT_DOMAIN:
    total_post_data = []
    subreddit = reddit.subreddit(domain)

    # Get new posts
    new_posts_subreddit = subreddit.new(limit=MAX_POST)
    new_posts_data = get_subreddit_posts(new_posts_subreddit)
    File.write_json_file(new_posts_data, f"crawl_data/{domain}_data_new.json")

    # Get hot posts
    hot_posts_subreddit = subreddit.hot(limit=MAX_POST)
    hot_posts_data = get_subreddit_posts(hot_posts_subreddit)
    File.write_json_file(hot_posts_data, f"crawl_data/{domain}_data_hot.json")

    # Get top posts
    top_posts_subreddit = subreddit.top(limit=MAX_POST)
    top_posts_data = get_subreddit_posts(top_posts_subreddit)
    File.write_json_file(top_posts_data, f"crawl_data/{domain}_data_top.json")

    # Get rising posts
    rising_posts_subreddit = subreddit.rising(limit=MAX_POST)
    rising_posts_data = get_subreddit_posts(rising_posts_subreddit)
    File.write_json_file(rising_posts_data, f"crawl_data/{domain}_data_rising.json")
