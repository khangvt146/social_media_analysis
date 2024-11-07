import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import dag, task
from airflow.models.xcom_arg import XComArg
from dotenv import load_dotenv

from utils.logger import Logger

load_dotenv()
config = {
    "STACK_EXCHANGE_API": {
        "CLIENT_ID": os.getenv("STACK_EXCHANGE_CLIENT_ID"),
        "CLIENT_SECRET": os.getenv("STACK_EXCHANGE_CLIENT_SECRET"),
        "CLIENT_KEY": os.getenv("STACK_EXCHANGE_CLIENT_KEY"),
        "ACCESS_TOKEN": os.getenv("STACK_EXCHANGE_ACCESS_TOKEN"),
    },
    "KAFKA": {"BROKER_URL": os.getenv("KAFKA_BROKER_URL")},
}
logger = Logger("stack_exchange_api_fetching", None)


# Define default arguments for the DAG
default_args = {
    "owner": "khangvt146",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
}

STACK_EXCHANGE_PAGE = {
    "STACK_OVER_FLOW": {
        "API_PAGE_TYPE": "stackoverflow",
        "KAFKA_TOPIC": "stack_over_flow",
    },
    "AI_STACK_EXCHANGE": {
        "API_PAGE_TYPE": "ai",
        "KAFKA_TOPIC": "ai_stack_exchange",
    },
    "ASK_UBUNTU": {
        "API_PAGE_TYPE": "askubuntu",
        "KAFKA_TOPIC": "ask_ubuntu_stack_exchange",
    },
    "DEVOPS_STACK_EXCHANGE": {
        "API_PAGE_TYPE": "devops",
        "KAFKA_TOPIC": "devops_stack_exchange",
    },
    "SOFTWARE_ENGINEERING_STACK_EXCHANGE": {
        "API_PAGE_TYPE": "softwareengineering",
        "KAFKA_TOPIC": "software_engineering_stack_exchange",
    },
    "DATA_SCIENCE_STACK_EXCHANGE": {
        "API_PAGE_TYPE": "datascience",
        "KAFKA_TOPIC": "data_science_stack_exchange",
    },
    "INFORMATION_SECURITY_STACK_EXCHANGE": {
        "API_PAGE_TYPE": "security",
        "KAFKA_TOPIC": "security_stack_exchange",
    },
    "DATABASE_ADMINISTRATOR_STACK_EXCHANGE": {
        "API_PAGE_TYPE": "dba",
        "KAFKA_TOPIC": "database_administrator_stack_exchange",
    },
    "SUPER_USER": {
        "API_PAGE_TYPE": "superuser",
        "KAFKA_TOPIC": "super_user_stack_exchange",
    },
}

with DAG(
    "stack_exchange_api_fetching_dag",
    default_args=default_args,
    description="Fetching data from Stack Exchange top pages using API.",
    schedule_interval="0,15,30,45 * * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["Social Media", "Kafka"],
) as dag:
    # Extract task
    def create_extract_task(page_name: str):

        @task(task_id=f"extract_{page_name.lower()}_task")
        def extract_task():
            from airflow_dags.stack_exchange_fetching import (
                ExtractStackExchangeAPI,
            )

            page_type = STACK_EXCHANGE_PAGE[page_name]["API_PAGE_TYPE"]
            extract = ExtractStackExchangeAPI(config, logger)
            extract_data = extract.extract_api_data(page_type)
            return extract_data

        return extract_task()

    # Publish Kafka task
    def create_publish_kafka_task(xcom_args: XComArg, page_name: str):

        @task(task_id=f"publish_{page_name.lower()}_task")
        def publish_kafka_task(data_list: list):
            from airflow_dags.stack_exchange_fetching import (
                StackExchangeKafkaProducer,
            )

            topic = STACK_EXCHANGE_PAGE[page_name]["KAFKA_TOPIC"]
            producer = StackExchangeKafkaProducer(config, logger)
            producer.publish_message(data_list, topic)

        return publish_kafka_task(xcom_args)

    # Stack Overflow page
    stack_overflow_data = create_extract_task("STACK_OVER_FLOW")
    create_publish_kafka_task(stack_overflow_data, "STACK_OVER_FLOW")

    # Artificial Intelligence Stack Exchange page
    ai_stack_exchange_data = create_extract_task("AI_STACK_EXCHANGE")
    create_publish_kafka_task(ai_stack_exchange_data, "AI_STACK_EXCHANGE")

    # Ask Ubuntu page
    ask_ubuntu_data = create_extract_task("ASK_UBUNTU")
    create_publish_kafka_task(ask_ubuntu_data, "ASK_UBUNTU")

    # DevOps Stack Exchange page
    devops_stack_exchange_data = create_extract_task("DEVOPS_STACK_EXCHANGE")
    create_publish_kafka_task(devops_stack_exchange_data, "DEVOPS_STACK_EXCHANGE")

    # Software Engineering Stack Exchange page
    se_stack_exchange_data = create_extract_task("SOFTWARE_ENGINEERING_STACK_EXCHANGE")
    create_publish_kafka_task(
        se_stack_exchange_data, "SOFTWARE_ENGINEERING_STACK_EXCHANGE"
    )

    # Data Science Stack Exchange page
    ds_stack_exchange_data = create_extract_task("DATA_SCIENCE_STACK_EXCHANGE")
    create_publish_kafka_task(ds_stack_exchange_data, "DATA_SCIENCE_STACK_EXCHANGE")

    # Information Security Stack Exchange page
    security_stack_exchange_data = create_extract_task(
        "INFORMATION_SECURITY_STACK_EXCHANGE"
    )
    create_publish_kafka_task(
        security_stack_exchange_data, "INFORMATION_SECURITY_STACK_EXCHANGE"
    )

    # Database Administrators Stack Exchange page
    db_admin_stack_exchange_data = create_extract_task(
        "DATABASE_ADMINISTRATOR_STACK_EXCHANGE"
    )
    create_publish_kafka_task(
        db_admin_stack_exchange_data, "DATABASE_ADMINISTRATOR_STACK_EXCHANGE"
    )

    # Super User Stack Exchange page
    superuser_stack_exchange_data = create_extract_task("SUPER_USER")
    create_publish_kafka_task(superuser_stack_exchange_data, "SUPER_USER")
