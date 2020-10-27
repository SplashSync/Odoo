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

from collections import OrderedDict
from splashpy import const, Framework
from splashpy.componants import FieldFactory
from splashpy.helpers import ListHelper

class OrderDelivery:
    """
    Access to Order Delivery Fields
    """

    def buildDeliveryFields(self):
        # ====================================================================#
        # Delivery Qty Details (SKU)
        FieldFactory.create(const.__SPL_T_VARCHAR__, "default_code", "Product SKU")
        FieldFactory.inlist("delivery")
        FieldFactory.microData("http://schema.org/OrderItem", "orderItemNumber")
        FieldFactory.isNotTested()
        # ====================================================================#
        # Delivery Qty Details (Shipped)
        FieldFactory.create(const.__SPL_T_INT__, "product_uom_qty", "Ordered Qty")
        FieldFactory.inlist("delivery")
        FieldFactory.microData("http://schema.org/OrderItem", "orderQuantity")
        FieldFactory.isReadOnly().isNotTested()
        # ====================================================================#
        # Delivery Qty Details (Shipped)
        FieldFactory.create(const.__SPL_T_INT__, "qty_delivered", "Delivered Qty")
        FieldFactory.inlist("delivery")
        FieldFactory.microData("http://schema.org/OrderItem", "orderItemStatus")
        FieldFactory.isNotTested()

    def getDeliveryFields(self, index, field_id):
        """
        Get Order Delivered Details List

        :param index: str
        :param field_id: str
        :return: None
        """
        # ==================================================================== #
        # Init Lines List...
        lines_list = ListHelper.initOutput(self._out, "delivery", field_id)
        # ==================================================================== #
        # Safety Check
        if lines_list is None:
            return
        # ==================================================================== #
        # Read Lines Data
        lines_values = OrderDelivery.__get_delivered_values(self.object.order_line, lines_list)
        for pos in range(len(lines_values)):
            ListHelper.insert(self._out, "delivery", field_id, "line-" + str(pos), lines_values[pos])
        # ==================================================================== #
        # Force Lines Ordering
        self._out["delivery"] = OrderedDict(sorted(self._out["delivery"].items()))
        self._in.__delitem__(index)

    def setDeliveryFields(self, field_id, field_data):
        """
        Set Order Delivered Details List

        :param field_id: str
        :param field_data: hash
        :return: None
        """
        # ==================================================================== #
        # Safety Check - field_id is an Order lines List
        if field_id != "delivery":
            return
        self._in.__delitem__(field_id)
        # ==================================================================== #
        # Safety Check - Received List is Valid
        if not isinstance(field_data, dict):
            return
        # ==================================================================== #
        # Walk on Received Order Lines...
        for line_data in field_data.values():
            # ==================================================================== #
            # Detect Pointed Order Line
            order_line = None
            try:
                for line in self.object.order_line:
                    if line.product_id.default_code != line_data["default_code"]:
                        continue
                    order_line = line
            except:
                pass
            if order_line is None:
                continue
            # ==================================================================== #
            # Load Delivered Qty
            try:
                qty_delivered = int(line_data["qty_delivered"])
            except:
                continue
            # ==================================================================== #
            # Compare Delivered Qty
            if qty_delivered == order_line.qty_delivered:
                continue
            if qty_delivered > order_line.product_uom_qty:
                Framework.log().warn(
                    "Delivered Qty is Higher than Ordered Qty for "+str(line.product_id.default_code)
                )

            # ==================================================================== #
            # Update Delivered Qty
            order_line.qty_delivered_method = 'manual'
            order_line.qty_delivered_manual = qty_delivered

    @staticmethod
    def __get_delivered_values(order_lines, field_id):
        """
        Get List of Lines Values for given Field

        :param order_lines: recordset
        :param field_id: str
        :return: dict
        """
        values = []
        # ====================================================================#
        # Walk on Lines
        for order_line in order_lines.filtered(lambda r: r.display_type is False):
            # ==================================================================== #
            # Linked Product ID
            if field_id == "default_code":
                try:
                    values += [str(order_line.product_id[0].default_code)]
                except:
                    values += [None]
            # ====================================================================#
            # Qty Ordered | Qty Shipped/Delivered
            if field_id in ['product_uom_qty', 'qty_delivered']:
                values += [int(getattr(order_line, field_id))]

        return values

