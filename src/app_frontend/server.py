from flask import Flask, render_template, jsonify, request
from flasgger import Swagger
import requests

# load frontend
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    # Load template page and send it to the user
    return render_template(
        "index.html",
        inputDisplay="",
        result="",
        version="test"
    )

@app.route('/predict', methods=['POST'])
def predict():
    # Get the link from the html page and send it to the service
    url = request.args.get('url')
    data = {'url': url}
    response = requests.post('http://localhost:5000/process_link', json=data)

    # Extract result form response
    response_request = response.json()
    

    return render_template(
        "index.html",
        inputDisplay=url,
        result=response_request['result'],
        version="test"
    )



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)

def run_frontend():
    app.run(host="0.0.0.0", port=8080, debug=True)