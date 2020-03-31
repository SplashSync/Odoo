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

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    splash_ws_id = fields.Char(
        required=True,
        string="Server Identifier",
        default="ThisIsSplashWsId",
        help="Your Odoo Server Identifier, generated on your account."
    )
    splash_ws_key = fields.Char(
        required=True,
        string="Encryption Key",
        default="ThisIsYourEncryptionKeyForSplash"
    )
    splash_ws_expert = fields.Boolean(string="Advanced Mode")
    splash_ws_host = fields.Char(
        string="Splash Server",
        default="www.splashsync.com/ws/soap",
        help="Url of your Splash Server (default: www.splashsync.com/ws/soap"
    )
    splash_ws_user = fields.Many2one(
        string="Webservice User",
        comodel_name="res.users",
        default="2",
        help="ID of Local User used by Splash"
    )

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            splash_ws_id=self.env['ir.config_parameter'].sudo().get_param('splash_ws_id'),
            splash_ws_key=self.env['ir.config_parameter'].sudo().get_param('splash_ws_key'),
            splash_ws_expert=bool(self.env['ir.config_parameter'].sudo().get_param('splash_ws_expert')),
            splash_ws_host=self.env['ir.config_parameter'].sudo().get_param('splash_ws_host'),
            splash_ws_user=int(self.env['ir.config_parameter'].sudo().get_param('splash_ws_user')),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('splash_ws_id', self.splash_ws_id)
        self.env['ir.config_parameter'].sudo().set_param('splash_ws_key', self.splash_ws_key)
        self.env['ir.config_parameter'].sudo().set_param('splash_ws_expert', self.splash_ws_expert)
        self.env['ir.config_parameter'].sudo().set_param('splash_ws_host', self.splash_ws_host)
        self.env['ir.config_parameter'].sudo().set_param('splash_ws_user', self.splash_ws_user.id)
