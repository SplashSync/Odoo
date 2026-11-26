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

"""Product first supplier (V1 ids): vendor, price, vendor SKU, minimum quantity, currency.

The first supplier is the first vendor price line (``product.supplierinfo``) of the variant or of
its template, in the current company. Without one, it is created when a known vendor (commercial
partner, by name) and a positive price are received in the same request.
"""

from __future__ import annotations

from typing import Any, Final

from splashpy.fields import FieldsFactory, FieldType
from splashpy.objects import ObjectRequest, fields_group

from ...taxes import Taxes
from ..base import OdooGroup

GROUP: Final = "Supplier"
"""Splash fields group."""

MODEL: Final = "product.supplierinfo"
"""Odoo model of vendor prices."""

NAME: Final = "supplier_name"
"""Vendor name."""

PRICE: Final = "supplier_price"
"""Vendor price, as a Splash price."""

AMOUNT: Final = "supplier_price_dbl"
"""Vendor price, as a number."""

SKU: Final = "supplier_sku"
"""Vendor SKU."""

MOQ: Final = "supplier_min_qty"
"""Vendor minimum quantity."""

COLUMNS: Final = {
    SKU: "product_code",
    MOQ: "min_qty",
    AMOUNT: "price",
}
"""Plain values: V1 field id => Odoo field of the vendor price."""

CURRENCY: Final = "supplier_currency"
"""Vendor price currency (ISO code)."""

VENDORS: Final = [("parent_id", "=", False), ("supplier_rank", ">", 0)]
"""Vendors given as choices: commercial partners already used as vendors."""

PARTNERS: Final = [("parent_id", "=", False)]
"""Vendors found by name: commercial partners (``is_company`` depends on the VAT number since Odoo 20)."""

MAX_VENDORS: Final = 200
"""Maximum vendors given as choices."""

FIELDS: Final = frozenset({NAME, PRICE, CURRENCY, *COLUMNS})
"""Field ids of this group."""


@fields_group("suppliers", priority=60, after=("core", "prices"))
class ProductSuppliers(OdooGroup):
    """First supplier of the product."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare supplier fields: vendor & price are associated (a vendor price needs both to be created)."""
        factory.create(FieldType.VARCHAR, NAME, "Supplier Name").group(GROUP).association(AMOUNT)
        factory.micro_data("http://schema.org/Product", "supplierName")
        for vendor in self.vendors():
            factory.add_choice(vendor.name, vendor.name)
        factory.create(FieldType.DOUBLE, AMOUNT, "Supplier Price (Float)").group(GROUP).association(NAME)
        factory.micro_data("http://schema.org/Product", "supplierPriceDbl")
        factory.create(FieldType.PRICE, PRICE, "Supplier Price").group(GROUP).is_not_tested()
        factory.micro_data("http://schema.org/Product", "supplierPrice")
        factory.create_from_template(SKU, "Splash.Templates.Product.Identifiers.Mpn").group(GROUP)
        factory.name("Supplier SKU").association(NAME, AMOUNT)
        factory.create(FieldType.INT, MOQ, "Supplier MOQ").group(GROUP).association(NAME, AMOUNT)
        factory.micro_data("http://schema.org/Product", "supplierMinQty")
        factory.create(FieldType.CURRENCY, CURRENCY, "Supplier Currency").group(GROUP).is_not_tested()
        factory.micro_data("http://schema.org/Product", "supplierCurrency")

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a value of the first supplier."""
        supplier = self.first(req.object)
        if not supplier:
            return None
        if field_id == NAME:
            return supplier.partner_id.name or None
        if field_id == CURRENCY:
            return supplier.currency_id.name or None
        if field_id == PRICE:
            taxes = Taxes.company_taxes(req.object.supplier_taxes_id, self.context.company, Taxes.PURCHASE)
            return Taxes.encode(float(supplier.price), taxes, str(supplier.currency_id.name or ""))
        value = supplier[COLUMNS[field_id]]
        if field_id == MOQ:
            return int(value)
        return value if field_id == AMOUNT else value or None

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write a value of the first supplier (created with the received vendor & price if needed)."""
        supplier = self.first(req.object) or self.create_supplier(req)
        if not supplier:
            return True
        values: dict[str, Any] = {}
        if field_id == NAME:
            vendor = self.vendor(str(value or ""))
            if vendor and vendor != supplier.partner_id:
                values["partner_id"] = vendor.id
        elif field_id == CURRENCY:
            currency = req.object.env["res.currency"].search([("name", "=", str(value or "").upper())], limit=1)
            if currency and currency != supplier.currency_id:
                values["currency_id"] = currency.id
        elif field_id == PRICE:
            amount = received_price(req)
            if amount is not None and abs(amount - float(supplier.price)) > Taxes.PRECISION:
                values["price"] = amount
        elif field_id == SKU:
            sku = str(value).strip() if value not in (None, "") else False
            if sku != (supplier.product_code or False):
                values["product_code"] = sku
        else:
            column = COLUMNS[field_id]
            number = float(value or 0)
            if abs(number - float(supplier[column] or 0)) > Taxes.PRECISION:
                values[column] = number
        if values:
            supplier.write(values)
            req.need_update()
        return True

    # ====================================================================#
    # Vendors & vendor prices
    # ====================================================================#

    def vendors(self) -> Any:
        """Vendors given as choices."""
        if self.odoo is None:
            return []
        return self.odoo.model("res.partner").search(VENDORS, order="name", limit=MAX_VENDORS)

    def vendor(self, name: str) -> Any:
        """Find a vendor by name, empty when unknown."""
        partners = self.context.model("res.partner")
        if not name.strip():
            return partners
        return partners.search([*PARTNERS, ("name", "=ilike", name.strip())], order="supplier_rank desc, id", limit=1)

    def first(self, product: Any) -> Any:
        """First vendor price of the variant or its template in the company, empty when none."""
        return product.env[MODEL].search(
            [
                ("product_tmpl_id", "=", product.product_tmpl_id.id),
                ("product_id", "in", [False, product.id]),
                ("company_id", "in", [False, self.context.company_id]),
            ],
            limit=1,
        )

    def create_supplier(self, req: ObjectRequest) -> Any:
        """Create the first vendor price from the received vendor & price, empty when missing or invalid."""
        product = req.object
        vendor = self.vendor(str(req.inputs.get(NAME) or ""))
        amount = received_price(req)
        if not vendor or amount is None or amount <= 0:
            return product.env[MODEL]
        return product.env[MODEL].create(
            {
                "partner_id": vendor.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_id": product.id,
                "company_id": self.context.company_id,
                "min_qty": 1,
                "price": amount,
            }
        )


def received_price(req: ObjectRequest) -> float | None:
    """Vendor price received in the request (number first, then Splash price tax excluded), None when missing."""
    if req.inputs.get(AMOUNT) not in (None, ""):
        try:
            return float(req.inputs[AMOUNT])
        except (TypeError, ValueError):
            return None
    if req.inputs.get(PRICE):
        return Taxes.decode(req.inputs[PRICE], [])
    return None
