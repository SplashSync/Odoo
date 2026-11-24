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
"""ThirdParty postal address: street, city, region & country."""

from __future__ import annotations

from typing import Any, ClassVar, Final

from splashpy.fields import FieldsFactory
from splashpy.objects import ObjectRequest, fields_group

from ..base import OdooGroup, build_fields

TEMPLATES: Final = {
    "street": "Splash.Templates.Address.PostalAddress.StreetAddress",
    "street2": "Splash.Templates.Address.PostalAddress.PostOfficeBoxNumber",
    "zip": "Splash.Templates.Address.PostalAddress.PostalCode",
    "city": "Splash.Templates.Address.PostalAddress.Locality",
    "state_id": "Splash.Templates.Address.PostalAddress.RegionCode",
    "country_code": "Splash.Templates.Address.PostalAddress.CountryCode",
    "country_name": "Splash.Templates.Address.PostalAddress.CountryName",
}
"""Fields: V1 field id => template code."""

FIELDS: Final = frozenset(TEMPLATES)
"""Field ids of this group."""

GROUP: Final = "Address"
"""Fields group label (as V1)."""


@fields_group("address", priority=20, after=("identity",))
class ThirdPartyAddress(OdooGroup):
    """Postal address of the partner."""

    listed: ClassVar[tuple[str, ...]] = ()
    """Fields shown in objects lists."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare address fields."""
        flags: dict[str, tuple[str, ...]] = {"country_name": ("is_read_only",)}
        flags.update(dict.fromkeys(self.listed, ("is_listed",)))
        build_fields(factory, TEMPLATES, GROUP, flags=flags)

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a field; country & region by their codes."""
        partner = req.object
        if field_id == "country_code":
            return partner.country_id.code or None
        if field_id == "country_name":
            return partner.country_id.name or None
        if field_id == "state_id":
            return partner.state_id.code or None
        return partner[field_id] or None

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write a field; country & region found by their codes."""
        partner = req.object
        if field_id == "country_name":
            return True
        if field_id == "country_code":
            country = partner.env["res.country"].search([("code", "=ilike", value)], limit=1) if value else None
            if value and not country:
                req.logger.warning(f"{req.object_type}: unknown country code {value}.")
                return True
            return self.stage(req, "country_id", country.id if country else False)
        if field_id == "state_id":
            return self.set_state(req, value)
        return self.stage(req, field_id, value or False)

    def set_state(self, req: ObjectRequest, value: Any) -> bool:
        """Write the region, by code, within the (new) country."""
        if not value:
            return self.stage(req, "state_id", False)
        country_id = self.current(req, "country_id")
        country_id = country_id.id if hasattr(country_id, "id") else country_id
        domain: list[Any] = [("code", "=ilike", value)]
        if country_id:
            domain.append(("country_id", "=", country_id))
        state = req.object.env["res.country.state"].search(domain, limit=1)
        if not state:
            req.logger.warning(f"{req.object_type}: unknown region code {value}.")
            return True
        return self.stage(req, "state_id", state.id)
