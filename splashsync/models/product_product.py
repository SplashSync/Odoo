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

"""Product variants: features values of the "Advanced Variants" mode."""

from __future__ import annotations

from odoo import fields, models


class ProductProduct(models.Model):
    """Variant: its own features values (Advanced Variants mode).

    Same declaration as the V1 connector (field, relation table & columns): databases upgraded from V1
    keep their values.
    """

    _inherit = "product.product"

    features_value_ids = fields.Many2many(
        "product.attribute.value",
        string="Features Values",
        relation="product_variant_features",
        help="Product Variants Features Only Values",
    )
