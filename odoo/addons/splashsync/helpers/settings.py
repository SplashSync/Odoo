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
    def get_user():
        return SettingsManager.get_configuration()["splash_ws_user"]

    @staticmethod
    def get_company_id():
        """Get Requested Company Id"""
        # ====================================================================#
        # Detect Company Id
        company_id = 1
        if "c" in request.params.keys():
            company_id = int(request.params['c'])
        return company_id

    @staticmethod
    def get_configuration():
        """Get Company Configuration"""
        # ====================================================================#
        # Already Done
        if isinstance(SettingsManager.__settings__, dict):
            return SettingsManager.__settings__
        # ====================================================================#
        # Load Company Configuration
        settings = request.env['res.config.settings'].search(
            [('company_id', '=', SettingsManager.get_company_id())],
            limit=1
        )
        if len(settings) != 1:
            import logging
            logging.warning("Company Settings Not Found")
            SettingsManager.__settings__ = {
                'splash_ws_id': "",
                'splash_ws_key': "",
                'splash_ws_expert': False,
                'splash_ws_host': "https://www.splashsync.com/ws/soap",
                'splash_ws_user': None,
            }
        else:
            SettingsManager.__settings__ = settings.get_values()

        return SettingsManager.__settings__

    @staticmethod
    def ensure_company():
        """Ensure Current User Company Requested One"""
        expected_company_id = SettingsManager.get_company_id()
        if request.env.user.company_id.id != expected_company_id:
            request.env.user.company_id = expected_company_id
            # request.env.user.write({"company_id": expected_company_id})
            # request.session.get_context()

    @staticmethod
    def reset():
        SettingsManager.__settings__ = None
