FROM python:3.11-slim

RUN mkdir /home/app
RUN mkdir /home/app/src
RUN mkdir /home/app/src/staticfiles
WORKDIR /home/app/src


COPY ./src /home/app/src
COPY ./requirements.txt /home/app
COPY ./scripts /home/app/scripts

WORKDIR /home/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt install netcat-traditional
RUN chmod a+x scripts/*.sh

RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt




EXPOSE 8000

