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

    __known_state_extras = {
        'OrderOutOfStock': 'done',
        'OrderInTransit': 'done',
        'OrderPickupAvailable': 'done',
        'OrderReturned': 'done',
        'OrderProblem': 'done',
    }

    def buildStatusFields(self):
        # ====================================================================#
        # Order Global State
        FieldFactory.create(const.__SPL_T_VARCHAR__, "state", "Order Status")
        FieldFactory.microData("http://schema.org/Order", "orderStatus")
        FieldFactory.addChoices(OrderStatus.__get_status_choices())
        FieldFactory.group("General")
        FieldFactory.isNotTested()
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
        # ====================================================================#
        # Order is Canceled
        if field_id == "isCanceled":
            self._out[field_id] = (self.object.state in ["cancel"])
            self._in.__delitem__(index)
        # ====================================================================#
        # Order is Validated
        if field_id == "isValidated":
            self._out[field_id] = (self.object.state in ["sent", "sale", "done"])
            self._in.__delitem__(index)
        # ====================================================================#
        # Order is Processing
        if field_id == "isProcessing":
            self._out[field_id] = (self.object.state in ["sale"])
            self._in.__delitem__(index)
        # ====================================================================#
        # Order is Closed
        if field_id == "isClosed":
            self._out[field_id] = (self.object.state in ["done"])
            self._in.__delitem__(index)

    def setStatusFields(self, field_id, field_data):
        # ====================================================================#
        # Is Order Global State Field
        if field_id != "state":
            return
        self._in.__delitem__(field_id)
        # ====================================================================#
        # Load Picking Helper
        from odoo.addons.splashsync.helpers import OrderPickingHelper
        # ====================================================================#
        # Check if State Changed
        state = self._get_odoo_status(field_data)
        if not isinstance(state, str) or self.object.state == state:
            return
        # ====================================================================#
        # Update Order State
        try:
            # ====================================================================#
            # UNLOCK Required
            if self.object.state == "done" and state in ['cancel', 'draft', 'send', 'sale']:
                self.object.action_unlock()
            # ====================================================================#
            # UN RESERVE STOCKS
            if state in ['cancel', 'draft']:
                for picking in self.object.picking_ids:
                    picking.action_cancel()
            # ====================================================================#
            # Cancel State
            if state == 'cancel':
                self.object.action_cancel()
            # ====================================================================#
            # IS Draft
            if state == 'draft':
                self.object.action_draft()
            # ====================================================================#
            # IS Send
            if state == 'send':
                self.object.state = state
            # ====================================================================#
            # IS Order
            if state == 'sale':
                self.object.action_confirm()
                for picking in self.object.picking_ids:
                    OrderPickingHelper.confirm(picking)
            # ====================================================================#
            # IS Delivered
            if state == 'done':
                self.object.action_done()
                for picking in self.object.picking_ids:
                    OrderPickingHelper.done(picking)

        except Exception as exception:
            return Framework.log().fromException(exception)

    def _is_editable(self, state=None):
        """
        Check if Order Status is Editable

        :rtype: bool
        """
        if state is None:
            return self.object.state == "draft"
        return state == "draft"

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
        # ====================================================================#
        # Loop on Odoo Standard Order States
        for odoo_state, splash_state in OrderStatus.__known_state_trans.items():
            if state == splash_state:
                return odoo_state
        # ====================================================================#
        # Loop on Splash Extra Order States
        for splash_state, odoo_state in OrderStatus.__known_state_extras.items():
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
