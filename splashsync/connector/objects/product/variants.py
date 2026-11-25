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
"""Product variants: parent template and variants list.

The variants list read is every variant of the parent template, the current one included (Splash
variants contract). It is only written on creation: a received sibling attaches the new variant to
the same Odoo product template (see ``Product.create_values()``).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from splashpy.fields import FieldsFactory, ObjectIds
from splashpy.objects import ObjectRequest, fields_group

from ...context import OdooContext
from ..base import OdooGroup, build_fields
from .features import has_variants

LIST: Final = "variants"
"""Variants list name."""

TEMPLATES: Final = {
    "variant_template": "Splash.Templates.Product.Variants.ParentProduct",
    f"id@{LIST}": "Splash.Templates.Product.Variants.VariantList",
    f"sku@{LIST}": "Splash.Templates.Product.Variants.VariantSku",
}
"""Fields: V1 field id => template code."""

FIELDS: Final = frozenset({"variant_template", LIST})
"""Field ids & lists of this group."""


@fields_group("variants", priority=20, after=("core",))
class ProductVariants(OdooGroup):
    """Parent template (read-only) and all the variants of the same template."""

    @classmethod
    def available(cls, odoo: OdooContext) -> bool:
        """Only when the "Variants" setting of Odoo is enabled."""
        return has_variants(odoo.env)

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare variants fields (the list is not tested: it is only used on creation)."""
        flags: dict[str, tuple[str | tuple[str, ...], ...]] = {
            "variant_template": ("is_read_only",),
            f"id@{LIST}": ("is_not_tested",),
            f"sku@{LIST}": ("is_read_only",),
        }
        build_fields(factory, TEMPLATES, "Variants", flags=flags)

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read the parent template id, or the variants of the template (the current one included)."""
        product = req.object
        if field_id == "variant_template":
            return str(product.product_tmpl_id.id)
        variants = product.product_tmpl_id.product_variant_ids.sorted("id")
        if field_id == f"id@{LIST}":
            return [ObjectIds.encode("Product", variant.id) for variant in variants]
        return [variant.default_code or None for variant in variants]

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Ignore the received variants (used on creation only)."""
        return True


def sibling_template(env: Any, variants: Any) -> Any:
    """Product template of the first existing variant of a received variants list, or None."""
    items = variants.values() if isinstance(variants, Mapping) else (variants or [])
    for item in items:
        object_id = ObjectIds.id(str(item.get("id") or "")) if isinstance(item, Mapping) else None
        if object_id and object_id.isdigit():
            variant = env["product.product"].browse(int(object_id)).exists()
            if variant:
                return variant.product_tmpl_id
    return None
