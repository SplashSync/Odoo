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
"""Product: Odoo product variants (``product.product``), one Splash product per variant.

Field ids are the V1 ids. Scopes: Variants Receiver (attributes & variants declared on the fly,
without generating every combination), when the "Variants" setting of Odoo is enabled, and Gallery
Receiver, when the eCommerce module is installed (extra images).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar, Final

from splashpy.core.context import RequestContext
from splashpy.objects import ObjectRequest

from ...context import OdooContext
from ..base import OdooObject
from ..generic import GenericFields
from .attributes import FIELDS as ATTRIBUTES_FIELDS
from .attributes import ProductAttributes, clean_lines
from .core import TEMPLATES as CORE_TEMPLATES
from .core import TRANSLATED, ProductCore
from .features import has_gallery, has_variants
from .gallery import FIELDS as GALLERY_FIELDS
from .gallery import ProductGallery, read_file
from .variants import FIELDS as VARIANTS_FIELDS
from .variants import ProductVariants, sibling_template

VARIANTS_SCOPE: Final = "Splash.Scopes.Product.VariantsReceiver"
"""Scope declared when the "Variants" setting is enabled."""

GALLERY_SCOPE: Final = "Splash.Scopes.Product.GalleryReceiver"
"""Scope declared when the eCommerce module is installed."""

MODEL: Final = "product.product"
"""Odoo model."""

NO_VARIANTS: Final = {"create_product_product": False}
"""Odoo context: never generate variants automatically while Splash writes."""


def scopes(odoo: OdooContext) -> list[str]:
    """Scopes declared for Product, by enabled features."""
    return [
        *([VARIANTS_SCOPE] if has_variants(odoo.env) else []),
        *([GALLERY_SCOPE] if has_gallery(odoo.env) else []),
    ]


class ProductFields(GenericFields):
    """Generic Odoo fields of product variants."""

    owned_elsewhere = frozenset(
        {*TRANSLATED, *CORE_TEMPLATES, "purchase_ok", *VARIANTS_FIELDS, *ATTRIBUTES_FIELDS, *GALLERY_FIELDS}
    )
    """Explicit fields of the object."""

    def model_name(self) -> str:
        """Odoo model."""
        return MODEL


class Product(OdooObject):
    """Odoo product variant: each variant is a Splash product, siblings share their template."""

    type = "Product"
    name = "Product"
    description = "Odoo Product (variants)"
    icon = "fa fa-product-hunt"
    model = MODEL
    listed_fields = ("default_code", "name")
    groups: ClassVar[Any] = (ProductCore, ProductVariants, ProductAttributes, ProductGallery, ProductFields)

    def records(self) -> Any:
        """Product variants, without automatic variants generation."""
        return super().records().with_context(**NO_VARIANTS)

    def domain(self) -> list[Any]:
        """Products of the current company or shared."""
        return [("company_id", "in", [self.odoo.company_id, False])]

    def search_domain(self, text: str) -> list[Any]:
        """Search by name or SKU."""
        return ["|", ("name", "ilike", text), ("default_code", "ilike", text)]

    def list_values(self, record: Any) -> dict[str, Any]:
        """SKU and name, with the name translations (listed by the name template)."""
        values = super().list_values(record)
        for lang in self.odoo.languages()[1:]:
            values[f"name_{lang}"] = record.product_tmpl_id.with_context(lang=lang).name or None
        return values

    def create_values(self, req: ObjectRequest) -> dict[str, Any]:
        """Name & type; attached to the template of a received sibling variant, if any."""
        values: dict[str, Any] = {"name": req.inputs.get("name") or req.inputs.get("default_code") or "New Product"}
        values.setdefault("type", "consu")
        template = sibling_template(self.odoo.env, req.inputs.get("variants")) if has_variants(self.odoo.env) else None
        if template and not req.inputs.get("attributes"):
            # Odoo refuses two variants with the same (empty) attributes on one template
            req.logger.warning("Product: variant received without attributes, created as a separate product.")
        elif template:
            values["product_tmpl_id"] = template.id
        return values

    def get_by_primary(self, ctx: RequestContext, keys: Mapping[str, str]) -> str | None:
        """Identify a product by SKU."""
        sku = str(keys.get("default_code") or "").strip()
        if not sku:
            return None
        records = self.records().search([*self.domain(), ("default_code", "=", sku)], limit=2)
        return str(records.id) if len(records) == 1 else None

    def read_file(self, ctx: RequestContext, path: str, md5: str) -> dict[str, Any] | None:
        """Read a gallery image for Splash."""
        return read_file(self.odoo.env, path, md5)

    def delete_record(self, record: Any) -> None:
        """Delete a variant: Odoo deletes the template with its last variant, then clean its lines."""
        template = record.product_tmpl_id
        record.with_context(create_product_product=True).unlink()
        if template.exists():
            clean_lines(template.with_context(**NO_VARIANTS))
