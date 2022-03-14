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
. app/scripts/functions.sh


################################################################
# Init Docker
title "BEFORE --> Init Docker"
docker info
#      # Install Git & Docker Compose
#      - apk add --no-cache git docker-compose
#      # Load SplashPy Module
#      - rm -Rf ../Py-Core
#      - git clone --depth=1 https://github.com/SplashSync/PyCore.git ../Py-Core
#      - chmod 7777 -Rf ../Py-Core
#      # Configure Docker Compose
#      - sed -i 's|odoo:12|${ODOO_VERSION}|g' docker-compose.yml
#      # Build Docker Compose
#      - mkdir logs
#      - docker network create splashsync --attachable
#      - docker-compose up -d