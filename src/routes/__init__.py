from lib.json import KegtronProxyJsonEncoder

from flask import Flask

APP_NAME = "kegtron_v1_api_proxy"

def create_app(config):
    app = Flask(APP_NAME)
    app.config = config
    app.json_encoder = KegtronProxyJsonEncoder

    return app

def print_routes(app, print_fn=None):
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        line = "{:30s} {:20s} {}".format(rule.endpoint, methods, rule)
        output.append(line)

    for line in sorted(output):
        if print_fn:
            print_fn(line)
        else:
            app.logger.debug(line)
