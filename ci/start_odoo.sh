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
#set -e
################################################################
# import Layout Functions
. scripts/functions.sh
################################################################
# Ensure Toolkit Started
title "TEST --> Start Toolkit"
docker-compose exec -T toolkit "php bin/console | grep Symfony"
################################################################
# Wait Until Odoo Container Started
title "TEST --> Start Odoo"
cpt=0;
http_code="000";
subtitle "$cpt => $http_code: Wait for Odoo...";
while [ "$http_code" != "200" ]
do
  http_code=$(docker-compose exec -T toolkit bash -c 'curl -s -o /dev/null -w ''%{http_code}'' odoo:80');
  cpt=$(( cpt+1 ));
  subtitle "$cpt => $http_code: Wait for Odoo...";
  docker-compose logs --tail="10" odoo
  sleep 10;
  if [ $cpt == '6' ];
  then
      subtitle "Odoo takes too long to start...";
      exit 1;
  fi
done
subtitle "TEST --> Odoo Started !"
docker-compose logs --tail="2000" odoo >> logs/odoo.init.txt