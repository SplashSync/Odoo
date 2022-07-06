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

from splashpy import const, Framework
from splashpy.componants import FieldFactory
from datetime import date, datetime


class Odoo13PaymentCrudHelper:
    """
    Odoo 13 Invoice Payments Crud Helper
    """

    @staticmethod
    def add(invoice, payment_data):
        """
        Uses Odoo V12 Version
        Add a New Payment to an Invoice

        :param invoice: account.move
        :param payment_data: str

        :return: account.payment
        """
        from odoo.addons.splashsync.helpers.objects.invoices.paymentsCrudV12 import Odoo12PaymentCrudHelper
        return Odoo12PaymentCrudHelper.add(invoice, payment_data)

    @staticmethod
    def remove(invoice, payment):
        """
        Remove a Payment fom an Invoice

        :param invoice: account.move
        :param payment: account.payment

        :rtype: bool
        """
        Framework.log().warn("V13 Remove "+payment.communication)
        # ====================================================================#
        # Unit Tests => Force Journal to Allow Update Posted
        if Framework.isDebugMode():
            payment.journal_id.update_posted = True
        # ====================================================================#
        # Cancel && Delete Payment
        payment.cancel()
        payment.action_draft()
        payment.move_name = False
        payment.unreconcile()
        payment.unlink()

        return True

    @staticmethod
    def get_payments_list(invoice):
        """
        Get List of Payments For this Invoice

        :return: List of Payments
        :rtype: dict
        """
        from odoo.addons.splashsync.helpers import SystemManager
        return SystemManager.getModel("account.payment").search([
            ('reconciled_invoice_ids.id', '=', invoice.id)
        ]).sorted(key=lambda r: r.id)

    @staticmethod
    def get_sales_types_filter():
        """
        Get Filters for Listing Available Payment Methods

        :return: tuple
        """
        return [
            ('type', 'in', ["cash", "bank", "general"]),
            ('default_credit_account_id', '<>', None),
        ]