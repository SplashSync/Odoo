#!/bin/bash
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
#  @author Bernard Paquier <contact@splashsync.com>
#
################################################################################

################################################################
# Ensure Git is Installed
apt-get update && apt-get install git -y -q

################################################################
# Install Splash PyCore Module if not already installed
if (pip3 list -l --format=columns | grep 'splashpy');
then
  echo "[splashpy] Already Installed >> Update"
  pip3 install splashpy --upgrade
else
  echo "[splashpy] Install Splash PyCore Module"
  pip3 install splashpy
fi;

################################################################
# Install Splash Module
if [ -f ~/splashsync/setup.py ]; then
  echo "Splash Odoo Module Already Installed"
  cd ~/splashsync && git pull
else
  echo "Clone & Install Splash Odoo Module"
  git clone https://github.com/SplashSync/odoo.git ~/splashsync --depth=1
  ln -s ~/splashsync/odoo/addons/splashsync /mnt/extra-addons
fi