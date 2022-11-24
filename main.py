import datetime
import json
import re

import requests
from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS
from waitress import serve

app = Flask(__name__)
cors = CORS(app)
from flask_jwt_extended import create_access_token, verify_jwt_in_request
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import JWTManager

app.config["JWT_SECRET_KEY"] = "super-secret"  # Cambiar por el que se conveniente
jwt = JWTManager(app)


@app.route("/login", methods=["POST"])
def createToken():
    data = request.get_json()
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = dataConfig["url-backend-auth"] + '/api/user/validate/'
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        user = response.json()
        expires = datetime.timedelta(days=1)
        access_token = create_access_token(identity=user, expires_delta=expires)
        return jsonify({"token": access_token, "userId": user["_id"], "userRole": user["role"]["name"]}), 200
    else:
        return jsonify({"message": "Bad username or password"}), 401


@app.before_request
def before_request_callback():
    endpoint = cleanURL(request.path)
    excludedRoutes = ["/login"]
    if excludedRoutes.__contains__(request.path):
        pass
    elif verify_jwt_in_request():
        user = get_jwt_identity()
        if user["role"] is not None:
            grant = validatePermission(endpoint, request.method, user["role"]["_id"])
            if not grant:
                return jsonify({"message": "Unauthorized"}), 401
        else:
            return jsonify({"message": "Unauthorized"}), 401


def cleanURL(url):
    split = url.split("/")
    for i in split:
        if re.search("\\d", i):
            url = url.replace(i, "?")
    return url


def validatePermission(endpoint, method, idRole):
    url = dataConfig["url-backend-auth"] + '/api/permission-role/validate-permission/' + str(idRole)
    grant = False
    headers = {"Content-Type": "application/json; charset=utf-8"}
    body = {"url": endpoint, "method": method}
    print(body)
    response = requests.get(url, json=body, headers=headers)

    try:
        data = response.json()
        if ("_id" in data):
            grant = True

    except:
        pass
    return grant


@app.route("/", methods=['GET'])
def test():
    res = {"message": "Server running ..."}
    return jsonify(res)


@app.route("/tables", methods=['GET'])
def getTables():
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = dataConfig["url-backend-flask"] + '/tables'
    response = requests.get(url, headers=headers)
    response = response.json()
    return jsonify(response)


@app.route("/tables/<id>", methods=['GET'])
def getTable(id):
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = dataConfig["url-backend-flask"] + '/tables/' + id
    response = requests.get(url, headers=headers)
    response = response.json()
    return jsonify(response)


@app.route("/tables", methods=['POST'])
def createTable():
    data = request.get_json()
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = dataConfig["url-backend-flask"] + '/tables'
    response = requests.post(url, data=json.dumps(data), headers=headers)
    response = response.json()
    return jsonify(response)


@app.route("/tables/<id>", methods=['PUT'])
def updateTable(id):
    data = request.get_json()
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = dataConfig["url-backend-flask"] + '/tables/' + id
    response = requests.put(url, data=json.dumps(data), headers=headers)
    response = response.json()
    return jsonify(response)


@app.route("/tables/<id>", methods=['DELETE'])
def deleteTable(id):
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = dataConfig["url-backend-flask"] + '/tables/' + id
    response = requests.delete(url, headers=headers)
    response = response.json()
    return jsonify(response)


@app.route("/candidates", methods=['GET'])
def getCandidates():
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = dataConfig["url-backend-flask"] + '/candidates'
    response = requests.get(url, headers=headers)
    response = response.json()
    return jsonify(response)


@app.route("/parties", methods=["GET"])
def getParties():
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = dataConfig["url-backend-flask"] + '/parties'
    response = requests.get(url, headers=headers)
    response = response.json()
    return jsonify(response)


@app.route("/results", methods=["GET"])
def getResults():
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = dataConfig["url-backend-flask"] + '/results'
    response = requests.get(url, headers=headers)
    response = response.json()
    return jsonify(response)

def loadFileConfig():
    with open('config.json') as f:
        data = json.load(f)
    return data


if __name__ == '__main__':
    dataConfig = loadFileConfig()
    print("Server running : " + "http://" + dataConfig["dev"] + ":" + str(dataConfig["port"]))
    serve(app, host=dataConfig["dev"], port=dataConfig["port"])
