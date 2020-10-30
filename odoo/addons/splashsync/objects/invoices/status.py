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


class InvoiceStatus:
    """
    Access to Invoice Status Fields
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
        'in_payment': 'PaymentComplete',
        'paid': 'PaymentComplete',
        'cancel': 'PaymentCanceled',
    }

    def buildStatusFields(self):
        # ====================================================================#
        # Order Global State
        FieldFactory.create(const.__SPL_T_VARCHAR__, "state", "Invoice Status")
        FieldFactory.microData("http://schema.org/Invoice", "paymentStatus")
        FieldFactory.addChoices(InvoiceStatus.__get_status_choices())
        FieldFactory.group("General")
        # ====================================================================#
        # Order is Draft
        FieldFactory.create(const.__SPL_T_BOOL__, "isDraft", "Is Draft")
        FieldFactory.microData("http://schema.org/PaymentStatusType", "InvoiceDraft")
        FieldFactory.group("Meta")
        FieldFactory.isReadOnly()
        # ====================================================================#
        # Order is Canceled
        FieldFactory.create(const.__SPL_T_BOOL__, "isCanceled", "Is canceled")
        FieldFactory.microData("http://schema.org/PaymentStatusType", "PaymentDeclined")
        FieldFactory.group("Meta")
        FieldFactory.isReadOnly()
        # ====================================================================#
        # Order is Validated
        FieldFactory.create(const.__SPL_T_BOOL__, "isValidated", "Is Validated")
        FieldFactory.microData("http://schema.org/PaymentStatusType", "PaymentDue")
        FieldFactory.group("Meta")
        FieldFactory.isReadOnly()
        # ====================================================================#
        # Order is Paid
        FieldFactory.create(const.__SPL_T_BOOL__, "isPaid", "Is Paid")
        FieldFactory.microData("http://schema.org/PaymentStatusType", "PaymentComplete")
        FieldFactory.group("Meta")
        FieldFactory.isReadOnly()

    def getStatusFields(self, index, field_id):
        # ====================================================================#
        # Invoice Global State
        if field_id == "state":
            self._out[field_id] = self._get_splash_status()
            self._in.__delitem__(index)
        # Invoice is Draft
        if field_id == "isDraft":
            self._out[field_id] = (self.object.state in ["draft"])
            self._in.__delitem__(index)
        # Invoice is Validated
        if field_id == "isValidated":
            self._out[field_id] = (self.object.state in ["in_payment", "paid"])
            self._in.__delitem__(index)
        # Invoice is Closed
        if field_id == "isPaid":
            self._out[field_id] = (self.object.state in ["paid"])
            self._in.__delitem__(index)
        # Invoice is Canceled
        if field_id == "isCanceled":
            self._out[field_id] = (self.object.state in ["cancel"])
            self._in.__delitem__(index)

    def setStatusFields(self, field_id, field_data):
        # ====================================================================#
        # Order Global State
        if field_id == "state":
            state = self._get_odoo_status(field_data)
            if isinstance(state, str) and self.object.state != state:
                self.object.state = state
            self._in.__delitem__(field_id)

    def _is_editable(self, state=None):
        """
        Check if Order Status is Editable

        :rtype: bool
        """
        if state is None:
            return self.object.state is "draft"
        return state is "draft"

    def _get_splash_status(self):
        """
        Get Translated Order Status

        :rtype: str
        """
        if self.object.state in InvoiceStatus.__known_state_trans.keys():
            return InvoiceStatus.__known_state_trans[self.object.state]
        return ""

    def _get_odoo_status(self, state):
        """
        Get Odoo Order Status

        :rtype: str|None
        """
        for odoo_state, splash_state in InvoiceStatus.__known_state_trans.items():
            if state == splash_state:
                return odoo_state
        return None

    @staticmethod
    def __get_status_choices():
        """
        Get List Of Possible Order Status Choices

        :rtype: dict
        """
        response = []
        for status, name in InvoiceStatus.__known_state.items():
            if Framework.isDebugMode() and status in ['in_payment', 'paid']:
                pass
            response.append((InvoiceStatus.__known_state_trans[status], name))

        return response
