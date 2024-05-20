# dockerfile for the frontend and service

# Use the official image as a parent image
FROM ubuntu:latest
FROM python:3.10-slim
LABEL org.opencontainers.image.source https://github.com/Release-Engineering-4/app
#
WORKDIR /app
COPY . /app/
RUN apt-get update 
RUN apt-get upgrade -y
RUN apt-get install -y git

RUN pip install poetry
RUN poetry install

CMD ["poetry", "run", "python", "src/server.py"]
