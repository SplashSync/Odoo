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
"""Widgets of the connector."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from odoo import release
from splashpy.core.context import RequestContext
from splashpy.widgets import BaseWidget, WidgetRender

from .context import OdooContext


class OdooInfos(BaseWidget):
    """Odoo server & company information."""

    type = "OdooInfos"
    name = "Odoo Infos"
    description = "Odoo server and company information"
    icon = "fa fa-info-circle"

    def __init__(self, odoo: OdooContext) -> None:
        """Use the Odoo context of the request."""
        self.odoo = odoo

    def render(self, ctx: RequestContext, params: Mapping[str, Any], output: WidgetRender) -> bool | None:
        """Fill the widget."""
        company = self.odoo.company
        partners = self.odoo.model("res.partner").search_count([("parent_id", "=", False)])
        output.set_sub_title(f"Odoo {release.version}")
        output.blocks.add_table_block(
            [
                ["Information", "Value"],
                ["Odoo", str(release.version)],
                ["Company", str(company.name)],
                ["Database", str(self.odoo.env.cr.dbname)],
                ["ThirdParties", str(partners)],
            ]
        )
        return True


WIDGETS: Final = (OdooInfos,)
"""Widgets of the connector."""
