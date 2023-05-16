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
from odoo.addons.splashsync.helpers import InvoiceStatusHelper

class InvoiceStatus:
    """
    Access to Invoice Status Fields
    """

    __new_state = None

    def buildStatusFields(self):
        """
        Build Invoices Status Fields

        :return: void
        """
        # ====================================================================#
        # Invoice Global State
        FieldFactory.create(const.__SPL_T_VARCHAR__, "state", "Invoice Status")
        FieldFactory.microData("http://schema.org/Invoice", "paymentStatus")
        FieldFactory.addChoices(InvoiceStatusHelper.get_status_choices())
        FieldFactory.association("name@lines", "quantity@lines", "price_unit@lines")
        FieldFactory.group("General")
        FieldFactory.isNotTested()
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
        """
        Get Invoices Status Fields

        :param index: str
        :param field_id: str
        :return: void
        """
        # ====================================================================#
        # Invoice Global State
        if field_id == "state":
            self._out[field_id] = InvoiceStatusHelper.to_splash(self.object)
            self._in.__delitem__(index)
        # Invoice is Draft
        if field_id == "isDraft":
            self._out[field_id] = InvoiceStatusHelper.is_draft(self.object)
            self._in.__delitem__(index)
        # Invoice is Validated
        if field_id == "isValidated":
            self._out[field_id] = InvoiceStatusHelper.is_validated(self.object)
            self._in.__delitem__(index)
        # Invoice is Closed
        if field_id == "isPaid":
            self._out[field_id] = InvoiceStatusHelper.is_paid(self.object)
            self._in.__delitem__(index)
        # Invoice is Canceled
        if field_id == "isCanceled":
            self._out[field_id] = InvoiceStatusHelper.is_canceled(self.object)
            self._in.__delitem__(index)

    def setStatusFields(self, field_id, field_data):
        """
        Set Invoices Status Fields
            - Only Translate & Store Requested Status for Post Update
        :param field_id:
        :param field_data:
        :return:
        """
        # ====================================================================#
        # New Invoice State
        if field_id == "state":
            #  Translate State
            self.__new_state = InvoiceStatusHelper.to_odoo(field_data)
            self._in.__delitem__(field_id)

    def post_set_status(self):
        """
        Post set of Invoice Status

        :rtype: bool
        """
        from odoo.exceptions import UserError
        # ====================================================================#
        # Check if New State received
        if self.__new_state is None:
            return True
        new_state = self.__new_state
        self.__new_state = None
        # ====================================================================#
        # Compare States
        if new_state == self.object.state:
            return True
        # ====================================================================#
        # Update State
        try:
            InvoiceStatusHelper.set_status(self.object, new_state)
        except UserError as exception:
            return Framework.log().fromException(exception, False)

        return True
