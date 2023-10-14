FROM python:3.11-slim

COPY ./src /app/src
COPY ./requirements.txt /app
COPY ./scripts /app/scripts

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt install netcat-traditional
RUN chmod a+x scripts/*.sh

RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 8000

