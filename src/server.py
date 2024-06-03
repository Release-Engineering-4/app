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
correct_predictions = Counter('correct_predictions',
                              'Total number of requests giving \
                                correct prediction')
incorrect_predictions = Counter('incorrect_predictions',
                                'Total number of requests giving \
                                    incorrect prediction')
cpu_usage = Gauge('cpu_usage',
                  'CPU usage of app')
memory_usage = Gauge('memory_usage',
                     'Memory usage of app')
model_accuracy = Gauge('model_accuracy',
                       'Measure of prediction accuracy based on feedback')
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


@app.route('/feedback')
def feedback():
    '''
    Define the /feedback route.
    Returns: The legit web template.
    '''
    user_feedback = request.args.get("prediction_feedback") == "correct"
    if user_feedback:
        correct_predictions.inc()
    else:
        incorrect_predictions.inc()
    # pylint: disable = protected-access
    accuracy = correct_predictions._value.get() / \
        (correct_predictions._value.get()
         + incorrect_predictions._value.get())
    model_accuracy.set(accuracy)
    return "Thank you for your feedback!"


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
