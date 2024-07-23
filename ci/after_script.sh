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
# Stop Container & Show Logs
title "AFTER --> Stop Docker"
docker compose stop

subtitle "AFTER --> Archive Odoo Logs"
docker compose logs --tail="2000" app >> logs/odoo.all.txt

if [ $CI_JOB_STATUS != 'success' ];
then
  subtitle "AFTER --> Show Odoo Logs"
  docker compose logs --tail="50" app
fi;
