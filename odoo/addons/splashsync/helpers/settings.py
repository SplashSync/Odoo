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
        try:
            return bool(http.request.env['ir.config_parameter'].sudo().get_param('splash_ws_no_commits'))
        except Exception:
            pass
        try:
            return bool(SettingsManager.get_configuration()["ws_no_commits"])
        except Exception:
            pass
        return True

    @staticmethod
    def get_user():
        return SettingsManager.get_configuration()["ws_user"]

    @staticmethod
    def get_company_id():
        return SettingsManager.get_configuration().company_id.id

    @staticmethod
    def get_company():
        from odoo.addons.splashsync.helpers import SystemManager

        return SystemManager.getModelSudo('res.company').browse([
            SettingsManager.get_configuration().company_id.id
        ]).ensure_one()

    @staticmethod
    def get_company_filter():
        return [('company_id', '=', SettingsManager.get_configuration().company_id.id)]

    @staticmethod
    def is_prd_simple_prices():
        try:
            from odoo.addons.splashsync.helpers import SystemManager
            return bool(SystemManager.getModelSudo('ir.config_parameter').get_param('splash_product_simplified_prices'))
        except Exception:
            pass
        try:
            return bool(SettingsManager.get_configuration()["product_simplified_prices"])
        except Exception:
            pass
        return False

    @staticmethod
    def is_prd_adv_variants():
        return bool(SettingsManager.get_configuration()["product_advanced_variants"])

    @staticmethod
    def is_prd_adv_taxes():
        return bool(SettingsManager.get_configuration()["product_advanced_taxes"])

    @staticmethod
    def is_prd_sku_detection():
        return bool(SettingsManager.get_configuration()["product_sku_detection"])

    @staticmethod
    def is_sales_adv_taxes():
        return bool(SettingsManager.get_configuration()["sales_advanced_taxes"])

    @staticmethod
    def is_sales_check_payments():
        return bool(SettingsManager.get_configuration()["sales_check_payments_amount"])

    @staticmethod
    def get_sales_account_id():
        return SettingsManager.get_configuration().sales_account_id.id

    @staticmethod
    def get_sales_journal_id():
        return SettingsManager.get_configuration().sales_journal_id.id

    @staticmethod
    def get_sales_default_team_id():
        try:
            return SettingsManager.get_configuration().sales_default_team_id.id
        except Exception:
            return None

    @staticmethod
    def get_configuration():
        """
        Get Company Configuration for WebService Requests

        :return:  res.config.splash
        """
        # ====================================================================#
        # Detect Company Id
        from odoo.addons.splashsync.helpers import CompanyManager, SystemManager
        company_id = CompanyManager.detect_company_id()
        if not company_id:
            raise Exception("[SPLASH] Unknown Company")
        # ====================================================================#
        # Load Splash Configuration from Cache
        if SettingsManager.__current__ is not None and SettingsManager.__current__.company_id.id == company_id:
            return SettingsManager.__current__
        # ====================================================================#
        # Load Splash Configuration For Company
        config = SystemManager.getModelSudo('res.config.splash').get_config(company_id)
        if config is None:
            raise Exception("[SPLASH] Unable to find configuration for "+str(company_id))
        # ====================================================================#
        # Cache Splash Configuration
        SettingsManager.__current__ = config
        # ====================================================================#
        # Cache Splash Configuration
        from odoo.addons.splashsync.client import OdooClient
        OdooClient.reset()

        return config

    @staticmethod
    def reset():
        SettingsManager.__current__ = None
        # ====================================================================#
        # Cache Splash Configuration
        from odoo.addons.splashsync.client import OdooClient
        OdooClient.reset()

        pass
