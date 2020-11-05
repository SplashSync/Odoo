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

        from odoo.addons.splashsync.helpers import SettingsManager, TaxHelper

        # ==================================================================== #
        # [CORE] Invoice Payments Fields
        # ==================================================================== #

        # # ==================================================================== #
        # # Payment Method Name
        # FieldFactory.create(ObjectsHelper.encode("Product", const.__SPL_T_ID__), "product_id", "Product ID")
        # FieldFactory.inlist("payments")
        # FieldFactory.microData("http://schema.org/Invoice", "PaymentMethod")
        # FieldFactory.association("product_uom_qty@lines", "price_unit@lines")
        # # ==================================================================== #
        # # Description
        # FieldFactory.create(const.__SPL_T_VARCHAR__, "name", "Product Desc.")
        # FieldFactory.inlist("payments")
        # FieldFactory.microData("http://schema.org/partOfInvoice", "description")
        # FieldFactory.association("product_id@lines", "product_uom_qty@lines", "price_unit@lines")
        # ==================================================================== #
        # Payment Date
        FieldFactory.create(const.__SPL_T_DATE__, "payment_date", "Date")
        FieldFactory.inlist("payments")
        FieldFactory.microData("http://schema.org/PaymentChargeSpecification", "validFrom")
        # ==================================================================== #
        # Payment Transaction Id
        FieldFactory.create(const.__SPL_T_INT__, "payment_reference", "Transaction Id")
        FieldFactory.inlist("payments")
        FieldFactory.microData("http://schema.org/Invoice", "paymentMethodId")
        # ==================================================================== #
        # Payment Amount
        FieldFactory.create(const.__SPL_T_DOUBLE__, "amount", "Amount")
        FieldFactory.inlist("payments")
        FieldFactory.microData("http://schema.org/PaymentChargeSpecification", "price")

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
        # from odoo.addons.splashsync.helpers import OrderLinesHelper
        #
        # # ==================================================================== #
        # # Safety Check - field_id is an Order lines List
        # if field_id != "lines":
        #     return
        # self._in.__delitem__(field_id)
        # # ==================================================================== #
        # # Safety Check - Received List is Valid
        # if not isinstance(field_data, dict):
        #     return
        # # ==================================================================== #
        # # Walk on Received Order Lines...
        # index = 0
        # updated_order_line_ids = []
        # for line_data in OrderedDict(sorted(field_data.items())).values():
        #     # ==================================================================== #
        #     # Complete Order Line values with computed Information
        #     line_data = OrderLinesHelper.complete_values(line_data)
        #     # ==================================================================== #
        #     # Load or Create Order Line
        #     try:
        #         order_line = self.object.order_line[index]
        #     except:
        #         order_line = OrderLinesHelper.add_order_line(self.object, line_data)
        #         if order_line is None:
        #             return
        #     # ==================================================================== #
        #     # Store Updated Order Line Id
        #     updated_order_line_ids.append(order_line.id)
        #     index += 1
        #     # ==================================================================== #
        #     # Check if Comment Order Line
        #     if OrderLinesHelper.is_comment(order_line):
        #         continue
        #     # ==================================================================== #
        #     # Update Order Line Values
        #     if not OrderLinesHelper.set_values(order_line, line_data):
        #         return
        # # ==================================================================== #
        # # Delete Remaining Order Lines...
        # for order_line in self.object.order_line:
        #     if order_line.id not in updated_order_line_ids:
        #         self.object.order_line = [(3, order_line.id, 0)]
