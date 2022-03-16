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

function import_image() {
    name="$1"
    md5=$(echo -n $name | md5sum | awk '{print $1}')
    if [ -f "images/$md5.tar" ]; then
        subtitle "Load Docker Image from Cache: $name"
        cat "images/$md5.tar" | docker import - $name
    else
        subtitle "Load Docker Image from Registry: $name"
        docker pull postgres:10
        subtitle "Save Docker Image to Cache: $name"
        mkdir -p "images"
        docker save -o "images/$md5.tar" $name
    fi
    docker image ls
}

title "[$CI_REGISTRY_IMAGE:$ODOO_VERSION] Build & Upload Docker Images"
################################################################
# Connect Docker to GitLab
subtitle "Connect Docker to GitLab"
docker login -u gitlab-ci-token -p $CI_BUILD_TOKEN registry.gitlab.com

import_image "postgres:10"

#if [ -f "images/postgres.10.tar" ]; then
#
#  cat images/postgres.10.tar | docker import - postgres:10
##  echo "[ODOO BOOT] Normal Mode"
##  check_odoo_config "init" "$ODOO_MODULES"
##else
##  echo "[ODOO BOOT] FAST Mode"
#fi
#mkdir -p "images"
#subtitle "Before Push"
#ls -l ./images
#docker image ls
#
#docker pull postgres:10
#docker save -o images/postgres.10.tar postgres:10
#
#subtitle "After Push"
#ls -l ./images
#docker image ls

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