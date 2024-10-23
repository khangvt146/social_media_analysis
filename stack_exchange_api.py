import requests
from utils.file import File

STACK_API_URL = "https://api.stackexchange.com/2.3/questions"
STACK_ACCESS_TOKEN_URL = "https://stackoverflow.com/oauth/access_token"

# stackoverflow, ai,
"""
- Stack Overflow: stackoverflow
- Artificial Intelligence Stack Exchange: ai
- Ask Ubuntu: askubuntu
- DevOps Stack Exchange: devops
- Software Engineering Stack Exchange: softwareengineering
- Data Science Stack Exchange: datascience
- Information Security Stack Exchange: security
- Database Administrators Stack Exchange: dba
- Super User: superuser
"""
PAGE_TYPE = "askubuntu"

config = File.read_yaml_file("configs/config.yml")


def get_access_token() -> str:
    """
    First, send a request like below to Approve application and get "code" value:
    https://stackoverflow.com/oauth?client_id=<YOUR_CLIENT_ID>&scope=read_inbox,no_expiry&redirect_uri=<YOUR_REDIRECT_URI>
    """
    data = {
        "client_id": config["STACK_CLIENT_ID"],
        "client_secret": config["STACK_CLIENT_SECRET"],
        "code": "OE4K2qdkAAC1Hdpk7U3uyw))",
        "redirect_uri": "https://howizz.com/",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(STACK_ACCESS_TOKEN_URL, data=data, headers=headers)

    if response.status_code != 200:
        print(f"Calling request to get access token failed. Details: {response.reason}")

    return response.json()

total_posts = []

for page in range(1, 11):
    # Set up parameters for the API request
    params = {
        "order": "desc",
        "sort": "creation",
        "site": PAGE_TYPE,
        "access_token": config["STACK_ACCESS_TOKEN"],
        "key": config["STACK_CLIENT_KEY"],
        "page": page,
        "pagesize": 100,
        # "fromdate": "1729666800",
        # "todate": "1729670400",
    }

    # Make the API request
    response = requests.get(STACK_API_URL, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        total_posts.extend(data["items"])
    else:
        print(f"Failed to fetch data: {response.status_code}")

File.write_json_file(total_posts, "data/ask_ubuntu/questions_data.json")
