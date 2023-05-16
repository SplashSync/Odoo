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

from splashpy import Framework

class OdooV12StatusHelper:
    """
    Odoo V12 Invoice Status Helper
    """

    __known_state = {
        'draft': 'Draft',
        'open': 'Open',
        'in_payment': 'In Payment',
        'paid': 'Paid',
        'cancel': 'Cancelled',
    }

    __known_state_trans = {
        'draft': 'PaymentDraft',
        'open': 'PaymentDue',
        'in_payment': 'PaymentDue',
        'paid': 'PaymentComplete',
        'cancel': 'PaymentCanceled',
    }

    # ====================================================================#
    # Invoice State Getters
    # ====================================================================#

    @staticmethod
    def is_validated(invoice):
        """
        Check if Invoice is Validated

        :param invoice:
        :return: bool
        """
        return invoice.state in ["open", "in_payment", "paid"]

    @staticmethod
    def is_paid(invoice):
        """
        Check if Invoice is Paid

        :param invoice:
        :return: bool
        """
        return invoice.state in ["paid"]



    # ====================================================================#
    # Invoice State Setters
    # ====================================================================#

    @staticmethod
    def set_validated(invoice):
        """
        Mark Invoice as Validated

        :param invoice: account.invoice
        :rtype: None
        """
        OdooV12StatusHelper.set_status(invoice, 'open')

    @staticmethod
    def set_status(invoice, new_state):
        """
        Really set Invoice Status

        :param invoice: account.invoice
        :param new_state: str

        :rtype: bool
        """
        # ====================================================================#
        # IS Cancel
        if new_state == 'cancel' and invoice.state in ['draft', 'open', 'in_payment', 'paid']:
            if Framework.isDebugMode():
                invoice.journal_id.update_posted = True
            invoice.action_invoice_cancel()
            invoice.refresh()
        # ====================================================================#
        # NOT Cancel
        if invoice.state == 'cancel' and new_state in ['draft', 'open', 'in_payment', 'paid']:
            invoice.action_invoice_draft()
            invoice.refresh()
        # ====================================================================#
        # IS Draft
        if new_state == 'draft':
            # ====================================================================#
            # TRY Validated => Cancel (Require Journal Update)
            if invoice.state in ['open', 'in_payment', 'paid']:
                if Framework.isDebugMode():
                    invoice.journal_id.update_posted = True
                invoice.action_invoice_cancel()
                invoice.refresh()
            # ====================================================================#
            # Cancel => Draft
            if invoice.state in ['cancel']:
                invoice.action_invoice_draft()
                invoice.refresh()
        # ====================================================================#
        # Draft => Open
        if invoice.state == 'draft' and new_state in ['open', 'in_payment', 'paid']:
            invoice.action_invoice_open()
            invoice.refresh()
        # # ====================================================================#
        # # Open => Paid
        # if invoice.state == 'open' and new_state in ['in_payment', 'paid']:
        #     invoice.action_invoice_paid()
        #     invoice.refresh()

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
        if isinstance(invoice_or_state, str):
            state = invoice_or_state
        else:
            state = invoice_or_state.state

        if state in OdooV12StatusHelper.__known_state_trans.keys():
            return OdooV12StatusHelper.__known_state_trans[state]
        return ""

    @staticmethod
    def to_odoo(state):
        """
        Get Odoo Invoice Status

        :param state: str
        :rtype: str|None
        """
        for odoo_state, splash_state in OdooV12StatusHelper.__known_state_trans.items():
            if state == splash_state:
                return odoo_state
        return None

    @staticmethod
    def get_status_choices():
        """
        Get List Of Possible Order Status Choices

        :rtype: dict
        """
        response = []
        for status, name in OdooV12StatusHelper.__known_state.items():
            if Framework.isDebugMode() and status in ['in_payment', 'paid']:
                continue
            response.append((
                OdooV12StatusHelper.__known_state_trans[status],
                '['+OdooV12StatusHelper.__known_state_trans[status]+'] '+name
            ))

        return response


