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

    __new_state = None

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

    def buildStatusFields(self):
        """
        Build Invoices Status Fields

        :return: void
        """
        # ====================================================================#
        # Order Global State
        FieldFactory.create(const.__SPL_T_VARCHAR__, "state", "Invoice Status")
        FieldFactory.microData("http://schema.org/Invoice", "paymentStatus")
        FieldFactory.addChoices(InvoiceStatus.__get_status_choices())
        FieldFactory.association("name@lines", "quantity@lines", "price_unit@lines")
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
        """
        Get Invoices Status Fields

        :param index: str
        :param field_id: str
        :return: void
        """
        # ====================================================================#
        # Invoice Global State
        if field_id == "state":
            self._out[field_id] = self.__spl_state(self.object.state)
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
            self.__new_state = self.__odoo_state(field_data)
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
        # Check if Status Change is Allowed
        if not InvoiceStatus.__is_allowed_status_change(self.object.state, new_state):
            Framework.log().warn('Invoice State Skipped')
            return True
        # ====================================================================#
        # Update State
        try:
            self._set_status(new_state)
        except UserError as exception:
            return Framework.log().fromException(exception, False)
        # ====================================================================#
        # Verify Splash States
        new_state = InvoiceStatus.__spl_state(new_state)
        inv_state = InvoiceStatus.__spl_state(self.object.state)
        if new_state == inv_state:
            return True
        # ====================================================================#
        # An Error Occurred
        Framework.log().error('Splash was unable to update Invoice State')
        Framework.log().error('Asked for '+new_state+" but found "+inv_state)

        return False

    def pre_validate_status_if_possible(self):
        """
        Pre Validate Invoice if Possible
        I.e: When we want to Add Payment to a New Invoice (Already Validated)
        :rtype: bool
        """
        # ====================================================================#
        # Check if Invoice is Draft
        if self.object.state not in ['draft']:
            return True
        # ====================================================================#
        # Check if New State received but NOT parsed
        if "state" in self._in and isinstance(self._in['state'], str):
            self.__new_state = self.__odoo_state(self._in['state'])
        # ====================================================================#
        # Check New State is Valid
        if not isinstance(self.__new_state, str):
            return False
        if self.__new_state not in ['open', 'in_payment', 'paid']:
            return False
        # ====================================================================#
        # Update State DRAFT => OPEN
        self._set_status('open')

        return True

    def _is_editable(self, state=None):
        """
        Check if Order Status is Editable

        :rtype: bool
        """
        if state is None:
            return self.object.state == "draft"
        return state == "draft"

    def _set_status(self, new_state):
        """
        Really set Invoice Status
        :rtype: bool
        """
        # ====================================================================#
        # IS Cancel
        if new_state == 'cancel' and self.object.state in ['draft', 'open', 'in_payment', 'paid']:
            if Framework.isDebugMode():
                self.object.journal_id.update_posted = True
            self.object.action_invoice_cancel()
            self.object.refresh()
        # ====================================================================#
        # NOT Cancel
        if self.object.state == 'cancel' and new_state in ['draft', 'open', 'in_payment', 'paid']:
            self.object.action_invoice_draft()
            self.object.refresh()
        # ====================================================================#
        # IS Draft
        if new_state == 'draft':
            # ====================================================================#
            # TRY Validated => Cancel (Require Journal Update)
            if self.object.state in ['open', 'in_payment', 'paid']:
                if Framework.isDebugMode():
                    self.object.journal_id.update_posted = True
                self.object.action_invoice_cancel()
                self.object.refresh()
            # ====================================================================#
            # Cancel => Draft
            if self.object.state in ['cancel']:
                self.object.action_invoice_draft()
                self.object.refresh()
        # ====================================================================#
        # Draft => Open
        if self.object.state == 'draft' and new_state in ['open', 'in_payment', 'paid']:
            self.object.action_invoice_open()
            self.object.refresh()
        # ====================================================================#
        # Open => Paid
        if self.object.state == 'open' and new_state in ['in_payment', 'paid']:
            self.object.action_invoice_paid()
            self.object.refresh()

    @staticmethod
    def __spl_state(state):
        """
        Get Translated Order Status

        :param state: str
        :rtype: str
        """
        if state in InvoiceStatus.__known_state_trans.keys():
            return InvoiceStatus.__known_state_trans[state]
        return ""

    @staticmethod
    def __odoo_state(state):
        """
        Get Odoo Order Status

        :param state: str
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
                continue
            response.append((InvoiceStatus.__known_state_trans[status], name))

        return response

    @staticmethod
    def __is_allowed_status_change(old_status, new_status):
        """
        Check if Invoice Status Change is Allowed
        Strategy: Validation is only possible via Payments Parsing.

        :param old_status:  string
        :param new_status:  string

        :return: bool
        """
        # ==================================================================== #
        # Check if Feature is Enabled
        from odoo.addons.splashsync.helpers import SettingsManager
        if not SettingsManager.is_sales_check_payments():
            return True
        # ====================================================================#
        # Check if Old/Current Status is Validated Status
        if old_status in ['open', 'in_payment', 'paid']:
            return True
        # ====================================================================#
        # Check if New Status is Validated Status
        if new_status in ['open', 'in_payment', 'paid']:
            return False
        return True