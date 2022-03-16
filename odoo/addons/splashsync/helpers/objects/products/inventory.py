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

from odoo import http
from splashpy import Framework


class InventoryHelper:
    """
    Collection of Static Functions to manage Odoo Product Inventory
    """

    @staticmethod
    def create_inventory_adjustment(product, new_quantity):
        """
        Create Product Inventory Adjustment

        :param product: Product
        :param new_quantity: float
        :return: None, stock.inventory
        """
        from odoo.addons.splashsync.helpers import SystemManager
        # ====================================================================#
        # Create New Product Inventory Adjustment
        if SystemManager.compare_version(13) >= 0:
            inventory = InventoryHelper.__get_inventory().create({
                'name': '[SPLASH] Stock Update for %s' % product.display_name,
                'product_ids': [product.id],
                # 'location_id': product.env.ref('stock.stock_location_stock').id,
                'line_ids': [(0, 0, InventoryHelper.__get_adjustment_line(product, new_quantity))],
            })
        else:
            inventory = InventoryHelper.__get_inventory().create({
                'name': '[SPLASH] Stock Update for %s' % product.display_name,
                'filter': 'product',
                'product_id': product.id,
                'location_id': product.env.ref('stock.stock_location_stock').id,
                'line_ids': [(0, 0, InventoryHelper.__get_adjustment_line(product, new_quantity))],
            })
        inventory._action_done()

    @staticmethod
    def unlink_all_inventory_adjustment(product_id):
        """
        Delete All Product Inventory Adjustment so that it could be Deleted
        ONLY IN DEBUG MODE

        :param product_id: str|int
        :return: void
        """
        # ====================================================================#
        # Safety Check - ONLY In Debug Mode
        if not Framework.isDebugMode():
            return
        from odoo.addons.splashsync.helpers import SystemManager
        # ====================================================================#
        # Search for All Product Inventory Adjustments Moves
        if SystemManager.compare_version(13) >= 0:
            results = InventoryHelper.__get_inventory().search([("product_ids", "in", int(product_id))])
        else:
            results = InventoryHelper.__get_inventory().search([("product_id", "=", int(product_id))])
        for inventory in results:
            for inventory_move in inventory.move_ids:
                inventory_move.state = 'assigned'
                inventory_move._action_cancel()
                inventory_move.unlink()
        # ====================================================================#
        # Search for All Product Inventory Adjustments
        if SystemManager.compare_version(13) >= 0:
            results = InventoryHelper.__get_inventory().search([("product_ids", "in", int(product_id))])
        else:
            results = InventoryHelper.__get_inventory().search([("product_id", "=", int(product_id))])
        # ====================================================================#
        # FORCED DELETE of All Product Inventory Adjustments
        for inventory in results:
            item = InventoryHelper.__get_inventory().browse([int(inventory.id)])
            item.state = 'draft'
            item.action_cancel_draft()
            item.unlink()
        # ====================================================================#
        # Search for All Product Quantities
        results = InventoryHelper.__get_quants().sudo().search([("product_id", "=", int(product_id))])
        # ====================================================================#
        # FORCED DELETE of All Product Inventory Adjustments
        for quant in results:
            quant.unlink()
        # ====================================================================#
        # Since V13 - Stock Valuation Feature Added
        if SystemManager.compare_version(13) < 0:
            return
        # ====================================================================#
        # Search for All Product Stock Valuation Layer
        results = InventoryHelper.__get_valuation().sudo().search([("product_id", "=", int(product_id))])
        # ====================================================================#
        # FORCED DELETE of All Product Stock Valuation Layer
        for layer in results:
            layer.unlink()

    # ====================================================================#
    # Low Level Methods
    # ====================================================================#

    @staticmethod
    def __get_adjustment_line(product, new_quantity):
            """
            Create Product Inventory Adjustment Line

            :param product: Product
            :param new_quantity: float
            :return: dict
            """
            return {
                'product_qty': float(new_quantity),
                'location_id': product.env.ref('stock.stock_location_stock').id,
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'theoretical_qty': product.qty_available,
            }

    # ====================================================================#
    # Odoo ORM Access
    # ====================================================================#

    @staticmethod
    def __get_inventory():
        """
        Get Product Inventory Adjustment Model Class

        :rtype: stock.inventory
        """
        return http.request.env['stock.inventory']

    @staticmethod
    def __get_quants():
        """
        Get Product Quantities Model Class

        :rtype: stock.inventory
        """
        return http.request.env['stock.quant']

    @staticmethod
    def __get_valuation():
        """
        Get Stock Valuation Model Class

        :rtype: stock.valuation.layer
        """
        return http.request.env['stock.valuation.layer']