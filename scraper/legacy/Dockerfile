FROM python:3.10

WORKDIR /src

RUN [ "pip", "install", "pipenv" ]
COPY ./Pipfile ./
RUN ["pipenv", "install"]

COPY ./scraper ./scraper
