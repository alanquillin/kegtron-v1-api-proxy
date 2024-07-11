from data import devices as deviceDB

from flask import current_app as app, jsonify

PREFIX = "/api/v1"

@app.route(f'{PREFIX}/health')
def health():
    return "We are up and running!"


@app.route(f'{PREFIX}/ping')
def ping():
    return "pong"


@app.route(f'{PREFIX}/devices')
def get_devices_int():
    return jsonify(deviceDB.list())


@app.route(f'{PREFIX}/devices/<string:id>', methods=['GET'])
def get_device(id):
    data = deviceDB.get(id)
    if not data:
        return 404

    return jsonify(data), 200