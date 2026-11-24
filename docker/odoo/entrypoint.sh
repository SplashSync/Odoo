#!/bin/bash
################################################################################
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#
################################################################################

# Odoo start: the database is ready in the "db" image, nothing is installed here.
#   ODOO_UPDATE=1   upgrade the splashsync addon before start (models / views changed, CI)
#   ODOO_DEV=1      developer mode: reload on code change, views read from files

set -e

ARGS=(-c /etc/odoo/odoo.conf --db_host="${DB_HOST:-db}" --db_user="${DB_USER:-odoo}" --db_password="${DB_PASSWORD:-odoo}")

if [ "$1" = "odoo" ]; then
    shift
    if [ "${ODOO_UPDATE:-0}" = "1" ]; then
        echo "[SPLASH] Upgrade splashsync addon"
        odoo "${ARGS[@]}" -u splashsync --stop-after-init
    fi
    if [ "${ODOO_DEV:-0}" = "1" ]; then
        ARGS+=(--dev=reload,xml)
    fi
    exec odoo "${ARGS[@]}" "$@"
fi

exec "$@"
