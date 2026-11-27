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

"""Totals of accounting documents (read only), as computed by Odoo: products, shipping, discounts, document.

Each total is a Splash price (amount without tax, VAT rate of its tax amount, currency); a total
without lines is a zero price. Discounts are the line discounts (percentage of the line price).
"""

from __future__ import annotations

from typing import Any, ClassVar, Final

from splashpy.fields import FieldsFactory, Prices
from splashpy.objects import ObjectRequest, fields_group

from ..base import OdooGroup, build_fields

GROUP: Final = "Totals"
"""Fields group label."""

TEMPLATES: Final = {
    "total_products": "Splash.Templates.Accounting.Totals.TotalProducts",
    "total_shipping": "Splash.Templates.Accounting.Totals.TotalShipping",
    "total_discount": "Splash.Templates.Accounting.Totals.TotalDiscount",
    "total_price": "Splash.Templates.Accounting.Totals.Total",
}
"""Fields: field id => template code."""

FIELDS: Final = frozenset(TEMPLATES)
"""Field ids of this group."""

CURRENCY: Final = "Currency"
"""Price field option: currency code."""


@fields_group("totals", priority=80, after=("lines",))
class AccountingTotals(OdooGroup):
    """Products, shipping, discount & grand totals (configured by each object)."""

    lines_field: ClassVar[str] = "order_line"
    """Odoo field of the document lines."""

    quantity: ClassVar[str] = "product_uom_qty"
    """Odoo field of the line quantity."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare totals (read only)."""
        currency = str(self.odoo.company.currency_id.name) if self.odoo is not None else "EUR"
        flags = dict.fromkeys(TEMPLATES, ("is_read_only", ("add_option", CURRENCY, currency)))
        build_fields(factory, TEMPLATES, GROUP, flags=flags)

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a total."""
        document = req.object
        currency = str(document.currency_id.name or "")
        if field_id == "total_price":
            return price(float(document.amount_untaxed), float(document.amount_tax), currency)
        lines = self.lines(document)
        if field_id == "total_discount":
            untaxed = tax = 0.0
            for line in lines:
                full = float(line.price_unit) * float(line[self.quantity] or 0)
                discount = full * float(line.discount or 0) / 100
                untaxed += discount
                tax += discount * rate(line)
            return price(untaxed, tax, currency)
        shipping = field_id == "total_shipping"
        selected = lines.filtered(lambda line: self.is_shipping(line) == shipping)
        untaxed = sum(selected.mapped("price_subtotal"))
        return price(untaxed, sum(selected.mapped("price_total")) - untaxed, currency)

    def lines(self, document: Any) -> Any:
        """Product lines of a document (sections & notes excluded)."""
        return document[self.lines_field].filtered(self.is_product_line)

    def is_product_line(self, line: Any) -> bool:
        """Tell if a line is a product line (default: not a section nor a note)."""
        return not line.display_type

    def is_shipping(self, line: Any) -> bool:
        """Tell if a line is a shipping line (delivery fees)."""
        return bool(line.is_delivery)


def rate(line: Any) -> float:
    """Tax rate of a line, as a ratio of its subtotal."""
    subtotal = float(line.price_subtotal or 0)
    return float(line.price_total - line.price_subtotal) / subtotal if subtotal else 0.0


def price(untaxed: float, tax: float, currency: str) -> dict[str, Any] | None:
    """Splash price of a total: VAT rate from its tax amount."""
    vat = round(tax / untaxed * 100, 4) if abs(untaxed) > 0.0001 else 0.0
    return Prices.encode(float(untaxed), vat, None, currency or "EUR")
