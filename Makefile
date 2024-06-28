#!make
ROOT_PY3 := python3

POETRY := $(shell which poetry)
POETRY_VARS :=
ifeq ($(shell uname -s),Darwin)
	HOMEBREW_OPENSSL_DIR := $(shell brew --prefix openssl)
	POETRY_VARS += CFLAGS="-I$(HOMEBREW_OPENSSL_DIR)/include"
	POETRY_VARS += LDFLAGS="-L$(HOMEBREW_OPENSSL_DIR)/lib"
endif

ifeq ($(shell uname -p),arm)
	POETRY_VARS += arch -arm64
endif

BLACK := $(POETRY) run black
ISORT := $(POETRY) run isort
PYLINT := $(POETRY) run pylint
PYTEST := $(POETRY) run pytest
PYTHON := $(POETRY) run python3

ifeq ($(POETRY),)
$(error Poetry is not installed and is required)
endif

ifneq ("$(wildcard .env)","")
    include .env
	export $(shell sed 's/=.*//' .env)
endif

ifeq ($(TAG_LATEST),true)
override DOCKER_BUILD_ARGS += -t $(IMAGE_REPOSITORY)/$(REPOSITORY_IMAGE):latest
endif

.PHONY: depends update-depends run-dev-local run-local lint format #create-migration

# dependency targets

depends: 
	$(POETRY_VARS) $(POETRY) install --no-root

update-depends:
	$(POETRY_VARS) $(POETRY) update


# Targets for running the app

run-dev-local: build-dev build-db-seed
	$(PYTHON) api/api.pi --debug

run-local:
	$(PYTHON) api/api.pi

scan:
	$(PYTHON) scan.py 

scan-dev:
	$(PYTHON) scan.py --debug

# run-db-migrations:
# 	./migrate.sh upgrade head

# Testing and Syntax targets

lint:
	$(ISORT) --check-only api
	pushd ./api && $(PYLINT) .	 && popd
	$(BLACK) --check api

format:
	$(ISORT) api
	$(BLACK) api

# Migrations

# create-migration: 
# 	pushd ./api && ./migrate.sh create $@ && popd
