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
"""Address contact: names (encoded in the Odoo name, as V1), parent, email, phones, job, website.

Odoo name = ``first, last`` / ``first``.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from splashpy.fields import FieldsFactory, ObjectIds
from splashpy.objects import ObjectRequest, fields_group

from ..base import OdooGroup, build_fields

NAMES: Final = ("first", "last")
"""Name parts, encoded in the Odoo name."""

TEMPLATES: Final = {
    "parent_id": "Splash.Templates.Address.Core.ThirdParty",
    "first": "Splash.Templates.Address.Contact.Firstname",
    "last": "Splash.Templates.Address.Contact.Lastname",
    "email": "Splash.Templates.Address.Contact.Email",
    "website": "Splash.Templates.ThirdParty.Profile.Website",
}
"""Fields: V1 field id => template code."""

PHONE: Final = "Splash.Templates.Address.Contact.Phone"
"""Phone template: the only phone of Odoo 19+ (``mobile`` merged into ``phone``), as V1 mobile metadata."""

FIELDS: Final = frozenset({*TEMPLATES, "phone", "mobile", "function"})
"""Field ids of this group."""

STASH: Final = "address_names"
"""Stash key of the name parts being written."""


@fields_group("contact", priority=10)
class AddressContact(OdooGroup):
    """Parent, names, email, phones, job position and website."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare contact fields."""
        flags: dict[str, tuple[str | tuple[str, ...], ...]] = {
            "parent_id": ("is_required",),
            "first": ("is_required", "is_listed"),
            "last": ("is_listed",),
            "website": (("add_option", "Url_Prefix", "http://"),),
        }
        build_fields(factory, TEMPLATES, flags=flags)
        if self.odoo is not None and "mobile" in self.odoo.model("res.partner")._fields:
            factory.create_from_template("phone", "Splash.Templates.ThirdParty.Core.Phone")
            factory.create_from_template("mobile", PHONE)
        else:
            factory.create_from_template("phone", PHONE)
        factory.create("varchar", "function", "Job Position")
        factory.micro_data("http://schema.org/Person", "jobTitle")

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a field; names are decoded from the Odoo name."""
        if field_id in NAMES:
            return decode_name(req.object.name).get(field_id) or None
        if field_id == "parent_id":
            return ObjectIds.encode("ThirdParty", req.object.parent_id.id) if req.object.parent_id else None
        return req.object[field_id] or None

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write a field; names are encoded in the Odoo name."""
        if field_id in NAMES:
            names = req.stash.setdefault(STASH, decode_name(req.object.name))
            names[field_id] = str(value or "").strip()
            return self.stage(req, "name", encode_name(names))
        if field_id == "parent_id":
            return self.set_parent(req, value)
        return self.stage(req, field_id, value or False)

    def set_parent(self, req: ObjectRequest, value: Any) -> bool:
        """Write the parent ThirdParty: it must exist (an address always has a parent)."""
        parent_id = ObjectIds.id(str(value or ""))
        parent = req.object.browse(int(parent_id)).exists() if parent_id and parent_id.isdigit() else None
        if not parent:
            req.logger.error(f"Address: parent ThirdParty {value} not found.")
            return False
        return self.stage(req, "parent_id", parent.id)


def decode_name(fullname: Any) -> dict[str, str]:
    """Split an Odoo name into first & last names."""
    fullname = str(fullname or "").strip()
    first, _, last = fullname.partition(", ")
    return {"first": first.strip(), "last": last.strip()}


def encode_name(names: Mapping[str, Any]) -> str:
    """Build the Odoo name from first & last names."""
    first, last = (str(names.get(key) or "").strip() for key in NAMES)
    return f"{first}, {last}" if last else first
