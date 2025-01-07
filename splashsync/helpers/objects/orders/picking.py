# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

from splashpy import Framework

class OrderPickingHelper:
    """
    Collection of Static Functions to manage Order Stock Picking
    """

    @staticmethod
    def is_enabled():
        """
        Check if Auto-Picking Features is Active

        :return: bool
        """
        return True

    @staticmethod
    def confirm(picking):
        """
        Confirm All Stock Picking Moves

        :return: None
        """
        if not OrderPickingHelper.is_enabled() or picking.state == "cancel":
            return

        picking.action_confirm()

    @staticmethod
    def done(picking):
        """
        Validate All Stock Picking Moves

        :param picking: stock.picking
        :return: None
        """
        # ====================================================================#
        # Safety Checks
        if not OrderPickingHelper.is_enabled() or picking.state == "cancel":
            return
        # ====================================================================#
        # Odoo 15 & 16
        Framework.log().warn("Picking Done: Odoo 15+")
        picking.action_set_quantities_to_reservation()
        picking._action_done()

    @staticmethod
    def get_reserved_qty(order_line):
        """
        Get Reserved Qty for a Product

        :return: int
        """
        reserved_qty = 0
        # ====================================================================#
        # Walk on Order Pickings
        for move in order_line.move_ids:
            # ====================================================================#
            # Pickings Canceled
            if move.state == "cancel":
                continue
            reserved_qty += move.product_uom_qty

        return int(reserved_qty)
