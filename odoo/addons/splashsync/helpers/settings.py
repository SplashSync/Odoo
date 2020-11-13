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

from odoo import http
from splashpy import Framework
from odoo.addons.splashsync.models.configuration import ResConfigSplash

class SettingsManager():

    __current__ = None

    @staticmethod
    def get_id():
        return SettingsManager.get_configuration()["ws_id"]

    @staticmethod
    def get_key():
        return SettingsManager.get_configuration()["ws_key"]

    @staticmethod
    def get_host():
        return SettingsManager.get_configuration()["ws_host"]

    @staticmethod
    def is_expert():
        return bool(SettingsManager.get_configuration()["ws_expert"])

    @staticmethod
    def is_no_commits():
        return bool(SettingsManager.get_configuration()["ws_no_commits"])

    @staticmethod
    def get_user():
        return SettingsManager.get_configuration()["ws_user"]

    @staticmethod
    def get_company_id():
        return SettingsManager.get_configuration().company_id.id

    @staticmethod
    def get_company():
        return http.request.env['res.company'].sudo().browse([
            SettingsManager.get_configuration().company_id.id
        ]).ensure_one()

    @staticmethod
    def get_company_filter():
        return [('company_id', '=', SettingsManager.get_configuration().company_id.id)]

    @staticmethod
    def is_prd_simple_prices():
        return bool(SettingsManager.get_configuration()["product_simplified_prices"])

    @staticmethod
    def is_prd_adv_variants():
        return bool(SettingsManager.get_configuration()["product_advanced_variants"])

    @staticmethod
    def is_prd_adv_taxes():
        return bool(SettingsManager.get_configuration()["product_advanced_taxes"])

    @staticmethod
    def is_sales_adv_taxes():
        return bool(SettingsManager.get_configuration()["sales_advanced_taxes"])

    @staticmethod
    def get_configuration():
        """
        Get Company Configuration for WebService Requests
        """
        # ====================================================================#
        # Detect Company Id
        company_id = SettingsManager.__detect_company_id()
        if not company_id:
            raise Exception("[SPLASH] Unknown Company")
        # ====================================================================#
        # Load Splash Configuration from Cache
        if SettingsManager.__current__ is not None and SettingsManager.__current__.company_id.id == company_id:
            return SettingsManager.__current__
        # ====================================================================#
        # Load Splash Configuration For Company
        config = ResConfigSplash.get_config(company_id)
        if config is None:
            raise Exception("[SPLASH] Unable to find configuration")
        # ====================================================================#
        # Cache Splash Configuration
        SettingsManager.__current__ = config

        return config

    @staticmethod
    def reset():
        SettingsManager.__current__ = None

        pass

    @staticmethod
    def ensure_company():
        """
        Ensure Current User Company Requested One
        """
        expected_company_id = SettingsManager.get_company_id()
        try:
            if http.request.env.user.company_id.id != expected_company_id:
                http.request.env.user.company_id = expected_company_id
        except RuntimeError as e:
            return

    @staticmethod
    def __detect_company_id():
        """
        Get Requested Company Id
        """
        # ====================================================================#
        # Detect Company Id from Request Query
        try:
            if "c" in http.request.params.keys() and int(http.request.params['c']) > 0:
                return int(http.request.params['c'])
        except Exception:
            pass
        # ====================================================================#
        # Detect Company Id from Logged User
        try:
            if not Framework.isServerMode() and http.request.env.user.company_id.id:
                return http.request.env.user.company_id.id
        except Exception:
            pass

        # ====================================================================#
        # Use Default Company Id
        return http.request.env['res.company']._get_main_company().id
