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

    splash_attribute_lock = False

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

    def _unlink_or_archive(self, check_access=True):
        """Unlink or archive products.
        Try in batch as much as possible because it is much faster.
        Use dichotomy when an exception occurs.

        This method override default one to prevent archive/unlink
        when template attributes are updated by Splash
        """
        # ====================================================================#
        # Product is Locked by Splash
        if type(self).splash_attribute_lock:
            return
        # ====================================================================#
        # Redirect to Odoo Core Action
        super(ProductProduct, self)._unlink_or_archive(check_access)

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

        # ====================================================================#
        # Execute Splash Commit for linked Products (BOMs)
        self.__do_splash_commit_boms(const.__SPL_A_UPDATE__)

        return res

    def unlink(self):
        # ====================================================================#
        # Execute Splash Commit
        self.__do_splash_commit(const.__SPL_A_DELETE__)

        res = super(ProductProduct, self).unlink()

        return res


    def set_splash_attribute_lock(self, state=False):
        type(self).splash_attribute_lock = state

    def __do_splash_commit(self, action):
        """
        Execute Splash Commit for this Product

        :param action: str
        :return: void
        """
        # ====================================================================#
        # Check if Splash Commit is Allowed
        from odoo.addons.splashsync.helpers import SettingsManager
        if SettingsManager.is_no_commits():
            return
        # ====================================================================#
        # Execute Splash Commit for this Product
        from odoo.addons.splashsync.objects import Product
        from odoo.addons.splashsync.client import OdooClient
        for product in self:
            OdooClient.commit(Product(), action, str(product.id))

    def __do_splash_commit_boms(self, action):
        """
        Execute Splash Commit for this linked Products (BOMs)

        :param action: str
        :return: void
        """
        # ====================================================================#
        # Check if Splash Commit is Allowed
        from odoo.addons.splashsync.helpers import SettingsManager
        if SettingsManager.is_no_commits():
            return
        # ====================================================================#
        # Execute Splash Commit for this Product
        from odoo.addons.splashsync.objects import Product
        from odoo.addons.splashsync.client import OdooClient

        for product in self:
            try:
                for bom_line in product.bom_line_ids:
                    # ====================================================================#
                    # Single Product Selected
                    if bom_line.bom_id.product_id.id > 0:
                        OdooClient.commit(Product(), action, str(bom_line.bom_id.product_id.id))
                    else:
                        # ====================================================================#
                        # Product Template Selected
                        OdooClient.commit(
                            Product(),
                            action,
                            list(map(str, bom_line.bom_id.product_tmpl_id.product_variant_ids.ids))
                        )
            except Exception:
                pass

