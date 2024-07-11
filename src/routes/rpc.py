from data import devices as deviceDB
from routes.public import PREFIX

from flask import current_app as app, jsonify

@app.route(f'{PREFIX}/devices/<string:id>/rpc/Kegtron.ResetVolume', methods=['POST'])
async def reset_volume_rpc(id):
    return "Method not yet implemented", 405
    # device = deviceDB.get(id)
    # if not device:
    #     return f'unknow device with id {id}', 404

    # data = request.get_json()
    # port_index = data.get("port")
    # size = data.get("size")
    # volume = data.get("startVolume")

    # if port_index is None:
    #     port_cnt = device.get("port_cnt", 1)
    #     if port_cnt > 1:
    #         return "port value is required but not supplied.", 400
    #     port_index = 0

    # u_data = {}
    # size_key = None
    # volume_key = None
    # if port_index == 0:
    #     u_data[kegtron.CHAR_XGATT0_PULSE_ACCUM_RST_HANDLE] = 0x42
    #     size_key = kegtron.CHAR_XGATT0_VOL_SIZE_HANDLE
    #     volume_key = kegtron.CHAR_XGATT0_VOL_START_HANDLE
    # elif port_index == 1:
    #     u_data[kegtron.CHAR_XGATT1_PULSE_ACCUM_RST_HANDLE] = 0x42
    #     size_key = kegtron.CHAR_XGATT1_VOL_SIZE_HANDLE
    #     volume_key = kegtron.CHAR_XGATT1_VOL_START_HANDLE
    # else:
    #     return f'unknown port index: {port_index}.  Must be 0 or 1', 400

    # if size:
    #     u_data[size_key] = size

    # if volume:
    #     u_data[volume_key] = volume

    # app.logger.debug(f'attempting to write data to device: {u_data}')
    # await gatt.write_chars(device, u_data)

    # return jsonify({"success": True}), 200


@app.route(f'{PREFIX}/devices/<string:id>/rpc/Kegtron.UnlockWriteAll', methods=['POST'])
async def unlock_write_all_rpc(id):
    return "Method not yet implemented", 405
    # device = deviceDB.get(id)
    # if not device:
    #     return f'unknow device with id {id}', 404

    # await gatt.unlock(device)

    # return jsonify({"success": True}), 200

@app.route(f'{PREFIX}/devices/<string:id>/rpc/Kegtron.UnlockWrite', methods=['POST'])
async def unlock_write_rpc(id):
    return "Method not yet implemented", 405
    # device = deviceDB.get(id)
    # if not device:
    #     return f'unknow device with id {id}', 404

    # data = request.get_json()
    # port_index = data.get("port")

    # if port_index is None:
    #     port_cnt = device.get("port_cnt", 1)
    #     if port_cnt > 1:
    #         return "port value is required but not supplied.", 400
    #     port_index = 0

    # key = None
    # if port_index == 0:
    #     key = kegtron.CHAR_XGATT0_WR_UNLOCK_HANDLE
    # elif port_index == 1:
    #     key = kegtron.CHAR_XGATT1_WR_UNLOCK_HANDLE
    # else:
    #     return f'unknown port index: {port_index}.  Must be 0 or 1', 400

    # await gatt.write_chars(device, {key: kegtron.XGATT_WR_UNLOCK_VALUE})

    # return jsonify({"success": True}), 200
