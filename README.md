# Realtime Social Media Analysis
This project is designed to extract valuable insights from social media platforms, with a particular focus on Reddit and Stack Exchange. Leveraging the vast amount of user-generated content on these platforms, the project aims to identify and analyze trending topics, discussions, and emerging themes. By utilizing Big Data and natural language processing (NLP) techniques, the project will uncover real-time conversations that are gaining traction within the science and technology domains.

## System Architecture
![Local Image](images/system_architecture.png)

## Prerequisites
- Apache Spark >= `3.5.0`
- Apache Airflow >= `2.8.0`
- PostgreSQL version `15`

## How to run ?
```
# Start infrastructure (Kafka & Kafdrop)
docker compose -f docker-compose.infra.yml up -d 

# Start related services
docker compose -f docker-compose.services.yml up -d
```

## Dashboard Results
![Local Image](images/reddit_dashboard.png)
*Reddit Dashboard*
</br>
</br>
</br>
![Local Image](images/stack_exchange_dashboard.png)
*Stack Exchange Dashboard*

