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
"""Product gallery images: per variant visibility & cover, as received from Splash."""

from __future__ import annotations

from odoo import fields, models


class ProductImage(models.Model):
    """Gallery image of a product template: variants hiding it, variants using it as cover."""

    _inherit = "product.image"

    splash_hidden_variant_ids = fields.Many2many(
        "product.product",
        "splash_product_image_hidden_rel",
        "image_id",
        "product_id",
        string="Hidden for Variants",
        help="Variants that do not show this image (Splash gallery).",
    )
    splash_cover_variant_ids = fields.Many2many(
        "product.product",
        "splash_product_image_cover_rel",
        "image_id",
        "product_id",
        string="Cover of Variants",
        help="Variants using this image as cover (Splash gallery).",
    )
