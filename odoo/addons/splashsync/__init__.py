# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) 2015-2019 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

from . import controllers
from . import models
from . import objects
from odoo.api import Environment, SUPERUSER_ID
import logging

__VERSION__ = "0.2.3"

def post_init_hook(cr, registry):
    """
    This Hook is run just after Splashsync Module Installation
    """
    from odoo.addons.splashsync.helpers import TestsManager

    logging.info("[SPLASH] Execute post init hook")
    TestsManager.init(Environment(cr, SUPERUSER_ID, {}))

