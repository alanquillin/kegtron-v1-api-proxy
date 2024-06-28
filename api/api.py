import argparse
import logging
import os
from struct import unpack
import sys
from time import sleep
from datetime import datetime, timezone

from bleson import get_provider, Observer
from flask import Flask, jsonify, request
from gevent.pywsgi import WSGIServer

from lib.logging import init as init_logging 

init_logging()
LOG = logging.getLogger("ble_scanner")
LOG.setLevel(logging.INFO)

ignore_logging_modules = ['bleson']
for i in ignore_logging_modules:
    _l = logging.getLogger(i)
    _l.setLevel(logging.ERROR)

app = Flask(__name__)


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
    log_level = getattr(logging, args.loglevel)
    LOG.setLevel(log_level)

    port = 5000

    # LOG.debug("app.config: %s", app.config)
    # LOG.debug("config: %s", app_config.data_flat)
    LOG.info("Serving on port %s", port)
    http_server = WSGIServer(('', port), app)

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        LOG.info("User interrupted - Goodbye")
        sys.exit()