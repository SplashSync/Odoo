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

from splashpy import const, Framework
from splashpy.componants import FieldFactory
from splashpy.helpers import ListHelper, PricesHelper, ObjectsHelper
from odoo.addons.splashsync.helpers import CurrencyHelper, TaxHelper, SettingsManager, M2MHelper


class Orderslines:
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
        FieldFactory.create(const.__SPL_T_VARCHAR__, "desc", "Product Desc")
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
        """
        # ==================================================================== #
        # Check if this Field is Orderlines List...
        base_field_id = ListHelper.initOutput(self._out, "Orderlines", field_id)
        if base_field_id is None:
            return
        # ==================================================================== #
        # List Order Lines Ids
        for line in self.object.order_line:
            # ==================================================================== #
            # Debug Mode => Filter Current Order From List
            if Framework.isDebugMode() and line.id == self.object.id:
                continue
            # ==================================================================== #
            # Read Product Lines Data
            lin_values = self._get_lines_values(base_field_id)
            for pos in range(len(lin_values)):
                ListHelper.insert(self._out, "Orderlines", field_id, "attr-" + str(pos), lin_values[pos])
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
        for lin_value in self.object.order_line:
            # Collect Values
            if value_id == "product_id":
                values += [ObjectsHelper.encode("Product", str(lin_value.product_id[0].id))]
                # values += [lin_value.product_id[0].code]
            elif value_id == "desc":
                values += [lin_value.name]
            elif value_id == "ord_qty":
                values += [lin_value.product_uom_qty]
            elif value_id == "delv_qty":
                values += [lin_value.qty_delivered]
            elif value_id == "inv_qty":
                values += [lin_value.qty_invoiced]
            elif value_id == "ut_price":
                values += [PricesHelper.encode(
                            float(lin_value.price_unit),
                            TaxHelper.get_tax_rate(lin_value.tax_id, 'sale') if not SettingsManager.is_prd_adv_taxes() else float(0),
                            None,
                            CurrencyHelper.get_main_currency_code()
                            )]
            elif value_id == "tax_name":
                values += [M2MHelper.get_names(lin_value, "tax_id")]
            elif value_id == "lead_time":
                values += [lin_value.customer_lead]

        return values


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