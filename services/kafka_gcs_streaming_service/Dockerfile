FROM python:3.8.20-slim-bullseye

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install Java (required by Spark)
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk procps && \
    apt-get clean

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

WORKDIR /app

ENV HADOOP_CONF_DIR=/app/configs
ENV PYTHONPATH=$PYTHONPATH:/app

ARG ROOT_PATH=./services/kafka_gcs_streaming_service

COPY $ROOT_PATH/requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./utils ./utils
COPY ./assets ./assets
COPY $ROOT_PATH $ROOT_PATH

# Run the main service
CMD python services/kafka_gcs_streaming_service/main.py