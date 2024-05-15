from flask import Flask, jsonify, request

import requests
import random


app = Flask(__name__)


@app.route('/process_link', methods=['POST'])
def process_link():
    data = request.get_json()

    response = call_model(data['url'])
    #return jsonify({'message': f'{data} received successfully'})
    return jsonify({'result': response})


def call_model(data):
    i = random.randint(0, 100)
    if i < 50:
        return 'positive' + data
    else:
        return  'negative' + data


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6000, debug=True)