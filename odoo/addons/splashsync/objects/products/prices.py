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
from odoo.addons.splashsync.helpers import CurrencyHelper

class ProductsPrices:
    """
    Access to product Prices Fields
    """

    def buildPricesFields(self):
        # ==================================================================== #
        # Product Selling Price
        FieldFactory.create(const.__SPL_T_PRICE__, "price", "Customer Price")
        FieldFactory.group("General")
        FieldFactory.microData("http://schema.org/Product", "price")

    def getPricesFields(self, index, field_id):
        # ==================================================================== #
        # Read Product Template Id
        if field_id != "price":
            return

        # ==================================================================== #
        # Fetch Product Infos
        price_ht = float(self.object.price)
        tax_rate = 0.0
        code = CurrencyHelper.get_main_currency_code()
        # ==================================================================== #
        # Build Price Array
        self._out[field_id] = PricesHelper.encode(price_ht, tax_rate, None, code)
        self._in.__delitem__(index)


    # def getVariantsFields(self, index, field_id):
    #     # ==================================================================== #
    #     # Check if this Variant Field...
    #     base_field_id = ListHelper.initOutput(self._out, "Variants", field_id)
    #     if base_field_id is None:
    #         return
    #     # ==================================================================== #
    #     # Check if Product has Variants
    #     if not AttributesHelper.has_attr(self.object):
    #         self._in.__delitem__(index)
    #         return
    #     # ==================================================================== #
    #     # List Product Variants Ids
    #     for variant in self.object.product_variant_ids:
    #         # ==================================================================== #
    #         # Debug Mode => Filter Current Product From List
    #         if Framework.isDebugMode() and variant.id == self.object.id:
    #             continue
    #         # ==================================================================== #
    #         # Read Variant Data
    #         if base_field_id == "id":
    #             value = ObjectsHelper.encode("Product", str(variant.id))
    #         elif base_field_id == "sku":
    #             value = str(variant.code)
    #         ListHelper.insert(self._out, "Variants", field_id, "var-"+str(variant.id), value)
    #
    #     self._in.__delitem__(index)

    # def setVariantsFields(self, field_id, field_data):
    #     """Update of Product Variants Not Allowed"""
    #     if field_id == "Variants":
    #         self.detect_variant_template()
    #         self._in.__delitem__(field_id)



