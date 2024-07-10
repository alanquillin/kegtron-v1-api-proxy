# Python base
# ############################################################
FROM python:3.11-slim-bullseye as python-base

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential libpq-dev libffi-dev libssl-dev bluetooth    \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip 
RUN pip install setuptools wheel
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
RUN pip install "cryptography<3.5"
RUN pip install "poetry>=1.2.2"

RUN poetry config virtualenvs.in-project true
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --only main --no-root
RUN poetry run pip install psycopg2-binary "flask[async]"
RUN poetry run pip install -U bleak

RUN apt-get purge -y --auto-remove gcc build-essential libffi-dev libssl-dev

ENV PYTHONUNBUFFERED=1
ENV CONFIG_BASE_DIR=/kegtron-v1-api-proxy/config

COPY src /kegtron-v1-api-proxy/src
COPY entrypoint.sh /kegtron-v1-api-proxy/src

WORKDIR /kegtron-v1-api-proxy/src

EXPOSE 5000

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]