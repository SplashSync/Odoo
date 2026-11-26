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
"""Product core: SKU, translated name & description, flags, identifiers, dimensions, dates."""

from __future__ import annotations

from typing import Any, Final

from odoo import fields as odoo_fields
from odoo.tools import html2plaintext, plaintext2html
from splashpy.fields import FieldsFactory
from splashpy.objects import ObjectRequest, fields_group

from ..base import OdooGroup, build_fields

TRANSLATED: Final = {
    "name": "Splash.Templates.Product.Core.Name",
    "description": "Splash.Templates.Product.Core.ShortDescription",
}
"""Translated fields (template field, one Splash field per language): V1 id => template code."""

TEMPLATES: Final = {
    "default_code": "Splash.Templates.Product.Core.ProductSku",
    "active": "Splash.Templates.Product.Flags.Active",
    "sale_ok": "Splash.Templates.Product.Flags.Offered",
    "barcode": "Splash.Templates.Product.Identifiers.Ean13",  # Odoo product barcodes are EAN-13 (GTIN-13)
    "weight": "Splash.Templates.Product.Dimensions.Weight",
    "volume": "Splash.Templates.Product.Dimensions.Volume",
    "create_date": "Splash.Templates.Common.Audit.DateCreated",
    "write_date": "Splash.Templates.Common.Audit.DateModified",
}
"""Fields: V1 field id => template code."""

AUDIT: Final = ("create_date", "write_date")
"""Read-only audit dates."""

HTML: Final = ("description",)
"""Odoo HTML fields, exchanged as plain text."""

BOOLS: Final = ("active", "sale_ok", "purchase_ok")
"""Boolean fields."""


def field_ids(languages: list[str]) -> frozenset[str]:
    """Field ids of this group, translations included."""
    translated = {f"{name}_{lang}" for name in TRANSLATED for lang in languages[1:]}
    return frozenset({*TRANSLATED, *translated, *TEMPLATES, "purchase_ok"})


@fields_group("core", priority=10)
class ProductCore(OdooGroup):
    """SKU, name & description (translated), sale & purchase flags, barcode, dimensions."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare core fields."""
        languages = self.odoo.languages() if self.odoo else ["en_US"]
        factory.set_default_language(languages[0])
        for name, template in TRANSLATED.items():
            for lang in languages:
                factory.create_from_template(name, template).set_multi_lang(lang)
                if name == "name" and lang == languages[0]:
                    factory.is_required()
        flags: dict[str, tuple[str | tuple[str, ...], ...]] = dict.fromkeys(AUDIT, ("is_read_only",))
        flags["default_code"] = ("is_required", "is_indexed")
        flags["active"] = ("is_not_tested",)
        build_fields(factory, TEMPLATES, flags=flags)
        factory.create("bool", "purchase_ok", "Can be Purchased")
        factory.micro_data("http://schema.org/Product", "ordered")

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a field; translations from the product template."""
        name, lang = self.split(field_id)
        product = req.object
        value = product.product_tmpl_id.with_context(lang=lang)[name] if lang else product[name]
        if name in HTML:
            return html2plaintext(value).strip() or None if value else None
        if name in BOOLS:
            return bool(value)
        if name in AUDIT:
            return odoo_fields.Datetime.to_string(value) if value else None
        return value or None

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write a field; translations on the product template."""
        name, lang = self.split(field_id)
        if name in AUDIT:
            return True
        if name in HTML:
            value = plaintext2html(str(value)) if value else False
        if lang:
            return self.stage_translation(req, req.object.product_tmpl_id, name, lang, value)
        if name in BOOLS:
            return self.stage(req, name, str(value) in ("1", "True", "true"))
        if name in ("weight", "volume"):
            return self.stage(req, name, float(value or 0))
        if name == "description" and req.object and self.same_html(req.object[name], value):
            return True
        return self.stage(req, name, value or False)

    @staticmethod
    def split(field_id: str) -> tuple[str, str | None]:
        """Split a translated field id: (``name``, ``fr_FR``), or (field id, None)."""
        for name in TRANSLATED:
            if field_id.startswith(f"{name}_") and len(field_id) == len(name) + 6:
                return name, field_id[len(name) + 1 :]
        return field_id, None

    @staticmethod
    def same_html(current: Any, value: Any) -> bool:
        """Compare an HTML value with a received one, as plain text."""
        return bool(html2plaintext(current or "").strip() == html2plaintext(value or "").strip())
