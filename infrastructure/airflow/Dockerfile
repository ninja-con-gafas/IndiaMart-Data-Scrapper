FROM apache/airflow:2.11.0-python3.9

USER root
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt