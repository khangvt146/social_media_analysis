import requests

API_URL = "https://api.pushshift.io/reddit/search/submission/"
MAX_POSTS = 10000
SUBREDDIT = "technology"

total_post_data = []
params = {
    "subreddit": SUBREDDIT,
    "size": 100,  # Max allowed by Pushshift in a single request
    "sort": "desc",
    "sort_type": "created_utc",
}

while len(total_post_data) < MAX_POSTS:
    try:
        response = requests.get(API_URL, params=params)

        if response.status_code != 200:
            print(f"Calling Push Shift API error. Details: {response.reason}")

        data = response.json().get("data", [])

        if not data:
            break
        total_post_data.extend(data)

    except Exception as e:
        print("Error occurs. Details: {e}")
