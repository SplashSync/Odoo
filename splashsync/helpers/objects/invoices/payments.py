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
        'name', 'state', 'payment_type', 'communication'
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
        # Search for Account Journals with Filter
        results = []
        journals = http.request.env["account.journal"].search(
            InvoicePaymentsHelper.get_sales_types_filter(),
            limit=50
        )
        # ====================================================================#
        # Walk on Sales Journals
        for journal in journals:
            # ====================================================================#
            # Add Journal Default Payment Method
            results += [(
                journal.name,
                "[%s] %s Journal (%s)" % (journal.name, journal.name, journal.code)
            )]
            # ====================================================================#
            # Walk on Payment Method
            for inbound_payment_method in journal.inbound_payment_method_line_ids:
                # ====================================================================#
                # Add Journal Manual Payment Method
                if inbound_payment_method.code == 'manual':
                    results += [(
                        inbound_payment_method.name,
                        "[%s] %s Manual Payment Method" % (inbound_payment_method.name, journal.name)
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


        # ====================================================================#
        # Detect Payment Method
        payment_data["payment_method"] = InvoicePaymentsHelper.__detect_payment_method(payment_data)
        if payment_data["payment_method"] is None:
            Framework.log().error("Unable to detect Payment Method")
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
                from odoo.addons.splashsync.helpers.objects.invoices import InvoiceStatusHelper
                InvoiceStatusHelper.set_validated(invoice)
            # ====================================================================#
            # Create Raw Payment
            return InvoicePaymentsHelper.add_payment(invoice, payment_data)

        except Exception as exception:
            Framework.log().error("Unable to create Payment, please check inputs.")
            Framework.log().fromException(exception, True)

            return None

    @staticmethod
    def add_payment(invoice, payment_data):
        """
        Add a New Payment to an Invoice

        :param invoice: account.move
        :param payment_data: str

        :return: account.payment
        """
        from odoo.addons.splashsync.helpers import SystemManager
        # ====================================================================#
        # Detect Payment Date
        try:
            payment_date = datetime.strptime(payment_data["date"], const.__SPL_T_DATECAST__).date()
        except:
            Framework.log().error("Unable to format payment date.")
            return None
        # ====================================================================#
        # Create Payment Using Wizard
        payments = SystemManager.getModel("account.payment.register").with_context({
            'active_model': 'account.move',
            'active_ids': invoice.ids
        }).create({
            "journal_id":       payment_data["payment_method"].journal_id.id,
            "payment_method_line_id":       payment_data["payment_method"].id,
            "amount":           payment_data["amount"],
            "communication":    payment_data["ref"],
            'payment_date':     payment_date,
            "payment_type":     payment_data["payment_method"].payment_type,
        }).action_create_payments()

        return SystemManager.getModel("account.payment").browse(payments['res_id'])

    @staticmethod
    def validate(payment_data):
        """
        Verify all Required Payment Data are There

        :param payment_data: dict

        :return: bool
        """
        from odoo.addons.splashsync.helpers import SystemManager

        for key in ['ref', 'journal_code', 'date', 'amount']:
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
        # ==================================================================== #
        # Compare Payment Number
        if isinstance(data["ref"], str) and len(data["ref"]) > 1:
            if getattr(payment, "memo") != data["ref"]:
                return False

        # ====================================================================#
        # Detect Payment Method
        payment_method = InvoicePaymentsHelper.__detect_payment_method(data)
        # ==================================================================== #
        # Compare Payment Journal
        if payment_method is None or payment.journal_id.id == payment_method.journal_id.id:
            return None

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
        from odoo.addons.splashsync.helpers.objects.invoices import InvoiceStatusHelper
        payment_name = str(payment.name)
        try:
            # ==================================================================== #
            # Unit Tests - Ensure Invoice is Open (Default draft)
            if Framework.isDebugMode() and invoice.state == 'draft':
                InvoiceStatusHelper.set_validated(invoice)
            # ====================================================================#
            # UnReconcile Payment
            for partials in invoice._get_reconciled_invoices_partials()[0]:
                if partials[2].payment_id.id == payment.id:
                    invoice.js_remove_outstanding_partial(partials[0].id)
            # ====================================================================#
            # Cancel && Delete Payment
            payment.action_cancel()
            payment.unlink()

            return True
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

    # ====================================================================#
    # Forwarded Methods
    # ====================================================================#

    @staticmethod
    def get_payments_list(invoice):
        """
        Get List of Payments For this Invoice

        :return: List of Payments
        :rtype: dict
        """
        return invoice._get_reconciled_payments()

    @staticmethod
    def get_sales_types_filter():
        """
        Get Account Journals Filters for Listing Available Customers Payment Methods

        :return: tuple
        """
        return [
            ('type', 'in', ["cash", "bank", "credit", "general"]),
            ('default_account_id', '<>', None),
        ]

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
        # Payment Number
        if field_id in ["ref", "memo"]:
            return getattr(payment, "memo")
        # ==================================================================== #
        # Payment Method
        if field_id == "journal_code":
            return M2OHelper.get_name(payment, "payment_method_line_id", "name")
        if field_id == "journal_name":
            return M2OHelper.get_name(payment, "journal_id")
        if field_id == "journal_type":
            return M2OHelper.get_name(payment, "journal_id", "type")
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
    def __detect_payment_method(payment_data):
        """
        Search for Payment method on all Available Journals

        :param payment_data: dict

        :return: None|account.payment.method.line
        """

        # ====================================================================#
        # Detect Payment Method Code
        method_code = payment_data["journal_code"] if "journal_code" in payment_data else "default"
        # ====================================================================#
        # Search for Account Journals with Filter
        journals = http.request.env["account.journal"].search(
            InvoicePaymentsHelper.get_sales_types_filter(),
            limit=50
        )
        # ====================================================================#
        # Walk on Sales Journals to Identify by Payment methode Name
        for journal in journals:
            # ====================================================================#
            # Get Journal Payment Methods
            payment_methods = journal.inbound_payment_method_line_ids if float(payment_data["amount"]) > 0 else journal.outbound_payment_method_line_ids
            # ====================================================================#
            # Walk on Payment Method
            for payment_method in payment_methods:
                # ====================================================================#
                # Filter on Manual Payment Method
                if payment_method.code != 'manual':
                    continue
                # ====================================================================#
                # Filter on Method Name
                if payment_method.name.lower() != method_code.lower():
                    continue

                return payment_method
        # ====================================================================#
        # Walk on Sales Journals to Identify by Journal Name
        for journal in journals:
            # ====================================================================#
            # Filter on Journal Name
            if journal.name.lower() != method_code.lower():
                continue
            # ====================================================================#
            # Get Journal Payment Methods
            payment_methods = journal.inbound_payment_method_line_ids if float(payment_data["amount"]) > 0 else journal.outbound_payment_method_line_ids
            # ====================================================================#
            # Walk on Payment Method
            for payment_method in payment_methods:
                # ====================================================================#
                # Filter on Manual Payment Method
                if payment_method.code != 'manual':
                    continue
                # ====================================================================#
                # Return Fist Manual Payment Method
                return payment_method

        # ====================================================================#
        # Use Default Journal
        from odoo.addons.splashsync.helpers.settings import SettingsManager
        journal = SettingsManager.get_sales_journal()
        if journal:
            # ====================================================================#
            # Get Journal Payment Methods
            payment_methods = journal.inbound_payment_method_line_ids if float(payment_data["amount"]) > 0 else journal.outbound_payment_method_line_ids
            # ====================================================================#
            # Walk on Payment Method
            for payment_method in payment_methods:
                # ====================================================================#
                # Filter on Manual Payment Method
                if payment_method.code != 'manual':
                    continue
                # ====================================================================#
                # Return Fist Manual Payment Method
                return payment_method

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

