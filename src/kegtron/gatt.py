import logging
from struct import unpack
from datetime import datetime, timezone

from bleak import BleakClient, BleakScanner

from lib.exceptions import InvalidKegtronAdvertisementData
import kegtron

LOG = logging.getLogger("kegtron.gatt")


async def write_chars(device, data, response=True):
    mac = device.get("mac")

    async with BleakClient(mac) as client:
        print(f'connected to Kegtron at {mac}')
        for k, v in data.items():
            client.services.get_characteristic(k)
            print(f"writing '{v}' to character handle '{k}'")
            await client.write_gatt_char(k, v, response=response)


async def unlock(device):
    port_cnt = device.get("port_cnt", 1)

    data = {kegtron.CHAR_XGATT0_WR_UNLOCK_HANDLE: kegtron.XGATT_WR_UNLOCK_VALUE}
    if port_cnt > 1:
        data[kegtron.CHAR_XGATT1_WR_UNLOCK_HANDLE] = kegtron.XGATT_WR_UNLOCK_VALUE

    await write_chars(device, data)
