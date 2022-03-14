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
. scripts/functions.sh
################################################################
# Wait Until Odoo Container Started
title "TEST --> Start Toolkit"
docker-compose exec -T toolkit php bin/console
title "TEST --> Start Odoo"
docker-compose exec -T toolkit bash -c 'while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' odoo:8069)" != "200" ]]; do echo "Wait for Odoo..."; sleep 10; done'
docker-compose logs --tail="2000" odoo >> logs/odoo.init.txt