FROM python:3.11.7-slim-bullseye

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ENV PYTHONPATH=$PYTHONPATH:/app

ARG ROOT_PATH=./services/reddit_streaming_service

COPY $ROOT_PATH/requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./utils ./utils
COPY $ROOT_PATH $ROOT_PATH

# Run the main service
CMD python services/reddit_streaming_service/main.py