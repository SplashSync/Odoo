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
"""Address type, flags, parent company name & audit dates."""

from __future__ import annotations

from typing import Any, Final

from odoo import fields as odoo_fields
from splashpy.fields import FieldsFactory
from splashpy.objects import ObjectRequest, fields_group

from ..base import build_fields
from ..thirdparty.meta import FLAGS, RankFlags, read_flag

TEMPLATES: Final = {
    "type": "Splash.Templates.Address.Core.Type",
    "parent_name": "Splash.Templates.Address.Contact.Name",
    "create_date": "Splash.Templates.Common.Audit.DateCreated",
    "write_date": "Splash.Templates.Common.Audit.DateModified",
}
"""Fields: V1 field id => template code."""

FIELDS: Final = frozenset({*TEMPLATES, *FLAGS, "active"})
"""Field ids of this group."""

READ_ONLY: Final = ("parent_name", "create_date", "write_date", "prospect")
"""Read-only fields."""

TYPES: Final = {"invoice": "billing", "delivery": "delivery", "other": "other", "contact": "other"}
"""Odoo address types => Splash normalized types (template choices)."""


@fields_group("meta", priority=30, after=("contact",))
class AddressMeta(RankFlags):
    """Type, flags (active, customer, supplier, prospect), parent company name and audit dates."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare meta fields."""
        flags: dict[str, tuple[str | tuple[str, ...], ...]] = dict.fromkeys(READ_ONLY, ("is_read_only",))
        build_fields(factory, {**TEMPLATES, **FLAGS}, flags=flags)
        factory.create("bool", "active", "Active")
        factory.micro_data("http://schema.org/Person", "active")
        factory.group("Meta")
        factory.is_not_tested()

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a field."""
        if field_id in FLAGS:
            return read_flag(req, field_id)
        value = req.object[field_id]
        if field_id == "type":
            return TYPES.get(str(value), "other")
        if field_id == "active":
            return bool(value)
        if field_id in ("create_date", "write_date"):
            return odoo_fields.Datetime.to_string(value) if value else None
        return value or None

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write a field."""
        if field_id in READ_ONLY:
            return True
        if field_id in FLAGS:
            return self.write_flag(req, field_id, value)
        if field_id == "type":
            return self.stage(req, "type", to_odoo_type(value, req.object.type))
        if field_id == "active":
            return self.stage(req, field_id, str(value) in ("1", "True", "true"))
        return self.stage(req, field_id, value or False)


def to_odoo_type(value: Any, current: str | None) -> str:
    """Splash normalized type => Odoo type ("other" keeps an Odoo contact as it is)."""
    odoo_type = {"billing": "invoice", "delivery": "delivery"}.get(str(value or ""), "other")
    return "contact" if odoo_type == "other" and current == "contact" else odoo_type
