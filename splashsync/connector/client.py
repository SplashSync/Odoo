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

"""Splash client of one Odoo database & company, built per request (no static state)."""

from __future__ import annotations

import base64
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final

from odoo import release
from splashpy import ClientInfo, SplashClient, SplashConfig

from .context import OdooContext
from .objects import OBJECTS, SCOPES
from .widgets import WIDGETS

STATIC: Final = Path(__file__).resolve().parent.parent / "static" / "assets" / "img"
"""Connector images."""

MODULE: Final = "splashsync"
"""Technical name of the addon."""


class OdooConfig:
    """splashpy configuration provider: Splash settings of an Odoo company."""

    def __init__(self, company: Any) -> None:
        """Read the settings of a company (record read as superuser)."""
        self.company = company

    def load(self) -> SplashConfig:
        """Build the splashpy configuration."""
        company = self.company
        settings: dict[str, Any] = {
            "ws_id": company.splash_ws_id or "",
            "ws_key": company.splash_ws_key or "",
            "lang": company.partner_id.lang or "en_US",
        }
        if company.splash_ws_expert and company.splash_ws_host:
            settings["ws_host"] = company.splash_ws_host
        return SplashConfig(**settings)


def resolve_company(env: Any, params: Mapping[str, Any]) -> Any:
    """Company of a Splash request: ``cid`` (id), ``cname`` (name) or the main company.

    :param env: Odoo environment (superuser).
    :param params: query parameters of the request.
    """
    companies = env["res.company"].sudo()
    if params.get("cid"):
        company = companies.browse(int(params["cid"])).exists()
        if company:
            return company
    if params.get("cname"):
        company = companies.search([("name", "=", str(params["cname"]))], limit=1)
        if company:
            return company
    return companies.search([], order="id", limit=1)


def build_client(env: Any, company: Any) -> SplashClient:
    """Build the Splash client of a company.

    :param env: Odoo environment (any user, superuser access is used to read the settings).
    :param company: company record (``res.company``).
    """
    company = company.sudo()
    user = company.splash_ws_user_id or env.ref("base.user_admin")
    odoo_env = env(
        user=user.id,
        context={
            **env.context,
            "allowed_company_ids": [company.id],
            "mail_notrack": True,
            "tracking_disable": True,
            "lang": company.partner_id.lang or "en_US",
        },
    )
    odoo = OdooContext(env=odoo_env, company=company)
    return SplashClient(
        OdooConfig(company),
        info=client_info(odoo),
        objects=[obj(odoo) for obj in OBJECTS],
        widgets=[widget(odoo) for widget in WIDGETS],
    )


def client_info(odoo: OdooContext) -> ClientInfo:
    """Server information sent to Splash."""
    company = odoo.company
    module = odoo.env["ir.module.module"].sudo().search([("name", "=", MODULE)], limit=1)
    return ClientInfo(
        shortdesc=f"Splash for Odoo {release.major_version}",
        longdesc="Splash Sync connector for Odoo",
        company=company.name or None,
        address=company.street or None,
        zip=company.zip or None,
        town=company.city or None,
        country=company.country_id.name or None,
        www=company.website or None,
        email=company.email or None,
        phone=company.phone or None,
        icoraw=_asset("favicon.ico"),
        logoraw=_asset("logo.png"),
        logourl=None,
        scopes=list(SCOPES),
        servertype=f"Odoo {release.version}",
        serverurl=company.get_base_url() or None,
        moduleauthor="Splash Sync",
        moduleversion=module.latest_version or "3.0.0",
    )


def _asset(name: str) -> str | None:
    """Read a connector image, base64 encoded."""
    path = STATIC / name
    if not path.is_file():
        return None
    return base64.b64encode(path.read_bytes()).decode("ascii")
