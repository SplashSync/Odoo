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
        # Load Odoo System Manager
        from odoo.addons.splashsync.helpers import SystemManager
        # ====================================================================#
        # Odoo 15 & 16
        if SystemManager.compare_version(15) >= 0:
            Framework.log().warn("Picking Done: Odoo 15+")
            picking.action_set_quantities_to_reservation()
            picking._action_done()
        # ====================================================================#
        # Odoo 14
        elif SystemManager.compare_version(14) >= 0:
            Framework.log().warn("Picking Done: Odoo 14")
            from odoo.tools.float_utils import float_is_zero
            for move_line in picking.move_line_ids.filtered(lambda m: float_is_zero(m.qty_done, precision_rounding=m.product_uom_id.rounding)):
                move_line.qty_done = move_line.product_qty
            picking._action_done()
        # ====================================================================#
        # Odoo 12 & 13
        if SystemManager.compare_version(12) >= 0:
            Framework.log().warn("Picking Done: Odoo 12")
            from odoo.tools.float_utils import float_is_zero
            for move_line in picking.move_ids_without_package.filtered(lambda m: float_is_zero(m.quantity_done, precision_rounding=m.product_uom.rounding)):
                move_line.quantity_done = move_line.product_qty
            picking.action_done()


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

            # Framework.log().dump({"move": move.id })

        return int(reserved_qty)
