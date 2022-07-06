# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) Splash Sync  <www.splashsync.com>
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
from datetime import date, datetime
from splashpy import const


class InvoicePaymentsHelper:
    """
    Collection of Static Functions to manage Invoices Payments
    """

    # Codes of Generic Payment Fields
    __generic_fields = [
        'name', 'ref', 'state', 'payment_type', 'communication'
    ]

    # Default Payment Method ID
    __payment_method_id = None

    # Margin per Line for Payment Amount Rounding
    __payment_line_margin = 0.01

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
        if payment is not None and InvoicePaymentsHelper.compare(invoice, payment, payment_data):
            Framework.log().warn("Payments are Similar >> Update Skipped")
            return payment.id
        # ====================================================================#
        # Check if Invoice is Open
        if invoice.state not in ['open', 'posted'] and not Framework.isDebugMode():
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
        methods = http.request.env["account.journal"].search(
            InvoicePaymentsHelper.get_helper().get_sales_types_filter(),
            limit=50
        )
        # ====================================================================#
        # Parse results
        for method in methods:
            results += [(
                method.name,
                "[%s] %s (%s)" % (method.code, method.name, method.type)
            )]
        # ====================================================================#
        # Add Default Value
        if not Framework.isDebugMode():
            results += [("Unknown", "[Unknown] Use default payment method")]

        return results

    # ====================================================================#
    # Add Payment Methods
    # ====================================================================#

    @staticmethod
    def add(invoice, payment_data):
        """
        Add a New Payment to an Invoice

        :param invoice: account.invoice|account.move
        :param payment_data: str

        :return: account.payment
        """
        from odoo.addons.splashsync.objects.invoice import InvoiceStatus
        # ====================================================================#
        # Detect Payment Method
        payment_data["journal_id"] = InvoicePaymentsHelper.__detect_journal_id(payment_data["journal_code"])
        if payment_data["journal_id"] is None:
            Framework.log().error("Unable to detect Journal Id (Payment Method)")
            return None
        # ====================================================================#
        # Detect Payment Method Id
        payment_data["payment_type"] = "inbound" if float(payment_data["amount"]) > 0 else 'outbound'
        payment_data["payment_method_id"] = InvoicePaymentsHelper.__detect_payment_type(payment_data["payment_type"])
        if payment_data["payment_method_id"] is None:
            Framework.log().error("Unable to detect manual payments method")
            return None
        # ====================================================================#
        # Adjust Payment Amount
        payment_data["amount"] = InvoicePaymentsHelper.__adjust_payment_amount(invoice, payment_data["amount"])
        # ====================================================================#
        # Create Payment
        try:
            # ==================================================================== #
            # Unit Tests - Ensure Invoice is Open/Posted (Default draft)
            if Framework.isDebugMode() and invoice.state == 'draft':
                InvoiceStatus.get_helper().set_validated(invoice)
            # ====================================================================#
            # Create Raw Payment
            return InvoicePaymentsHelper.get_helper().add(invoice, payment_data)

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
        from odoo.addons.splashsync.helpers import SystemManager
        if SystemManager.compare_version(14) >= 0:
            required_fields = ['ref', 'journal_code', 'date', 'amount']
        else:
            required_fields = ['communication', 'journal_code', 'payment_date', 'amount']

        for key in required_fields:
            if key not in payment_data:
                return False

        return True

    @staticmethod
    def compare(invoice, payment, data):
        """
        Compare a Payment with Received Data

        :param invoice: account.invoice
        :param payment: account.payment
        :param data: dict

        :return: True if Similar
        :rtype: bool
        """
        from odoo.addons.splashsync.helpers import SystemManager
        if SystemManager.compare_version(14) >= 0:
            number_attr = "ref"
            date_attr = "date"
        else:
            number_attr = "communication"
            date_attr = "payment_date"
        # ==================================================================== #
        # Compare Payment Number
        if isinstance(data[number_attr], str) and len(data[number_attr]) > 1:
            if getattr(payment, number_attr) != data[number_attr]:
                return False
        # ==================================================================== #
        # Compare Payment Method
        if payment.journal_id.id != InvoicePaymentsHelper.__detect_journal_id(data["journal_code"]):
            return False
        # ==================================================================== #
        # Compare Payment Date
        try:
            payment_date = datetime.strptime(data[date_attr], const.__SPL_T_DATECAST__).date()
            if getattr(payment, date_attr) != payment_date:
                return False
        except Exception:
            return False
        # ====================================================================#
        # Compute Allowed Margin
        margin = InvoicePaymentsHelper.__get_payment_margin(invoice)
        # ==================================================================== #
        # Compare Payment Amount
        if abs(payment.amount - float(data["amount"])) >= margin:
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
        from odoo.addons.splashsync.objects.invoice import InvoiceStatus
        payment_name = str(payment.name)
        try:
            # ==================================================================== #
            # Unit Tests - Ensure Invoice is Open (Default draft)
            if Framework.isDebugMode() and invoice.state == 'draft':
                InvoiceStatus.get_helper().set_validated(invoice)
            # ====================================================================#
            # Remove Payment
            return InvoicePaymentsHelper.get_helper().remove(invoice, payment)
        except Exception as exception:
            Framework.log().error("Failed to remove Payment " + payment_name + " from INV " + str(invoice.id))
            Framework.log().fromException(exception, False)
            return False

    @staticmethod
    def validate_payments_amounts(invoice, payments):
        """
        Check Payment Amounts ensure Invoice Can Close
        Strategy: Allow 0.01 error per invoice line.

        :param invoice: account.invoice
        :param payments:  dict

        :return: bool
        """
        # ==================================================================== #
        # Check if Feature is Enabled
        from odoo.addons.splashsync.helpers import SettingsManager
        if not SettingsManager.is_sales_check_payments():
            return True
        # ==================================================================== #
        # Sum Received Payments...
        payments_total = 0
        for payment_data in payments:
            payments_total += float(payment_data["amount"]) if InvoicePaymentsHelper.validate(payment_data) else 0
        # ====================================================================#
        # Compute Allowed Margin
        margin = InvoicePaymentsHelper.__get_payment_margin(invoice)
        # ====================================================================#
        # Compare Payment Amount vs Invoice Residual
        if abs(float(invoice.amount_total) - float(payments_total)) <= margin:
            return True
        return Framework.log().error(
            "Payments Validation fail: "+str(payments_total)+", expected "+str(invoice.amount_total)
        )

    @staticmethod
    def get_helper():
        """
        Get Adapted Invoices Payments Helper

        :rtype: Odoo12PaymentCrudHelper|Odoo13PaymentCrudHelper

        """
        from odoo.addons.splashsync.helpers import SystemManager

        if SystemManager.compare_version(14) >= 0:
            from odoo.addons.splashsync.helpers.objects.invoices.paymentsCrudV14 import Odoo14PaymentCrudHelper
            return Odoo14PaymentCrudHelper
        elif SystemManager.compare_version(13) >= 0:
            from odoo.addons.splashsync.helpers.objects.invoices.paymentsCrudV13 import Odoo13PaymentCrudHelper
            return Odoo13PaymentCrudHelper
        elif SystemManager.compare_version(12) >= 0:
            from odoo.addons.splashsync.helpers.objects.invoices.paymentsCrudV12 import Odoo12PaymentCrudHelper
            return Odoo12PaymentCrudHelper

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
            return M2OHelper.get_name(payment, "journal_id", "name")
        if field_id == "journal_type":
            return M2OHelper.get_name(payment, "journal_id", "type")
        if field_id == "journal_name":
            return M2OHelper.get_name(payment, "journal_id")
        # ==================================================================== #
        # Payment Date
        if field_id in ["date", "payment_date"]:
            if isinstance(getattr(payment, field_id), date):
                return getattr(payment, field_id).strftime(const.__SPL_T_DATECAST__)
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
                "name",
                "account.journal",
                InvoicePaymentsHelper.get_helper().get_sales_types_filter()
            )
            if isinstance(journal_id, int) and journal_id > 0:
                return journal_id

            from odoo.addons.splashsync.helpers.settings import SettingsManager
            default_id = SettingsManager.get_sales_journal_id()

            return default_id if isinstance(default_id, int) and default_id > 0 else None
        except Exception as exception:
            return None

    @staticmethod
    def __detect_payment_type(mode='inbound'):
        """
        Search for Manual Payment Method ID

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
        except Exception as exception:
            return None

    @staticmethod
    def __adjust_payment_amount(invoice, amount):
        """
        Adjust Payment Amount to fix Decimals Errors
        Strategy: Allow 0.01 error per invoice line.

        :param invoice: account.invoice
        :param amount:  float
        :return: float
        """
        from odoo.addons.splashsync.helpers import SystemManager
        # ====================================================================#
        # Compute Allowed Margin
        margin = InvoicePaymentsHelper.__get_payment_margin(invoice)
        # ====================================================================#
        # Get Residual Amount
        if SystemManager.compare_version(13) >= 0:
            residual = invoice.amount_residual
        else:
            residual = invoice.residual
        # ====================================================================#
        # Compare Payment Amount vs Invoice Residual
        if abs(float(residual) - float(amount)) <= margin:
            # Amounts are close enough to MERGE
            Framework.log().warn("Payment Amount changed to "+str(residual))
            return residual
        # Amounts are too far to MERGE
        return amount

    @staticmethod
    def __get_payment_margin(invoice):
        """
        Compute Accepted Payment Amount Delta to fix Decimals Errors
        Strategy: Allow 0.01 error per invoice line.

        :param invoice: account.invoice

        :return: float
        """
        # ====================================================================#
        # Compute Allowed Margin
        return float(len(invoice.invoice_line_ids.ids) * InvoicePaymentsHelper.__payment_line_margin)
