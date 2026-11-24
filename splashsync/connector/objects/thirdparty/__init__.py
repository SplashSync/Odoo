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
"""ThirdParty: companies and persons (``res.partner`` without parent).

Field ids are the V1 ids. Fields come from contracts templates (scope ``ThirdParty.Provider``),
every other simple Odoo field is exposed by the generic group.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar, Final

from splashpy.objects import ObjectRequest

from ..base import OdooObject
from ..generic import GenericFields
from .address import FIELDS as ADDRESS_FIELDS
from .address import ThirdPartyAddress
from .identity import FIELDS as IDENTITY_FIELDS
from .identity import ThirdPartyIdentity, decode_name, encode_name
from .meta import FIELDS as META_FIELDS
from .meta import ThirdPartyMeta

SCOPE: Final = "Splash.Scopes.ThirdParty.Provider"
"""Scope declared for ThirdParty."""

MODEL: Final = "res.partner"
"""Odoo model."""


class ThirdPartyFields(GenericFields):
    """Generic Odoo fields of partners."""

    owned_elsewhere = frozenset({*IDENTITY_FIELDS, *ADDRESS_FIELDS, *META_FIELDS})
    """Explicit fields; ``customer_rank`` / ``supplier_rank`` stay exposed as generic fields too."""

    def model_name(self) -> str:
        """Odoo model."""
        return MODEL


class ThirdParty(OdooObject):
    """Odoo partner without parent: a customer, a supplier, a company or a person."""

    type = "ThirdParty"
    name = "ThirdParty"
    description = "Odoo Partner (companies & persons)"
    icon = "fa fa-user"
    model = MODEL
    listed_fields = ("name", "email")
    groups: ClassVar[Any] = (ThirdPartyIdentity, ThirdPartyAddress, ThirdPartyMeta, ThirdPartyFields)
    enable_push_deleted = False

    def domain(self) -> list[Any]:
        """Partners without parent, of the current company or shared."""
        return [("parent_id", "=", False), ("company_id", "in", [self.odoo.company_id, False])]

    def search_domain(self, text: str) -> list[Any]:
        """Search by name or email."""
        return ["|", ("name", "ilike", text), ("email", "ilike", text)]

    def list_values(self, record: Any) -> dict[str, Any]:
        """Odoo name and email, plus the legal name (listed by its template)."""
        return {**super().list_values(record), "legal": decode_name(record.name)["legal"] or None}

    def get_by_primary(self, ctx: Any, keys: Mapping[str, str]) -> str | None:
        """Identify a partner by email (primary key of the ThirdParty scope)."""
        email = str(keys.get("email") or "").strip()
        if not email:
            return None
        records = self.records().search([*self.domain(), ("email", "=ilike", email)], limit=2)
        return str(records.id) if len(records) == 1 else None

    def create_values(self, req: ObjectRequest) -> dict[str, Any]:
        """Name (required by Odoo) from the received names; a company unless told otherwise."""
        values: dict[str, Any] = {"name": encode_name(req.inputs, req)}
        if "is_company" not in req.inputs and "company_type" not in req.inputs:
            values["is_company"] = True
        return values
