"""Module providing templates for the various routes of the web app."""

import os
import time
import psutil
import requests
from flask import Flask, render_template, request, Response
from libversion import version_util
from prometheus_client import (Counter,
                               Histogram,
                               Summary,
                               Gauge,
                               generate_latest,
                               CONTENT_TYPE_LATEST)

# load class
lv = version_util.VersionUtil()
ver = lv.get_version()

num_pred_requests = Counter('prediction_requests_total',
                            'Total number of prediction requests')
index_requests = Counter('flask_app_index_requests_total',
                         'Total number of requests to the index page')
errored_requests = Counter('error_requests_total',
                           'Total number of requests that errored out')
cpu_usage = Gauge('cpu_usage',
                  'CPU usage of app')
memory_usage = Gauge('memory_usage',
                     'Memory usage of app')
request_duration_histogram = Histogram(
    'flask_app_request_duration_seconds',
    'Histogram for request duration in seconds')
request_duration_summary = Summary(
    'flask_app_request_duration_seconds_summary',
    'Summary for request duration in seconds')


# get environment variables from docker ran command
model_url = os.getenv('MODEL_URL', 'http://localhost:5000/predict')

print(f"Using model_url: {model_url}")
# load frontend
app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    '''
    Load template page and send it to the user.
    Returns: The default web template.
    '''
    index_requests.inc()
    return render_template(
        "index.html",
        inputDisplay="",
        result="",
        version=ver
    )


@app.route('/predict')
def predict():
    '''
    Define the /predict route.
    Returns: The results web template.
    '''
    num_pred_requests.inc()
    # Get the link from the html page and send it to the service
    url = request.args.get("url")
    data = {"url": url}
    start_time = time.time()
    try:
        response = requests.post(model_url, json=data, timeout=10)
        # Extract result form response
        response_request = response.json()
        duration = time.time() - start_time
        request_duration_histogram.observe(duration)
        request_duration_summary.observe(duration)
        return render_template(
            "results.html",
            inputDisplay=url,
            result=response_request['result'],
            version=ver
        )
    except requests.exceptions.RequestException:
        errored_requests.inc()
        duration = time.time() - start_time
        request_duration_histogram.observe(duration)
        request_duration_summary.observe(duration)
        return render_template(
            "error.html",
            inputDisplay=url,
            version=ver
        )


# @app.route('/url_was_phising')
# def url_was_phising():
#     '''
#     Define the /url_was_phising route.
#     Returns: The phising web template.
#     '''
#     return


# @app.route('/url_was_legit')
# def url_was_legit():
#     '''
#     Define the /url_was_legit route.
#     Returns: The legit web template.
#     '''
#     return


@app.route('/metrics')
def metrics():
    '''
    Define the /metric route.
    Returns: The metrics web template.
    '''
    cpu_usage.set(psutil.cpu_percent())
    memory_usage.set(psutil.virtual_memory().used)
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
