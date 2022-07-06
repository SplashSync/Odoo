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


class Odoo14PaymentCrudHelper:
    """
    Odoo 14 Invoice Payments Crud Helper
    """

    @staticmethod
    def add(invoice, payment_data):
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
            if SystemManager.compare_version(14) >= 0:
                payment_date = datetime.strptime(payment_data["date"], const.__SPL_T_DATECAST__).date()
            else:
                payment_date = datetime.strptime(payment_data["payment_date"], const.__SPL_T_DATECAST__).date()
        except:
            Framework.log().error("Unable to format payment date.")
            return None
        # ====================================================================#
        # Create Payment Using Wizard
        payments = SystemManager.getModel("account.payment.register").with_context(
            {'active_model': 'account.move',
             'active_ids': invoice.ids}
        ).create({
            "journal_id":       payment_data["journal_id"],
            "amount":           payment_data["amount"],
            "communication":    payment_data["ref"] if SystemManager.compare_version(14) >= 0 else payment_data["communication"],
            'payment_date':     payment_date,
            "payment_type":     payment_data["payment_type"],
        }).action_create_payments()

        return SystemManager.getModel("account.payment").browse(payments['res_id'])

    @staticmethod
    def remove(invoice, payment):
        """
        Remove a Payment fom an Invoice

        :param invoice: account.move
        :param payment: account.payment

        :rtype: bool
        """
        # ====================================================================#
        # UnReconcile Payment
        invoice.refresh()
        for partials in invoice._get_reconciled_invoices_partials():
            if partials[2].payment_id.id == payment.id:
                invoice.js_remove_outstanding_partial(partials[0].id)
        # ====================================================================#
        # Cancel && Delete Payment
        payment.action_cancel()
        try:
            payment.unlink()
        except Exception as exception:
            Framework.log().fromException(exception, False)

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
            ('default_account_id', '<>', None),
        ]
