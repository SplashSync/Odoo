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

from odoo.addons.splashsync.helpers import InventoryHelper


class ProductsInventory:
    """
    Access to product Inventory Fields
    """

    def buildInventoryFields(self):
        # ==================================================================== #
        # Product Global Stock
        FieldFactory.create(const.__SPL_T_INT__, "qty_available", "Quantity On Hand")
        FieldFactory.description("Current quantity of products.")
        FieldFactory.microData("http://schema.org/Offer", "inventoryLevel")
        FieldFactory.setPreferNone()

    def getInventoryFields(self, index, field_id):
        # Check if Inventory Field...
        if field_id != "qty_available":
            return
        # ==================================================================== #
        # Read Inventory Level
        self.getSimple(index, field_id)

    def setInventoryFields(self, field_id, field_data):
        # ==================================================================== #
        # Check if Inventory Field...
        if field_id != "qty_available":
            return
        self._in.__delitem__(field_id)
        # ==================================================================== #
        # Ensure Float Value
        field_data = field_data if field_data is not None and float(field_data) > 0 else float(0)
        # ==================================================================== #
        # Compare Stocks Levels
        stock_delta = float(self.object.qty_available) - float(field_data)
        if abs(stock_delta) < 0.001:
            return
        # ==================================================================== #
        # Safety Check - Is Tracked Product
        if self.object.type not in ['product']:
            Framework.log().warn("You can only adjust inventory of storable products.")
            Framework.log().warn("Product "+str(self.object.id)+" is a "+str(self.object.type))
            return
        # ==================================================================== #
        # BASIC METHOD - Create Inventory Adjustment
        InventoryHelper.update_qty_available(self.object, float(field_data))
