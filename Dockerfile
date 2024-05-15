# dockerfile for the frontend and service

# Use the official image as a parent image
FROM python:3.10-slim

#
WORKDIR /root
COPY requirements.txt /root/
RUN pip install -r requirements.txt
COPY src/ /root/
ENTRYPOINT [ "python" ]
CMD ["server.py"]
