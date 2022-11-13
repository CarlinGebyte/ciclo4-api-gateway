from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS
import json
from waitress import serve
import datetime
import requests
import re

app = Flask(__name__)
cors = CORS(app)


@app.route("/", methods=['GET'])
def test():
    res = {"message": "Server running ..."}
    return jsonify(res)


def loadFileConfig():
    with open('config.json') as f:
        data = json.load(f)
    return data


if __name__ == '__main__':
    dataConfig = loadFileConfig()
    print("Server running : " + "http://" + dataConfig["dev"] + ":" + str(dataConfig["port"]))
    serve(app, host=dataConfig["dev"], port=dataConfig["port"])
