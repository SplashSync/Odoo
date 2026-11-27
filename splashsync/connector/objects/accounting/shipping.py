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

"""Shipping address of accounting documents, inline (V1 ids ``__shipping__*``), preferably read.

Read from the shipping partner of the document (the customer when it has no shipping address).

The recipient company is the customer (read only): Odoo delivery addresses belong to the customer,
the recipient is the contact name of the address.

Odoo stores addresses as partners: received documents point to their Address objects (links), the
inline fields prefer the read direction and are only written when the mapping asks for it. Written as
a whole: the received fields complete the current shipping address (Splash only sends changed fields),
the result is a delivery address of the customer. An existing one with the same values is used, else
a new one is created. Existing partners are never changed: they may be used by other documents. The
received shipping address link always wins over the inline address.
"""

from __future__ import annotations

from typing import Any, Final

from splashpy.fields import FieldsFactory
from splashpy.objects import ObjectRequest, fields_group
from splashpy.objects.group import Phase

from ..base import OdooGroup, build_fields
from ..thirdparty.identity import decode_name
from .parties import CUSTOMER

PREFIX: Final = "__shipping__"
"""Prefix of the inline address fields (V1)."""

LINK: Final = "partner_shipping_id"
"""Odoo field of the shipping address."""

GROUP: Final = "Address"
"""Fields group label (as V1)."""

TEMPLATES: Final = {
    f"{PREFIX}name": "Splash.Templates.ThirdParty.Core.Name",
    f"{PREFIX}contact": "Splash.Templates.ThirdParty.Core.AlternateName",
    f"{PREFIX}street": "Splash.Templates.Address.PostalAddress.StreetAddress",
    f"{PREFIX}street2": "Splash.Templates.Address.PostalAddress.ExtendedAddress",
    f"{PREFIX}zip": "Splash.Templates.Address.PostalAddress.PostalCode",
    f"{PREFIX}city": "Splash.Templates.Address.PostalAddress.Locality",
    f"{PREFIX}state_id": "Splash.Templates.Address.PostalAddress.RegionCode",
    f"{PREFIX}state_name": "Splash.Templates.Address.PostalAddress.RegionName",
    f"{PREFIX}country_code": "Splash.Templates.Address.PostalAddress.CountryCode",
    f"{PREFIX}country_name": "Splash.Templates.Address.PostalAddress.CountryName",
    f"{PREFIX}phone": "Splash.Templates.ThirdParty.Core.Phone",
    f"{PREFIX}email": "Splash.Templates.ThirdParty.Core.Email",
}
"""Fields: V1 field id => template code (``email`` is new)."""

READ_ONLY: Final = (f"{PREFIX}name", f"{PREFIX}state_name", f"{PREFIX}country_name")
"""Recipient company (the customer), names of the region & country (written by their codes)."""

FIELDS: Final = frozenset(TEMPLATES)
"""Field ids of this group."""

COLUMNS: Final = ("street", "street2", "zip", "city", "phone", "email")
"""Fields copied as is on the delivery partner."""

STASH: Final = "shipping_written"
"""Stash flag: the inline address of this request is already written."""


@fields_group("shipping", priority=25, after=("parties",), phases=(Phase.CREATE, Phase.UPDATE))
class AccountingShipping(OdooGroup):
    """Inline shipping address, preferably read: recipient, postal address, phone & email."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare shipping address fields, preferably read; the company is read only, not required."""
        # templates list some of them; the link wins when both are received: random values can not match
        hidden: tuple[str | tuple[Any, ...], ...] = (("is_listed", False), "set_prefer_read")
        flags: dict[str, tuple[str | tuple[Any, ...], ...]] = dict.fromkeys(TEMPLATES, ("is_not_tested", *hidden))
        flags.update(dict.fromkeys(READ_ONLY, ("is_read_only", *hidden)))
        flags[f"{PREFIX}name"] = ("is_read_only", ("is_required", False), *hidden)
        build_fields(factory, TEMPLATES, GROUP, flags=flags)

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a field of the shipping partner (else the customer)."""
        partner = req.object[LINK] or req.object[CUSTOMER]
        name = field_id.removeprefix(PREFIX)
        if name == "name":
            return decode_name((partner.parent_id or partner).name)["legal"] or None
        if name == "contact":
            return partner.name if partner.parent_id else None
        if name == "country_code":
            return partner.country_id.code or None
        if name == "state_id":
            return partner.state_id.code or None
        if name in ("country_name", "state_name"):
            return partner[name.replace("_name", "_id")].name or None
        return partner[name] or None

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write the received address once (first inline field), as the shipping partner; the link wins."""
        if field_id in READ_ONLY or req.stash.get(STASH):
            return True
        req.stash[STASH] = True
        if req.inputs.get(LINK):
            return True
        received = {name.removeprefix(PREFIX): req.inputs[name] for name in TEMPLATES if name in req.inputs}
        customer = self.customer(req)
        if not customer:
            req.logger.warning(f"{req.object_type}: no customer, shipping address not written.")
            return True
        partner = self.find_or_create(customer, self.values(req, self.address(req, customer), received))
        return self.stage(req, LINK, partner.id)

    def address(self, req: ObjectRequest, customer: Any) -> Any:
        """Get the current shipping address of the document, when it is an address of the customer."""
        current = req.object[LINK] if req.object is not None else None
        return current if current and current.parent_id == customer.commercial_partner_id else None

    def customer(self, req: ObjectRequest) -> Any:
        """Get the customer of the document: received (staged) or current, as its commercial partner."""
        customer = self.current(req, CUSTOMER)
        if isinstance(customer, int):
            customer = self.context.model("res.partner").browse(customer).exists()
        return customer.commercial_partner_id if customer else customer

    def values(self, req: ObjectRequest, current: Any, received: dict[str, Any]) -> dict[str, Any]:
        """Odoo values of the address: received fields, else the current address ones."""
        env = self.context.env
        values: dict[str, Any] = {
            "name": current.name if current else False,
            **{column: current[column] if current else False for column in COLUMNS},
            "country_id": current.country_id.id if current else False,
            "state_id": current.state_id.id if current else False,
        }
        if "contact" in received:
            values["name"] = str(received["contact"] or "").strip() or False
        for column in COLUMNS:
            if column in received:
                values[column] = str(received[column] or "").strip() or False
        if "country_code" in received:
            code = str(received["country_code"] or "").strip()
            country = env["res.country"].search([("code", "=ilike", code)], limit=1) if code else env["res.country"]
            if code and not country:
                req.logger.warning(f"{req.object_type}: unknown country code {code}.")
            values["country_id"] = country.id or False
        if "state_id" in received:
            region = str(received["state_id"] or "").strip()
            domain: list[Any] = [("code", "=ilike", region)]
            if values["country_id"]:
                domain.append(("country_id", "=", values["country_id"]))
            state = env["res.country.state"].search(domain, limit=1) if region else env["res.country.state"]
            values["state_id"] = state.id or False
        return values

    def find_or_create(self, customer: Any, values: dict[str, Any]) -> Any:
        """Find a delivery address of the customer with these values, else create it."""
        partners = self.context.model("res.partner")
        domain: list[Any] = [("parent_id", "=", customer.id), ("type", "=", "delivery")]
        domain += [(name, "=", value) for name, value in values.items()]
        existing = partners.search(domain, limit=1)
        if existing:
            return existing
        values.update(parent_id=customer.id, type="delivery", company_id=customer.company_id.id)
        values["name"] = values["name"] or customer.name
        return partners.create(values)
