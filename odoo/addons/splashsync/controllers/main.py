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

from odoo import http
from splashpy import Framework
from splashpy.server import SplashServer
from splashpy.templates.widgets import Basic
from odoo.addons.splashsync.client import OdooClient
from odoo.addons.splashsync.objects import ThirdParty, Product


class Webservice(http.Controller):

    def get_server(self):
        """Build Splash Server"""
        # ====================================================================#
        # Load Odoo Configuration
        config = http.request.env['ir.config_parameter'].sudo()
        # ====================================================================#
        # Build Splash Server with Common Options
        splash_server = SplashServer(
            config.get_param('splash_ws_id'),
            config.get_param('splash_ws_key'),
            [Product()],
            # [ThirdParty(), Product()],
            [Basic()],
            OdooClient()
        )
        # ====================================================================#
        # Force Ws Host if Needed
        if config.get_param('splash_ws_expert'):
            Framework.config().force_host(config.get_param('splash_ws_host'))

        return splash_server

    @http.route('/splash', type='http', auth='splash', website=True, csrf=False)
    def splash( self, **kw ):
        """
         Respond to Splash Webservice Requests
         """
        return self.get_server().fromWerkzeug(http.request.httprequest)

    @http.route('/splash/debug', type='http', auth='public', website=True)
    def debug( self, **kw ):
        """
         Respond to User Debug Requets
         """
        return self.get_server().fromWerkzeug(http.request.httprequest)

    @http.route('/test', type='http', auth='public', website=True)
    def test( self, **kw ):
        """
         Respond to User Debug Requets
         """
        import logging

        partner = ThirdParty(http.request.env)
        model = partner.load(10)
        logging.warning(model['email'])
        logging.warning(getattr(model, 'email'))
        # logging.warning(http.request.env.su)
        # logging.warning(http.request.env.context)

        return "Ok"