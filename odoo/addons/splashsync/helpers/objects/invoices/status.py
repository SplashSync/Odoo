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


class InvoiceStatusHelper:
    """
    Odoo Invoice Status Helper
    """

    # ====================================================================#
    # Invoice State Getters
    # ====================================================================#

    @staticmethod
    def is_draft(invoice):
        """
        Check if Invoice is Draft

        :param invoice:
        :return: bool
        """
        return invoice.state in ["draft"]

    @staticmethod
    def is_canceled(invoice):
        """
        Check if Invoice is Canceled

        :param invoice:
        :return: bool
        """
        return invoice.state in ["cancel"]


    @staticmethod
    def is_validated(invoice):
        """
        Check if Invoice is Validated

        :param invoice:
        :return: bool
        """
        return InvoiceStatusHelper.__get_helper().is_validated(invoice)

    @staticmethod
    def is_paid(invoice):
        """
        Check if Invoice is Paid

        :param invoice:
        :return: bool
        """
        return InvoiceStatusHelper.__get_helper().is_paid(invoice)

    @staticmethod
    def is_editable(invoice):
        """
        Check if Invoice Status is Editable

        :param invoice:
        :rtype: bool
        """
        return not InvoiceStatusHelper.is_validated(invoice)

    # ====================================================================#
    # Invoice State Setters
    # ====================================================================#

    def set_validated(invoice):
        """
        Mark Invoice as Validated

        :param invoice: account.invoice
        :rtype: None
        """
        InvoiceStatusHelper.__get_helper().set_validated(invoice)

    @staticmethod
    def set_status(invoice, new_state):
        """
        Really set Invoice Status
        :param invoice: account.invoice
        :param new_state: str

        :rtype: bool
        """
        return InvoiceStatusHelper.__get_helper().set_status(invoice, new_state)

    # ====================================================================#
    # Splash Methods
    # ====================================================================#

    @staticmethod
    def to_splash(invoice_or_state):
        """
        Get Translated Invoice Status

        :param invoice_or_state: account.invoice|str
        :rtype: str
        """
        return InvoiceStatusHelper.__get_helper().to_splash(invoice_or_state)

    @staticmethod
    def to_odoo(state):
        """
        Get Odoo Invoice Status

        :param state: str
        :rtype: str|None
        """
        return InvoiceStatusHelper.__get_helper().to_odoo(state)

    @staticmethod
    def get_status_choices():
        """
        Get List Of Possible Order Status Choices

        :rtype: dict
        """
        return InvoiceStatusHelper.__get_helper().get_status_choices()

    # ====================================================================#
    # Private Methods
    # ====================================================================#

    @staticmethod
    def __get_helper():
        """
        Get Adapted Invoices Status Helper

        :rtype: OdooV12StatusHelper|OdooV13StatusHelper
        """
        from odoo.addons.splashsync.helpers import SystemManager
        if SystemManager.compare_version(12) == 0:
            from odoo.addons.splashsync.helpers.objects.invoices.V12 import OdooV12StatusHelper
            return OdooV12StatusHelper
        elif SystemManager.compare_version(13) >= 0:
            from odoo.addons.splashsync.helpers.objects.invoices.V13 import OdooV13StatusHelper
            return OdooV13StatusHelper
