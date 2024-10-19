FROM python:3.11-slim

RUN apt-get update \
    && apt-get -y install gcc libmariadb-dev \
    && apt-get clean

ENV TZ="Asia/Tokyo"
RUN echo $TZ > /etc/timezone

WORKDIR /workspace
COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt
