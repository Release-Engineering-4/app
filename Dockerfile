# dockerfile for the frontend and service

# Use the official image as a parent image
FROM python:3.10-slim

#
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY src/app_frontend /app/app_frontend
ENTRYPOINT [ "python" ]
CMD [ "app/app_frontend/server.py"]
