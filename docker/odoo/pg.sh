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

# Local Postgres used while building the database image (init stage only).

set -e

case "$1" in
    start)  su postgres -c "${PG_BIN}/pg_ctl -D ${PGDATA} -w -l /tmp/postgres.log start" ;;
    stop)   su postgres -c "${PG_BIN}/pg_ctl -D ${PGDATA} -w -m fast stop" ;;
    exec)   su postgres -c "$2" ;;
    *)      echo "Usage: pg.sh start|stop|exec <command>" && exit 1 ;;
esac
