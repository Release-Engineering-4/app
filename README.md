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

The app page is hosted on the following URL:`http://localhost:8080/`. This URl isonly valid if you mapped the ports as `-p 8080:8080` when running the docker run command.


## Kubernetes deployment
Use your favourite local kubernetes development distribution package to start a local cluster. The following example will use minikuber with a docker driver.

First start your cluster:

```bash
minikube start --driver=docker
```

Make sure to enable ingress:
```bash
minikube addons enable ingress
```

Furthermore, to allow monitoring of the app you must install the full [Prometheus stack](https://artifacthub.io/packages/helm/prometheus-community/kube-prometheus-stack) to the Kubernetes cluster. We recommend using [Helm](https://helm.sh/) to install the Prometheus stack. The followings steps assume you've installed Helm.

After you've installed Helm we first must get the Helm repository info:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

Now you can install the Prometheus Stack with:

```bash
helm install myprom prom-repo/kube-prometheus-stack
```

Apply the `kubernetes.yml` file to deploy the application, change the `replicas` variable to change the amount of copies to deploy:

```bash
kubectl apply -f kubernetes.yml
```

Because we use Minikube, there are limitations with virtualization through the Docker network. So, we need to create a Minikube tunnel to access the Ingress:

```bash
minikube tunnel
```

Run this command in a separate terminal and keep it open to be able to access the application through the following URL: `http://localhost/`.

## Monitoring

Metrics of type Gauge, Counter, Histogram and Summary are defined. They monitor the app usage in number of visits, number of errored requests, cpu and memory usage. These metrics are available on the ```/metrics``` endpoint and are also visible on Prometheus.

Alerting based on number of errored requests is to be set up. If the number exceeds a certain threshold, it implies that there is an issue with the ```app``` service and needs immediate fixing, thus an email alert will be configured. Alert can be tested by disabling the ```model-service```.

The app asks the user to input whether the prediction given by our service was correct or incorrect. Metrics for prediction accuracy are also created to keep track of this. Based on this accuracy metric, we can find out the real-time effectiveness of the model. The Istio Service mesh for traffic management will divert portion of the traffic to the app which uses another fine-tuned version of the model. The accuracy for both models can thus be compared to see which performs better for user requests.