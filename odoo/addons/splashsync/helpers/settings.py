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

from odoo.http import request


class SettingsManager():

    __settings__ = None

    # Default Settings
    __default__ = {
        'splash_ws_id': "",
        'splash_ws_key': "",
        'splash_ws_expert': False,
        'splash_ws_no_commits': False,
        'splash_ws_host': "https://www.splashsync.com/ws/soap",
        'splash_ws_user': None,
        'splash_product_simplified_prices': False,
        'splash_product_advanced_variants': False,
        'splash_product_advanced_taxes': False,
        'splash_sales_advanced_taxes': False,
    }

    @staticmethod
    def get_id():
        config = SettingsManager.get_configuration()
        return config["splash_ws_id"]

    @staticmethod
    def get_key():
        return SettingsManager.get_configuration()["splash_ws_key"]

    @staticmethod
    def get_host():
        return SettingsManager.get_configuration()["splash_ws_host"]

    @staticmethod
    def is_expert():
        return bool(SettingsManager.get_configuration()["splash_ws_expert"])

    @staticmethod
    def is_no_commits():
        return bool(SettingsManager.get_configuration()["splash_ws_no_commits"])

    @staticmethod
    def get_user():
        return SettingsManager.get_configuration()["splash_ws_user"]

    @staticmethod
    def is_prd_simple_prices():
        return bool(SettingsManager.get_configuration()["splash_product_simplified_prices"])

    @staticmethod
    def is_prd_adv_variants():
        return bool(SettingsManager.get_configuration()["splash_product_advanced_variants"])

    @staticmethod
    def is_prd_adv_taxes():
        return bool(SettingsManager.get_configuration()["splash_product_advanced_taxes"])

    @staticmethod
    def is_sales_adv_taxes():
        return bool(SettingsManager.get_configuration()["splash_sales_advanced_taxes"])

    @staticmethod
    def get_company_id():
        """Get Requested Company Id"""
        # ====================================================================#
        # Detect Company Id
        company_id = 1
        try:
            if "c" in request.params.keys():
                company_id = int(request.params['c'])
        except Exception as e:
            return company_id
        return company_id

    @staticmethod
    def get_configuration():
        """Get Company Configuration"""
        # ====================================================================#
        # Already Done
        if isinstance(SettingsManager.__settings__, dict):
            return SettingsManager.__settings__
        # ====================================================================#
        # Load Splash Configuration For Company
        company_id = SettingsManager.get_company_id()
        # ====================================================================#
        # First/Default Company => Take Params from Core Config
        if company_id == 1:
            SettingsManager.__settings__ = SettingsManager.__get_core_config()
        # ====================================================================#
        # Other Companies => Take params from Company Config
        else:
            SettingsManager.__settings__ = SettingsManager.__get_company_config()

        return SettingsManager.__settings__

    @staticmethod
    def ensure_company():
        """Ensure Current User Company Requested One"""
        expected_company_id = SettingsManager.get_company_id()
        try:
            if request.env.user.company_id.id != expected_company_id:
                request.env.user.company_id = expected_company_id
        except RuntimeError as e:
            return


    @staticmethod
    def reset():
        SettingsManager.__settings__ = None

    @staticmethod
    def __get_company_config():
        """
        Get Company Configuration
        :return: None, dict
        """
        # ====================================================================#
        # Load Company Configuration
        settings = request.env['res.config.settings'].search(
            [('company_id', '=', SettingsManager.get_company_id())],
            limit=1
        )
        if len(settings) != 1:
            import logging
            logging.warning("Company Settings Not Found")
            return SettingsManager.__default__

        return settings.get_values()

    @staticmethod
    def __get_core_config():
        """
        Get Configuration from Core Parameters
        :return: None, dict
        """
        # ====================================================================#
        # Load Core Configuration
        parameters = request.env['ir.config_parameter'].sudo()
        defaults = SettingsManager.__default__
        # ====================================================================#
        # Build Configuration
        return {
            "splash_ws_id":       parameters.get_param('splash_ws_id', defaults['splash_ws_id']),
            "splash_ws_key":      parameters.get_param('splash_ws_key', defaults['splash_ws_key']),
            "splash_ws_expert":   bool(parameters.get_param('splash_ws_expert', defaults['splash_ws_expert'])),
            "splash_ws_no_commits":   bool(parameters.get_param('splash_ws_no_commits', defaults['splash_ws_no_commits'])),
            "splash_ws_host":     parameters.get_param('splash_ws_host', defaults['splash_ws_host']),
            "splash_ws_user":     int(parameters.get_param('splash_ws_user', defaults['splash_ws_user'])),
            "splash_product_simplified_prices": bool(parameters.get_param('splash_product_simplified_prices', False)),
            "splash_product_advanced_taxes": bool(parameters.get_param('splash_product_advanced_taxes', False)),
            "splash_product_advanced_variants": bool(parameters.get_param('splash_product_advanced_variants', False)),
            "splash_sales_advanced_taxes": bool(parameters.get_param('splash_sales_advanced_taxes', False)),
        }
