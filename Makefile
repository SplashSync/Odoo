################################################################################
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) Splash Sync <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#
#  @author Bernard Paquier <contact@splashsync.com>
#
################################################################################

### ——————————————————————————————————————————————————————————————————
### —— Local Makefile
### ——————————————————————————————————————————————————————————————————

include resources/make/docker.mk

.PHONY: test
test: ## Execute Functional Test
	@$(DOCKER_COMPOSE) exec toolkit php vendor/bin/phpunit $(opt)
