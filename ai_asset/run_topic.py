import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(
    filename='api_requests.log',  # Log file name
    level=logging.INFO,           # Logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    filemode='w'                  # Overwrite log file each run
)

# Create logger object
logger = logging.getLogger()

# API endpoint
url = "http://127.0.0.1:5000/model"

# Platform and corresponding subtopics
platforms_and_subtopics = {
    "silver_reddit": [
        "reddit_futurology",
        "reddit_technology",
        "reddit_science"
    ],
    "silver_stack_exchange": [
        "stack_over_flow",
        "super_user_stack_exchange",
        "ask_ubuntu_stack_exchange",
        "database_administrator_stack_exchange",
        "ai_stack_exchange",
        "security_stack_exchange",
        "data_science_stack_exchange",
        "software_engineering_stack_exchange",
        "devops_stack_exchange"
    ]
}

# Common parameters
common_payload = {
    "days": 90  # Adjust this if needed
}

# Loop through each platform and its subtopics
for platform, subtopics in platforms_and_subtopics.items():
    message = f"--- Processing platform: {platform} ---"
    print(message)
    logger.info(message)

    for idx, subtopic in enumerate(subtopics):
        message = f"[{idx + 1}/{len(subtopics)}] Processing subtopic: {subtopic}"
        print(message)
        logger.info(message)
        
        # Prepare payload for current platform and subtopic
        payload = common_payload.copy()
        payload["platform"] = platform
        payload["subtopic"] = subtopic

        # Send POST request
        try:
            message = f"Sending request for platform '{platform}', subtopic '{subtopic}'..."
            print(message)
            logger.info(message)

            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )

            # Print the response
            message = f"Response for subtopic '{subtopic}' on platform '{platform}':"
            print(message)
            logger.info(message)
            
            status_code_message = f"Status Code: {response.status_code}"
            print(status_code_message)
            logger.info(status_code_message)

            try:
                response_json_message = f"Response JSON: {response.json()}"
                print(response_json_message)
                logger.info(response_json_message)
            except json.JSONDecodeError:
                response_text_message = f"Failed to decode JSON response. Raw response text: {response.text}"
                print(response_text_message)
                logger.error(response_text_message)
            
        except Exception as e:
            error_message = f"Error occurred for subtopic '{subtopic}' on platform '{platform}': {str(e)}"
            print(error_message)
            logger.error(error_message)
        
        # Optional: Add delay to avoid overwhelming the server
        delay_message = "Waiting 2 seconds before the next request...\n"
        print(delay_message)
        logger.info(delay_message)
        time.sleep(2)

    finish_message = f"--- Finished processing platform: {platform} ---\n"
    print(finish_message)
    logger.info(finish_message)
