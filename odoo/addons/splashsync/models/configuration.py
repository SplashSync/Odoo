# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) 2015-2020 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

from odoo import api, models, fields, http


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _check_company_auto = True

    # ====================================================================#
    # CORE Settings
    # ====================================================================#

    splash_ws_id = fields.Char(
        required=True,
        company_dependent=True,
        string="Server Identifier",
        default="ThisIsSplashWsId",
        help="Your Odoo Server Identifier, generated on your account."
    )
    splash_ws_key = fields.Char(
        required=True,
        company_dependent=True,
        string="Encryption Key",
        default="ThisIsYourEncryptionKeyForSplash"
    )
    splash_ws_expert = fields.Boolean(
        company_dependent=True,
        string="Advanced Mode",
        help="Check this to Enable Advanced Configuration"
    )

    splash_ws_no_commits = fields.Boolean(
        company_dependent=True,
        string="Disable Commits",
        help="Check this to Disable Change Commits to Splash Server"
    )

    splash_ws_host = fields.Char(
        company_dependent=True,
        string="Splash Server",
        default="https://www.splashsync.com/ws/soap",
        help="Url of your Splash Server (default: www.splashsync.com/ws/soap"
    )
    splash_ws_user = fields.Many2one(
        company_dependent=True,
        string="Webservice User",
        comodel_name="res.users",
        default="2",
        help="ID of Local User used by Splash"
    )

    # ====================================================================#
    # PRODUCTS Settings
    # ====================================================================#

    splash_product_simplified_prices = fields.Boolean(
        company_dependent=True,
        string="Product Simplified Prices",
        default=False,
        help="Enable Simplified Mode to Store Product Extra Price at Product Level."
    )
    splash_product_advanced_taxes = fields.Boolean(
        company_dependent=True,
        string="Product Advanced Taxes",
        default=False,
        help="Enable Advanced Taxes Mode."
    )
    splash_product_advanced_variants = fields.Boolean(
        company_dependent=True,
        string="Product Advanced Variants",
        default=False,
        help="Enable to store Products Features on features_value_ids instead of Template attribute_line_ids."
    )

    # ====================================================================#
    # SALES Settings
    # ====================================================================#

    splash_sales_advanced_taxes = fields.Boolean(
        company_dependent=True,
        string="Order & Invoices Advanced Taxes",
        default=False,
        help="Enable Advanced Taxes Mode."
    )

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        # Load Current Company Configuration
        config = self.env['res.config.settings'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        # Fetch Company Values
        res.update(
            splash_ws_id=config.splash_ws_id,
            splash_ws_key=config.splash_ws_key,
            splash_ws_expert=bool(config.splash_ws_expert),
            splash_ws_no_commits=bool(config.splash_ws_no_commits),
            splash_ws_host=config.splash_ws_host,
            splash_ws_user=config.splash_ws_user.id,
            splash_product_simplified_prices=bool(config.splash_product_simplified_prices),
            splash_product_advanced_taxes=bool(config.splash_product_advanced_taxes),
            splash_product_advanced_variants=bool(config.splash_product_advanced_variants),
            splash_sales_advanced_taxes=bool(config.splash_sales_advanced_taxes),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        # Load Current Company Configuration
        config = self.env['res.config.settings'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        # Update Company Values
        config.write({
            'splash_ws_id': self.splash_ws_id,
            'splash_ws_key': self.splash_ws_key,
            'splash_ws_expert': self.splash_ws_expert,
            'splash_ws_no_commits': self.splash_ws_no_commits,
            'splash_ws_host': self.splash_ws_host,
            'splash_ws_user': self.splash_ws_user,
            'splash_product_simplified_prices': self.splash_product_simplified_prices,
            'splash_product_advanced_taxes': self.splash_product_advanced_taxes,
            'splash_product_advanced_variants': self.splash_product_advanced_variants,
            'splash_sales_advanced_taxes': self.splash_sales_advanced_taxes,
        })
        # ====================================================================#
        # Default Company => Copy Configuration to Main Parameters
        if self.env.user.company_id.id == 1:
            self.env['ir.config_parameter'].sudo().set_param('splash_ws_id', self.splash_ws_id)
            self.env['ir.config_parameter'].sudo().set_param('splash_ws_key', self.splash_ws_key)
            self.env['ir.config_parameter'].sudo().set_param('splash_ws_expert', self.splash_ws_expert)
            self.env['ir.config_parameter'].sudo().set_param('splash_ws_no_commits', self.splash_ws_no_commits)
            self.env['ir.config_parameter'].sudo().set_param('splash_ws_host', self.splash_ws_host)
            self.env['ir.config_parameter'].sudo().set_param('splash_ws_user', self.splash_ws_user.id)
            self.env['ir.config_parameter'].sudo().set_param('splash_product_simplified_prices', self.splash_product_simplified_prices)
            self.env['ir.config_parameter'].sudo().set_param('splash_product_advanced_taxes', self.splash_product_advanced_taxes)
            self.env['ir.config_parameter'].sudo().set_param('splash_product_advanced_variants', self.splash_product_advanced_variants)
            self.env['ir.config_parameter'].sudo().set_param('splash_sales_advanced_taxes', self.splash_sales_advanced_taxes)

    @staticmethod
    def get_base_url():
        from odoo import http
        return http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
