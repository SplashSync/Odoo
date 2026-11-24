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
"""Address: contacts & addresses of a partner (``res.partner`` with a parent).

Field ids are the V1 ids. Fields come from contracts templates (scope ``Address.PostalAddress``),
every other simple Odoo field is exposed by the generic group.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar, Final

from splashpy.fields import ObjectIds
from splashpy.objects import ObjectRequest

from ..base import OdooObject
from ..generic import GenericFields
from .contact import FIELDS as CONTACT_FIELDS
from .contact import AddressContact, decode_name, encode_name
from .meta import FIELDS as META_FIELDS
from .meta import AddressMeta, to_odoo_type
from .postal import FIELDS as POSTAL_FIELDS
from .postal import AddressPostal

SCOPE: Final = "Splash.Scopes.Address.PostalAddress"
"""Scope declared for Address."""

MODEL: Final = "res.partner"
"""Odoo model."""

LISTED: Final = {"complete_name": "Address"}
"""Odoo fields shown in lists (read-only), with their group."""


class AddressFields(GenericFields):
    """Generic Odoo fields of addresses."""

    owned_elsewhere = frozenset({*CONTACT_FIELDS, *POSTAL_FIELDS, *META_FIELDS})
    """Explicit fields of the object."""

    listed = LISTED
    """Odoo complete name (parent, name), shown in lists."""

    def model_name(self) -> str:
        """Odoo model."""
        return MODEL


class Address(OdooObject):
    """Odoo partner with a parent: a contact, an invoice, delivery or other address."""

    type = "Address"
    name = "Address"
    description = "Odoo Contacts & Addresses"
    icon = "fa fa-envelope-o"
    model = MODEL
    listed_fields = ("complete_name", "street", "zip", "city")
    groups: ClassVar[Any] = (AddressContact, AddressPostal, AddressMeta, AddressFields)

    def domain(self) -> list[Any]:
        """Partners with a parent, of the current company or shared."""
        return [("parent_id", "!=", False), ("company_id", "in", [self.odoo.company_id, False])]

    def search_domain(self, text: str) -> list[Any]:
        """Search by name or email."""
        return ["|", ("name", "ilike", text), ("email", "ilike", text)]

    def list_values(self, record: Any) -> dict[str, Any]:
        """Complete name, first & last names, street, postal code & city."""
        names = {key: value or None for key, value in decode_name(record.name).items()}
        return {**super().list_values(record), **names}

    def create_values(self, req: ObjectRequest) -> dict[str, Any]:
        """Name & parent (required by Odoo), type from the received one ("other" by default)."""
        parent_id = ObjectIds.id(str(req.inputs.get("parent_id") or ""))
        parent = self.records().browse(int(parent_id)).exists() if parent_id and parent_id.isdigit() else None
        if not parent:
            raise ValueError(f"Address: parent {req.inputs.get('parent_id')} not found.")
        return {
            "name": encode_name(req.inputs),
            "parent_id": parent.id,
            "type": to_odoo_type(req.inputs.get("type"), None),
        }

    def get_by_primary(self, ctx: Any, keys: Mapping[str, str]) -> str | None:
        """No primary key for addresses."""
        return None
