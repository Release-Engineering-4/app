"""Module providing templates for the various routes of the web app."""

# pylint: disable = protected-access, import-error
import os
import time
import psutil
import requests
from flask import Flask, render_template, request, Response
from libversion import version_util
from prometheus_client import (generate_latest,
                               CONTENT_TYPE_LATEST)
from metrics_init import (num_pred_requests,
                          index_requests,
                          errored_requests,
                          correct_predictions,
                          incorrect_predictions,
                          cpu_usage,
                          memory_usage,
                          model_accuracy,
                          request_duration_histogram,
                          request_duration_summary,
                          beta_correct_predictions,
                          beta_incorrect_predictions,
                          beta_model_accuracy)

# load class
lv = version_util.VersionUtil()
ver = lv.get_version()

# get environment variables
model_url = os.getenv('MODEL_URL', 'http://localhost:5000/predict')
model_url_beta = os.getenv('MODEL_URL_BETA', 'http://localhost:5000/predict')
beta_test = os.getenv('BETA_TEST_FLAG', "False") == "True"

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
    result_tx = ""
    if beta_test:
        result_tx = "This app will test our beta model too"
    return render_template(
        "index.html",
        inputDisplay="",
        result=result_tx,
        feedback="",
        version=ver
    )


@app.route('/predict')
def predict():
    '''
    Define the /predict route.
    Returns: The results web template.
    '''
    num_pred_requests.inc()
    url = request.args.get("url")
    data = {"url": url}
    start_time = time.time()
    try:
        response = requests.post(model_url, json=data, timeout=30)
        response_request = response.json()
        duration = time.time() - start_time
        request_duration_histogram.observe(duration)
        request_duration_summary.observe(duration)
        url_result = ""
        if response_request["prediction"]:
            if response_request["prediction"][0][0] > 0.5:
                url_result = "The provided input is a phishing URL!"
            else:
                url_result = "The provided input is not a phishing URL!"
        return render_template(
            "results.html", inputDisplay=url, result=url_result, version=ver
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
    result = request.args.get("result") == "The provided input \
        is a phishing URL!"
    was_phishing = (user_feedback and result) or \
        (not user_feedback and not result)
    feedback_given = "Thank you for your feedback!"

    if user_feedback:
        correct_predictions.inc()
    else:
        incorrect_predictions.inc()
    accuracy = correct_predictions._value.get() / \
        (correct_predictions._value.get()
         + incorrect_predictions._value.get())
    model_accuracy.set(accuracy)

    if beta_test:
        # Need to run for beta model-service
        url = request.args.get("url")
        data = {"url": url}
        response = requests.post(model_url_beta, json=data, timeout=30)
        response_request = response.json()
        if response_request["prediction"]:
            if (response_request["prediction"][0][0] > 0.5 and was_phishing) \
                    or (response_request["prediction"][0][0] <= 0.5
                        and not was_phishing):
                beta_correct_predictions.inc()
            else:
                beta_incorrect_predictions.inc()
            accuracy = correct_predictions._value.get() / \
                (correct_predictions._value.get()
                 + incorrect_predictions._value.get())
            beta_model_accuracy.set(accuracy)
        feedback_given = f'{feedback_given} This will help improve our model.'
    return render_template(
        "index.html",
        inputDisplay="",
        result="",
        feedback=feedback_given,
        version=ver
    )


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
