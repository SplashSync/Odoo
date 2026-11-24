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


"""Settings page: the Splash settings of the current company."""

from __future__ import annotations

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Settings: Splash block (fields of the current company)."""

    _inherit = "res.config.settings"

    splash_ws_id = fields.Char(related="company_id.splash_ws_id", readonly=False)
    splash_ws_key = fields.Char(related="company_id.splash_ws_key", readonly=False)
    splash_ws_expert = fields.Boolean(related="company_id.splash_ws_expert", readonly=False)
    splash_ws_host = fields.Char(related="company_id.splash_ws_host", readonly=False)
    splash_ws_user_id = fields.Many2one(related="company_id.splash_ws_user_id", readonly=False)
    splash_no_commits = fields.Boolean(related="company_id.splash_no_commits", readonly=False)
    splash_product_simplified_prices = fields.Boolean(
        related="company_id.splash_product_simplified_prices", readonly=False
    )
    splash_product_advanced_taxes = fields.Boolean(related="company_id.splash_product_advanced_taxes", readonly=False)
    splash_product_advanced_variants = fields.Boolean(
        related="company_id.splash_product_advanced_variants", readonly=False
    )
    splash_product_sku_detection = fields.Boolean(related="company_id.splash_product_sku_detection", readonly=False)
    splash_sales_team_id = fields.Many2one(related="company_id.splash_sales_team_id", readonly=False)
    splash_sales_advanced_taxes = fields.Boolean(related="company_id.splash_sales_advanced_taxes", readonly=False)
    splash_sales_self_invoiced = fields.Boolean(related="company_id.splash_sales_self_invoiced", readonly=False)
    splash_sales_check_payments = fields.Boolean(related="company_id.splash_sales_check_payments", readonly=False)
