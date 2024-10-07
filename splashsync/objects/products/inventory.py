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

import re
from splashpy import const, Framework
from splashpy.componants import FieldFactory

from odoo.addons.splashsync.helpers import InventoryHelper, SystemManager

class ProductsInventory:
    """
    Access to product Inventory Fields
    """

    def buildInventoryFields(self):
        # ==================================================================== #
        # Product Global Stock
        FieldFactory.create(const.__SPL_T_INT__, "qty_available", "Quantity On Hand")
        FieldFactory.description("Current quantity of products.")
        FieldFactory.group("Stocks")
        FieldFactory.microData("http://schema.org/Offer", "inventoryLevel")
        FieldFactory.setPreferNone()
        # ==================================================================== #
        # Product Warehouses Stock
        warehouses = SystemManager.getModel("stock.warehouse").search([], limit=50)
        for warehouse in warehouses:
            FieldFactory.create(const.__SPL_T_INT__, "free_qty_wh_"+str(warehouse.id), "Free Qty On "+str(warehouse.code))
            FieldFactory.description("Free quantity of product on Warehouse "+str(warehouse.name))
            FieldFactory.group("Stocks")
            FieldFactory.microData("http://schema.org/Offer", "inventoryLevel"+str(warehouse.code))
            FieldFactory.isReadOnly()

    def getInventoryFields(self, index, field_id):
        # Check if Inventory Field...
        if field_id != "qty_available":
            return
        # ==================================================================== #
        # Read Inventory Level
        self.getSimple(index, field_id)

    def getInventoryWarehouseFields(self, index, field_id):
        """
        Get Stocks by Warehouse Fields
        """
        # ==================================================================== #
        # Check if Inventory Free Qty by Warehouse Field...
        if field_id.startswith("free_qty_wh_"):
            # ==================================================================== #
            # Get Free Qty by Warehouse for Product
            wh_id = re.search(r'\d+$', field_id)
            if wh_id:
                self._out[field_id] = self.object.with_context(warehouse=int(wh_id.group())).free_qty
            else:
                self._out[field_id] = 0
            self._in.__delitem__(index)

            return

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
