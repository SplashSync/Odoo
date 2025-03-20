### ——————————————————————————————————————————————————————————————————
### —— Docker Compose Variables
### ——————————————————————————————————————————————————————————————————

user := $(shell id -u)
group := $(shell id -g)

DOCKER := docker
DOCKER_COMPOSE := USER_ID=$(user) GROUP_ID=$(group) docker compose
DOCKER_TEST := APP_ENV=test

### ——————————————————————————————————————————————————————————————————
### —— Docker Compose Basic Actions
### ——————————————————————————————————————————————————————————————————

build:
	@echo "Building project containers..."
	$(DOCKER_COMPOSE) pull --ignore-pull-failures
	$(DOCKER_COMPOSE) build --no-cache

up:
	@echo "Launching project containers..."
	$(DOCKER_COMPOSE) up -d
	$(DOCKER_COMPOSE) ps

stop:
	@echo "Stopping project containers..."
	$(DOCKER_COMPOSE) stop
	$(DOCKER_COMPOSE) ps

reboot:
	@echo "Reboot project containers..."
	$(DOCKER_COMPOSE) stop
	$(DOCKER_COMPOSE) up -d
	$(DOCKER_COMPOSE) ps

prune:
	@echo "Prune project containers..."
	$(DOCKER_COMPOSE) down --remove-orphans
	$(DOCKER_COMPOSE) down --volumes
	$(DOCKER_COMPOSE) rm -f

running:
	$(eval RUNNING = $(shell docker compose ps --services | grep $(CONTAINER)$(ARGS)))
	@if [ ! -z $(RUNNING) ]; then echo "$(CONTAINER)$(ARGS) is running..."; return 1; else return 0; fi
	return 0





