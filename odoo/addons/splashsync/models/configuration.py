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


class ResConfigSplash(models.Model):
    _name = 'res.config.splash'
    _description = 'Splash Sync Module Configuration'
    _transient = False
    _inherit = 'res.config'

    # Default Company Settings
    __default__ = {
        'ws_id': "",
        'ws_key': "",
        'ws_expert': False,
        'ws_no_commits': False,
        'ws_host': "https://www.splashsync.com/ws/soap",
        'ws_user': None,
        'product_simplified_prices': False,
        'product_advanced_variants': False,
        'product_advanced_taxes': False,
        'sales_default_team_id': None,
        'sales_account_id': None,
        'sales_advanced_taxes': False,
        'sales_check_payments_amount': False,
    }

    company_id = fields.Many2one('res.company', required=True)

    # ====================================================================#
    # CORE Settings
    # ====================================================================#

    ws_id = fields.Char(
        required=True,
        string="Server Identifier",
        help="Your Odoo Server Identifier, generated on your account."
    )
    ws_key = fields.Char(
        required=True,
        string="Encryption Key"
    )
    ws_expert = fields.Boolean(
        string="Advanced Mode",
        help="Check this to Enable Advanced Configuration"
    )

    ws_no_commits = fields.Boolean(
        string="Disable Commits",
        help="Check this to Disable Change Commits to Splash Server"
    )

    ws_host = fields.Char(
        string="Splash Server",
        help="Url of your Splash Server (default: www.splashsync.com/ws/soap"
    )
    ws_user = fields.Many2one(
        string="Webservice User",
        required=True,
        comodel_name="res.users",
        help="ID of Local User used by Splash"
    )

    # ====================================================================#
    # PRODUCTS Settings
    # ====================================================================#

    product_simplified_prices = fields.Boolean(
        string="Product Simplified Prices",
        help="Enable Simplified Mode to Store Product Extra Price at Product Level."
    )
    product_advanced_taxes = fields.Boolean(
        string="Product Advanced Taxes",
        help="Enable Advanced Taxes Mode."
    )
    product_advanced_variants = fields.Boolean(
        string="Product Advanced Variants",
        help="Enable to store Products Features on features_value_ids instead of Template attribute_line_ids."
    )

    # ====================================================================#
    # SALES Settings
    # ====================================================================#

    sales_default_team_id = fields.Many2one(
        'crm.team',
        string="Default Sales Team"
    )

    sales_account_id = fields.Many2one(
        'account.account',
        domain=[("user_type_id", "=ilike", "income")],
        string="Account for New Invoices Line"
    )

    sales_journal_id = fields.Many2one(
        'account.journal',
        domain=[
            ('type', 'in', ["sale", "cash", "bank", "general"]),
            ('default_credit_account_id', '<>', None),
        ],
        string="Default Payment Journal for Invoices"
    )

    sales_advanced_taxes = fields.Boolean(
        string="Order & Invoices Advanced Taxes",
        help="Enable Advanced Taxes Mode."
    )

    sales_check_payments_amount = fields.Boolean(
        string="Invoices Payments Amounts Check",
        help="Validate Invoice only if Payments Amounts match Invoice Total."
    )

    def execute(self):
        """
        Called when settings are saved.
        """
        from odoo.addons.splashsync.helpers import SettingsManager

        self.ensure_one()
        # ====================================================================#
        # Save Company Configuration
        self.set_values()
        # ====================================================================#
        # Clean Company Configuration
        self.clean(self.env.user.company_id.id)
        # ====================================================================#
        # Reset Configuration
        SettingsManager.reset()

        return self.next()

    @api.multi
    def default_get(self, fields=None):
        """
        Load configuration with Default Values

        :param fields: None | dict
        :return: dict
        """
        # ====================================================================#
        # Load Current Company Configuration
        config = self.get_config(self.env.user.company_id.id)
        # ====================================================================#
        # Return Company Configuration or default Values
        return config.get_values() if config is not None else self.get_default_values(self.env.user.company_id.id)

    def get_values(self):
        """
        Get Company Configuration Values

        :return: dict
        """
        return {
            'company_id': self.company_id.id,
            'ws_id': self.ws_id,
            'ws_key': self.ws_key,
            'ws_expert': self.ws_expert,
            'ws_no_commits': self.env['ir.config_parameter'].sudo().get_param('splash_ws_no_commits'),
            'ws_host': self.ws_host,
            'ws_user': self.ws_user.id,
            'product_simplified_prices': self.env['ir.config_parameter'].sudo().get_param('splash_product_simplified_prices'),
            'product_advanced_taxes': self.product_advanced_taxes,
            'product_advanced_variants': self.product_advanced_variants,
            'sales_default_team_id': self.sales_default_team_id.id,
            'sales_account_id': self.sales_account_id.id,
            'sales_journal_id': self.sales_journal_id.id,
            'sales_advanced_taxes': self.sales_advanced_taxes,
            'sales_check_payments_amount': self.sales_check_payments_amount,
        }

    @api.multi
    def set_values(self):
        """
        Save Company Configuration

        :return: void
        """
        # ====================================================================#
        # Detect Current User Company ID
        try:
            company_id = http.request.env.user.company_id.id
        except Exception:
            company_id = self.env.user.company_id.id
        # ====================================================================#
        # Update Global Values
        parameters = self.env['ir.config_parameter'].sudo()
        parameters.set_param('splash_ws_no_commits', self.ws_no_commits)
        parameters.set_param('splash_product_simplified_prices', self.product_simplified_prices)
        # ====================================================================#
        # Load Current Company Configuration
        config = self.env['res.config.splash'].sudo().search([('company_id', '=', company_id)], limit=1)
        # ====================================================================#
        # Update Company Values
        config.write({
            'company_id': company_id,
            'ws_id': self.ws_id,
            'ws_key': self.ws_key,
            'ws_expert': self.ws_expert,
            'ws_no_commits': self.ws_no_commits,
            'ws_host': self.ws_host,
            'ws_user': self.ws_user.id,
            'product_simplified_prices': self.product_simplified_prices,
            'product_advanced_taxes': self.product_advanced_taxes,
            'product_advanced_variants': self.product_advanced_variants,
            'sales_default_team_id': self.sales_default_team_id.id,
            'sales_account_id': self.sales_account_id.id,
            'sales_journal_id': self.sales_journal_id.id,
            'sales_advanced_taxes': self.sales_advanced_taxes,
            'sales_check_payments_amount': self.sales_check_payments_amount,
        })

    @api.multi
    def get_default_values(self, company_id):
        """
        Build Default configuration for a Company

        :param company_id: int
        :rtype: dict
        """
        default = ResConfigSplash.__default__.copy()
        default['company_id'] = company_id

        return default

    def get_config(self, company_id):
        """
        Load Company Configuration

        :param company_id: int
        :rtype: None | ResConfigSplash
        """
        # ====================================================================#
        # Search for Company Configuration
        config = self.env['res.config.splash'].sudo().search([('company_id', '=', company_id)], limit=1)

        return config if len(config) else None

    def clean(self, company_id):
        """
        Clean Company Configurations

        :param company_id: int
        :rtype: None | ResConfigSplash
        """
        # Search for Company Configuration
        config = self.env['res.config.splash'].search([('company_id', '=', company_id)], limit=1)
        if len(config) == 0:
            return

        for conf in self.env['res.config.splash'].search([('company_id', '=', company_id)]):
            if conf.id != config.id:
                conf.unlink()

    @staticmethod
    def get_base_url():
        return http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
