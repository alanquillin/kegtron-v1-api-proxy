#! /bin/bash

if [ "${RUN_ENV}" = "dev" ]; then
    export FLASK_ENV="development"
    export LOG_LEVEL_PARAM="--log DEBUG"
fi

if [ "${KEGTRON_PROXY_ROLE}" = "scanner" ]; then
    service dbus start
    bluetoothd &
    poetry run python scan.py ${LOG_LEVEL_PARAM}
fi

if [ "${KEGTRON_PROXY_ROLE}" = "api" ]; then
    poetry run python api.py ${LOG_LEVEL_PARAM}
fi
