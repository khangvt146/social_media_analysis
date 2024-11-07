from datetime import datetime, timedelta
from typing import Optional

import pytz
import requests

from utils.logger import Logger

STACK_API_URL = "https://api.stackexchange.com/2.3/questions"
STACK_ACCESS_TOKEN_URL = "https://stackoverflow.com/oauth/access_token"
MAX_PAGE = 50


class ExtractStackExchangeAPI:
    """
    Class for extracting data from Stack Exchange API top pages.
    """

    def __init__(self, config: dict, logger: Logger) -> None:
        self.logger = logger
        self.config = config

    def _get_access_token(self) -> Optional[str]:
        """
        Get access token from Stack Exchange API.

        Send a request like below to Approve application and get "code" value:
        https://stackoverflow.com/oauth?client_id=<YOUR_CLIENT_ID>&scope=read_inbox,no_expiry&redirect_uri=<YOUR_REDIRECT_URI>

        Returns:
            str: The Stack Exchange API token (no expired token)
        """
        data = {
            "client_id": self.config["STACK_EXCHANGE_API"]["CLIENT_ID"],
            "client_secret": self.config["STACK_EXCHANGE_API"]["CLIENT_SECRET"],
            "code": "OE4K2qdkAAC1Hdpk7U3uyw))",
            "redirect_uri": "https://howizz.com/",
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(STACK_ACCESS_TOKEN_URL, data=data, headers=headers)

        if response.status_code != 200:
            self.logger.error(
                f"Calling request to get access token failed. Details: {response.reason}"
            )
            return None

        return response.json()

    def extract_api_data(self, page_type: str) -> list:
        """
        Extract data using Stack Exchange API based on the specified page type.

        Parameters:
            page_type (str): The type of page to retrieve data from (Stack Overflow, Ask Ubuntu, ...)

        Returns:
            list: The extracted data in list format.
        """
        # Fetch data from the last 15 minutes
        dt_now = datetime.now(tz=pytz.timezone("Asia/Ho_Chi_Minh")).replace(
            second=0, microsecond=0
        )
        rounded_dt_now = dt_now - timedelta(minutes=dt_now.minute % 15)

        to_date = rounded_dt_now.timestamp()
        from_date = (rounded_dt_now - timedelta(minutes=15)).timestamp()

        total_posts = []

        for page in range(1, MAX_PAGE):
            # Set up parameters for the API request
            params = {
                "order": "desc",
                "sort": "creation",
                "site": page_type,
                "access_token": self.config["STACK_EXCHANGE_API"]["ACCESS_TOKEN"],
                "key": self.config["STACK_EXCHANGE_API"]["CLIENT_KEY"],
                "page": page,
                "pagesize": 100,
                "fromdate": int(from_date),
                "todate": int(to_date),
            }

            # Make the API request
            response = requests.get(STACK_API_URL, params=params)

            if response.status_code != 200:
                msg = f"Failed to fetch API data on page {page}. Details: {response.reason}"
                self.logger.error(msg)
                raise Exception(msg)

            data = response.json()
            total_posts.extend(data["items"])

            if data["has_more"] is False:
                break

        return total_posts
