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
"""Splash endpoint: a thin controller serving the splashpy client of the current company.

POST: Splash SOAP requests. GET: status text, or the splashpy debug page with ``?node=<ws_id>``.
Company: ``?cid=<id>`` or ``?cname=<name>``, the main company otherwise.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

from odoo import http
from odoo.http import request
from splashpy.adapters import SplashWsgiApp
from werkzeug.wrappers import Response

from ..connector import build_client, resolve_company


class SplashController(http.Controller):
    """Splash webservice endpoint."""

    @http.route("/splash", type="http", auth="public", methods=["GET", "POST"], csrf=False, save_session=False)
    def splash(self, **params: Any) -> Response:
        """Serve a Splash request with the client of the requested company."""
        company = resolve_company(request.env, params)
        app = SplashWsgiApp(factory=lambda _environ: build_client(request.env, company))
        body = request.httprequest.get_data()
        environ = {
            **request.httprequest.environ,
            "wsgi.input": BytesIO(body),
            "CONTENT_LENGTH": str(len(body)),
        }
        return Response.from_app(app, environ)
