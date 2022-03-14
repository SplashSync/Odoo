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
# Init Docker
title "BEFORE --> Init Docker"
docker info
apk add --no-cache git docker-compose
################################################################
# Load SplashPy Module
title "BEFORE --> Install Splash Py Module"
rm -Rf ../Py-Core
git clone --depth=1 https://github.com/SplashSync/PyCore.git ../Py-Core
chmod 7777 -Rf ../Py-Core
################################################################
# Configure Docker Compose
title "BEFORE --> Configure Docker Compose"
sed -i 's|odoo:12|${ODOO_VERSION}|g' ci/docker-compose.yml
mkdir logs
################################################################
# Build Docker Compose
title "BEFORE --> Start Docker Compose"
- docker-compose up -d