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
cpt=0;
docker-compose exec -T toolkit bash -c 'curl -s -o /dev/null -w ''%{http_code}'' odoo:80'
while [[ "$(docker-compose exec -T toolkit bash -c 'curl -s -o /dev/null -w ''%{http_code}'' odoo:80')" != "200" ]];
do
  ((cpt+=1));
  echo "$cpt : Wait for Odoo...";
  docker-compose logs --tail="100" odoo
  sleep 10;
  if [$cpt -eq 6]
  then
      echo "Odoo takes too long to start...";
      exit 1;
  fi
done
title "TEST --> Odoo Started !"
docker-compose logs --tail="2000" odoo >> logs/odoo.init.txt