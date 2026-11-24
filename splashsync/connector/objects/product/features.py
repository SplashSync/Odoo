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

"""Product features enabled in the Odoo database: variants setting, eCommerce gallery.

- Variants: the "Variants" setting of Odoo (``product.group_product_variant`` implied for every
  internal user). Odoo itself only hides the variants screens when it is off; the connector
  follows it: no attributes, no variants fields, no Variants Receiver scope.
- Gallery: the extra images (``product.image``) only exist with the eCommerce module
  (``website_sale``). Without it, a product only has its main images.
"""

from __future__ import annotations

from typing import Any, Final

VARIANTS_GROUP: Final = "product.group_product_variant"
"""Odoo group of the "Variants" setting."""

USERS_GROUP: Final = "base.group_user"
"""Odoo group of internal users (implies the settings groups)."""

GALLERY_MODEL: Final = "product.image"
"""Odoo model of the extra product images (eCommerce module)."""


def has_variants(env: Any) -> bool:
    """Tell if the "Variants" setting is enabled."""
    group = env.ref(VARIANTS_GROUP, raise_if_not_found=False)
    users = env.ref(USERS_GROUP, raise_if_not_found=False)
    return bool(group and users and group in users.sudo().all_implied_ids)


def has_gallery(env: Any) -> bool:
    """Tell if extra product images are available (eCommerce module installed)."""
    return GALLERY_MODEL in env
