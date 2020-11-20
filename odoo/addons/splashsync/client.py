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

from odoo.addons.splashsync.helpers import SettingsManager
from splashpy import Framework
from splashpy.models.client import ClientInfo


class OdooClient(ClientInfo):
    """
    Build & Configure Splash Client & Server
    Define General Information about this Splash Client
    """

    __splash_client = None
    __splash_server = None

    def __init__(self):
        pass

    @staticmethod
    def get_mapped_objects():
        """
        Get List of Active Objects Class

        :return: list
        """
        from odoo.addons.splashsync.objects import ThirdParty, Address, Product, Order, Invoice
        return [
            Product(),
            ThirdParty(),
            Address(),
            Order(),
            Invoice(),
        ]

    @staticmethod
    def get_mapped_widgets():
        """
        Get List of Active Widgets Class

        :return: list
        """
        from splashpy.templates.widgets import Basic
        return [
            Basic(),
        ]

        return OdooClient.__mapped_widgets

    @staticmethod
    def get_server():
        """
        Build Splash Server

        :return SplashServer
        """
        from splashpy.server import SplashServer
        # ====================================================================#
        # Init Odoo User & Company
        SettingsManager.ensure_company()
        # ====================================================================#
        # Build Splash Server with Common Options
        splash_server = SplashServer(
            SettingsManager.get_id(),
            SettingsManager.get_key(),
            OdooClient.get_mapped_objects(),
            OdooClient.get_mapped_widgets(),
            OdooClient()
        )
        # ====================================================================#
        # Force Ws Host if Needed
        if SettingsManager.is_expert():
            Framework.config().force_host(SettingsManager.get_host())

        return splash_server

    @staticmethod
    def get_client():
        """
        Build Splash Client

        :return SplashClient
        """
        from splashpy.client import SplashClient
        if isinstance(OdooClient.__splash_client, SplashClient):
            # ====================================================================#
            # Ensure Framework is in Client Mode
            Framework.setServerMode(False)
            return OdooClient.__splash_client
        # ====================================================================#
        # Init Odoo User & Company
        # SettingsManager.ensure_company()
        # ====================================================================#
        # Build Splash Client with Common Options
        OdooClient.__splash_client = SplashClient(
            SettingsManager.get_id(),
            SettingsManager.get_key(),
            OdooClient.get_mapped_objects(),
            OdooClient.get_mapped_widgets(),
            OdooClient()
        )
        # ====================================================================#
        # Ensure Framework is in Client Mode
        Framework.setServerMode(False)
        # ====================================================================#
        # Force Ws Host if Needed
        if SettingsManager.is_expert():
            Framework.config().force_host(SettingsManager.get_host())

        return OdooClient.__splash_client

    # ====================================================================#
    # OBJECTS COMMITS
    # ====================================================================#

    @staticmethod
    def commit(splash_object, action, object_ids):
        """
        Execute Splash Commit for this Odoo Object

        :return: bool
        """
        # ====================================================================#
        # Try to detect User Name
        try:
            from odoo.http import request
            user_name = request.env.user.name
        except Exception:
            user_name = "Unknown User"
        # ====================================================================#
        # Send Commit Notification
        try:
            # ====================================================================#
            # Check if Commits Are Allowed
            if SettingsManager.is_no_commits():
                return True
            # ====================================================================#
            # Execute Commits with Client
            return OdooClient.get_client().commit(
                str(splash_object.name),
                object_ids,
                action,
                user_name,
                "[" + str(action).capitalize() + "]" + str(splash_object.desc) + " modified on Odoo"
            )
        except Exception as exception:
            splashLogger = Framework.log()
            if splashLogger:
                Framework.log().fromException(exception, False)
                Framework.log().to_logging().clear()
            return False

    def complete(self):
        """
        Complete Client Module Information
        """
        # ====================================================================#
        # Use Default Icons Set
        # self.loadDefaultIcons()
        # ====================================================================#
        # Use Odoo Icons Set
        self.load_odoo_icons()
        # ====================================================================#
        # Override Info to Says we are Faker Mode
        self.short_desc = "Splash Odoo Client"
        self.long_desc = "Splash Client for connecting Odoo Erp Systems"
        try:
            # ====================================================================#
            # Load Odoo Company Object
            company = SettingsManager.get_company()
            # ====================================================================#
            # Company Information
            self.company = company.name
            self.address = company.street
            self.zip = company.zip
            self.town = company.city
            self.country = company.country_id.name
            self.www = company.website
            self.email = company.email
            self.phone = company.phone
        except:
            self.company = "Unable to fetch Main Company"
        try:
            from odoo.addons.splashsync import __VERSION__
            self.module_version = __VERSION__
        except:
            pass

    @staticmethod
    def reset():
        OdooClient.__splash_server = None
        OdooClient.__splash_client = None

        pass

    def load_odoo_icons(self):
        """Change Client Server Icons"""
        from splashpy.componants.files import Files
        import os
        assets_path = os.path.dirname(os.path.realpath(__file__))+"/static/assets/img"
        self.ico_raw = Files.getRawContents(assets_path + "/icon.png")
        self.logo_raw = Files.getRawContents(assets_path + "/logo.png")
