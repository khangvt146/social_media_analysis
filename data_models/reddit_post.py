import json
from dataclasses import asdict, dataclass
from datetime import time
from typing import Optional


@dataclass
class RedditPost:
    """
    Reddit Post data class

        - id (str): ID of the submission (post).
        - author (str): The submission author's name.
        - created_utc (float): Time the submission was created (timestamp).
        - selftext (str): The submissions's selftext - an empty string if a link post.
        - permalink (str): A permalink for the submission.
        - url (str): The URL the submission links to, or the permalink if a selfpost.
        - is_original_content (bool): Whether or not the submission has been set as original content.
        - is_self (bool): Whether or not the submission is a selfpost (text-only).
        - is_spoiler (bool): Whether or not the submission has been marked as a spoiler.
        - is_locked (bool): Whether or not the submission has been locked.
        - is_stickied (bool): Whether or not the submission is stickied.
        - is_over_18 (bool): Whether or not the submission has been marked as NSFW.
        - link_flair_template_id (str): The link flair's ID.
        - link_flair_text (str):The link flair's text content, or None if not flaired.
        - num_comments (int): The number of comments on the submission.
        - num_crossposts (int): The number of crossposts on the submission.
        - num_reports (int): The number of reports on the submission.
        - score (int): The score for the submission.
        - ups (int): The number of upvotes.
        - down (int): The number of downvotes.
        - upvote_ratio (float): The upvote ratio.
    """

    id: str
    name: str
    author: str
    title: str
    created_utc: float
    selftext: str
    permalink: str
    url: str

    is_original_content: bool
    is_self: bool
    is_spoiler: bool
    is_locked: bool
    is_stickied: bool
    is_over_18: bool

    # link_flair_template_id: str
    link_flair_text: str

    num_comments: int
    num_crossposts: int
    num_reports: int
    score: int
    ups: int
    downs: int
    upvote_ratio: float

    def to_dict(self) -> str:
        return asdict(self)
