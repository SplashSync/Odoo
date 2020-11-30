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
        # ====================================================================#
        # Create New Product Inventory Adjustment
        inventory = InventoryHelper.__get_inventory().create({
            'name': '[SPLASH] Stock Update for %s' % product.display_name,
            'filter': 'product',
            'product_id': product.id,
            'location_id': product.env.ref('stock.stock_location_stock').id,
            'line_ids': [(0, 0, InventoryHelper.__get_adjustment_line(product, new_quantity))],
        })
        inventory._action_done()

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
