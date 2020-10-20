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


class TaxHelper:
    """Collection of Static Functions to manage Odoo Tax Rules"""

    tax_domain = "account.tax"

    @staticmethod
    def get_tax_rate(taxes_ids, type_tax_use):
        tax_rate = 0.0
        for tax in taxes_ids:
            tax_rate += TaxHelper.__get_tax_rate(tax, type_tax_use)
        return tax_rate

    @staticmethod
    def get_name_values(type_tax_use='sale'):
        """
        Get a Relation Possible Values Dict

        :param type_tax_use: str
        :rtype: dict
        """
        from odoo.addons.splashsync.helpers import M2OHelper\

        return M2OHelper.get_name_values(TaxHelper.tax_domain, [("type_tax_use", "=", type_tax_use)])

    @staticmethod
    def __get_tax_rate(tax, type_tax_use):
        tax_rate = 0
        # Filter on Taxes types
        if tax.type_tax_use != type_tax_use:
            return tax_rate
        # Tax By Percent
        if tax.amount_type == "percent":
            return tax.amount
        # Tax Group
        if len(tax.children_tax_ids) > 0:
            for child_tax in tax.children_tax_ids:
                tax_rate += TaxHelper.__get_tax_rate(child_tax)

        return tax_rate

    # ====================================================================#
    # Odoo ORM Access
    # ====================================================================#

    @staticmethod
    def find_by_rate(tax_rate, type_tax_use):
        """
        Find Odoo Tax by Rate

        :param tax_rate: float
        :param type_tax_use: str
        :rtype: account.tax|None
        """
        taxes = TaxHelper.getModel().search([
            ("amount", "=", tax_rate),
            ("amount_type", "=", "percent"),
            ("type_tax_use", "=", type_tax_use),
        ])
        if len(taxes) == 0:
            return TaxHelper.__create_for_debug(tax_rate, type_tax_use)
        return taxes[0]

    @staticmethod
    def __create_for_debug(tax_rate, type_tax_use):
        """
        Create an Odoo Tax Rate For Debug

        :param tax_rate: float
        :param type_tax_use: str
        :rtype: account.tax
        """
        # from splashpy import Framework
        # if not Framework.isDebugMode():
        #     return None
        tax_data = {
            "amount": tax_rate,
            "amount_type": "percent",
            "company_id": http.request.env['res.company']._get_main_company().id,
            "name": "UNIT TESTS " + str(tax_rate) + "%",
            "type_tax_use": type_tax_use,
            "sequence": 1,
            "tax_group_id": 1,
        }
        return TaxHelper.getModel().create(tax_data)

    @staticmethod
    def getModel():
        """
        Get Taxes Model Class

        :rtype: str
        """
        return http.request.env[TaxHelper.tax_domain].sudo()
