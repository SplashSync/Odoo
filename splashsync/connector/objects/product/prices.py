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

"""Product prices: sell base price, cost price, variant prices, taxes (V1 ids).

- Sell base price (``list_price``) is the price of the product template, shared by its variants.
  A variant adds its extra price: Odoo attribute values extra prices, or, in "Simplified Prices"
  mode (Splash setting), its own extra price (``variant_price_extra`` on the variant).
- Simplified Prices: ``lst_price`` (final price) and ``variant_price`` (V1 alias) write the variant
  extra price, the base price is never changed by them.
- Taxes: the VAT rate of a received price selects the tax of the company with that rate (sell taxes
  for sell prices, purchase taxes for the cost). With "Advanced Taxes" (Splash setting), prices are
  exchanged without taxes and taxes are written by ids or names.
"""

from __future__ import annotations

from typing import Any, Final

from splashpy.fields import FieldsFactory, FieldType
from splashpy.objects import ObjectRequest, fields_group

from ...taxes import Taxes
from ..base import OdooGroup

GROUP: Final = "Prices"
"""Splash fields group."""

PRICES: Final = {
    "list_price": ("Splash.Templates.Product.Pricing.BasePrice", Taxes.SALE),
    "standard_price": ("Splash.Templates.Product.Pricing.WholesalePrice", Taxes.PURCHASE),
}
"""Prices written as is: V1 field id => (template code, tax use)."""

FINAL: Final = "lst_price"
"""Final sell price of the variant (Simplified Prices mode)."""

VARIANT: Final = "variant_price"
"""Final sell price of the variant, V1 alias of ``lst_price`` (Simplified Prices mode, zero: base price)."""

EXTRA: Final = "variant_price_extra"
"""Extra price of the variant (read-only; Simplified Prices mode: stored on the variant)."""

TAXES: Final = {
    "list_price_tax_ids": ("taxes_id", Taxes.SALE, "id"),
    "list_price_tax_names": ("taxes_id", Taxes.SALE, "name"),
    "standard_price_tax_ids": ("supplier_taxes_id", Taxes.PURCHASE, "id"),
    "standard_price_tax_names": ("supplier_taxes_id", Taxes.PURCHASE, "name"),
}
"""Taxes fields (Advanced Taxes mode): V1 field id => (Odoo field, tax use, tax key)."""

TAX_FIELDS: Final = {Taxes.SALE: "taxes_id", Taxes.PURCHASE: "supplier_taxes_id"}
"""Odoo taxes field by tax use."""

SIMPLIFIED: Final = "product_simplified_prices"
"""Splash setting: variants own extra prices."""

ADVANCED: Final = "product_advanced_taxes"
"""Splash setting: prices without taxes, taxes written apart."""

CURRENCY: Final = "Currency"
"""Field option: currency of the prices (Toolkit tests)."""

ZERO: Final = 0.001
"""Prices compare precision."""

FIELDS: Final = frozenset({*PRICES, FINAL, VARIANT, EXTRA, *TAXES})
"""Field ids of this group."""


