from flask import Flask, render_template, jsonify, request
from flasgger import Swagger
import requests

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/')
@app.route('/index')
def index():
    return render_template(
        "index.html",
        inputDisplay="test1",
        result="test2"
    )

@app.route('/predict', methods=['GET'])
def predict():
    link = request.args.get('link')
    data = {'link': link}
    response = requests.get('http://localhost:5000/process_link', json=data)

    response_request = response.json()
    

    return render_template(
        "index.html",
        inputDisplay=link,
        result=response_request['result']
    )



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)