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
"""ThirdParty identifiers, flags, profile & audit dates."""

from __future__ import annotations

from typing import Any, Final

from odoo import fields as odoo_fields
from splashpy.fields import FieldsFactory, ObjectIds
from splashpy.objects import ObjectRequest, fields_group

from ..base import OdooGroup, build_fields

TEMPLATES: Final = {
    "vat": "Splash.Templates.ThirdParty.Identifiers.VatId",
    "ref": "Splash.Templates.ThirdParty.Identifiers.Identifier",
    "lang": "Splash.Templates.ThirdParty.Profile.Language",
    "active": "Splash.Templates.ThirdParty.Flags.Active",
    "parent_id": "Splash.Templates.Address.Core.ThirdParty",
    "create_date": "Splash.Templates.Common.Audit.DateCreated",
    "write_date": "Splash.Templates.Common.Audit.DateModified",
}
"""Fields: V1 field id => template code."""

FIELDS: Final = frozenset({*TEMPLATES, "customer", "supplier", "prospect"})
"""Field ids of this group."""

AUDIT: Final = ("create_date", "write_date")
"""Read-only audit dates."""

RANKS: Final = {"customer": "customer_rank", "supplier": "supplier_rank"}
"""Customer & supplier flags (V1 ids): Odoo ranks, raised by sales, invoices, purchases and bills."""


FLAGS: Final = {
    "customer": "Splash.Templates.ThirdParty.Flags.Customer",
    "supplier": "Splash.Templates.ThirdParty.Flags.Supplier",
    "prospect": "Splash.Templates.ThirdParty.Flags.Prospect",
}
"""Customer, supplier & prospect flags (V1 ids), computed from the Odoo ranks."""


def read_flag(req: ObjectRequest, field_id: str) -> bool:
    """Read a rank flag: customer / supplier when the rank is set, prospect when none is."""
    if field_id in RANKS:
        return int(req.object[RANKS[field_id]] or 0) > 0
    return not any(int(req.object[rank] or 0) > 0 for rank in RANKS.values())


class RankFlags(OdooGroup):
    """Base of groups exposing the customer / supplier / prospect flags."""

    def write_flag(self, req: ObjectRequest, field_id: str, value: Any) -> bool:
        """Write a rank flag: set the rank (kept when already set) or clear it; prospect is read-only."""
        if field_id not in RANKS:
            return True
        rank = int(self.current(req, RANKS[field_id]) or 0)
        flag = str(value) in ("1", "True", "true")
        return self.stage(req, RANKS[field_id], max(rank, 1) if flag else 0)


@fields_group("meta", priority=30, after=("identity",))
class ThirdPartyMeta(RankFlags):
    """Identifiers, flags (active, customer, supplier, prospect), language and audit dates."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare meta fields."""
        flags: dict[str, tuple[str | tuple[str, ...], ...]] = dict.fromkeys(AUDIT, ("is_read_only",))
        flags["active"] = ("is_not_tested",)
        flags["vat"] = ("is_not_tested",)  # Odoo checks VAT numbers per country
        flags["parent_id"] = (("name", "Parent Company"), "is_not_tested")  # a parent makes it an Address
        flags["prospect"] = ("is_read_only",)  # neither customer nor supplier yet
        build_fields(factory, {**TEMPLATES, **FLAGS}, flags=flags)

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a field."""
        if field_id in FLAGS:
            return read_flag(req, field_id)
        value = req.object[field_id]
        if field_id == "parent_id":
            return ObjectIds.encode("ThirdParty", value.id) if value else None
        if field_id == "active":
            return bool(value)
        if field_id in AUDIT:
            return odoo_fields.Datetime.to_string(value) if value else None
        return value or None

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write a field."""
        if field_id in AUDIT:
            return True
        if field_id in FLAGS:
            return self.write_flag(req, field_id, value)
        if field_id == "active":
            return self.stage(req, field_id, str(value) in ("1", "True", "true"))
        if field_id == "parent_id":
            parent_id = ObjectIds.id(value) if value else None
            return self.stage(req, field_id, int(parent_id) if parent_id and parent_id.isdigit() else False)
        return self.stage(req, field_id, value or False)
