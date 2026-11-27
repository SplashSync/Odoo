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

"""Order header (V1 ids): customer reference (the shop number), Odoo reference, dates, salesperson & team.

The customer reference is the number given by the shop; the Odoo numbering is the internal
reference, never written. Dates are Odoo date-times, exchanged as dates.
"""

from __future__ import annotations

from typing import Any, Final

from odoo import fields as odoo_fields
from splashpy.fields import FieldsFactory, FieldType
from splashpy.objects import ObjectRequest, fields_group
from splashpy.objects.group import Phase

from ..base import OdooGroup, build_fields

GROUP: Final = "General"
"""Fields group label (as V1)."""

TEMPLATES: Final = {
    "client_order_ref": "Splash.Templates.Order.Core.RefCustomer",
    "name": "Splash.Templates.Order.Core.RefInternal",
    "date_order": "Splash.Templates.Order.Core.Date",
    "commitment_date": "Splash.Templates.Accounting.Core.DeliveryDate",
    "create_date": "Splash.Templates.Common.Audit.DateCreated",
    "write_date": "Splash.Templates.Common.Audit.DateModified",
}
"""Fields: V1 field id => template code (``commitment_date`` is new)."""

AUTHOR: Final = {
    "user_id": ("Salesperson Name", "name"),
    "user_email": ("Salesperson Email", "email"),
    "team_id": ("Sales team Name", "memberOf"),
}
"""Salesperson & team (read only, V1): field id => (name, ``schema.org/Author`` property)."""

DATES: Final = ("date_order", "commitment_date")
"""Odoo date-times exchanged as dates."""

READ_ONLY: Final = ("name", "create_date", "write_date")
"""Fields given by Odoo."""

FIELDS: Final = frozenset({*TEMPLATES, *AUTHOR})
"""Field ids of this group."""


@fields_group("core", priority=10, phases=(Phase.CREATE, Phase.UPDATE))
class OrderCore(OdooGroup):
    """References, dates, salesperson & team; written before the order is created."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare header fields."""
        flags: dict[str, tuple[str | tuple[Any, ...], ...]] = dict.fromkeys(READ_ONLY, ("is_read_only",))
        flags["client_order_ref"] = ("is_required", "is_listed")
        flags["date_order"] = ("is_required", "is_listed")
        build_fields(factory, TEMPLATES, GROUP, flags=flags)
        for field_id, (name, item_prop) in AUTHOR.items():
            factory.create(FieldType.VARCHAR, field_id, name).group(GROUP)
            factory.micro_data("http://schema.org/Author", item_prop).is_read_only()

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a header field."""
        order = req.object
        if field_id in DATES:
            return order[field_id].date().isoformat() if order[field_id] else None
        if field_id in ("create_date", "write_date"):
            return odoo_fields.Datetime.to_string(order[field_id]) if order[field_id] else None
        if field_id == "user_id":
            return order.user_id.name or None
        if field_id == "user_email":
            return order.user_id.email or None
        if field_id == "team_id":
            return order.team_id.name or None
        return order[field_id] or None

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write a header field; dates at midnight."""
        if field_id in READ_ONLY or field_id in AUTHOR:
            return True
        if field_id in DATES:
            date = str(value or "")[:10]
            current = req.object[field_id] if req.object is not None else None
            if current and current.date().isoformat() == date:
                return True
            return self.stage(req, field_id, f"{date} 00:00:00" if date else False)
        return self.stage(req, field_id, str(value or "").strip() or False)
