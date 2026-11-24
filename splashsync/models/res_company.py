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

"""Splash settings, one set per company. The key is only readable by administrators."""

from __future__ import annotations

from odoo import fields, models

SYSTEM = "base.group_system"
"""Only administrators read or write Splash credentials."""


class ResCompany(models.Model):
    """Company: Splash node settings."""

    _inherit = "res.company"

    # ====================================================================#
    # Node
    # ====================================================================#

    splash_ws_id = fields.Char("Splash Server Id", groups=SYSTEM, copy=False)
    splash_ws_key = fields.Char("Splash Encryption Key", groups=SYSTEM, copy=False)
    splash_ws_expert = fields.Boolean("Splash Expert Mode", groups=SYSTEM)
    splash_ws_host = fields.Char("Splash Server Host", groups=SYSTEM)
    splash_ws_user_id = fields.Many2one(
        "res.users",
        "Splash User",
        groups=SYSTEM,
        help="Odoo user used for every change made by Splash.",
    )
    splash_no_commits = fields.Boolean("Splash: Disable Commits", groups=SYSTEM)

    # ====================================================================#
    # Products
    # ====================================================================#

    splash_product_simplified_prices = fields.Boolean("Splash: Simplified Prices", groups=SYSTEM)
    splash_product_advanced_taxes = fields.Boolean("Splash: Products Advanced Taxes", groups=SYSTEM)
    splash_product_advanced_variants = fields.Boolean("Splash: Advanced Variants", groups=SYSTEM)
    splash_product_sku_detection = fields.Boolean("Splash: Detect Products by SKU", groups=SYSTEM)

    # ====================================================================#
    # Sales
    # ====================================================================#

    splash_sales_team_id = fields.Many2one("crm.team", "Splash: Default Sales Team", groups=SYSTEM)
    splash_sales_advanced_taxes = fields.Boolean("Splash: Sales Advanced Taxes", groups=SYSTEM)
    splash_sales_self_invoiced = fields.Boolean("Splash: Orders are Self Invoiced", groups=SYSTEM)
    splash_sales_check_payments = fields.Boolean("Splash: Check Payments Amounts", groups=SYSTEM)
