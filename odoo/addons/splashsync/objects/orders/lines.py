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

class Orderlines:
    """
    Access to Order line Fields
    """

    def buildLinesFields(self):
        """Build Order Lines Fields"""

        from odoo.addons.splashsync.helpers import SettingsManager, TaxHelper

        # ==================================================================== #
        # [CORE] Order Line Fields
        # ==================================================================== #

        # ==================================================================== #
        # Linked Product ID
        FieldFactory.create(ObjectsHelper.encode("Product", const.__SPL_T_ID__), "product_id", "Product ID")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/Product", "productID")
        FieldFactory.association("product_uom_qty@lines", "price_unit@lines")
        # ==================================================================== #
        # Description
        FieldFactory.create(const.__SPL_T_VARCHAR__, "name", "Product Desc.")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/partOfInvoice", "description")
        FieldFactory.association("product_id@lines", "product_uom_qty@lines", "price_unit@lines")
        # ==================================================================== #
        # Qty Ordered
        FieldFactory.create(const.__SPL_T_INT__, "product_uom_qty", "Ordered Qty")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/QuantitativeValue", "value")
        FieldFactory.association("product_id@lines", "product_uom_qty@lines", "price_unit@lines")
        # ==================================================================== #
        # Qty Shipped/Delivered
        FieldFactory.create(const.__SPL_T_INT__, "qty_delivered_manual", "Delivered Qty")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/OrderItem", "orderDelivery")
        FieldFactory.association("product_id@lines", "product_uom_qty@lines", "price_unit@lines")
        # ==================================================================== #
        # Qty Invoiced
        FieldFactory.create(const.__SPL_T_INT__, "qty_invoiced", "Invoiced Qty")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/OrderItem", "orderQuantity")
        FieldFactory.association("product_id@lines", "product_uom_qty@lines", "price_unit@lines")
        FieldFactory.isReadOnly()
        # ==================================================================== #
        # Line Unit Price (HT)
        FieldFactory.create(const.__SPL_T_PRICE__, "price_unit", "Unit Price")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/PriceSpecification", "price")
        FieldFactory.association("product_id@lines", "product_uom_qty@lines", "price_unit@lines")
        # ==================================================================== #
        # Line Unit Price Reduction (Percent)
        FieldFactory.create(const.__SPL_T_DOUBLE__, "discount", "Discount")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/Order", "discount")
        FieldFactory.association("product_id@lines", "product_uom_qty@lines", "price_unit@lines")
        # ==================================================================== #
        # Sales Taxes (One)
        FieldFactory.create(const.__SPL_T_VARCHAR__, "tax_name", "Tax Name")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/PriceSpecification", "valueAddedTaxName")
        FieldFactory.addChoices(TaxHelper.get_name_values("sale"))
        FieldFactory.isReadOnly(not SettingsManager.is_sales_adv_taxes())
        FieldFactory.isNotTested()
        # ==================================================================== #
        # Sales Taxes (Multi)
        FieldFactory.create(const.__SPL_T_INLINE__, "tax_names", "Taxes")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/PriceSpecification", "valueAddedTaxNames")
        FieldFactory.addChoices(TaxHelper.get_name_values("sale"))
        FieldFactory.isReadOnly(not SettingsManager.is_sales_adv_taxes())
        FieldFactory.isNotTested()

        # ==================================================================== #
        # [EXTRA] Order Line Fields
        # ==================================================================== #

        # ==================================================================== #
        # Product reference
        FieldFactory.create(const.__SPL_T_VARCHAR__, "product_ref", "Product Ref.")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/Product", "ref")
        FieldFactory.isReadOnly().isNotTested()
        # ==================================================================== #
        # Delivery Lead Time
        FieldFactory.create(const.__SPL_T_DOUBLE__, "lead_time", "Customer LeadTime")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/Offer", "deliveryLeadTime")
        FieldFactory.isNotTested()
        # ==================================================================== #
        # Line Status
        FieldFactory.create(const.__SPL_T_VARCHAR__, "state", "Line Status")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/OrderItem", "LineStatus")
        FieldFactory.isReadOnly().isNotTested()

    def getLinesFields(self, index, field_id):
        """
        Get Order Lines List

        :param index: str
        :param field_id: str
        :return: None
        """
        from odoo.addons.splashsync.helpers import OrderLinesHelper

        # ==================================================================== #
        # Init Lines List...
        lines_list = ListHelper.initOutput(self._out, "lines", field_id)
        # ==================================================================== #
        # Safety Check
        if lines_list is None:
            return
        # ==================================================================== #
        # Read Lines Data
        lines_values = OrderLinesHelper.get_values(self.object.order_line, lines_list)
        for pos in range(len(lines_values)):
            ListHelper.insert(self._out, "lines", field_id, "line-" + str(pos), lines_values[pos])
        # ==================================================================== #
        # Force Lines Ordering
        self._out["lines"] = OrderedDict(sorted(self._out["lines"].items()))
        self._in.__delitem__(index)

    def setLinesFields(self, field_id, field_data):
        """
        Set Order Lines List

        :param field_id: str
        :param field_data: hash
        :return: None
        """
        from odoo.addons.splashsync.helpers import OrderLinesHelper

        # ==================================================================== #
        # Safety Check - field_id is an Order lines List
        if field_id != "lines":
            return
        self._in.__delitem__(field_id)
        # ==================================================================== #
        # Safety Check - Received List is Valid
        if not isinstance(field_data, dict):
            return
        # ==================================================================== #
        # Walk on Received Order Lines...
        index = 0
        updated_order_line_ids = []
        for line_data in OrderedDict(sorted(field_data.items())).values():
            # ==================================================================== #
            # Complete Order Line values with computed Information
            line_data = OrderLinesHelper.complete_values(line_data)
            # ==================================================================== #
            # Load or Create Order Line
            try:
                order_line = self.object.order_line[index]
            except:
                order_line = OrderLinesHelper.add_order_line(self.object, line_data)
                if order_line is None:
                    return
            # ==================================================================== #
            # Store Updated Order Line Id
            updated_order_line_ids.append(order_line.id)
            index += 1
            # ==================================================================== #
            # Check if Comment Order Line
            if OrderLinesHelper.is_comment(order_line):
                continue
            # ==================================================================== #
            # Update Order Line Values
            if not OrderLinesHelper.set_values(order_line, line_data):
                return
        # ==================================================================== #
        # Delete Remaining Order Lines...
        for order_line in self.object.order_line:
            if order_line.id not in updated_order_line_ids:
                self.object.order_line = [(3, order_line.id, 0)]
