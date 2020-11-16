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
from splashpy.helpers import PricesHelper, ObjectsHelper
from splashpy import Framework
from datetime import date, datetime
from splashpy import const
# from odoo.addons.splashsync.helpers import M2OHelper
from collections import OrderedDict

class InvoicePaymentsHelper:
    """Collection of Static Functions to manage Invoices Payments content"""

    __generic_fields = [
        'name', 'state', 'payment_type', 'communication'
    ]

    __required_fields = [
        'name', 'journal_code', 'payment_date', 'amount'
    ]

    __sales_types_filter = [
        ('type', 'in', ["sale", "cash", "bank", "general"]),
        ('default_credit_account_id', '<>', None),
    ]

    __payment_method_id = None

    @staticmethod
    def get_values(payments, field_id):
        """
        Get List of Payments Values for given Field

        :param payments: recordset
        :param field_id: str
        :return: dict
        """
        values = []
        # ====================================================================#
        # Walk on Lines
        for payment_line in payments.sorted(key=lambda r: r.id):
            # ====================================================================#
            # Collect Values
            values += [InvoicePaymentsHelper.__get_raw_values(payment_line, field_id)]

        return values

    @staticmethod
    def set_values(invoice, payment, payment_data):
        """
        Set values of Payments Line

        :param invoice: account.invoice
        :param payment: None|account.payment
        :param payment_data: dict
        :rtype: None|int
        """
        # ====================================================================#
        # Check if Payment Data are Valid
        if not InvoicePaymentsHelper.validate(payment_data):
            Framework.log().warn("Payment Data are incomplete or invalid")
            return None
        # ====================================================================#
        # Check if Payment Data are Modified
        if payment is not None and InvoicePaymentsHelper.compare(payment, payment_data):
            Framework.log().warn("Payments are Similar >> Update Skipped")
            return payment.id
        # ====================================================================#
        # Check if Invoice is Open
        if invoice.state != 'open' and not Framework.isDebugMode():
            Framework.log().error("Payments cannot be processed because the invoice is not open!")
            return None

        # ====================================================================#
        # Recreate Payment
        # ====================================================================#
        try:
            # ====================================================================#
            # Remove Payment Item
            if payment is not None:
                if not InvoicePaymentsHelper.remove(invoice, payment):
                    return None
                # DEBUG
                # else:
                #     Framework.log().warn("Payments Deleted >> "+payment.name)
            # ====================================================================#
            # Add Payment Item
            payment = InvoicePaymentsHelper.add(invoice, payment_data)
            # DEBUG
            # if payment is not None:
            #     Framework.log().warn("Payments Created >> "+payment_data["name"])
        except Exception as ex:
            # ====================================================================#
            # Update Failed => Line may be protected
            Framework.log().error(ex)
            return None

        return payment.id if payment is not None else None

    @staticmethod
    def get_payment_code_names():
        """
        Get List of Available Payment Methods

        :return: List of Available Payment Methods
        :rtype: dict
        """
        # ====================================================================#
        # Execute Domain Search with Filter
        results = []
        methods = http.request.env["account.journal"].search(InvoicePaymentsHelper.__sales_types_filter, limit=50)
        # ====================================================================#
        # Parse results
        for method in methods:
            results += [(
                method.code,
                "[%s] %s (%s)" % (method.code, method.name, method.type)
            )]
        return results

    # ====================================================================#
    # Add Payment Methods
    # ====================================================================#

    @staticmethod
    def add(invoice, payment_data):
        """
        Add a New Payment to an Invoice

        :param invoice: account.invoice
        :param payment_data: str

        :return: account.payment
        """
        # ====================================================================#
        # Detect Payment Method
        journal_id = InvoicePaymentsHelper.__detect_journal_id(payment_data["journal_code"])
        if journal_id is None:
            return None
        # ====================================================================#
        # Detect Payment Method Id
        payment_type = "inbound" if float(payment_data["amount"]) > 0 else 'outbound'
        payment_method_id = InvoicePaymentsHelper.__detect_payment_type(payment_type)
        if payment_method_id is None:
            return None
        # ====================================================================#
        # Detect Payment Date
        try:
            payment_date = datetime.strptime(payment_data["payment_date"], const.__SPL_T_DATECAST__).date()
        except:
            Framework.log().error("Unable to format payment date.")
            return None
        # ====================================================================#
        # Prepare Minimal Payment Data
        req_fields = {
            "invoice_ids": [invoice.id],
            "partner_id": invoice.partner_id.id,
            "partner_type": 'customer',
            "journal_id": journal_id,
            "name": payment_data["name"],
            "communication": payment_data["name"],
            "amount": payment_data["amount"],
            "payment_date": payment_date,
            "payment_type": payment_type,
            "payment_method_id": payment_method_id,
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
    def validate(payment_data):
        """
        Verify all Required Payment Data are There

        :param payment_data: dict

        :return: bool
        """
        for key in InvoicePaymentsHelper.__required_fields:
            if key not in payment_data:
                return False

        return True

    @staticmethod
    def compare(payment, data):
        """
        Compare a Payment with Received Data

        :param payment: account.payment
        :param data: dict

        :return: True if Similar
        :rtype: bool
        """

        # ==================================================================== #
        # Compare Payment Number
        if payment.name != data["name"]:
            return False
        # ==================================================================== #
        # Compare Payment Method
        if payment.journal_id.code != data["journal_code"]:
            return False
        # ==================================================================== #
        # Compare Payment Date
        try:
            payment_date = datetime.strptime(data["payment_date"], const.__SPL_T_DATECAST__).date()
            if payment.payment_date != payment_date:
                return False
        except Exception:
            return False
        # ==================================================================== #
        # Compare Payment Amount
        if abs(payment.amount - float(data["amount"])) >= 0.001:
            return False

        return True

    @staticmethod
    def remove(invoice, payment):
        """
        Remove a Payment fom an Invoice

        :param invoice: account.invoice
        :param payment: account.payment

        :rtype: bool
        """
        try:
            # ==================================================================== #
            # Unit Tests - Ensure Invoice is Open (Default draft)
            if Framework.isDebugMode() and invoice.state == 'draft':
                invoice.action_invoice_open()
                invoice.refresh()
            # ====================================================================#
            # Unit Tests => Force Journal to Allow Update Posted
            if Framework.isDebugMode():
                payment.journal_id.update_posted = True
            # ====================================================================#
            # Cancel Payment
            if payment.state == "posted":
                payment.cancel()
            # ====================================================================#
            # Remove Payment
            invoice.payment_ids = [(3, payment.id, 0)]

            return True
        except Exception as exception:
            Framework.log().fromException(exception, False)
            return False

    # ====================================================================#
    # Private Methods
    # ====================================================================#

    @staticmethod
    def __get_raw_values(payment, field_id):
        """
        Line Single Value for given Field

        :param payment: account.payment
        :param field_id: str
        :return: dict
        """

        from odoo.addons.splashsync.helpers import M2OHelper

        # ==================================================================== #
        # Generic Fields
        if field_id in InvoicePaymentsHelper.__generic_fields:
            return getattr(payment, field_id)
        # ==================================================================== #
        # Payment Method
        if field_id == "journal_code":
            return M2OHelper.get_name(payment, "journal_id", "code")
        if field_id == "journal_type":
            return M2OHelper.get_name(payment, "journal_id", "type")
        if field_id == "journal_name":
            return M2OHelper.get_name(payment, "journal_id")
        # ==================================================================== #
        # Payment Date
        if field_id == "payment_date":
            if isinstance(payment.payment_date, date):
                return payment.payment_date.strftime(const.__SPL_T_DATECAST__)
            else:
                return
        # ==================================================================== #
        # Payment Amount
        if field_id == "amount":
            return float(getattr(payment, field_id))

    @staticmethod
    def __detect_journal_id(journal_code):
        """
        Search for Journal using Payment method Code

        :param journal_code: str

        :return: int|None
        """
        from odoo.addons.splashsync.helpers import M2OHelper
        try:
            journal_id = M2OHelper.verify_name(
                journal_code,
                "code",
                "account.journal",
                InvoicePaymentsHelper.__sales_types_filter
            )
            return journal_id if isinstance(journal_id, int) and journal_id > 0 else None
        except:
            Framework.log().error("Unable to detect Journal Id (Payment Method)")
            return None

    @staticmethod
    def __detect_payment_type(mode='inbound'):
        """
        Search for Manual Payment Method Id

        :return: int|None
        """
        from odoo.addons.splashsync.helpers import M2OHelper
        try:
            payment_method_id = M2OHelper.verify_name(
                "manual",
                "name",
                "account.payment.method",
                [('payment_type', '=', mode)]
            )
            return payment_method_id if isinstance(payment_method_id, int) and payment_method_id > 0 else None
        except:
            Framework.log().error("Unable to detect manual payments method")
            return None
