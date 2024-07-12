import argparse
import os
import logging
from datetime import datetime
import sys

from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from flask import jsonify
import requests

from lib.logging import init as init_logging 
from lib.config import Config
from lib.time import utcnow_aware
from kegtron import parser as kegtron_parser

LOG = logging.getLogger("ble_scanner")
CONFIG = Config()
proxy_url_prefix = None

kegtron_devices = {}


def name_to_id(name):
    return name.lower().replace(" ", "-")


def to_json(data):
    if isinstance(data, dict):
        for k, v in data.items():
            data[k] = to_json(v)    
        return data 
    
    if isinstance(data, datetime):
        return data.isoformat()
    
    return data

def add_new_dev(addr, name, adv):
    data = {"mac": addr, "name": name, "id": name_to_id(name), "ports": {}}
    if save_device(data):
        kegtron_devices[addr] = data
        LOG.info(f'Discovered new device: {data})')


def save_device(data):
    if not CONFIG.get("proxy.enabled"):
        return True

    LOG.info(f'Saving device to proxy: "{data.get("name")}"')
    LOG.debug(f'Device data: {data}')
    r = requests.post(f'{proxy_url_prefix}/devices', json=to_json(data))
    if r.status_code != 201:
        if r.status_code == 400 and "The device already exists" in r.text:
            LOG.debug("Device already exists, so we are good!")
            return True
        else:    
            LOG.error(f'Failed to save new device. Status Code: {r.status_code}, Message: {r.text}')
            return False
    else:
        LOG.debug('Device data saved!')
        return True


def update_device(data):
    if not CONFIG.get("proxy.enabled"):
        return

    # TODO This is going to get chatty.  Should store that hash for the data and last saved time and on update on a change to the device OR after a period of time.  
    LOG.debug(f'Updating device "{data.get("name")}" on proxy.  Device data: {data}')
    r = requests.put(f'{proxy_url_prefix}/devices/{data.get("id")}', json=to_json(data))
    if r.status_code != 200:
        LOG.error(f'Failed to update device data. Status Code: {r.status_code}, Message: {r.text}')
    else:
        LOG.debug('Device data updated!')


def on_adv(adv):
    addr = adv.address.string
    if(addr not in kegtron_devices.keys()):
        if adv.short_name and adv.short_name.startswith("Kegtron"):
            add_new_dev(addr, adv.short_name, adv)
        elif adv.complete_name and adv.complete_name.startswith("Kegtron"):
            add_new_dev(addr, adv.complete_name, adv)

    if(addr in kegtron_devices.keys()):
        kegtron_devices[addr]["rssi"] = adv.rssi
        kegtron_devices[addr]["last_advertisement_timestamp_utc"] = utcnow_aware()
        raw_data = bytes(adv)
        LOG.debug(f'Raw Data: {raw_data}')
        try:
            parsed_data = kegtron_parser.parse(raw_data[0:31])
        except Exception as ex:
            LOG.error(f'Failed to parse Kegtron data: Error: {ex.message}, Data: {raw_data}')
            return
        
        kegtron_devices[addr]["model"] = parsed_data["model"]
        kegtron_devices[addr]["port_cnt"] = parsed_data["port_cnt"]
        
        port_data = parsed_data["port_data"]
        kegtron_devices[addr]["ports"][port_data["port_index"]] = port_data

        update_device(kegtron_devices[addr])

        LOG.debug(kegtron_devices[addr])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--log",
        dest="loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=os.environ.get("LOG_LEVEL", "INFO").upper(),
        help="Set the logging level",
        
    )
    parser.add_argument("--no-proxy", action="store_true", help="When true, do not send data to proxy service")

    args = parser.parse_args()

    CONFIG.setup(env_prefix="KENGTRON_SCANNER", config_overrides={"proxy": {"enabled": not args.no_proxy}})
    app_config = CONFIG

    proxy_url_prefix = f'{CONFIG.get("proxy.scheme")}://{CONFIG.get("proxy.hostname")}:{CONFIG.get("proxy.port")}/api/internal/v1'
    
    init_logging(config=CONFIG)

    ignore_logging_modules = ['bleson']
    for i in ignore_logging_modules:
        _l = logging.getLogger(i)
        _l.setLevel(logging.ERROR)

    log_level = getattr(logging, args.loglevel)
    LOG.setLevel(log_level)

    ble = BLERadio()
    try:
        LOG.info("Starting scanner...")
        for advertisement in ble.start_scan(ProvideServicesAdvertisement, Advertisement):
            on_adv(advertisement)

    except KeyboardInterrupt:
        LOG.info("Stopping scanner..")
        ble.stop_scan()
        LOG.info("Scanner stopped!")
        sys.exit()
