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

from .address import SCOPE as ADDRESS_SCOPE
from .address import Address
from .product import SCOPES as PRODUCT_SCOPES
from .product import Product
from .thirdparty import SCOPE as THIRDPARTY_SCOPE
from .thirdparty import ThirdParty

OBJECTS: Final = (ThirdParty, Address, Product)
"""Objects of the connector."""

SCOPES: Final = (THIRDPARTY_SCOPE, ADDRESS_SCOPE, *PRODUCT_SCOPES)
"""Scopes declared to Splash (contracts catalog)."""
