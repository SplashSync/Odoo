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
"""Product variants: features values of the "Advanced Variants" mode, extra price of the "Simplified Prices" mode."""

from __future__ import annotations

from odoo import api, fields, models


class ProductProduct(models.Model):
    """Variant: its own features values (Advanced Variants mode), its own extra price (Simplified Prices mode).

    Same declarations as the V1 connector (fields, relation table & columns): databases upgraded from V1
    keep their values.
    """

    _inherit = "product.product"

    features_value_ids = fields.Many2many(
        "product.attribute.value",
        string="Features Values",
        relation="product_variant_features",
        help="Product Variants Features Only Values",
    )

    variant_price_extra = fields.Float(
        string="Variant Extra Price",
        help="Variant Extra Price. Used by Splash Module to manage variants extra prices at product level.",
    )

    @api.depends("product_template_attribute_value_ids.price_extra", "variant_price_extra")
    def _compute_product_price_extra(self) -> None:
        """Simplified Prices mode (Splash setting): the extra price is the variant's own one.

        The sale price (``lst_price``) is stored once for products shared by all companies: the mode
        applies to the whole database as soon as one company enables it.
        """
        companies = self.env["res.company"].sudo()
        if not companies.search_count([("splash_product_simplified_prices", "=", True)], limit=1):
            super()._compute_product_price_extra()
            return
        for product in self:
            product.price_extra = product.variant_price_extra
