FROM python:3.11-slim

COPY ./src /app/src
COPY ./requirements.txt /app
COPY ./scripts /app/scripts
WORKDIR /app

RUN chmod a+x scripts/*.sh
RUN pip3 install -r requirements.txt

EXPOSE 8000

