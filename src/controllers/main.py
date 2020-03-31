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
from splashpy.server import SplashServer
from odoo.addons.splashsync.objects.thirdparty import ThirdParty
from odoo.addons.splashsync.client import OdooClient


class Webservice(http.Controller):

    def get_server( self ):
        """Build Splash Server"""

        return SplashServer(
            http.request.env['ir.config_parameter'].sudo().get_param('splash_ws_id'),
            http.request.env['ir.config_parameter'].sudo().get_param('splash_ws_key'),
            [ThirdParty()],
            [],
            OdooClient()

        )

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