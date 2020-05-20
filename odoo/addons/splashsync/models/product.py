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


from odoo import api, models, fields
import logging


class ProductProduct(models.Model):
    """Override for Odoo Products to Make it Work with Splash"""
    _inherit = 'product.product'

    variant_price_extra = fields.Float(
        string='Variant Extra Price',
        help="Variant Extra Price. Used by Splash Module to manage variants extra prices at product level."
    )

    features_value_ids = fields.Many2many(
        'product.attribute.value',
        string="Features Values",
        relation='product_variant_features',
        help="Product Variants Features Only Values"
    )

    # ====================================================================#
    # !!! Odoo Core Features Overrides !!!
    # ====================================================================#

    @api.depends('variant_price_extra')
    def _compute_product_price_extra(self):
        # ====================================================================#
        # Check if Splash Simplified Prices Feature is Active
        from odoo.addons.splashsync.helpers import SettingsManager
        SettingsManager.reset()
        if SettingsManager.is_prd_simple_prices():
            for product in self:
                product.price_extra = product.variant_price_extra
            return
        # ====================================================================#
        # Redirect to Odoo Core Action
        super(ProductProduct, self)._compute_product_price_extra()

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        # _logger = logging.getLogger("SPLASH SYNC")
        # _logger.warning("New Product Detected: "+str(res.id))

        return res

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if not self:
            return res
        # _logger = logging.getLogger("SPLASH SYNC")
        # _logger.warning("Product Change Detected: "+str(self.id))

        return res

    def unlink(self):
        res = super(ProductProduct, self).unlink()
        if not self:
            return res
        # _logger = logging.getLogger("SPLASH SYNC")
        # _logger.warning("Product Delete Detected: "+str(self.id))

        return res