@fields_group("prices", priority=40, after=("core",))
class ProductPrices(OdooGroup):
    """Sell & cost prices with their taxes, variants prices."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare prices fields (by the Splash settings of the company)."""
        for field_id, (template, _use) in PRICES.items():
            factory.create_from_template(field_id, template).group(GROUP)
            self.test_options(factory)
        factory.create(FieldType.PRICE, EXTRA, "Variant Extra Price").group(GROUP).is_read_only()
        factory.micro_data("http://schema.org/Product", "extraPrice")
        if self.is_simplified():
            factory.create_from_template(FINAL, "Splash.Templates.Product.Pricing.Price").group(GROUP)
            factory.name("Price (tax excl.)").description("Final Price for Selling this Product.")
            factory.is_listed(False)
            self.test_options(factory)
            factory.create(FieldType.PRICE, VARIANT, "Variant Price (tax excl.)").group(GROUP).is_not_tested()
            factory.description("Final Price for this Variant. If set to Zero, we use Base Price.")
            factory.micro_data("http://schema.org/Product", "variantPrice")
        if self.is_advanced():
            for field_id, (_name, use, key) in TAXES.items():
                label = f"{'Sell' if use == Taxes.SALE else 'Buy'} Taxes {'Ids' if key == 'id' else 'Names'}"
                factory.create(FieldType.VARCHAR, field_id, label).group(GROUP).is_not_tested()
                factory.micro_data("http://schema.org/Product", micro_data(field_id))

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a price, or taxes ids / names."""
        product = req.object
        if field_id in TAXES:
            _name, use, key = TAXES[field_id]
            taxes = self.taxes(product, use)
            return ", ".join(str(tax[key]) for tax in taxes) or None
        use = PRICES[field_id][1] if field_id in PRICES else Taxes.SALE
        if field_id == EXTRA:
            amount = float(product.lst_price) - float(product.list_price)
        elif field_id in (FINAL, VARIANT):
            amount = float(product.lst_price)
        else:
            amount = float(product[field_id] or 0)
        return Taxes.encode(amount, self.price_taxes(product, use), self.currency())

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write a price (and the taxes of its VAT rate), or taxes ids / names."""
        if field_id == EXTRA:
            return True
        if field_id in TAXES:
            return self.set_taxes(req, field_id, value)
        use = PRICES[field_id][1] if field_id in PRICES else Taxes.SALE
        taxes = self.set_rate(req, use, Taxes.vat_of(value))
        amount = Taxes.decode(value, taxes)
        if field_id in PRICES:
            return self.stage(req, field_id, amount)
        if field_id == VARIANT and abs(amount) < ZERO:
            return self.stage(req, EXTRA, 0.0)
        return self.stage(req, EXTRA, round(amount - self.base_price(req, taxes), 6))

    # ====================================================================#
    # Settings
    # ====================================================================#

    def is_simplified(self) -> bool:
        """Tell if variants own their extra prices (Simplified Prices setting of the company)."""
        return bool(self.odoo and self.odoo.setting(SIMPLIFIED))

    def is_advanced(self) -> bool:
        """Tell if taxes are written apart from prices (Advanced Taxes setting of the company)."""
        return bool(self.odoo and self.odoo.setting(ADVANCED))

    def currency(self) -> str:
        """Currency code of the prices (company currency)."""
        return str(self.context.company.currency_id.name) if self.odoo else ""

    def test_options(self, factory: FieldsFactory) -> None:
        """Toolkit options of a price: the company currency (tests VAT rate: 20%, a tax of each test company)."""
        if self.odoo is not None:
            factory.add_option(CURRENCY, self.currency())

    # ====================================================================#
    # Taxes
    # ====================================================================#

    def taxes(self, product: Any, use: str) -> Any:
        """Taxes of the product for the company and a use."""
        return Taxes.company_taxes(product[TAX_FIELDS[use]], self.context.company, use)

    def price_taxes(self, product: Any, use: str) -> Any:
        """Taxes applied to the prices exchanged with Splash (none in Advanced Taxes mode)."""
        if self.is_advanced():
            return product.env["account.tax"]
        return self.taxes(product, use)

    def set_rate(self, req: ObjectRequest, use: str, vat: float | None) -> Any:
        """Select the taxes of a received VAT rate (not in Advanced Taxes mode), get the taxes of the price."""
        product = req.object
        current = self.price_taxes(product, use)
        if self.is_advanced() or vat is None:
            return current
        taxes = product.env["account.tax"]
        if vat > ZERO:
            taxes = Taxes.find(product.env, self.context.company, use, vat)
            if not taxes:
                req.logger.warning(f"Product: no {use} tax with a {vat}% rate, taxes not changed.")
                return current
        ids = Taxes.replace(product[TAX_FIELDS[use]], self.context.company, use, taxes)
        if ids is not None:
            self.stage_ids(req, TAX_FIELDS[use], ids)
        return taxes

    def set_taxes(self, req: ObjectRequest, field_id: str, value: Any) -> bool:
        """Write the taxes of the company for a use, by ids or names (comma separated, unknown ones ignored)."""
        name, use, key = TAXES[field_id]
        product = req.object
        items: list[Any] = [item.strip() for item in str(value or "").split(",") if item.strip()]
        if key == "id":
            items = [int(item) for item in items if item.isdigit()]
        domain = [("company_id", "=", self.context.company.id), ("type_tax_use", "=", use), (key, "in", items)]
        found = product.env["account.tax"].search(domain)
        ids = Taxes.replace(product[name], self.context.company, use, found)
        if ids is not None:
            self.stage_ids(req, name, ids)
        return True

    # ====================================================================#
    # Variants
    # ====================================================================#

    def base_price(self, req: ObjectRequest, taxes: Any) -> float:
        """Sell base price: received in the same request, else the current one."""
        if "list_price" in req.inputs:
            return Taxes.decode(req.inputs.get("list_price"), taxes)
        return float(self.current(req, "list_price") or 0)


def micro_data(field_id: str) -> str:
    """V1 microdata property of a taxes field."""
    use, _sep, kind = field_id.partition("_price_tax_")
    prefix = "price" if use == "list" else "wholesalePrice"
    return f"{prefix}Tax{'Ids' if kind == 'ids' else 'Names'}"
