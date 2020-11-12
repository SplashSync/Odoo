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
#

from collections import OrderedDict

from splashpy import const, Framework
from splashpy.componants import FieldFactory
from splashpy.helpers import ListHelper, ObjectsHelper

class InvoicePayments:
    """
    Access to Invoice Payments Fields
    """

    def buildPaymentsFields(self):
        """Build Invoice Payments Fields"""
        from odoo.addons.splashsync.helpers import InvoicePaymentsHelper

        # ==================================================================== #
        # [CORE] Invoice Payments Fields
        # ==================================================================== #

        # ==================================================================== #
        # Payment Method Code
        FieldFactory.create(const.__SPL_T_VARCHAR__, "journal_code", "Method")
        FieldFactory.inlist("payments")
        FieldFactory.microData("http://schema.org/Invoice", "PaymentMethod")
        FieldFactory.addChoices(InvoicePaymentsHelper.get_payment_code_names())
        FieldFactory.association("product_id@lines", "name@lines", "quantity@lines", "price_unit@lines", "journal_code@payments", "payment_date@payments", "name@payments", "amount@payments")
        # ==================================================================== #
        # Payment Journal Name
        FieldFactory.create(const.__SPL_T_VARCHAR__, "journal_name", "Journal")
        FieldFactory.inlist("payments")
        FieldFactory.isReadOnly()
        # ==================================================================== #
        # Payment Journal Type
        FieldFactory.create(const.__SPL_T_VARCHAR__, "journal_type", "Journal Type")
        FieldFactory.inlist("payments")
        FieldFactory.isReadOnly()
        # ==================================================================== #
        # Payment Type
        FieldFactory.create(const.__SPL_T_VARCHAR__, "payment_type", "Type")
        FieldFactory.inlist("payments")
        FieldFactory.isReadOnly()
        # ==================================================================== #
        # Payment State
        FieldFactory.create(const.__SPL_T_VARCHAR__, "state", "Status")
        FieldFactory.inlist("payments")
        FieldFactory.isReadOnly()
        # ==================================================================== #
        # Payment Date
        FieldFactory.create(const.__SPL_T_DATE__, "payment_date", "Date")
        FieldFactory.inlist("payments")
        FieldFactory.microData("http://schema.org/PaymentChargeSpecification", "validFrom")
        FieldFactory.association("product_id@lines", "name@lines", "quantity@lines", "price_unit@lines", "journal_code@payments", "payment_date@payments", "name@payments", "amount@payments")
        # ==================================================================== #
        # Payment Transaction Id
        FieldFactory.create(const.__SPL_T_VARCHAR__, "name", "Number")
        FieldFactory.inlist("payments")
        FieldFactory.microData("http://schema.org/Invoice", "paymentMethodId")
        FieldFactory.association("product_id@lines", "name@lines", "quantity@lines", "price_unit@lines", "journal_code@payments", "payment_date@payments", "name@payments", "amount@payments")
        # ==================================================================== #
        # Payment Amount
        FieldFactory.create(const.__SPL_T_DOUBLE__, "amount", "Amount")
        FieldFactory.inlist("payments")
        FieldFactory.microData("http://schema.org/PaymentChargeSpecification", "price")
        FieldFactory.association("product_id@lines", "name@lines", "quantity@lines", "price_unit@lines", "journal_code@payments", "payment_date@payments", "name@payments", "amount@payments")
        if Framework.isDebugMode():
            FieldFactory.addChoice(1.0, 1)
            FieldFactory.addChoice(2.0, 2)
            FieldFactory.addChoice(3.0, 3)

    def getPaymentsFields(self, index, field_id):
        """
        Get Invoice Payments List

        :param index: str
        :param field_id: str
        :return: None
        """
        from odoo.addons.splashsync.helpers import InvoicePaymentsHelper

        # ==================================================================== #
        # Init Payments List...
        payments_list = ListHelper.initOutput(self._out, "payments", field_id)
        # ==================================================================== #
        # Safety Check
        if payments_list is None:
            return
        # ==================================================================== #
        # Read Payments Data
        payment_values = InvoicePaymentsHelper.get_values(self.object.payment_ids, payments_list)
        for pos in range(len(payment_values)):
            ListHelper.insert(self._out, "payments", field_id, "pay-" + str(pos), payment_values[pos])
        # ==================================================================== #
        # Force Lines Ordering
        self._out["payments"] = OrderedDict(sorted(self._out["payments"].items()))
        self._in.__delitem__(index)

    def setPaymentsFields(self, field_id, field_data):
        """
        Set Invoice Payments List

        :param field_id: str
        :param field_data: hash
        :return: None
        """
        from odoo.addons.splashsync.helpers import InvoicePaymentsHelper

        # ==================================================================== #
        # Safety Check - field_id is an Payment List
        if field_id != "payments":
            return
        # ==================================================================== #
        # Safety Check - Received List is Valid
        if not isinstance(field_data, dict):
            field_data = {}
        # ==================================================================== #
        # Walk on Received Payments...
        index = 0
        updated_payment_ids = []
        for payment_data in OrderedDict(sorted(field_data.items())).values():
            # ==================================================================== #
            # Load or Create Order Line
            try:
                payment = self.object.payment_ids.sorted(key=lambda r: r.id)[index]
            except:
                payment = None
            # ==================================================================== #
            # Update Order Line Values
            payment_id = InvoicePaymentsHelper.set_values(self.object, payment, payment_data)
            if payment_id is None:
                return
            # ==================================================================== #
            # Store Updated Order Line Id
            updated_payment_ids.append(payment_id)
            index += 1
        # ==================================================================== #
        # Delete Remaining Payments...
        for payment in self.object.payment_ids:
            if payment.id not in updated_payment_ids:
                InvoicePaymentsHelper.remove(self.object, payment)
        # ==================================================================== #
        # Mark Field as Processed...
        self._in.__delitem__(field_id)
