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
    def update_qty_available(product, new_quantity):
        """
        Create Product Inventory Adjustment

        :param product: Product
        :param new_quantity: float
        :return: None, stock.inventory
        """
        from odoo.addons.splashsync.helpers import SystemManager
        # ====================================================================#
        # ODOO V15+ - Create New Product Quant
        if SystemManager.compare_version(15) >= 0:
            InventoryHelper.__get_quants().create({
                'product_id': product.id,
                'location_id': product.env.ref('stock.stock_location_stock').id,
                'inventory_quantity':  float(float(new_quantity) - float(product.qty_available)),
            }).action_apply_inventory()

            return
        # ====================================================================#
        # ODOO V13/V14 - Create New Product Inventory Adjustment
        elif SystemManager.compare_version(13) >= 0:
            inventory = InventoryHelper.__get_inventory().create({
                'name': '[SPLASH] Stock Update for %s' % product.display_name,
                'product_ids': [product.id],
                'line_ids': [(0, 0, InventoryHelper.__get_adjustment_line(product, new_quantity))],
            })
        # ====================================================================#
        # ODOO V12 - Create New Product Inventory Adjustment
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

        InventoryHelper.__unlink_all_inventory_moves(product_id)
        InventoryHelper.__unlink_all_inventories(product_id)
        InventoryHelper.__unlink_all_stock_valuations(product_id)
        InventoryHelper.__unlink_all_stock_quants(product_id)

    @staticmethod
    def __unlink_all_inventories(product_id):
        """
        Delete All Product Inventory so that it could be Deleted
        ONLY IN DEBUG MODE

        :param: product_id: str|int
        :return: void
        """
        from odoo.addons.splashsync.helpers import SystemManager
        # ====================================================================#
        # ODOO V15+ - Nothing to Do
        if not Framework.isDebugMode() or SystemManager.compare_version(15) >= 0:
            return
        # ====================================================================#
        # ODOO V13/V14 - Search for All Product Inventory Adjustments Moves
        elif SystemManager.compare_version(13) >= 0:
            results = InventoryHelper.__get_inventory().search([("product_ids", "in", int(product_id))])
        # ====================================================================#
        # ODOO V12 - Search for All Product Inventory Adjustments Moves
        else:
            results = InventoryHelper.__get_inventory().search([("product_id", "=", int(product_id))])
        # ====================================================================#
        # FORCED DELETE of All Product Inventory Adjustments
        for inventory in results:
            item = InventoryHelper.__get_inventory().browse([int(inventory.id)])
            item.state = 'draft'
            item.action_cancel_draft()
            item.unlink()


    @staticmethod
    def __unlink_all_inventory_moves(product_id):
        """
        Delete All Product Inventory Moves so that it could be Deleted

        :param:     product_id: str|int
        :return:    void
        """
        from odoo.addons.splashsync.helpers import SystemManager
        # ====================================================================#
        # ODOO V15+ - Nothing to Do
        if SystemManager.compare_version(15) >= 0:
            # ====================================================================#
            # Search for All Product Stock Moves
            results = http.request.env['stock.move'].sudo().search([("product_id", "=", int(product_id))])
            # ====================================================================#
            # FORCED DELETE of All Product Stock Moves
            for move in results:
                for move_line in move.move_line_ids:
                    move_line.state = 'assigned'
                    move_line.unlink()
                move.state = 'draft'
                move._action_cancel()
                move.unlink()

            return
        # ====================================================================#
        # ODOO V13/V14 - Search for All Product Inventory Adjustments
        elif SystemManager.compare_version(13) >= 0:
            results = InventoryHelper.__get_inventory().search([("product_ids", "in", int(product_id))])
        # ====================================================================#
        # ODOO V12 - Search for All Product Inventory Adjustments
        else:
            results = InventoryHelper.__get_inventory().search([("product_id", "=", int(product_id))])
        for inventory in results:
            for inventory_move in inventory.move_ids:
                inventory_move.state = 'assigned'
                inventory_move._action_cancel()
                inventory_move.unlink()

    @staticmethod
    def __unlink_all_stock_quants(product_id):
        """
        Delete All Product Stock Quants so that it could be Deleted
        ONLY IN DEBUG MODE

        :param: product_id: str|int
        :return: void
        """
        # ====================================================================#
        # Safety Check - ONLY In Debug Mode
        if not Framework.isDebugMode():
            return
        # ====================================================================#
        # Search for All Product Quantities
        results = InventoryHelper.__get_quants().sudo().search([("product_id", "=", int(product_id))])
        # ====================================================================#
        # FORCED DELETE of All Product Inventory Adjustments
        for quant in results:
            quant.unlink()

    @staticmethod
    def __unlink_all_stock_valuations(product_id):
        """
        Delete All Product Stock Valuations so that it could be Deleted
        ONLY IN DEBUG MODE

        :param: product_id: str|int
        :return: void
        """
        from odoo.addons.splashsync.helpers import SystemManager
        # ====================================================================#
        # Since V13+ - Stock Valuation Feature Added
        if not Framework.isDebugMode() or SystemManager.compare_version(13) < 0:
            return
        # ====================================================================#
        # Search for All Product Stock Valuation Layer
        results = http.request.env['stock.valuation.layer'].sudo().search([("product_id", "=", int(product_id))])
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
