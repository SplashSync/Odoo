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

from odoo.addons.splashsync.helpers import CurrencyHelper, TaxHelper, SettingsManager, M2MHelper
from splashpy import const, Framework
from splashpy.componants import FieldFactory
from splashpy.helpers import ListHelper, PricesHelper, ObjectsHelper


class Orderlines:
    """
    Access to Order line Fields
    """
    def buildLinesFields(self):
        # ==================================================================== #
        # Order line child fields
        # ==================================================================== #
        FieldFactory.create(ObjectsHelper.encode("Product", const.__SPL_T_ID__), "product_id", "Product ID")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/OrderItem", "orderedItem")
        FieldFactory.isNotTested()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_INT__, "id", "Line ID")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/OrderItem", "lineId")
        FieldFactory.isNotTested()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "state", "Line Status")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/OrderItem", "LineStatus")
        FieldFactory.isNotTested()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "ref", "Product Ref.")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/Product", "ref")
        FieldFactory.isNotTested()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "desc", "Product Desc.")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/Product", "description")
        FieldFactory.isNotTested()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_DOUBLE__, "ord_qty", "Ordered Qty")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/OrderItem", "orderQuantity")
        FieldFactory.isNotTested()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_DOUBLE__, "delv_qty", "Delivered Qty")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/OrderItem", "orderDelivery")
        FieldFactory.isNotTested()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_DOUBLE__, "inv_qty", "Invoiced Qty")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/OrderItem", "orderQuantity")
        FieldFactory.isNotTested()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_PRICE__, "ut_price", "Unit Price")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/UnitPriceSpecification", "price")
        FieldFactory.isNotTested()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_DOUBLE__, "lead_time", "Customer LeadTime")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/Offer", "deliveryLeadTime")
        FieldFactory.isNotTested()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "tax_name", "Taxes")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/Product", "priceTaxNames")
        FieldFactory.isNotTested()

    def getLinesFields(self, index, field_id):
        """
        Get Order Lines List
        :param index: str
        :param field_id: str
        :return: None
        """
        # ==================================================================== #
        # Init Lines List...
        lines_list = ListHelper.initOutput(self._out, "Orderlines", field_id)
        # ==================================================================== #
        # Safety Check
        if lines_list is None:
            return
        # ==================================================================== #
        # List Order Lines Ids
        for line in self.object.order_line:
            # ==================================================================== #
            # Debug Mode => Filter Current Order From List
            if Framework.isDebugMode() and line.id == self.object.id:
                continue
            # ==================================================================== #
            # Read Lines Data
            lines_values = self._get_lines_values(lines_list)
            for pos in range(len(lines_values)):
                ListHelper.insert(self._out, "Orderlines", field_id, "line-" + str(pos), lines_values[pos])
        # ==================================================================== #
        # Force Lines Ordering
        self._out["Orderlines"] = OrderedDict(sorted(self._out["Orderlines"].items()))

        self._in.__delitem__(index)

    def _get_lines_values(self, value_id):
        """
        Get List of Lines Values for given Field
        :param value_id: str
        :return: dict
        """
        values = []
        # ====================================================================#
        # Walk on Product Attributes Values
        for orderline_field in self.object.order_line:
            # Collect Values
            if value_id == "product_id":
                values += [ObjectsHelper.encode("Product", str(orderline_field.product_id[0].id))]
            if value_id == "ref":
                values += [orderline_field.product_id[0].default_code]
            if value_id == "id":
                values += [orderline_field.id]
            if value_id == "state":
                values += [orderline_field.state]
            if value_id == "desc":
                values += [orderline_field.name]
            if value_id == "ord_qty":
                values += [orderline_field.product_uom_qty]
            if value_id == "delv_qty":
                values += [orderline_field.qty_delivered]
            if value_id == "inv_qty":
                values += [orderline_field.qty_invoiced]
            if value_id == "ut_price":
                values += [PricesHelper.encode(
                            float(orderline_field.price_unit),
                            TaxHelper.get_tax_rate(orderline_field.tax_id, 'sale') if not SettingsManager.is_prd_adv_taxes() else float(0),
                            None,
                            CurrencyHelper.get_main_currency_code()
                            )]
            if value_id == "tax_name":
                values += [M2MHelper.get_names(orderline_field, "tax_id")]
            if value_id == "lead_time":
                values += [orderline_field.customer_lead]

        return values

    #######################################

    def setLinesFields(self, field_id, field_data):
        """
        Set Orderlines List
        :param field_id: str
        :param field_data: hash
        :return: None
        """
        # ==================================================================== #
        # Safety Check - field_id is an Orderlines List
        if field_id != "Orderlines":
            return
        # ==================================================================== #
        # Init Lines List
        new_orderline = []
        # Framework.log().dump(field_data, "field_data")
        # ==================================================================== #
        # Safety Check
        if not isinstance(field_data, dict):
            return
        # ==================================================================== #
        # Force Orderlines Ordering
        field_data = OrderedDict(sorted(field_data.items()))
        # ==================================================================== #
        # Walk on Lines Field...
        for pos, line in field_data.items():
            # TODO: set line state
            for obj_line in self.object.order_line:
                if int(obj_line.id) == int(line["id"]):
                    # if line["state"] in ["done", "cancel"]:
                    if line["state"] == "sale":
                        for key, value in line.items():
                            if key == "delv_qty":
                                Framework.log().dump(obj_line.qty_delivered, "obj_line.qty_delivered")
                                setattr(obj_line, "qty_delivered", float(value))
                            if key == "inv_qty":
                                setattr(obj_line, "qty_invoiced", float(value))
                    if line["state"] != "sale":
                        obj_line.product_uom_qty = 0
                        obj_line.unlink()
                        new_orderline.append(Orderlines._set_lines_values(line))
        setattr(self.object, "order_line", new_orderline)
        self._in.__delitem__(field_id)

    @staticmethod
    def _set_lines_values(line):
        """
        Set values of Line Fields
        :param line:
        :return: dict
        """
        ord_line = {}
        for key, value in line.items():
            # IF ORDER NOT CONFIRMED ("sale"), or NOT LOCKED ("done") or NOT CANCELLED ("cancel")
            if line["state"] not in ["sale", "done", "cancel"]:
                if key == "product_id":
                    ord_line["product_id"] = int(ObjectsHelper.id(value))
                if key == "ref":
                    ord_line["product_id[0].default_code"] = value
                if key == "desc":
                    ord_line["name"] = value
                if key == "ord_qty":
                    ord_line["product_uom_qty"] = float(value)
                if key == "delv_qty":
                    ord_line["qty_delivered"] = float(value)
                if key == "inv_qty":
                    ord_line["qty_invoiced"] = float(value)
                if key == "ut_price":
                    ord_line["price_unit"] = PricesHelper.extract(value, "ht")
                if key == "tax_name" and value is not None:
                    ord_line["tax_id"] = TaxHelper.find_by_rate(PricesHelper.extract(value, "vat"), 'sale')
                if key == "lead_time":
                    ord_line["customer_lead"] = float(value)

        return ord_line


class Invoicelines:
    """
    Access to Invoice line Fields
    """
    def buildLinesFields(self):
        # ==================================================================== #
        # Order line child fields
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "product_id", "Product")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/Product", "orderedItem")
        FieldFactory.isNotTested()
        # ==================================================================== #
