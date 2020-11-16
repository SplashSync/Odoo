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
from odoo.addons.splashsync.client import OdooClient

class Webservice(http.Controller):

    @http.route('/splash', type='http', auth='splash', website=False, csrf=False)
    def splash(self, **kw):
        """
         Respond to Splash Webservice Requests
         """
        return OdooClient.get_server().fromWerkzeug(http.request.httprequest)

    @http.route('/splash/test', type='http', auth='user', website=True)
    def test(self, **kw):
        """
         Respond to User Debug Requests
         """
        from splashpy.client import SplashClient

        # ====================================================================#
        # Init Splash Framework
        try:
            OdooClient.get_server()
        except Exception as exception:
            Framework.log().fromException(exception, False)
            return Framework.log().to_html_list(True)
        # ====================================================================#
        # Load Server Info
        wsId, wsKey, wsHost = Framework.config().identifiers()
        raw_html = "<h3>Server Debug</h3>"
        # ====================================================================#
        # Execute Ping Test
        ping = SplashClient.getInstance().ping()
        raw_html += Framework.log().to_html_list(True)
        if not ping:
            Framework.log().error('Ping Test Fail: ' + str(wsHost))
        # ====================================================================#
        # Execute Connect Test
        connect = SplashClient.getInstance().connect()
        raw_html += Framework.log().to_html_list(True)
        if not connect:
            Framework.log().error('Connect Test Fail: ' + str(wsHost))
        # ====================================================================#
        # Show Server Info
        infos = Framework.getClientInfo().get()
        Framework.log().info('Server Type: ' + str(infos['shortdesc']))
        Framework.log().info('Server Url: ' + str(infos["serverurl"]))
        Framework.log().info('Module Version: ' + str(infos["moduleversion"]))

        return raw_html + Framework.log().to_html_list(True)
