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

from odoo import http
from splashpy import Framework


class CurrencyHelper:
    """Collection of Static Functions to manage Odoo Currencies"""

    domain = "res.currency"

    @staticmethod
    def get_main_currency():
        try:
            company = http.request.env['res.company']._get_main_company().read([])
            return CurrencyHelper.load(company[0]["currency_id"][0])
        except:
            return None

    @staticmethod
    def get_main_currency_code():
        try:
            company = http.request.env['res.company']._get_main_company().read([])
            return company[0]["currency_id"][1]
        except Exception as exception:
            Framework.log().fromException(exception)
            return None

    @staticmethod
    def get_main_currency_id():
        try:
            company = http.request.env['res.company']._get_main_company().read([])
            return company[0]["currency_id"][0]
        except Exception as exception:
            Framework.log().fromException(exception)
            return None

    # ====================================================================#
    # Odoo ORM Access
    # ====================================================================#

    @staticmethod
    def load(currency_id):
        """Load Odoo Object by Id"""
        currency = CurrencyHelper.getModel().browse([int(currency_id)])
        if len(currency) != 1:
            return False

        return currency

    @staticmethod
    def getModel():
        """Get Currencies Model Class"""
        return http.request.env[CurrencyHelper.domain].sudo()
