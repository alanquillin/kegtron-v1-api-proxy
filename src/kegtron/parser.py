import logging
from struct import unpack
from datetime import datetime, timezone

from bleak import BleakClient, BleakScanner

from lib.exceptions import InvalidKegtronAdvertisementData

LOG = logging.getLogger("kegtron.parser")


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