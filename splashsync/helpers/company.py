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


class CompanyManager:
    """
    Manage Access to Odoo Companies vs Odoo Versions
    """

    __main_company = None

    @staticmethod
    def main_id():
        """
        Get Main Company ID

        :return: int
        """
        return CompanyManager.__main().id

    @staticmethod
    def main_name():
        """
        Get Main Company Name

        :return: str
        """
        return CompanyManager.__main().name

    @staticmethod
    def get_id(model):
        """
        Get Current Company ID from Odoo Model

        :param: odoo.models.TransientModel
        :return: int
        """
        try:
            return CompanyManager.__get_company(model).id
        except Exception:
            pass

        return CompanyManager.main_id()

    @staticmethod
    def get_name(model):
        """
        Get Current Company ID from Odoo Model

        :param: odoo.models.TransientModel
        :return: int
        """
        try:
            return CompanyManager.__get_company(model).name
        except Exception:
            pass

        return CompanyManager.main_name()

    @staticmethod
    def get_filters(model):
        """
        Get Company Search Filters from Odoo Model

        :param: odoo.models.TransientModel
        :return: dict
        """
        if "company_ids" in model.fields_get().keys():
            return [('company_ids', 'in', [CompanyManager.get_id(model), False])]
        if "company_id" in model.fields_get().keys():
            return ['|', ('company_id', 'in', [CompanyManager.get_id(model)]), ('company_id', '=', False)]

        return []

    @staticmethod
    def ensure_company():
        """
        Ensure Current User Company Requested One
        """
        # ====================================================================#
        # Odoo V12
        try:
            expected_company_id = CompanyManager.detect_company_id()

            if http.request.env.user.company_id.id != expected_company_id:
                http.request.env.user.company_id = expected_company_id
        except RuntimeError as e:
            return

    @staticmethod
    def detect_company_id():
        """
        Get Requested Company ID
        """
        from odoo.addons.splashsync.helpers import SystemManager
        # ====================================================================#
        # Detect Company Id from Request Query
        try:
            if "cid" in http.request.params.keys() and int(http.request.params['cid']) > 0:
                return int(http.request.params['cid'])
            if "cname" in http.request.params.keys() and len(str(http.request.params['cname'])) > 0:
                company = SystemManager.getModelSudo('res.company').name_search(str(http.request.params['cname']), limit=1)
                return int(company[0][0])
        except Exception:
            pass
        # ====================================================================#
        # Use Default Company Id
        return CompanyManager.main_id()

    @staticmethod
    def __main():
        """
        Get Main Company

        :return: res.company
        """
        if CompanyManager.__main_company is None:
            from odoo.addons.splashsync.helpers import SystemManager

            CompanyManager.__main_company = SystemManager.getModelSudo('res.company')._get_main_company()

        return CompanyManager.__main_company


    @staticmethod
    def __get_company(model):
        """
        Get Current Company from Odoo Model

        :param: odoo.models.TransientModel
        :return: res.company
        """
        from odoo.addons.splashsync.helpers import SystemManager
        # ====================================================================#
        # Detect Company Id from Object Environment
        if SystemManager.compare_version(13) >= 0:
            return model.env.company
        else:
            return model.env.user.company_id
