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

dvc-pull:
    poetry run dvc --cd data/ pull

deploy: dvc-pull
    $(PULUMI_CMD) stack init $(STACK_NAME) || true
	$(PULUMI_CMD) config set baseStackName $(BASE_STACK_NAME)
	$(PULUMI_CMD) config set runID $(shell poetry run train | awk '/Run ID/{print $$NF}')
	$(PULUMI_CMD) up --yes --skip-preview