from data import devices as deviceDB

from flask import current_app as app, jsonify, request


INTERNAL_PREFIX = "/api/internal/v1"

@app.route(f'{INTERNAL_PREFIX}/devices', methods=['POST'])
def save_device():
    data = request.get_json()
    id = data.get("id")

    if not id:
        return "The `id` field is required.", 400

    if deviceDB.exists(id):
        return "The device already exists", 400

    deviceDB.create(id, data)

    return jsonify({"created": True}), 201


@app.route(f'{INTERNAL_PREFIX}/devices/<string:id>', methods=['PUT'])
def update_device(id):
    data = request.get_json()

    deviceDB.update(id, data)

    return jsonify({"updated": True}), 200