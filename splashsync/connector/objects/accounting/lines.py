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

"""Lines of accounting documents (V1 ids ``<column>@lines``): product, description, quantity, price, discount, taxes.

Only product lines are exchanged: sections & notes are kept as they are.

Received lines are the complete list of lines: matched by position, missing lines are removed,
extra lines are created. A line without known product gets the product of its SKU (received as
description), else the generic "Service" product (as V1).

Taxes: the VAT rate of the received unit price selects the tax of the company with that rate. With
"Sales Advanced Taxes" (Splash setting), taxes are written by names and prices are decoded with them.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, ClassVar, Final

from splashpy.fields import FieldsFactory, FieldType, ObjectIds
from splashpy.objects import ObjectRequest, fields_group

from ...taxes import Taxes
from ..base import OdooGroup, build_fields

LIST: Final = "lines"
"""Lines list name (V1)."""

PRODUCT: Final = "product_id"
"""Line product column, also the Odoo field."""

PRICE: Final = "price_unit"
"""Line unit price column, also the Odoo field."""

TAX: Final = "tax_name"
"""Line first tax name column."""

TAXES: Final = "tax_names"
"""Line taxes names column."""

TAXES_FIELD: Final = "tax_ids"
"""Odoo field of the line taxes."""

CURRENCY: Final = "Currency"
"""Price field option: currency code."""

SERVICE: Final = {"name": "Service", "default_code": "SPL", "type": "service"}
"""Generic product of the lines without known product (V1)."""

ADVANCED: Final = "sales_advanced_taxes"
"""Splash setting: taxes written by names, apart from prices."""


def column(name: str) -> str:
    """Field id of a lines column."""
    return f"{name}@{LIST}"


@fields_group("lines", priority=50, after=("core", "parties"))
class AccountingLines(OdooGroup):
    """Product lines of a document (configured by each object)."""

    lines_field: ClassVar[str] = "order_line"
    """Odoo field of the document lines."""

    quantity: ClassVar[str] = "product_uom_qty"
    """Odoo field (and column) of the line quantity."""

    read_only: ClassVar[Mapping[str, tuple[str, str, str]]] = {}
    """Read-only quantity columns: Odoo field => (name, itemtype, itemprop)."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare lines columns."""
        main = (column(PRODUCT), column(self.quantity), column(PRICE))
        templates = {
            column(PRODUCT): "Splash.Templates.Accounting.Items.ProductId",
            column("name"): "Splash.Templates.Accounting.Items.Description",
            column(self.quantity): "Splash.Templates.Accounting.Items.Quantity",
            column(PRICE): "Splash.Templates.Accounting.Items.UnitPrice",
            column("discount"): "Splash.Templates.Accounting.Items.Discount",
        }
        flags: dict[str, tuple[str | tuple[Any, ...], ...]] = dict.fromkeys(templates, (("association", *main),))
        flags[column(PRICE)] = (("association", *main), ("add_option", CURRENCY, self.currency_code()))
        build_fields(factory, templates, flags=flags)
        advanced = self.is_advanced()
        factory.create_from_template(column(TAX), "Splash.Templates.Accounting.Items.VatCode", "Tax Name")
        factory.is_read_only(not advanced).is_not_tested()
        factory.create(FieldType.INLINE, TAXES, "Taxes").in_list(LIST)
        factory.micro_data("http://schema.org/PriceSpecification", "valueAddedTaxNames")
        factory.is_read_only(not advanced).is_not_tested()
        for name, (label, itemtype, itemprop) in self.read_only.items():
            factory.create(FieldType.INT, name, label).in_list(LIST).micro_data(itemtype, itemprop)
            factory.is_read_only()
        self.build_extra(factory)

    def build_extra(self, factory: FieldsFactory) -> None:
        """Declare the extra columns of an object (default: none)."""

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read one column of the product lines."""
        name = field_id.split("@", 1)[0]
        return [self.read_column(line, name) for line in self.product_lines(req.object)]

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write the complete product lines list: update by position, create, remove."""
        document = req.object
        if not self.is_editable(req, document):
            return True
        rows = sorted_rows(value)
        lines = self.product_lines(document)
        for position, row in enumerate(rows):
            line = lines[position] if position < len(lines) else None
            values = self.values(req, line, row)
            if line is None:
                self.create_line(req, document, values)
            elif values:
                line.write(values)
            req.need_update()
        for line in lines[len(rows) :]:
            with document.env.cr.savepoint():
                line.unlink()
            req.need_update()
        return True

    # ====================================================================#
    # Read
    # ====================================================================#

    def product_lines(self, document: Any) -> Any:
        """Product lines of a document, by position (sections & notes excluded)."""
        return document[self.lines_field].filtered(self.is_product_line).sorted(lambda line: (line.sequence, line.id))

    def is_product_line(self, line: Any) -> bool:
        """Tell if a line is a product line (default: not a section nor a note)."""
        return not line.display_type

    def read_column(self, line: Any, name: str) -> Any:
        """Read a line column."""
        if name == PRODUCT:
            return ObjectIds.encode("Product", line.product_id.id) if line.product_id else None
        if name == PRICE:
            return Taxes.encode(line.price_unit, line[TAXES_FIELD], line.currency_id.name or self.currency_code())
        if name == TAX:
            return line[TAXES_FIELD][:1].name or None
        if name == TAXES:
            return ", ".join(line[TAXES_FIELD].mapped("name")) or None
        if name == "discount":
            return float(line.discount or 0)
        if name == self.quantity or name in self.read_only:
            return int(line[name] or 0)
        return line[name] or None

    # ====================================================================#
    # Write
    # ====================================================================#

    def is_editable(self, req: ObjectRequest, document: Any) -> bool:
        """Tell if the lines of a document can be written (default: always)."""
        return True

    def values(self, req: ObjectRequest, line: Any, row: Mapping[str, Any]) -> dict[str, Any]:
        """Odoo values of a received line, only the changed ones for an existing line."""
        values: dict[str, Any] = {}
        product = self.product(req, row)
        if product is not None and (line is None or line.product_id != product):
            values[PRODUCT] = product.id
        if "name" in row and row["name"] and (line is None or line.name != row["name"]):
            values["name"] = str(row["name"])
        for name in (self.quantity, "discount"):
            if name in row and (line is None or abs(float(line[name] or 0) - number(row[name])) > Taxes.PRECISION):
                values[name] = number(row[name])
        taxes = self.taxes(req, line, row)
        if taxes is not None and (line is None or set(line[TAXES_FIELD].ids) != set(taxes.ids)):
            values[TAXES_FIELD] = [(6, 0, taxes.ids)]
        if PRICE in row:
            current = taxes if taxes is not None else (line[TAXES_FIELD] if line else self.context.env["account.tax"])
            amount = Taxes.decode(row[PRICE], current)
            if line is None or PRODUCT in values or abs(float(line.price_unit) - amount) > Taxes.PRECISION:
                values[PRICE] = amount
        return values

    def product(self, req: ObjectRequest, row: Mapping[str, Any]) -> Any:
        """Product of a received line: its id, else its SKU (description); None when not received."""
        products = self.context.model("product.product").with_context(active_test=False)
        company: list[Any] = [("company_id", "in", [self.context.company_id, False])]
        product_id = str(ObjectIds.id(str(row.get(PRODUCT) or "")) or "")
        if product_id.isdigit():
            product = products.search([("id", "=", int(product_id)), *company], limit=1)
            if product:
                return product
            req.logger.warning(f"{req.object_type}: product {row.get(PRODUCT)} not found.")
        if PRODUCT not in row and "name" not in row:
            return None
        sku = str(row.get("name") or "").strip()
        product = products.search([("default_code", "=", sku), *company], limit=1) if sku else None
        return product or self.service(products)

    def service(self, products: Any) -> Any:
        """Get the generic "Service" product of lines without product (created once)."""
        service = products.search([("default_code", "=", SERVICE["default_code"])], limit=1)
        return service or products.with_context(create_product_product=True).create(dict(SERVICE))

    def taxes(self, req: ObjectRequest, line: Any, row: Mapping[str, Any]) -> Any:
        """Taxes of a received line: by names (advanced taxes), else by VAT rate of the price; None: unchanged."""
        if self.is_advanced():
            names = row.get(TAXES) if TAXES in row else (row.get(TAX) if TAX in row else None)
            return None if names is None else self.taxes_by_names(names)
        if PRICE not in row:
            return None
        vat = Taxes.vat_of(row[PRICE])
        if vat is None:
            return None
        taxes = Taxes.find(self.context.env, self.context.company, Taxes.SALE, float(vat))
        if not taxes and float(vat) > Taxes.PRECISION:
            req.logger.warning(f"{req.object_type}: no sale tax with a {vat}% rate, line without taxes.")
        return taxes

    def taxes_by_names(self, names: Any) -> Any:
        """Sale taxes of the company by names (comma separated or list), unknown ones ignored."""
        items = names if isinstance(names, (list, tuple)) else str(names or "").split(",")
        wanted = [str(name).strip() for name in items if str(name).strip()]
        return self.context.env["account.tax"].search(
            [("company_id", "=", self.context.company_id), ("type_tax_use", "=", Taxes.SALE), ("name", "in", wanted)]
        )

    def create_line(self, req: ObjectRequest, document: Any, values: dict[str, Any]) -> Any:
        """Create a line at the end of the document (the generic product when none received)."""
        if PRODUCT not in values:
            values[PRODUCT] = self.service(self.context.model("product.product")).id
        sequences = document[self.lines_field].mapped("sequence")
        values.setdefault("sequence", (max(sequences) if sequences else 0) + 1)
        return document.write({self.lines_field: [(0, 0, values)]})

    # ====================================================================#
    # Settings
    # ====================================================================#

    def is_advanced(self) -> bool:
        """Tell if taxes are written apart from prices (Sales Advanced Taxes setting of the company)."""
        return bool(self.odoo is not None and self.odoo.setting(ADVANCED))

    def currency_code(self) -> str:
        """Currency of the company."""
        return str(self.odoo.company.currency_id.name) if self.odoo is not None else "EUR"


def sorted_rows(value: Any) -> Sequence[Mapping[str, Any]]:
    """Received rows, by key (Splash sends lists as mappings: ``0``, ``line-1``...) or position."""
    if not isinstance(value, Mapping):
        return [row for row in (value or []) if isinstance(row, Mapping)]

    def position(key: Any) -> tuple[int, str]:
        digits = "".join(char for char in str(key) if char.isdigit())
        return (int(digits) if digits else 0, str(key))

    return [value[key] for key in sorted(value, key=position) if isinstance(value[key], Mapping)]


def number(value: Any) -> float:
    """Received number (empty: zero)."""
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0
