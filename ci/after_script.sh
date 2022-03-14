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
# Stop Container & Show Logs
title "AFTER --> Stop Docker"
docker-compose stop
title "AFTER --> Show Odoo Logs"
docker-compose logs --tail="500" odoo
title "AFTER --> Archive Odoo Logs"
docker-compose logs --tail="2000" odoo >> logs/odoo.all.txt