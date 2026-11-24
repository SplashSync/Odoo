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
"""ThirdParty identity: names (encoded in the Odoo name, as V1), email, phones, website.

Odoo name = ``first, last - legal`` / ``first - legal`` / ``legal``.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from splashpy.fields import FieldsFactory
from splashpy.objects import ObjectRequest, fields_group

from ..base import OdooGroup, build_fields

NAMES: Final = ("legal", "first", "last")
"""Name parts, encoded in the Odoo name."""

TEMPLATES: Final = {
    "legal": "Splash.Templates.ThirdParty.Core.Name",
    "first": "Splash.Templates.ThirdParty.Core.Firstname",
    "last": "Splash.Templates.ThirdParty.Core.Lastname",
    "email": "Splash.Templates.ThirdParty.Core.Email",
    "website": "Splash.Templates.ThirdParty.Profile.Website",
}
"""Fields: V1 field id => template code."""

PHONE: Final = "Splash.Templates.ThirdParty.Core.Phone"
"""Phone template, when Odoo also has a mobile field (Odoo <= 18)."""

MOBILE: Final = "Splash.Templates.ThirdParty.Core.MobilePhone"
"""Mobile phone template: the only phone of Odoo 19+ (``mobile`` merged into ``phone``), as V1 metadata."""

FIELDS: Final = frozenset({*TEMPLATES, "phone", "mobile"})
"""Field ids of this group."""

URL_PREFIX: Final = "Url_Prefix"
"""Field option: prefix Odoo adds to websites without scheme (as V1)."""

STASH: Final = "thirdparty_names"
"""Stash key of the name parts being written."""


@fields_group("identity", priority=10)
class ThirdPartyIdentity(OdooGroup):
    """Names, email, phones and website."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare identity fields."""
        flags: dict[str, tuple[str | tuple[str, ...], ...]] = {
            "legal": ("is_required",),
            "email": ("is_indexed",),
            "website": (("add_option", URL_PREFIX, "http://"),),
        }
        build_fields(factory, TEMPLATES, flags=flags)
        if self.odoo is not None and "mobile" in self.odoo.model("res.partner")._fields:
            factory.create_from_template("phone", PHONE)
            factory.create_from_template("mobile", MOBILE)
        else:
            factory.create_from_template("phone", MOBILE)

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a field; names are decoded from the Odoo name."""
        if field_id in NAMES:
            return decode_name(req.object.name).get(field_id) or None
        return req.object[field_id] or None

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write a field; names are encoded in the Odoo name."""
        if field_id in NAMES:
            names = req.stash.setdefault(STASH, decode_name(req.object.name))
            names[field_id] = str(value or "").strip()
            return self.stage(req, "name", encode_name(names))
        return self.stage(req, field_id, value or False)


def decode_name(fullname: Any) -> dict[str, str]:
    """Split an Odoo name into first, last & legal names."""
    elements = {"first": "", "last": "", "legal": ""}
    fullname = str(fullname or "").strip()
    if " - " not in fullname:
        elements["legal"] = fullname
        return elements
    residual, elements["legal"] = (part.strip() for part in fullname.rsplit(" - ", 1))
    if ", " in residual:
        elements["first"], elements["last"] = (part.strip() for part in residual.split(", ", 1))
    else:
        elements["first"] = residual
    return elements


def encode_name(names: Mapping[str, Any], req: ObjectRequest | None = None) -> str:
    """Build the Odoo name from first, last & legal names."""
    first, last, legal = (str(names.get(key) or "").strip() for key in ("first", "last", "legal"))
    if not legal:
        legal = "Legal Name not Defined"
        if req is not None:
            req.logger.warning("ThirdParty: legal name not defined.")
    if last:
        return f"{first}, {last} - {legal}"
    if first:
        return f"{first} - {legal}"
    return legal
