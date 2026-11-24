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
"""Address postal address: same fields as ThirdParty, not written on contacts (synced from parent)."""

from __future__ import annotations

from typing import Any

from splashpy.objects import ObjectRequest, fields_group

from ..thirdparty.address import FIELDS, ThirdPartyAddress

__all__ = ["FIELDS", "AddressPostal"]


@fields_group("address", priority=20, after=("contact",))
class AddressPostal(ThirdPartyAddress):
    """Postal address; Odoo copies the parent address on contacts (type ``contact``)."""

    listed = ("street", "zip", "city")
    """Street, postal code & city shown in lists."""

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write a field, unless the address is a contact (its address comes from the parent)."""
        if req.object.type == "contact" and field_id != "country_name":
            req.logger.warning(f"Address: {field_id} not written, contacts use their parent address.")
            return True
        return super().set(req, field_id, value)
