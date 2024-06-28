import argparse
import logging
from struct import unpack
from time import sleep
from datetime import datetime, timezone

from bleson import get_provider, Observer

from api.lib.logging import init as init_logging 

init_logging()
LOG = logging.getLogger("ble_scanner")
LOG.setLevel(logging.INFO)

ignore_logging_modules = ['bleson']
for i in ignore_logging_modules:
    _l = logging.getLogger(i)
    _l.setLevel(logging.ERROR)

kegtron_devices = {}

def on_advertisement(advertisement):
    addr_obj = advertisement.address
    addr = addr_obj.address
    name = advertisement.name
    rssi = advertisement.rssi

    if not name is None:
        if name.startswith("Kegtron"):
            if not addr in kegtron_devices.keys():
                data = {"address": addr_obj, "name": name, "ports": {}}
                LOG.debug(f'Discovered new device: {data})')
                kegtron_devices[addr] = data
            kegtron_devices[addr]["rssi"] = rssi
            kegtron_devices[addr]["last_advertisement_timestamp_utc"] = datetime.now(timezone.utc)

    if addr in kegtron_devices.keys():
        raw_data = advertisement.raw_data
        mfg_data = raw_data[10::]
        if len(mfg_data) >= 31:
            mfg_data = mfg_data[0:31]
            LOG.debug("Parsing Kegtron Scan Response Data")
            
            (keg_vol, vol_start, vol_disp, port, port_name) = unpack(">HHHB20s", mfg_data[4::])

            if port & (1 << 6):
                model = "Kegtron KT-200"
                port_cnt = 2
                if port & (1 << 4):
                    port_num = 2
                else:
                    port_num = 1
            else:
                model = "Kegtron KT-100"
                port_num = 1
                port_cnt = 1

            if port & (1 << 0):
                port_configured = True
            else:
                port_configured = False

            data = {
                "keg_vol_ml": keg_vol,
                "start_volume": vol_start,
                "Volume_dispensed_ml": vol_disp,
                "port_name": port_name.decode("utf-8"),
                "last_update_timestamp_utc": datetime.now(timezone.utc),
                "configured": port_configured
            }
            LOG.debug(f'Parsed data: {data}')
            kegtron_devices[addr]["model"] = model
            kegtron_devices[addr]["port_cnt"] = port_cnt
            kegtron_devices[addr]["ports"][port_num] = data

            LOG.info(kegtron_devices[addr])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.debug:
        LOG.setLevel(logging.DEBUG)

    adapter = get_provider().get_adapter()
    observer = Observer(adapter)
    observer.on_advertising_data = on_advertisement

    observer.start()
    sleep(30)
    observer.stop()