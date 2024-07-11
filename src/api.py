import argparse
import logging
import os
import sys

from gevent.pywsgi import WSGIServer

from lib.config import Config
from lib.logging import init as init_logging
from routes import create_app, print_routes

CONFIG = Config()

app = create_app(CONFIG)

with app.app_context():
    from routes import internal, public, rpc

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

    CONFIG.setup(env_prefix="KENGTRON_PROXY")

    init_logging(config=CONFIG, arg_log_level=args.loglevel)

    port = CONFIG.get("proxy.port")

    logger = logging.getLogger(__name__)
    logger.debug("app.config: %s", app.config)
    logger.debug("config: %s", app.config.data_flat)
    logger.info("Serving on port %s", port)
    print_routes(app)
    http_server = WSGIServer(('', port), app)

    try:
        logger.debug(f'Starting API service on port {port}')
        http_server.serve_forever()
    except KeyboardInterrupt:
        logger.info("User interrupted - Goodbye")
        sys.exit()