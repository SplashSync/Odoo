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
"""Invoice: Odoo customer invoices (``account.move`` of type ``out_invoice``).

Invoices are received as drafts (header, customer, billing & shipping addresses, lines), then posted
and paid by their status and payments. Totals are computed by Odoo. Field ids are the V1 ids.
"""

from __future__ import annotations

from typing import Any, ClassVar, Final

from splashpy.objects import ObjectRequest

from ..accounting.lines import AccountingLines
from ..accounting.parties import TEMPLATES as PARTIES_FIELDS
from ..accounting.parties import AccountingParties
from ..accounting.shipping import FIELDS as SHIPPING_FIELDS
from ..accounting.shipping import AccountingShipping
from ..accounting.totals import FIELDS as TOTALS_FIELDS
from ..accounting.totals import AccountingTotals
from ..base import VALUES, OdooObject
from ..generic import GenericFields
from .core import FIELDS as CORE_FIELDS
from .core import InvoiceCore
from .payments import InvoicePayments
from .status import FIELDS as STATUS_FIELDS
from .status import InvoiceStatus, State

# Sales Header Receiver is not declared: it wants the customer reference as ``Order/orderNumber``,
# the invoice template (and V1) is ``Invoice/confirmationNumber``. Addresses are received as links
# (Parties Receiver), the inline shipping address prefers the read direction. Base scopes apply to every
# document type: the Order ones (Payments Receiver) are declared by Order.
SCOPES: Final = (
    "Splash.Scopes.Accounting.ItemsReceiver",
    "Splash.Scopes.Accounting.PartiesReceiver",
    "Splash.Scopes.Accounting.AddressProvider",
    "Splash.Scopes.Accounting.TotalsProvider",
)
"""Scopes declared for Invoice."""

MODEL: Final = "account.move"
"""Odoo model."""

TYPE: Final = "out_invoice"
"""Odoo move type of customer invoices."""

PRODUCT: Final = "product"
"""Odoo display type of invoice product lines."""


class InvoiceParties(AccountingParties):
    """Customer, billing (the invoice partner) & shipping addresses, currency (written on drafts)."""

    billing_partner: ClassVar[bool] = True
    currency_writable: ClassVar[bool] = True


class InvoiceShipping(AccountingShipping):
    """Inline shipping address, preferably read."""


class InvoiceLines(AccountingLines):
    """Invoice product lines; only written on drafts."""

    lines_field: ClassVar[str] = "invoice_line_ids"
    quantity: ClassVar[str] = "quantity"

    def is_product_line(self, line: Any) -> bool:
        """Invoice product lines (sections, notes... excluded)."""
        return bool(line.display_type == PRODUCT)

    def is_editable(self, req: ObjectRequest, document: Any) -> bool:
        """Lines of posted or cancelled invoices are kept."""
        if document.state != State.DRAFT:
            req.logger.warning(f"Invoice: {document.display_name} is not a draft, lines not changed.")
            return False
        return True


class InvoiceTotals(AccountingTotals):
    """Invoice totals; shipping lines are the invoiced delivery lines of orders."""

    lines_field: ClassVar[str] = "invoice_line_ids"
    quantity: ClassVar[str] = "quantity"

    def is_product_line(self, line: Any) -> bool:
        """Invoice product lines (sections, notes... excluded)."""
        return bool(line.display_type == PRODUCT)

    def is_shipping(self, line: Any) -> bool:
        """Tell if a line invoices delivery fees of an order."""
        return any(line.sale_line_ids.mapped("is_delivery"))


class InvoiceFields(GenericFields):
    """Generic Odoo fields of customer invoices."""

    owned_elsewhere = frozenset(
        {*CORE_FIELDS, *PARTIES_FIELDS, *SHIPPING_FIELDS, *TOTALS_FIELDS, *STATUS_FIELDS, "move_type"}
    )
    """Explicit fields of the object."""

    def model_name(self) -> str:
        """Odoo model."""
        return MODEL


class Invoice(OdooObject):
    """Odoo customer invoice."""

    type = "Invoice"
    name = "Invoice"
    description = "Odoo Customer Invoice"
    icon = "fa fa-money"
    model = MODEL
    listed_fields = ("ref", "name")
    groups: ClassVar[Any] = (
        InvoiceCore,
        InvoiceParties,
        InvoiceShipping,
        InvoiceLines,
        InvoiceStatus,
        InvoicePayments,
        InvoiceTotals,
        InvoiceFields,
    )

    def domain(self) -> list[Any]:
        """Expose the customer invoices of the current company."""
        return [("move_type", "=", TYPE), ("company_id", "=", self.odoo.company_id)]

    def search_domain(self, text: str) -> list[Any]:
        """Search by Odoo number or customer reference."""
        return ["|", ("name", "ilike", text), ("ref", "ilike", text)]

    def list_values(self, record: Any) -> dict[str, Any]:
        """List references and the invoice date."""
        values = super().list_values(record)
        values["name"] = record.name if record.name and record.name != "/" else None
        values["invoice_date"] = record.invoice_date.isoformat() if record.invoice_date else None
        return values

    def create_values(self, req: ObjectRequest) -> dict[str, Any]:
        """Create customer invoices, never posted automatically; the customer is required."""
        if not (req.stash.get(VALUES) or {}).get("partner_id"):
            raise ValueError("Invoice: no customer received, unable to create the invoice.")
        return {"move_type": TYPE, "auto_post": "no"}

    def records(self) -> Any:
        """Get the invoices model (customer invoices by default)."""
        return super().records().with_context(default_move_type=TYPE)

    def delete_record(self, record: Any) -> None:
        """Delete an invoice: back to draft first (Odoo only deletes drafts)."""
        if record.state != State.DRAFT:
            record.button_draft()
        record.unlink()
