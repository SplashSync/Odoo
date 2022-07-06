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

    def buildStatusFields(self):
        """
        Build Invoices Status Fields

        :return: void
        """
        # ====================================================================#
        # Invoice Global State
        FieldFactory.create(const.__SPL_T_VARCHAR__, "state", "Invoice Status")
        FieldFactory.microData("http://schema.org/Invoice", "paymentStatus")
        FieldFactory.addChoices(InvoiceStatus.get_helper().get_status_choices())
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
            self._out[field_id] = self.get_helper().to_splash(self.object)
            self._in.__delitem__(index)
        # Invoice is Draft
        if field_id == "isDraft":
            self._out[field_id] = self.get_helper().is_draft(self.object)
            self._in.__delitem__(index)
        # Invoice is Validated
        if field_id == "isValidated":
            self._out[field_id] = self.get_helper().is_validated(self.object)
            self._in.__delitem__(index)
        # Invoice is Closed
        if field_id == "isPaid":
            self._out[field_id] = self.get_helper().is_paid(self.object)
            self._in.__delitem__(index)
        # Invoice is Canceled
        if field_id == "isCanceled":
            self._out[field_id] = self.get_helper().is_canceled(self.object)
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
            self.__new_state = self.get_helper().to_odoo(field_data)
            self._in.__delitem__(field_id)

    @staticmethod
    def get_helper():
        """
        Get Adapted Invoices Status Helper

        :rtype: Odoo12StatusHelper|Odoo13StatusHelper
        """

        from odoo.addons.splashsync.helpers import SystemManager
        if SystemManager.compare_version(12) == 0:
            from odoo.addons.splashsync.helpers.objects.invoices.statusV12 import Odoo12StatusHelper
            return Odoo12StatusHelper
        elif SystemManager.compare_version(13) >= 0:
            from odoo.addons.splashsync.helpers.objects.invoices.statusV13 import Odoo13StatusHelper
            return Odoo13StatusHelper

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
        StatusHelper = InvoiceStatus.get_helper()
        # ====================================================================#
        # Update State
        try:
            StatusHelper.set_status(self.object, new_state)
        except UserError as exception:
            return Framework.log().fromException(exception, False)
        # ====================================================================#
        # Verify Splash States
        new_state = StatusHelper.to_splash(new_state)
        inv_state = StatusHelper.to_splash(self.object.state)
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
        if not InvoiceStatus.get_helper().is_draft(self.object):
            return True
        # ====================================================================#
        # Check if New State received but NOT parsed
        if "state" in self._in and isinstance(self._in['state'], str):
            self.__new_state = InvoiceStatus.get_helper().to_odoo(self._in['state'])
        # ====================================================================#
        # Check New State is Valid
        if not isinstance(self.__new_state, str):
            return False
        if self.__new_state not in ['open', 'posted', 'in_payment', 'paid']:
            return False
        # ====================================================================#
        # Update State DRAFT => OPEN
        InvoiceStatus.get_helper().set_validated(self.object)

        return True

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
        if old_status in ['open', 'posted', 'in_payment', 'paid']:
            return True
        # ====================================================================#
        # Check if New Status is Validated Status
        if new_status in ['open', 'posted', 'in_payment', 'paid']:
            return False
        return True
