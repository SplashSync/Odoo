from odoo import fields, models, http


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

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
        string="Default Sales Team",
        help="Default Sales Team for New Contacts, Orders & Invoices"
    )

    sales_account_id = fields.Many2one(
        'account.account',
        string="Account for New Invoices Line",
        help="Select the Account type to use when Splash will create new Invoices lines. I.e: 200000 Product Sales"
    )

    sales_journal_id = fields.Many2one(
        'account.journal',
        string="Default Payment Journal for Invoices",
        help="Select the default payment method to use if given Invoice Payment Method was not identified",
    )

    sales_advanced_taxes = fields.Boolean(
        string="Order & Invoices Advanced Taxes",
        help="Enable Advanced Taxes Mode."
    )

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        # ====================================================================#
        # Load Splash Configuration for Company
        res.update(self.env['res.config.splash'].default_get())

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        # ====================================================================#
        # Load Current Company Configuration
        splash_config = self.env['res.config.splash'].get_config(self.env.user.company_id.id)
        # ====================================================================#
        # Company Configuration NOT Found
        if splash_config is None:
            http.request.env['res.config.splash'].create({
                'company_id': self.env.user.company_id.id,
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
            })
        else:
            splash_config.ws_id = str(self.ws_id)
            splash_config.ws_key = str(self.ws_key)
            splash_config.ws_expert = bool(self.ws_expert)
            splash_config.ws_no_commits = bool(self.ws_no_commits)
            splash_config.ws_host = str(self.ws_host)
            splash_config.ws_user = int(self.ws_user.id)
            splash_config.product_simplified_prices = bool(self.product_simplified_prices)
            splash_config.product_advanced_taxes = bool(self.product_advanced_taxes)
            splash_config.product_advanced_variants = bool(self.product_advanced_variants)
            splash_config.sales_default_team_id = int(self.sales_default_team_id.id)
            splash_config.sales_account_id = int(self.sales_account_id.id)
            splash_config.sales_journal_id = int(self.sales_journal_id.id)
            splash_config.sales_advanced_taxes = bool(self.sales_advanced_taxes)
            splash_config.execute()

        self.show_debug()

    def show_debug(self):
        import logging

        logging.warning('[SPLASH] New Configuration')
        for cfg in self.env['res.config.splash'].sudo().search([]):
            logging.warning(cfg.company_id.name+" >> "+cfg.ws_key+" @ "+cfg.ws_id)
