SHELL := /bin/bash

STACK_NAME=mlapi-dev
BASE_STACK_NAME=sunxi/mlplatform-infra/dev
PULUMI_CMD=pulumi --non-interactive --stack $(STACK_NAME) --cwd infra/

install-deps:
	curl -fsSL https://get.pulumi.com | sh
	npm install -C infra/
	sudo pip3 install poetry --upgrade
	poetry install

train:
	poetry run train

