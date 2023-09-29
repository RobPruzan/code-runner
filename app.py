from flask import Flask, jsonify, request
import os

app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    print("got response")
    response.headers.add("Access-Control-Allow-Origin", "*")
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Methods"] = "POST"
        headers = request.headers.get("Access-Control-Request-Headers")
        if headers:
            response.headers["Access-Control-Allow-Headers"] = headers
    return response


@app.route("/")
def hello_world():
    return jsonify(message="Hello, World!")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
