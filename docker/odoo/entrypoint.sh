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

set -e

unset PYTHONHOME
unset PYTHONPATH

################################################################################
# Build Database Configuration
################################################################################
DB_ARGS=()
function check_db_config() {
    param="$1"
    value="$2"
    if grep -q -E "^\s*\b${param}\b\s*=" "$ODOO_RC" ; then
        value=$(grep -E "^\s*\b${param}\b\s*=" "$ODOO_RC" |cut -d " " -f3|sed 's/["\n\r]//g')
    fi;
    DB_ARGS+=("--${param}")
    DB_ARGS+=("${value}")
}
check_db_config "db_host" "db"
check_db_config "db_port" "5432"
check_db_config "db_user" "odoo"
check_db_config "db_password" "odoo"

################################################################################
# Build Odoo Configuration
################################################################################

ODOO_ARGS=()
function check_odoo_config() {
    param="$1"
    value="$2"
    if grep -q -E "^\s*\b${param}\b\s*=" "$ODOO_RC" ; then
        value=$(grep -E "^\s*\b${param}\b\s*=" "$ODOO_RC" |cut -d " " -f3|sed 's/["\n\r]//g')
    fi;
    ODOO_ARGS+=("--${param}")
    ODOO_ARGS+=("${value}")
}
check_odoo_config "database" "$ODOO_DATABASE"
check_odoo_config "http-interface" "$ODOO_INTERFACE"
check_odoo_config "http-port" "80"
check_odoo_config "log-handler" "$ODOO_LOG_LEVEL"
check_odoo_config "dev" "reload"
# Fast Boot => Disable All Modules Install && Updates
if [ -z "$FAST_BOOT" ]; then
  echo "[ODOO BOOT] Normal Mode"
  check_odoo_config "init" "$ODOO_MODULES"
#  check_odoo_config "update" "all"
else
  echo "[ODOO BOOT] FAST Mode"
#  check_odoo_config "update" "splashsync"
fi

echo "[ODOO BOOT] Database Args" "${DB_ARGS[@]}"
echo "[ODOO BOOT] Odoo Args" "${ODOO_ARGS[@]}"
echo "[ODOO BOOT] User Command" "$@"

################################################################################
# Install Splash PyCore Module if not already installed
################################################################################
if (pip3 list -l --format=columns | grep 'splashpy');
then
  echo "Splash PyCore Module Already Installed"
else
  pip3 install wheel
  if [ -f /mnt/splashpy/setup.py ]; then
    echo "Install Splash PyCore Module from Local Sources"
    pip3 install -e /mnt/splashpy
  else
    echo "Install Splash PyCore Module from Repository"
    pip3 install splashpy
  fi

  if (pip3 list -l --format=columns | grep 'splashpy');
  then
    echo "Splash PyCore Module Now Installed"
  else
    echo "Splash PyCore Module Install Fail"
    exit 1
  fi
fi;

################################################################################
# Wait for Database Server
################################################################################
echo "[ODOO BOOT] Wait for Database..."
python3 /etc/odoo/wait-for-psql.py ${DB_ARGS[@]} --timeout=30
echo "[ODOO BOOT] Database Connected !!"

################################################################################
# Start Odoo Server
################################################################################
case "$1" in
    -- | odoo)
        shift
        if [[ "$1" == "scaffold" ]] ; then
            exec odoo "$@"
        else
            echo "Odoo Final Command" odoo "$@" "${DB_ARGS[@]}" "${ODOO_ARGS[@]}"
            exec odoo "$@" "${DB_ARGS[@]}"  "${ODOO_ARGS[@]}"
        fi
        ;;
    -*)
        echo "Odoo Final Command" odoo "$@" "${DB_ARGS[@]}"  "${ODOO_ARGS[@]}"
        exec odoo "$@" "${DB_ARGS[@]}" "${ODOO_ARGS[@]}"
        ;;
    python3)
        echo "Interpreter Command" "$@" "${DB_ARGS[@]}"  "${ODOO_ARGS[@]}"
        exec "$@" "${DB_ARGS[@]}" "${ODOO_ARGS[@]}"
        ;;
    *)
        echo "Generic Odoo Command" odoo "$@" "${DB_ARGS[@]}"  "${ODOO_ARGS[@]}"
        exec odoo "$@" "${DB_ARGS[@]}" "${ODOO_ARGS[@]}"
esac

exit 1
