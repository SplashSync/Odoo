#!/bin/sh
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
################################################################################

################################################################
# Force Failure if ONE line Fails
set -e
################################################################
# import Layout Functions
. resources/scripts/functions.sh
################################################################
# Wait Until Odoo Container Started
title "TEST --> Execute Tests from Toolkit"
echo "Execute ${SPLASH_TYPES} Sequence on ${SPLASH_SEQUENCE}"
docker compose exec -T toolkit php vendor/bin/phpunit --testdox --log-junit test-report.xml
subtitle "TEST --> Archive Odoo Tests Logs"
docker cp "$(docker compose ps -q toolkit)":/app/test-report.xml  "$(pwd)"/reports/test-report.xml
docker compose logs --tail="2000" app >> logs/odoo.tests.txt

subtitle "TOOLKIT --> Build Splash Manifest"
docker compose exec -T toolkit php bin/console splash:server:manifest
docker cp "$(docker compose ps -q toolkit)":/app/splash.json  "$(pwd)"/manifest/splash.json
docker cp "$(docker compose ps -q toolkit)":/app/splash.yml   "$(pwd)"/manifest/splash.yml
echo "Manifests exported to $(pwd)/manifest"