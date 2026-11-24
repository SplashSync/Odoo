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
"""Odoo context of one Splash request: environment, company and settings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OdooContext:
    """What the objects of one client need from Odoo: built per request, never shared."""

    env: Any
    """Odoo environment, as the Splash user, restricted to the company."""

    company: Any
    """Current company (``res.company`` record, read as superuser)."""

    def model(self, name: str) -> Any:
        """Get an Odoo model, as the Splash user."""
        return self.env[name]

    def setting(self, name: str) -> Any:
        """Read a Splash setting of the company (``splash_<name>`` field)."""
        return self.company[f"splash_{name}"]

    @property
    def lang(self) -> str:
        """Default language of the request (the company language)."""
        return str(self.env.context.get("lang") or "en_US")

    def languages(self) -> list[str]:
        """Installed languages, the default one first."""
        installed = [str(code) for code, _name in self.env["res.lang"].get_installed()]
        return [self.lang, *[code for code in installed if code != self.lang]]

    @property
    def company_id(self) -> int:
        """Current company id."""
        return int(self.company.id)
