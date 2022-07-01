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
from odoo.release import version_info
from odoo.addons.splashsync.helpers import SettingsManager

class SystemManager():
    """
    Odoo System Manager
    """

    @staticmethod
    def getModel(domain):
        """
        Get Object Model Class
        """
        return http.request.env[domain].with_context(
            allowed_company_ids=[SettingsManager.get_company_id()],
            mail_notrack=True,
            check_move_validity=False
        )

    @staticmethod
    def getModelSudo(domain):
        """
        Get Object Model Class with Sudo
        """
        return http.request.env[domain].sudo()

    @staticmethod
    def major_version():
        """
        Get Odoo Core Version

        :rtype: int
        """
        return version_info[0]

    @staticmethod
    def compare_version(version):
        """
        Compare with Odoo Version.

        :param version: tuple|int
        :rtype: int
        """
        if isinstance(version, int):
            version = (version, 0, 0, 'final', 0, '')
        if version < version_info:
            return +1
        if version > version_info:
            return -1

        return 0
