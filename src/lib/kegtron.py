import logging
from struct import unpack
from datetime import datetime, timezone

from bleak import BleakClient, BleakScanner

from lib.exceptions import InvalidKegtronAdvertisementData

LOG = logging.getLogger("kegtron")


KEGTRON_SIZE_DICT = {
    9464: "Half Corny (2.5 gal)",
    18927: "Corny (5.0 gal)",
    19711: "1/6 Barrel (5.167 gal)",
    19550: "1/6 Barrel (5.167 gal)",
    20000: "20L (5.283 gal)",
    20457: "Pin (5.404 gal)",
    29337: "1/4 Barrel (7.75 gal)",
    40915: "Firkin (10.809 gal)",
    50000: "50L (13.209 gal)",
    58674: "1/2 Barrel (15.5 gal)",
}

SVC_FLOW_MON_0_HANDLE = 17
SVC_FLOW_MON_0_UUID = "25386e40-e04b-49ad-b0d0-5db64bbffe32"
SVC_FLOW_MON_1_HANDLE = 80
SVC_FLOW_MON_1_UUID = "17faa784-ddc8-428b-a9cb-d5a989c9002b"

XGATT_WR_UNLOCK_VALUE = 0xDEAD3056
CHAR_XGATT_WR_UNLOCK_UUID = "fbbb8d81-4f8f-4632-82fc-4ea2f56ed0ca"
CHAR_XGATT0_WR_UNLOCK_HANDLE = 62
CHAR_XGATT1_WR_UNLOCK_HANDLE = 125

CHAR_XGATT_PULSE_ACCUM_RST_UUID = "bfd0a23c-45a4-4362-aad4-6e78840d4957"
CHAR_XGATT0_PULSE_ACCUM_RST_HANDLE = 41
CHAR_XGATT1_PULSE_ACCUM_RST_HANDLE = 104

CHAR_XGATT_VOL_START_UUID = "385c9e36-14c7-4cc8-aa7b-26db918828a3"
CHAR_XGATT0_VOL_START_HANDLE = 27
CHAR_XGATT1_VOL_START_HANDLE = 90

CHAR_XGATT_VOL_SIZE_UUID = "f1849d4b-a033-4d97-a988-3259a3498b95"
CHAR_XGATT0_VOL_SIZE_HANDLE = 24
CHAR_XGATT1_VOL_SIZE_HANDLE = 87


def parse(data):
    if len(data) == 22:
        return parse_advertisement(data)

    if len(data) == 31:
        return parse_scan(data)

    raise InvalidKegtronAdvertisementData(message=f'Cannot parse Kegtron packet:  Invalid packet length: {len(data)}')


def parse_advertisement(data):
    return {}


def parse_scan(data):
    mfg_data = data[0:31]
    LOG.debug("Parsing Kegtron Scan Response Data")

    (ttl_len, type, cic, keg_vol, vol_start, vol_disp, port, port_name) = unpack(">BBHHHHB20s", mfg_data)

    if ttl_len != 0x1E:
        raise InvalidKegtronAdvertisementData(message=f'Total Length should be 0x1E (30), but received {ttl_len}')

    if type != 0xFF:
        raise InvalidKegtronAdvertisementData(message=f'Type byte should be 0xFF (255), but received {type}')

    if cic != 0xFFFF:
        raise InvalidKegtronAdvertisementData(message=f'Company Identifier Code (CIC) should be 0xFFFF (65535), but received {cic}')

    if port & (1 << 6):
        model = "Kegtron KT-200"
        port_cnt = 2
        if port & (1 << 4):
            port_index = 1
        else:
            port_index = 0
    else:
        model = "Kegtron KT-100"
        port_index = 0
        port_cnt = 1

    if port & (1 << 0):
        port_configured = True
    else:
        port_configured = False

    port_data = {
        "keg_vol_ml": keg_vol,
        "start_volume": vol_start,
        "Volume_dispensed_ml": vol_disp,
        "port_name": port_name.decode("utf-8"),
        #"last_update_timestamp_utc": datetime.now(timezone.utc),
        "configured": port_configured,
        "port_index": port_index
    }
    LOG.debug(f'Parsed data: model: {model}, port count: {port_cnt}, port: {port_data}')

    return {
        "model": model,
        "port_cnt": port_cnt,
        "port_data": port_data
    }


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

    data = {CHAR_XGATT0_WR_UNLOCK_HANDLE: XGATT_WR_UNLOCK_VALUE}
    if port_cnt > 1:
        data[CHAR_XGATT1_WR_UNLOCK_HANDLE] = XGATT_WR_UNLOCK_VALUE

    await write_chars(device, data)
