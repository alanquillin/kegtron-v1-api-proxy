#!python3

import argparse
import logging
from struct import unpack
from time import sleep
from datetime import datetime, timezone
import sys

from bleson import get_provider, Observer

from lib.logging import init as init_logging 
from lib.parsers import kegtron

init_logging()
LOG = logging.getLogger("ble_scanner")
LOG.setLevel(logging.INFO)

ignore_logging_modules = ['bleson']
for i in ignore_logging_modules:
    _l = logging.getLogger(i)
    _l.setLevel(logging.ERROR)

class BLEScanner():
    def __init__(self,fn=None):
        self.provider = get_provider()
        self.adapter = self.provider.get_adapter()
        self.observer = Observer(self.adapter)

        if not fn:
            fn = self.on_advertisement
        self.observer.on_advertising_data = fn

        self.kegtron_devices = {}

    def start(self):
        self.observer.start()
    
    def stop(self):
        self.observer.stop()

    def on_advertisement(self, advertisement):
        addr = advertisement.address.address
        name = advertisement.name

        if not name is None:
            if name.startswith("Kegtron"):
                rssi = advertisement.rssi

                if not addr in kegtron_devices.keys():
                    data = {"address": addr, "name": name, "ports": {}}
                    LOG.debug(f'Discovered new device: {data})')
                    self.kegtron_devices[addr] = data
                self.kegtron_devices[addr]["rssi"] = rssi
                self.kegtron_devices[addr]["last_advertisement_timestamp_utc"] = datetime.now(timezone.utc)

        if addr in self.kegtron_devices.keys():
            raw_data = advertisement.raw_data
            mfg_data = raw_data[10::]
            if len(mfg_data) >= 31:
                mfg_data = mfg_data[0:31]
                parsed_data = kegtron.parse(mfg_data)

                self.kegtron_devices[addr]["model"] = parsed_data["model"]
                self.kegtron_devices[addr]["port_cnt"] = parsed_data["port_cnt"]
                
                port_data = parsed_data["port_data"]
                self.kegtron_devices[addr]["ports"][port_data["port_num"]] = port_data

                LOG.info(self.kegtron_devices[addr])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.debug:
        LOG.setLevel(logging.DEBUG)

    scanner = BLEScanner()

    try:
        scanner.start()
        LOG.debug("Scanner started...")
        sleep(30)
    except KeyboardInterrupt:
        scanner.stop()
        sys.exit()
