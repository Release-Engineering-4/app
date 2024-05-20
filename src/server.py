"""Module providing templates for the various routes of the web app."""

import os
import requests
from flask import Flask, render_template, request
from libversion import version_util

# load class
lv = version_util.VersionUtil()
ver = lv.get_version()

# get environment variables from docker ran command
model_url = os.getenv('MODEL_URL', 'http://localhost:5000/process_link')

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
    # Get the link from the html page and send it to the service
    url = request.args.get("url")
    data = {"url": url}
    response = requests.post(model_url, json=data, timeout=10)
    # Extract result form response
    response_request = response.json()
    return render_template(
        "results.html",
        inputDisplay=url,
        result=response_request['result'],
        version=ver
    )


@app.route('/url_was_phising')
def url_was_phising():
    '''
    Define the /url_was_phising route.
    Returns: The phising web template.
    '''
    return


@app.route('/url_was_legit')
def url_was_legit():
    '''
    Define the /url_was_legit route.
    Returns: The legit web template.
    '''
    return


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)


def run_frontend():
    '''
    Exposes the app on port 8080.
    '''
    app.run(host="0.0.0.0", port=8080, debug=True)
