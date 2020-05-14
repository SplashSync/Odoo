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
    _inherit = 'product.product'

    features_value_ids = fields.Many2many(
        'product.attribute.value',
        string="Features Values",
        relation='product_variant_features',
        help="Product Variants Features Only Values"
    )