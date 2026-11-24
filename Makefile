################################################################################
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#
################################################################################

# Splash connector for Odoo (Gen 3). Everything runs in Docker, in the Odoo image of this branch.

COMPOSE     ?= docker compose
TOOLS       ?= $(COMPOSE) run --rm -T quality
PULL        ?= odoo db quality
TOOLKIT     := $(COMPOSE) exec -T toolkit
WS          ?= ThisIsOdooC0WsId
MANIFESTS   := splash.yml splash.json swagger.json
SUITE       ?= Validator
TYPES       ?= ThirdParty Address Product

.DEFAULT_GOAL := help
.PHONY: help pull build push up stop prune reset update logs shell lint style stan quality test manifest

help:		## Show this help
	@grep -hE '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

################################################################################
# Docker Stack
################################################################################

pull:		## Pull the images of the branch from the registry (PULL: Odoo, pre-initialised database, tools)
	$(COMPOSE) --profile tools pull $(PULL)

build:		## Build the images (only when docker/ changes: the addon & splashpy are mounted)
	$(COMPOSE) --profile tools build

push:		## Push the built images to the registry (docker login registry.gitlab.com first)
	$(COMPOSE) --profile tools push odoo db quality

up:		## Start Odoo, database & Toolkit (ready in seconds, nothing installed at start)
	docker network inspect splashsync >/dev/null 2>&1 || docker network create splashsync --attachable
	$(COMPOSE) up -d --wait --no-build

stop:		## Stop the stack
	$(COMPOSE) stop

prune:		## Remove containers, built images & network
	$(COMPOSE) --profile tools down -v --rmi local --remove-orphans

reset:		## Reset the database to the image state (recreate the db container)
	$(COMPOSE) up -d --wait --no-build --force-recreate db odoo

update:		## Upgrade the addon in the running database (models, views or data changed)
	$(COMPOSE) exec -T odoo odoo -c /etc/odoo/odoo.conf --db_host=db.odoo.local --db_user=odoo --db_password=odoo -u splashsync --stop-after-init --http-port=8070
	$(COMPOSE) restart odoo

logs:		## Follow Odoo logs
	$(COMPOSE) logs -f odoo

shell:		## Odoo shell on the database
	$(COMPOSE) exec odoo odoo shell -c /etc/odoo/odoo.conf --db_host=db.odoo.local --db_user=odoo --db_password=odoo --http-port=8070

################################################################################
# Quality (BadPixxel standard targets) - in the Odoo image of the branch (CI: TOOLS= in the dev image)
################################################################################

lint:		## Linters: ruff, pylint-odoo
	$(TOOLS) ruff check splashsync docker
	$(TOOLS) pylint --rcfile=.pylintrc splashsync

style:		## Code style (ruff format) & security (bandit)
	$(TOOLS) ruff format --check splashsync docker
	$(TOOLS) bandit -q -c pyproject.toml -r splashsync

stan:		## Static analysis: mypy strict
	$(TOOLS) mypy

quality: lint style stan	## Run ALL checks

################################################################################
# Functional Tests (Toolkit 3.0)
################################################################################

test:		## Run the Toolkit suites, one run per object type (TYPES="Product", SEQUENCE="[Gen 3] Odoo C1", FIELDS=sku, FILTER=O11)
	@for type in $(TYPES); do \
		echo "=== $$type"; \
		$(COMPOSE) exec -T -e SPLASH_TYPES=$$type -e SPLASH_SEQUENCE="$(SEQUENCE)" -e SPLASH_FIELDS="$(FIELDS)" toolkit \
			php vendor/bin/phpunit -c phpunit.odoo.xml --testsuite $(SUITE) $(if $(FILTER),--filter "$(FILTER)") || exit 1; \
	done

manifest:	## Generate Splash manifests (splash.yml, splash.json, swagger.json) with the Toolkit (WS=...)
	$(TOOLKIT) bin/console splash:server:manifest --ws=$(WS)
	$(TOOLKIT) bin/console splash:server:swagger --ws=$(WS)
	@for file in $(MANIFESTS); do $(COMPOSE) cp toolkit:/app/$$file ./$$file || exit 1; done
