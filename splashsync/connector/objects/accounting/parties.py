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

"""Parties of accounting documents (V1 ids): customer, billing & shipping addresses, currency.

The customer is a ThirdParty (partner without parent), addresses are Address objects (child partners).
Odoo also points the addresses to the customer itself: these are not Splash addresses, read as empty.
An empty address received points back to the customer.

Invoices have no billing address field: the Odoo partner of an invoice is the billing contact, the
customer is its commercial partner. The billing address is then written as the invoice partner, when
it is an address of the customer (else the customer is kept).
"""

from __future__ import annotations

from typing import Any, ClassVar, Final

from splashpy.fields import FieldsFactory, ObjectIds
from splashpy.objects import ObjectRequest, fields_group
from splashpy.objects.group import Phase

from ..base import OdooGroup, build_fields

CUSTOMER: Final = "partner_id"
"""Customer: a ThirdParty, also the Odoo field."""

CURRENCY: Final = "currency_id"
"""Currency, by ISO code, also the Odoo field."""

GROUP: Final = "General"
"""Fields group label (as V1)."""

TEMPLATES: Final = {
    CUSTOMER: "Splash.Templates.Accounting.Core.ThirdParty",
    "partner_invoice_id": "Splash.Templates.Accounting.Core.BillingAddress",
    "partner_shipping_id": "Splash.Templates.Accounting.Core.ShippingAddress",
    CURRENCY: "Splash.Templates.Accounting.Core.Currency",
}
"""Every party field: V1 field id => template code."""

BILLING: Final = "partner_invoice_id"
"""Billing address field id (V1)."""

PARTNERS: Final = "res.partner"
"""Odoo model of customers & addresses."""

STASH: Final = {"address": "billing_address", "customer": "billing_customer"}
"""Stash: received billing address & customer of an invoice (written as the invoice partner)."""


@fields_group("parties", priority=20, phases=(Phase.CREATE, Phase.UPDATE))
class AccountingParties(OdooGroup):
    """Customer, addresses & currency; written before the document is created (required by Odoo)."""

    addresses: ClassVar[tuple[str, ...]] = ("partner_invoice_id", "partner_shipping_id")
    """Address fields of the document."""

    currency_writable: ClassVar[bool] = False
    """Is the currency written (else read only: given by the document settings)?"""

    billing_partner: ClassVar[bool] = False
    """Is the billing address the document partner (invoices), the customer being its commercial partner?"""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare party fields."""
        templates = {name: TEMPLATES[name] for name in (CUSTOMER, *self.addresses, CURRENCY)}
        flags: dict[str, tuple[str | tuple[Any, ...], ...]] = {CUSTOMER: ("is_required",)}
        if not self.currency_writable:
            flags[CURRENCY] = ("is_read_only",)
        elif self.odoo is not None:
            # only active currencies (Odoo has no rates for the others): random ones are refused, not tested
            currencies = self.odoo.env["res.currency"].search([])
            flags[CURRENCY] = (
                ("add_choices", {currency.name: currency.full_name or currency.name for currency in currencies}),
                "is_not_tested",
            )
        if self.billing_partner:
            # an address of the customer only: random addresses of other customers are refused, not tested
            flags[BILLING] = ("is_not_tested",)
        build_fields(factory, templates, GROUP, flags=flags)

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read the customer, an address or the currency."""
        if self.billing_partner and field_id in (CUSTOMER, BILLING):
            return self.get_billing(req, field_id)
        record = req.object[field_id]
        if field_id == CURRENCY:
            return record.name or None
        if field_id == CUSTOMER:
            return ObjectIds.encode("ThirdParty", record.id) if record else None
        return ObjectIds.encode("Address", record.id) if record.parent_id else None

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write the customer, an address or the currency."""
        if field_id == CURRENCY:
            return self.set_currency(req, value)
        if self.billing_partner and field_id in (CUSTOMER, BILLING):
            return self.set_billing(req, field_id, value)
        if field_id == CUSTOMER:
            partner = self.find(req, value, [("parent_id", "=", False)])
            if partner is None:
                return False
            return self.stage(req, CUSTOMER, partner.id)
        if not ObjectIds.id(str(value or "")):
            customer = self.current(req, CUSTOMER)
            return self.stage(req, field_id, customer.id if hasattr(customer, "id") else customer or False)
        address = self.find(req, value, [("parent_id", "!=", False)])
        if address is None:
            return False
        return self.stage(req, field_id, address.id)

    def get_billing(self, req: ObjectRequest, field_id: str) -> Any:
        """Read the customer (commercial partner) or the billing address (partner, when an address) of an invoice."""
        partner = req.object[CUSTOMER]
        if field_id == CUSTOMER:
            customer = partner.commercial_partner_id or partner
            return ObjectIds.encode("ThirdParty", customer.id) if customer else None
        return ObjectIds.encode("Address", partner.id) if partner.parent_id else None

    def set_billing(self, req: ObjectRequest, field_id: str, value: Any) -> bool:
        """Write the customer or the billing address of an invoice: both are the invoice partner.

        The billing address wins when it is an address of the customer, whatever the received order.
        """
        if field_id == BILLING:
            if not ObjectIds.id(str(value or "")):
                req.stash[STASH["address"]] = False
            else:
                address = self.find(req, value, [("parent_id", "!=", False)])
                if address is None:
                    return False
                req.stash[STASH["address"]] = address.id
        else:
            customer = self.find(req, value, [("parent_id", "=", False)])
            if customer is None:
                return False
            req.stash[STASH["customer"]] = customer.id
        return self.stage_billing(req)

    def stage_billing(self, req: ObjectRequest) -> bool:
        """Stage the invoice partner: the received billing address of the customer, else the customer."""
        current = req.object[CUSTOMER] if req.object is not None else None
        customer_id = req.stash.get(STASH["customer"]) or (current.commercial_partner_id.id if current else None)
        if not customer_id:
            return True  # the customer comes next
        partner_id = customer_id
        billing = req.stash.get(STASH["address"])
        if billing is None and current and current.parent_id.id == customer_id:
            partner_id = current.id  # billing address not received: kept
        elif billing:
            address = self.context.model(PARTNERS).browse(billing)
            if address.commercial_partner_id.id == customer_id:
                partner_id = address.id
            else:
                req.logger.warning(f"{req.object_type}: {address.display_name} is not an address of the customer.")
        return self.stage(req, CUSTOMER, partner_id)

    def set_currency(self, req: ObjectRequest, value: Any) -> bool:
        """Write the currency by ISO code (when writable)."""
        if not self.currency_writable or not value:
            return True
        currency = self.context.env["res.currency"].search([("name", "=", str(value).upper())], limit=1)
        if not currency:
            req.logger.warning(f"{req.object_type}: unknown currency {value}, not changed.")
            return True
        return self.stage(req, CURRENCY, currency.id)

    def find(self, req: ObjectRequest, value: Any, domain: list[Any]) -> Any:
        """Find a received partner, of the company or shared; None (logged) when not found."""
        partner_id = str(ObjectIds.id(str(value or "")) or "")
        partner = None
        if partner_id.isdigit():
            company: list[Any] = [("company_id", "in", [self.context.company_id, False])]
            partner = self.context.model(PARTNERS).search([("id", "=", int(partner_id)), *domain, *company])
        if not partner:
            req.logger.error(f"{req.object_type}: partner {value} not found.")
            return None
        return partner
