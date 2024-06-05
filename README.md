# App
This repository contains the web application for the URL phishing project.

## Features

- **Frontend:** The user interface is created with plain HTML. It features a brief project description and clear instructions on how to use the application. Users can input their URL into a text box and click the "check" button to receive the model's prediction on whether the URL is phishing or not. Additionally, the current version of the package is displayed.

- **Backend:** The backend is built on Flask and offers various endpoints. These include endpoints for model predictions, metrics, and user feedback. The feedback mechanism allows users to provide input on the model's predictions, contributing to potential improvements for future iterations.

- **Containerization:** The application is containerized using Docker. 

## Get it started

Follow the steps below to run the application in a docker container.

To build the docker image use:

```bash
   docker build -t image-name .   
```

To run the docker container use:

```bash
   docker run --name container-name -d -p 8080:8080 image-name   
```

To pass the URL of the model-service as an environment vairable use:

```bash
   docker run --name container-name -d -p 8080:8080 -e MODEL_URL=url-here image-name   
```
