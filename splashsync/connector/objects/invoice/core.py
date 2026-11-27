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

"""Invoice header (V1 ids): customer reference, Odoo number, dates, salesperson & team.

The customer reference is the number given by the sending application; the Odoo number is given
when the invoice is posted, never written.
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
    "ref": "Splash.Templates.Invoice.Core.RefCustomer",
    "name": "Splash.Templates.Invoice.Core.RefInternal",
    "invoice_date": "Splash.Templates.Invoice.Core.Date",
    "invoice_date_due": "Splash.Templates.Invoice.Core.PaymentDueDate",
    "invoice_origin": "Splash.Templates.Invoice.Core.RefExternal",
    "create_date": "Splash.Templates.Common.Audit.DateCreated",
    "write_date": "Splash.Templates.Common.Audit.DateModified",
}
"""Fields: V1 field id => template code."""

AUTHOR: Final = {
    "user_id": ("Salesperson Name", "name"),
    "user_email": ("Salesperson Email", "email"),
    "team_id": ("Sales team Name", "memberOf"),
}
"""Salesperson & team (read only, V1): field id => (name, ``schema.org/Author`` property)."""

DATES: Final = ("invoice_date", "invoice_date_due")
"""Odoo dates."""

AUDIT: Final = ("create_date", "write_date")
"""Read-only audit dates."""

READ_ONLY: Final = ("name", "invoice_date_due", "invoice_origin", *AUDIT)
"""Fields given by Odoo (number, due date from the payment terms, origin documents)."""

FIELDS: Final = frozenset({*TEMPLATES, *AUTHOR})
"""Field ids of this group."""


@fields_group("core", priority=10, phases=(Phase.CREATE, Phase.UPDATE))
class InvoiceCore(OdooGroup):
    """References, dates, salesperson & team; written before the invoice is created."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare header fields."""
        flags: dict[str, tuple[str | tuple[Any, ...], ...]] = dict.fromkeys(READ_ONLY, ("is_read_only",))
        flags["invoice_origin"] = ("is_read_only", ("is_listed", False))
        build_fields(factory, TEMPLATES, GROUP, flags=flags)
        for field_id, (name, item_prop) in AUTHOR.items():
            factory.create(FieldType.VARCHAR, field_id, name).group(GROUP)
            factory.micro_data("http://schema.org/Author", item_prop).is_read_only()

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a header field."""
        invoice = req.object
        if field_id in DATES:
            return invoice[field_id].isoformat() if invoice[field_id] else None
        if field_id in AUDIT:
            return odoo_fields.Datetime.to_string(invoice[field_id]) if invoice[field_id] else None
        if field_id == "user_id":
            return invoice.invoice_user_id.name or None
        if field_id == "user_email":
            return invoice.invoice_user_id.email or None
        if field_id == "team_id":
            return invoice.team_id.name or None
        if field_id == "name":
            return invoice.name if invoice.name and invoice.name != "/" else None
        return invoice[field_id] or None

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write a header field (draft invoices only, Odoo refuses changes of posted ones)."""
        if field_id in READ_ONLY or field_id in AUTHOR:
            return True
        value = str(value or "").strip()
        if field_id in DATES:
            value = value[:10]
            current = req.object[field_id] if req.object is not None else None
            if current and current.isoformat() == value:
                return True
        if req.object is not None and req.object.state != "draft" and (req.object[field_id] or "") != value:
            req.logger.warning(f"Invoice: {req.object.name} is not a draft, {field_id} not changed.")
            return True
        return self.stage(req, field_id, value or False)
