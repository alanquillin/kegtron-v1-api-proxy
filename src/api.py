#!python3

import argparse
import logging
import os
from struct import unpack
import sys
from time import sleep
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from gevent.pywsgi import WSGIServer

from lib.logging import init as init_logging
from lib import kegtron
from lib.json import KegtronProxyJsonEncoder

LOG = logging.getLogger(__name__)

app = Flask(__name__)
#app.json_encoder = KegtronProxyJsonEncoder

kegtron_devices = {}

PREFIX = "/api/v1"
INTERNAL_PREFIX = "/api/internal/v1"


@app.route(f'{PREFIX}/health')
def health():
    return "We are up and running!"


@app.route(f'{PREFIX}/ping')
def ping():
    return "pong"


@app.route(f'{PREFIX}/devices')
def get_devices_int():
    return jsonify(kegtron_devices)


@app.route(f'{PREFIX}/devices/<string:id>', methods=['GET'])
def get_device(id):
    data = kegtron_devices.get(id)
    if not data:
        return 404

    return jsonify(data), 200


@app.route(f'{PREFIX}/devices/<string:id>/rpc/Kegtron.ResetVolume', methods=['POST'])
async def reset_volume_rpc(id):
    device = kegtron_devices.get(id)
    if not device:
        return f'unknow device with id {id}', 404

    data = request.get_json()
    port_index = data.get("port")
    size = data.get("size")
    volume = data.get("startVolume")

    if port_index is None:
        port_cnt = device.get("port_cnt", 1)
        if port_cnt > 1:
            return "port value is required but not supplied.", 400
        port_index = 0

    u_data = {}
    size_key = None
    volume_key = None
    if port_index == 0:
        # u_data[kegtron.CHAR_XGATT_PULSE_ACCUM_RST_UUID] = 0x42
        size_key = kegtron.CHAR_XGATT0_VOL_SIZE_HANDLE
        volume_key = kegtron.CHAR_XGATT0_VOL_START_HANDLE
    elif port_index == 1:
        u_data[kegtron.CHAR_XGATT1_PULSE_ACCUM_RST_HANDLE] = 0x42
        size_key = kegtron.CHAR_XGATT1_VOL_SIZE_HANDLE
        volume_key = kegtron.CHAR_XGATT1_VOL_START_HANDLE
    else:
        return f'unknown port index: {port_index}.  Must be 0 or 1', 400

    if size:
        u_data[size_key] = size

    if volume:
        u_data[volume_key] = volume

    LOG.debug(f'attempting to write data to device: {u_data}')
    await kegtron.write_chars(device, u_data)

    return jsonify({"success": True}), 200


# @app.route(f'{PREFIX}/devices/<string:id>/rpc/Kegtron.UnlockWrite', methods=['POST'])
# async def unlock_write_rpc(id):
#     device = kegtron_devices.get(id)
#     if not device:
#         return f'unknow device with id {id}', 404

#     await kegtron.unlock(device)

#     return jsonify({"success": True}), 200

@app.route(f'{PREFIX}/devices/<string:id>/rpc/Kegtron.UnlockWrite', methods=['POST'])
async def unlock_write_rpc(id):
    device = kegtron_devices.get(id)
    if not device:
        return f'unknow device with id {id}', 404

    data = request.get_json()
    port_index = data.get("port")

    if port_index is None:
        port_cnt = device.get("port_cnt", 1)
        if port_cnt > 1:
            return "port value is required but not supplied.", 400
        port_index = 0

    key = None
    if port_index == 0:
        key = kegtron.CHAR_XGATT0_WR_UNLOCK_HANDLE
    elif port_index == 1:
        key = kegtron.CHAR_XGATT1_WR_UNLOCK_HANDLE
    else:
        return f'unknown port index: {port_index}.  Must be 0 or 1', 400

    await kegtron.write_chars(device, {key: kegtron.XGATT_WR_UNLOCK_VALUE})

    return jsonify({"success": True}), 200


@app.route(f'{INTERNAL_PREFIX}/devices', methods=['POST'])
def save_device():
    data = request.get_json()
    id = data.get("id")

    if not id:
        return "The `id` field is required.", 400

    if id in kegtron_devices.keys():
        return "The device already exists", 400

    kegtron_devices[id] = data

    return jsonify({"created": True}), 201


@app.route(f'{INTERNAL_PREFIX}/devices/<string:id>', methods=['PUT'])
def update_device(id):
    original_data = kegtron_devices.get(id)
    data = request.get_json()

    if not original_data:
        kegtron_devices[id] = data
    else:
        original_data.update(data)
        kegtron_devices[id] = original_data

    return jsonify({"updated": True}), 200


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # parse logging level arg:
    parser.add_argument(
        "-l",
        "--log",
        dest="loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=os.environ.get("LOG_LEVEL", "INFO").upper(),
        help="Set the logging level",
    )
    args = parser.parse_args()

    init_logging()
    

    ignore_logging_modules = ['bleson']
    for i in ignore_logging_modules:
        _l = logging.getLogger(i)
    _l.setLevel(logging.ERROR)

    log_level = getattr(logging, args.loglevel)
    LOG.setLevel(log_level)

    port = 5000

    # LOG.debug("app.config: %s", app.config)
    # LOG.debug("config: %s", app_config.data_flat)
    LOG.info("Serving on port %s", port)
    http_server = WSGIServer(('', port), app)

    try:
        LOG.debug(f'Starting API service on port {port}')
        http_server.serve_forever()
    except KeyboardInterrupt:
        LOG.info("User interrupted - Goodbye")
        sys.exit()