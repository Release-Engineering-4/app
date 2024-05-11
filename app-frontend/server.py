from flask import Flask, request, render_template
from waitress import serve
from flasgger import Swagger

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

@app.route('/predict')
def predict():
    link = request.args.get('link')
    return render_template(
        "index.html",
        inputDisplay=link,
        result="test2"
    )



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)