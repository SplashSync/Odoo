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

################################################################################
# Load Docker Images from Cache or Registry
################################################################################
#DB_ARGS=()
#function check_db_config() {
#    param="$1"
#    value="$2"
#    if grep -q -E "^\s*\b${param}\b\s*=" "$ODOO_RC" ; then
#        value=$(grep -E "^\s*\b${param}\b\s*=" "$ODOO_RC" |cut -d " " -f3|sed 's/["\n\r]//g')
#    fi;
#    DB_ARGS+=("--${param}")
#    DB_ARGS+=("${value}")
#}

title "[$CI_REGISTRY_IMAGE:$ODOO_VERSION] Build & Upload Docker Images"
################################################################
# Connect Docker to GitLab
subtitle "Connect Docker to GitLab"
docker login -u gitlab-ci-token -p $CI_BUILD_TOKEN registry.gitlab.com

if [ -f "images/postgres.10.tar" ]; then

  docker import images/postgres.10.tar
#  echo "[ODOO BOOT] Normal Mode"
#  check_odoo_config "init" "$ODOO_MODULES"
#else
#  echo "[ODOO BOOT] FAST Mode"
fi
mkdir -p "images"
subtitle "Before Push"
ls -l ./images
docker image ls

docker pull postgres:10
docker save -o images/postgres.10.tar postgres:10

subtitle "After Push"
ls -l ./images
docker image ls

#################################################################
## Build & Upload Odoo Docker Image
#subtitle "Build & Upload Odoo Docker Image"
#sed -i "s|_ODOO_VERSION_|${ODOO_VERSION}|g" ci/Dockerfile
#docker build -t $CI_REGISTRY_IMAGE:$ODOO_VERSION ci
#docker push $CI_REGISTRY_IMAGE:$ODOO_VERSION
#################################################################
## Build & Upload Postgres Docker Image
#subtitle "Build & Upload Postgres Docker Image"
#docker pull postgres:10
#docker image tag postgres:10 $CI_REGISTRY_IMAGE:db
#docker push $CI_REGISTRY_IMAGE:db