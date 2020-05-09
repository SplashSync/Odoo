# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) 2015-2020 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

from odoo import SUPERUSER_ID, exceptions, models
from odoo.http import request


class IrHttp(models.AbstractModel):
    """Add Custom Auth Handler for Splash Requests"""
    _inherit = 'ir.http'

    @classmethod
    def _auth_method_splash(cls):
        # ====================================================================#
        # Only POST Requests
        if request.httprequest.method != 'POST':
            raise exceptions.AccessDenied()
        # ====================================================================#
        # Verify User Agent
        user_agent = request.httprequest.headers.get("User-Agent")
        if user_agent is None or user_agent.find("SOAP") < 0:
            raise exceptions.AccessDenied()
        # ====================================================================#
        # Init as Super User
        request.session.uid = None
        request.uid = SUPERUSER_ID
        # ====================================================================#
        # Setup Splash User
        from odoo.addons.splashsync.helpers import SettingsManager
        SettingsManager.reset()
        splash_user = SettingsManager.get_user()
        if splash_user is None:
            raise exceptions.AccessDenied()
        request.session.uid = None
        request.uid = splash_user

