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


def post_init_hook(cr, registry):
    """Init Odoo with Splash Sync Tests Configuration"""
    # ====================================================================#
    # Setup Default Configuration For Testing
    env = Environment(cr, SUPERUSER_ID, {})
    env['ir.config_parameter'].sudo().set_param('splash_ws_id', "ThisIsOdooC1WsId")
    env['ir.config_parameter'].sudo().set_param('splash_ws_key', "ThisIsYourEncryptionKeyForSplash")
    env['ir.config_parameter'].sudo().set_param('splash_ws_expert', True)
    env['ir.config_parameter'].sudo().set_param('splash_ws_host', "http://toolkit/ws/soap")
    env['ir.config_parameter'].sudo().set_param('splash_ws_user', 2)
    # ====================================================================#
    # Ensure Install of an Extra Language
    env['res.lang'].load_lang('fr_FR')


