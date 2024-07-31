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
# Init Docker
title "BEFORE --> Init Docker"
docker version
docker compose version
docker login -u $CI_DEPENDENCY_PROXY_USER -p $CI_DEPENDENCY_PROXY_PASSWORD $CI_DEPENDENCY_PROXY_SERVER
################################################################
# Load SplashPy Module
subtitle "BEFORE --> Install Splash Py Module"
apk add --no-cache git
rm -Rf ../Py-Core
git clone --depth=1 https://github.com/SplashSync/PyCore.git ../Py-Core
chmod 7777 -Rf ../Py-Core
################################################################
# Configure Docker Compose
subtitle "BEFORE --> Configure Docker Compose"
cp -Rf resources/ci/docker-compose.yaml resources/docker/docker-compose.yaml
mkdir -p logs
mkdir -p manifest
mkdir -p reports
################################################################
# Build Docker Compose
subtitle "BEFORE --> Start Docker Compose"
if [[ "$(docker network ls | grep "splashsync")" == "" ]] ; then
    docker network create splashsync
fi
docker compose up -d --force-recreate --quiet-pull
docker image ls