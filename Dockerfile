# dockerfile for the frontend and service

# Use the official image as a parent image
FROM ubuntu:latest
FROM python:3.10-slim
LABEL org.opencontainers.image.source https://github.com/Release-Engineering-4/app
#
WORKDIR /root
COPY requirements.txt /root/
RUN apt-get update 
RUN apt-get upgrade -y
RUN apt-get install -y git
#RUN apt-get install -y python3-pip
RUN pip install -r requirements.txt
COPY src/ /root/
ENTRYPOINT [ "python" ]
CMD ["server.py"]
