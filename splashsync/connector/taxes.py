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

"""Odoo taxes helper: VAT rate of taxes, taxes of a rate, prices tax excluded / included.

Products are shared between companies: their taxes hold the taxes of every company. Only the taxes
of the current company are read and replaced, the others are kept.
"""

from __future__ import annotations

from typing import Any, Final

from splashpy.fields import Prices


class Taxes:
    """Taxes of shared records per company, VAT rates, Splash prices of Odoo amounts."""

    SALE: Final = "sale"
    """Odoo tax use: sales."""

    PURCHASE: Final = "purchase"
    """Odoo tax use: purchases."""

    PERCENT: Final = "percent"
    """Odoo tax amount type: percentage of the price."""

    GROUP: Final = "group"
    """Odoo tax amount type: group of children taxes."""

    PRECISION: Final = 0.001
    """VAT rates compare precision."""

    @staticmethod
    def company_taxes(taxes: Any, company: Any, use: str) -> Any:
        """Taxes of a company for a use (sale / purchase), among the taxes of a shared record."""
        return taxes.filtered(lambda tax: tax.company_id == company and tax.type_tax_use == use)

    @staticmethod
    def rate(taxes: Any) -> float:
        """VAT rate of taxes: sum of percentage taxes, children of groups included."""
        total = 0.0
        for tax in taxes:
            if tax.amount_type == Taxes.PERCENT:
                total += float(tax.amount)
            elif tax.amount_type == Taxes.GROUP:
                total += Taxes.rate(tax.children_tax_ids)
        return total

    @staticmethod
    def is_included(taxes: Any) -> bool:
        """Tell if prices include taxes."""
        return any(tax.price_include for tax in taxes)

    @staticmethod
    def find(env: Any, company: Any, use: str, vat: float) -> Any:
        """Find the tax of a VAT rate for a company & use (taxes excluded first), empty when not found."""
        taxes = env["account.tax"].search(
            [
                ("company_id", "=", company.id),
                ("type_tax_use", "=", use),
                ("amount_type", "=", Taxes.PERCENT),
                ("amount", ">=", vat - Taxes.PRECISION),
                ("amount", "<=", vat + Taxes.PRECISION),
            ]
        )
        return taxes.sorted(lambda tax: (tax.price_include, tax.sequence, tax.id))[:1]

    @staticmethod
    def replace(taxes: Any, company: Any, use: str, new: Any) -> list[int] | None:
        """Ids of a record taxes once the company taxes of a use are replaced, None when unchanged."""
        current = Taxes.company_taxes(taxes, company, use)
        if set(current.ids) == set(new.ids):
            return None
        return sorted(set((taxes - current).ids) | set(new.ids))

    @staticmethod
    def encode(amount: float, taxes: Any, currency: str) -> dict[str, Any] | None:
        """Splash price of an Odoo amount, tax included when the taxes say so."""
        vat = Taxes.rate(taxes)
        if Taxes.is_included(taxes):
            return Prices.encode(None, vat, float(amount), currency)
        return Prices.encode(float(amount), vat, None, currency)

    @staticmethod
    def decode(price: Any, taxes: Any) -> float:
        """Odoo amount of a Splash price: tax included when the taxes say so, else tax excluded."""
        amount = Prices.extract(price, "ttc" if Taxes.is_included(taxes) else "ht")
        return float(amount or 0)

    @staticmethod
    def vat_of(price: Any) -> float | None:
        """VAT rate of a Splash price, None when missing."""
        return Prices.extract(price, "vat")
