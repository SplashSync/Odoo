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

import logging
import base64
from odoo import http
from splashpy.models.client import ClientInfo


class OdooClient(ClientInfo):
    """Define General Information about this Splash Client"""

    def __init__(self):
        pass

    def complete(self):
        """
        Complete Client Module Information
        """
        # ====================================================================#
        # Use Default Icons Set
        self.loadDefaultIcons()
        # ====================================================================#
        # Load Odoo Company Object
        company = http.request.env['res.company']._get_main_company().read([])
        # ====================================================================#
        # Override Info to Says we are Faker Mode
        self.short_desc = "Splash Odoo Client"
        self.long_desc = "Splash Client for connecting Odoo Erp Systems"
        # ====================================================================#
        # Company Information
        self.company = company[0]["name"]
        self.address = company[0]["street"]
        self.zip = company[0]["zip"]
        self.town = company[0]["city"]
        self.country = company[0]["phone"]
        self.www = company[0]["website"]
        self.email = company[0]["email"]
        self.phone = company[0]["phone"]
