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

from splashpy import const
from splashpy.componants import FieldFactory


class OrderStatus:
    """
    Access to Order Status Fields
    """

    __known_state = {
        'draft': 'Quotation',
        'sent': 'Quotation Sent',
        'sale': 'Sales Order',
        'done': 'Locked',
        'cancel': 'Cancelled',
    }

    __known_state_trans = {
        'draft': 'OrderDraft',
        'sent': 'OrderPaymentDue',
        'sale': 'OrderProcessing',
        'done': 'OrderDelivered',
        'cancel': 'OrderCanceled',
    }

    def buildStatusFields(self):
        # ====================================================================#
        # Order Global State
        FieldFactory.create(const.__SPL_T_VARCHAR__, "state", "Order Status")
        FieldFactory.microData("http://schema.org/Order", "orderStatus")
        FieldFactory.addChoices(OrderStatus.__get_status_choices())
        FieldFactory.group("General")
        # ====================================================================#
        # Order is Canceled
        FieldFactory.create(const.__SPL_T_BOOL__, "isCanceled", "Is canceled")
        FieldFactory.microData("http://schema.org/OrderStatus", "OrderCancelled")
        FieldFactory.group("Meta")
        FieldFactory.isReadOnly()
        # ====================================================================#
        # Order is Validated
        FieldFactory.create(const.__SPL_T_BOOL__, "isValidated", "Is Validated")
        FieldFactory.microData("http://schema.org/OrderStatus", "OrderPaymentDone")
        FieldFactory.group("Meta")
        FieldFactory.isReadOnly()
        # ====================================================================#
        # Order is Processing
        FieldFactory.create(const.__SPL_T_BOOL__, "isProcessing", "Is Processing")
        FieldFactory.microData("http://schema.org/OrderStatus", "OrderProcessing")
        FieldFactory.group("Meta")
        FieldFactory.isReadOnly()
        # ====================================================================#
        # Order is Closed
        FieldFactory.create(const.__SPL_T_BOOL__, "isClosed", "Is Closed")
        FieldFactory.microData("http://schema.org/OrderStatus", "OrderDelivered")
        FieldFactory.group("Meta")
        FieldFactory.isReadOnly()

    def getStatusFields(self, index, field_id):
        # ====================================================================#
        # Order Global State
        if field_id == "state":
            self._out[field_id] = self._get_splash_status()
            self._in.__delitem__(index)
        # Order is Canceled
        if field_id == "isCanceled":
            self._out[field_id] = (self.object.state in ["cancel"])
            self._in.__delitem__(index)
        # Order is Validated
        if field_id == "isValidated":
            self._out[field_id] = (self.object.state in ["sent", "sale", "done"])
            self._in.__delitem__(index)
        # Order is Processing
        if field_id == "isProcessing":
            self._out[field_id] = (self.object.state in ["sale"])
            self._in.__delitem__(index)
        # Order is Closed
        if field_id == "isClosed":
            self._out[field_id] = (self.object.state in ["done"])
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
        if self.object.state in OrderStatus.__known_state_trans.keys():
            return OrderStatus.__known_state_trans[self.object.state]
        return ""

    def _get_odoo_status(self, state):
        """
        Get Odoo Order Status

        :rtype: str|None
        """
        for odoo_state, splash_state in OrderStatus.__known_state_trans.items():
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
        for status, name in OrderStatus.__known_state.items():
            response.append((OrderStatus.__known_state_trans[status], name))

        return response
