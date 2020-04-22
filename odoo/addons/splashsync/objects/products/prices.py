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
from splashpy.helpers import PricesHelper
from odoo.addons.splashsync.models.configuration import ResConfigSettings
from odoo.addons.splashsync.helpers import CurrencyHelper, TaxHelper


class ProductsPrices:
    """
    Access to product Prices Fields
    """

    def buildPricesFields(self):
        # ==================================================================== #
        # Product Selling Price
        FieldFactory.create(const.__SPL_T_PRICE__, "list_price", "Sell Price")
        FieldFactory.group("General")
        FieldFactory.microData("http://schema.org/Product", "price")

        # ==================================================================== #
        # Product Cost Price
        FieldFactory.create(const.__SPL_T_PRICE__, "standard_price", "Buy Price")
        FieldFactory.group("General")
        FieldFactory.microData("http://schema.org/Product", "wholesalePrice")

    def getPricesFields(self, index, field_id):
        # Check if Price Field...
        if not self.isPricesFields(field_id):
            return
        # ==================================================================== #
        # Read Sell Price
        if field_id == "list_price":
            self._out[field_id] = PricesHelper.encode(
                float(self.object.lst_price),
                TaxHelper.get_tax_rate(self.object.taxes_id, 'sale'),
                None,
                CurrencyHelper.get_main_currency_code()
            )
            self._in.__delitem__(index)

        # ==================================================================== #
        # Read Buy Price
        if field_id == "standard_price":
            self._out[field_id] = PricesHelper.encode(
                float(self.object.standard_price),
                TaxHelper.get_tax_rate(self.object.supplier_taxes_id, 'purchase'),
                None,
                CurrencyHelper.get_main_currency_code()
            )
            self._in.__delitem__(index)

    def setPricesFields(self, field_id, field_data):
        # Check if Price Field...
        if not self.isPricesFields(field_id):
            return
        # ==================================================================== #
        # Update Price
        self.setSimple(field_id, PricesHelper.taxExcluded(field_data) - self.object.price_extra)
        # ==================================================================== #
        # Update Product Sell Taxes
        if field_id == "list_price":
            tax_rate = PricesHelper.taxPercent(field_data)
            if tax_rate > 0:
                tax = TaxHelper.find_by_rate(tax_rate, 'sale')
                if tax is None:
                    return Framework.log().error("Unable to Identify Tax ID for Rate "+str(tax_rate))
                else:
                    self.object.taxes_id = [(6, 0, [tax.id])]
            else:
                self.object.taxes_id = [(6, 0, [])]
        # ==================================================================== #
        # Update Product Buy Taxes
        if field_id == "standard_price":
            tax_rate = PricesHelper.taxPercent(field_data)
            if tax_rate > 0:
                tax = TaxHelper.find_by_rate(tax_rate, 'purchase')
                if tax is None:
                    return Framework.log().error("Unable to Identify Tax ID for Rate "+str(tax_rate))
                else:
                    self.object.supplier_taxes_id = [(6, 0, [tax.id])]
            else:
                self.object.supplier_taxes_id = [(6, 0, [])]

    @staticmethod
    def isPricesFields(field_id):
        if field_id in ["list_price", "standard_price"]:
            return True
        return False

