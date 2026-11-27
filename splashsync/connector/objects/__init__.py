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
"""Splash objects exposed by the connector, and the scopes they declare."""

from __future__ import annotations

from typing import Final

from ..context import OdooContext
from .address import SCOPE as ADDRESS_SCOPE
from .address import Address
from .invoice import SCOPES as INVOICE_SCOPES
from .invoice import Invoice
from .order import SCOPES as ORDER_SCOPES
from .order import Order
from .product import Product
from .product import scopes as product_scopes
from .thirdparty import SCOPE as THIRDPARTY_SCOPE
from .thirdparty import ThirdParty

OBJECTS: Final = (ThirdParty, Address, Product, Order, Invoice)
"""Objects of the connector."""


def scopes(odoo: OdooContext) -> list[str]:
    """Scopes declared to Splash (contracts catalog), by features enabled in the database."""
    return [THIRDPARTY_SCOPE, ADDRESS_SCOPE, *product_scopes(odoo), *dict.fromkeys((*ORDER_SCOPES, *INVOICE_SCOPES))]
