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

from odoo import SUPERUSER_ID, exceptions, http, models, tools
from odoo.http import request


class IrHttp(models.AbstractModel):
    """Add Custom Auth Handler for Splash Requests"""
    _inherit = 'ir.http'

    @classmethod
    def _auth_method_splash(cls):
        # Only POST Requests
        if request.httprequest.method != 'POST':
            raise exceptions.AccessDenied()
        # Verify User Agent
        user_agent = request.httprequest.headers.get("User-Agent")
        if user_agent is None or user_agent.find("SOAP") < 0:
            raise exceptions.AccessDenied()
        # Setup Splash User
        request.uid = http.request.env['ir.config_parameter'].sudo().get_param('splash_ws_user')
