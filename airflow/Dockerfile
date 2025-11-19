FROM --platform=linux/arm64 apache/airflow:2.9.0-python3.10

USER root

# Install Java 17
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt into Airflow image
COPY requirements.txt /requirements.txt

USER airflow
