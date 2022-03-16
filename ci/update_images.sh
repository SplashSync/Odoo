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
# Connect Docker to GitLab
subtitle "Connect Docker to GitLab"
docker login -u gitlab-ci-token -p $CI_BUILD_TOKEN registry.gitlab.com
################################################################
# Update Docker Images Cache
import_image "odoo:12" "12"
import_image "odoo:13" "13"
import_image "odoo:14" "14"
import_image "odoo:15" "14"
import_image "postgres:10" "db"
import_image "splashsync/toolkit" "toolkit"
docker image ls