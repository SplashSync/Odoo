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
from splashpy import const


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

        # ====================================================================#
        # Execute Splash Commit
        self.__do_splash_commit(const.__SPL_A_CREATE__)

        return res

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)

        # ====================================================================#
        # Execute Splash Commit
        self.__do_splash_commit(const.__SPL_A_UPDATE__)

        return res

    def unlink(self):
        res = super(ProductProduct, self).unlink()

        # ====================================================================#
        # Execute Splash Commit
        self.__do_splash_commit(const.__SPL_A_DELETE__)

        return res

    def __do_splash_commit(self, action):
        """
        Execute Splash Commit for this Product
        :param action: str

        :return: void
        """
        # ====================================================================#
        # Safety Check
        if not self:
            pass
        # ====================================================================#
        # Execute Splash Commit for this Product
        from odoo.addons.splashsync.objects import Product
        from odoo.addons.splashsync.client import OdooClient
        OdooClient.commit(Product(), action, str(self.id))

