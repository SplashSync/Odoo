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

from odoo import http
from splashpy import const, Framework
from splashpy.componants import FieldFactory
from datetime import date, datetime


class OdooV12PaymentsHelper:
    """
    Odoo V12 Invoice Payments Crud Helper
    """

    @staticmethod
    def add(invoice, payment_data):
        """
        Add a New Payment to an Invoice

        :param invoice: account.move
        :param payment_data: str

        :return: account.payment
        """
        # ====================================================================#
        # Prepare Minimal Payment Data
        req_fields = {
            "invoice_ids":          [invoice.id],
            "partner_id":           invoice.partner_id.id,
            "partner_type":         'customer',
            "journal_id":           payment_data["journal_id"],
            "communication":        payment_data["communication"],
            "amount":               payment_data["amount"],
            "payment_date":         datetime.strptime(payment_data["payment_date"], const.__SPL_T_DATECAST__).date(),
            "payment_type":         payment_data["payment_type"],
            "payment_method_id":    payment_data["payment_method_id"],
            "state": "draft"
        }
        # ====================================================================#
        # Create Payment
        try:
            # ==================================================================== #
            # Unit Tests - Ensure Invoice is Open (Default draft)
            if Framework.isDebugMode() and invoice.state == 'draft':
                invoice.action_invoice_open()
                invoice.refresh()
            # ====================================================================#
            # Create Raw Payment
            payment = http.request.env["account.payment"].create(req_fields)
            # ====================================================================#
            # Add Payment to Invoice
            invoice.payment_ids = [(4, payment.id, 0)]
            # ====================================================================#
            # Validate Payment
            payment.post()

            return payment
        except Exception as exception:
            Framework.log().error("Unable to create Payment, please check inputs.")
            Framework.log().fromException(exception, False)

            return None

    @staticmethod
    def remove(invoice, payment):
        """
        Remove a Payment fom an Invoice

        :param invoice: account.invoice
        :param payment: account.payment

        :rtype: bool
        """
        # ====================================================================#
        # Unit Tests => Force Journal to Allow Update Posted
        if Framework.isDebugMode():
            payment.journal_id.update_posted = True
        # ====================================================================#
        # Cancel Payment
        if payment.state == "posted":
            if Framework.isDebugMode():
                payment.sudo().cancel()
            else:
                payment.cancel()
        # ====================================================================#
        # Remove Payment
        invoice.payment_ids = [(3, payment.id, 0)]

        return True

    @staticmethod
    def get_payments_list(invoice):
        """
        Get List of Payments For this Invoice

        :return: List of Payments
        :rtype: dict
        """
        return invoice.payment_ids.sorted(key=lambda r: r.id)

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
