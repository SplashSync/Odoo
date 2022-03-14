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

title "[$CI_REGISTRY_IMAGE:$ODOO_VERSION] Build & Upload Docker Image"
################################################################
# Connect Docker to GitLab
subtitle "Connect Docker to GitLab"
docker login -u gitlab-ci-token -p $CI_BUILD_TOKEN registry.gitlab.com
################################################################
# Build & Upload Odoo Docker Image
subtitle "Build & Upload Odoo Docker Image"
sed -i "s|_ODOO_VERSION_|${ODOO_VERSION}|g" ci/Dockerfile
docker build -t $CI_REGISTRY_IMAGE:$ODOO_VERSION ci
docker push $CI_REGISTRY_IMAGE:$ODOO_VERSION
################################################################
# Build & Upload Postgres Docker Image
subtitle "Build & Upload Postgres Docker Image"
docker pull postgres:10
docker image tag postgres:10 $CI_REGISTRY_IMAGE:db
docker push $CI_REGISTRY_IMAGE:db