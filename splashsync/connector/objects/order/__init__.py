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
"""Order: Odoo sales orders (``sale.order``), the ``Order.Erp`` feature with addresses as links.

Odoo records the orders of the shops (header, customer, addresses, lines, payments), computes their
totals, invoices them and sends the invoice back (number, date, PDF). Field ids are the V1 ids.
"""

from __future__ import annotations

from typing import Any, ClassVar, Final

from splashpy.core.context import RequestContext
from splashpy.fields import FieldsFactory, FieldType
from splashpy.objects import ObjectRequest

from ..accounting.lines import LIST as LINES
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
from .core import OrderCore
from .invoicing import FIELDS as INVOICING_FIELDS
from .invoicing import OrderInvoicing, read_file
from .payments import OrderPayments
from .status import FIELDS as STATUS_FIELDS
from .status import QUIET, OrderStatus

# Order.Erp wants its Address Receiver: Odoo stores addresses as partners, received as links to
# Address objects (Parties Receiver), the inline shipping address prefers the read direction (provided). Its base
# scopes are declared instead; they apply to every document type, so the Sales Header Receiver is left out
# (it wants the invoice customer reference as ``Order/orderNumber``, see Invoice).
SCOPES: Final = (
    "Splash.Scopes.Accounting.ItemsReceiver",
    "Splash.Scopes.Accounting.PartiesReceiver",
    "Splash.Scopes.Accounting.AddressProvider",
    "Splash.Scopes.Accounting.PaymentsReceiver",
    "Splash.Scopes.Accounting.TotalsProvider",
    "Splash.Scopes.Order.InvoicingProvider",
)
"""Scopes declared for Order."""

MODEL: Final = "sale.order"
"""Odoo model."""

PRODUCT_TYPE: Final = "detailed_type"
"""Line product type column (V1)."""


class OrderParties(AccountingParties):
    """Customer, invoice & shipping addresses; currency given by the pricelist."""


class OrderShipping(AccountingShipping):
    """Inline shipping address, preferably read."""


class OrderLines(AccountingLines):
    """Order lines, with delivered, reserved & invoiced quantities, product type; not written on locked orders."""

    read_only: ClassVar[Any] = {
        "qty_delivered": ("Delivered Qty", "http://schema.org/OrderItem", "orderDelivery"),
        "qty_reserved": ("Reserved Qty", "http://schema.org/OrderItem", "orderItemStatus"),
        "qty_invoiced": ("Invoiced Qty", "http://schema.org/OrderItem", "orderQuantity"),
    }

    def build_extra(self, factory: FieldsFactory) -> None:
        """Declare the product type column (V1, read only)."""
        factory.create(FieldType.VARCHAR, PRODUCT_TYPE, "Product Type").in_list(LINES).is_read_only()
        factory.is_not_tested()

    def read_column(self, line: Any, name: str) -> Any:
        """Read a line column: reserved quantity of the line deliveries, product type."""
        if name == PRODUCT_TYPE:
            return line.product_id.type or None
        if name == "qty_reserved":
            # as V1: quantities of the deliveries not cancelled (delivered ones included)
            moves = line.move_ids.filtered(lambda move: move.state != "cancel")
            return int(sum(moves.mapped("product_uom_qty")))
        return super().read_column(line, name)

    def is_editable(self, req: ObjectRequest, document: Any) -> bool:
        """Lines of a locked (delivered) order are kept."""
        if document.locked:
            req.logger.warning(f"Order: {document.name} is locked, lines not changed.")
            return False
        return True


class OrderTotals(AccountingTotals):
    """Order totals."""


class OrderFields(GenericFields):
    """Generic Odoo fields of sales orders."""

    owned_elsewhere = frozenset(
        {
            *CORE_FIELDS,
            *PARTIES_FIELDS,
            *SHIPPING_FIELDS,
            *TOTALS_FIELDS,
            *INVOICING_FIELDS,
            *STATUS_FIELDS,
            "locked",
        }
    )
    """Explicit fields of the object."""

    def model_name(self) -> str:
        """Odoo model."""
        return MODEL


class Order(OdooObject):
    """Odoo sales order."""

    type = "Order"
    name = "Order"
    description = "Odoo Sales Order"
    icon = "fa fa-shopping-cart"
    model = MODEL
    listed_fields = ("client_order_ref", "name")
    groups: ClassVar[Any] = (
        OrderCore,
        OrderParties,
        OrderShipping,
        OrderLines,
        OrderPayments,
        OrderTotals,
        OrderInvoicing,
        OrderStatus,
        OrderFields,
    )

    def domain(self) -> list[Any]:
        """Orders of the current company."""
        return [("company_id", "=", self.odoo.company_id)]

    def search_domain(self, text: str) -> list[Any]:
        """Search by Odoo or customer reference."""
        return ["|", ("name", "ilike", text), ("client_order_ref", "ilike", text)]

    def list_values(self, record: Any) -> dict[str, Any]:
        """List references and the order date."""
        values = super().list_values(record)
        values["date_order"] = record.date_order.date().isoformat() if record.date_order else None
        return values

    def create_values(self, req: ObjectRequest) -> dict[str, Any]:
        """Odoo numbering, default sales team (Splash setting); the customer is required."""
        if not (req.stash.get(VALUES) or {}).get("partner_id"):
            raise ValueError("Order: no customer received, unable to create the order.")
        values: dict[str, Any] = {"name": self.odoo.env._("New"), "picking_policy": "one"}
        team = self.odoo.setting("sales_team_id")
        if team:
            values["team_id"] = team.id
        return values

    def read_file(self, ctx: RequestContext, path: str, md5: str) -> dict[str, Any] | None:
        """Read an invoice PDF for Splash."""
        return read_file(self.odoo.env, path, md5)

    def delete_record(self, record: Any) -> None:
        """Delete an order: cancelled first (Odoo only deletes quotations and cancelled orders)."""
        order = record.with_context(**QUIET)
        if order.state not in ("draft", "cancel"):
            if order.locked:
                order.action_unlock()
            order.action_cancel()
        order.unlink()
