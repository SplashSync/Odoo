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


class OdooV13StatusHelper:
    """
    Odoo 13 Invoice Status Helper
    """

    __known_state = {
        'cancel': 'Cancelled',
        'draft': 'Draft',
        'posted': 'Posted',
        'paid': 'Paid',
    }

    __known_state_trans = {
        'cancel': 'PaymentCanceled',
        'draft': 'PaymentDraft',
        'posted': 'PaymentDue',
        'paid': 'PaymentComplete',
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
        return invoice.state in ["posted"]

    @staticmethod
    def is_paid(invoice):
        """
        Check if Invoice is Paid

        :param invoice:
        :return: bool
        """
        if not OdooV13StatusHelper.is_validated(invoice):
            return False
        try:
            return invoice.payment_state in ["paid"]
        except Exception:
            return invoice.invoice_payment_state in ["paid"]

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
        OdooV13StatusHelper.set_status(invoice, 'posted')

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
        if new_state == 'cancel' and invoice.state in ['draft', 'posted']:
            invoice.button_cancel()
            invoice.refresh()
        # ====================================================================#
        # NOT Cancel
        if invoice.state == 'cancel' and new_state in ['draft', 'posted']:
            invoice.button_draft()
            invoice.refresh()
        # ====================================================================#
        # IS Draft
        if new_state == 'draft':
            # ====================================================================#
            # TRY Validated => Cancel (Require Journal Update)
            if invoice.state in ['posted']:
                invoice.button_cancel()
                invoice.refresh()
            # ====================================================================#
            # Cancel => Draft
            if invoice.state in ['cancel']:
                invoice.button_draft()
                invoice.refresh()
        # ====================================================================#
        # Draft => Posted
        if invoice.state == 'draft' and new_state in ['posted']:
            invoice.action_post()
            invoice._compute_amount()
            invoice.refresh()

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
            if OdooV13StatusHelper.is_paid(invoice_or_state):
                return "PaymentComplete"
            state = invoice_or_state.state

        if state in OdooV13StatusHelper.__known_state_trans.keys():
            return OdooV13StatusHelper.__known_state_trans[state]
        return ""

    @staticmethod
    def to_odoo(state):
        """
        Get Odoo Invoice Status

        :param state: str
        :rtype: str|None
        """
        for odoo_state, splash_state in OdooV13StatusHelper.__known_state_trans.items():
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
        for status, name in OdooV13StatusHelper.__known_state.items():
            response.append((
                OdooV13StatusHelper.__known_state_trans[status],
                '['+OdooV13StatusHelper.__known_state_trans[status]+'] '+name
            ))

        return response


