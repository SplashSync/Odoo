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

"""Product features: one translated field per "no variant" attribute of Odoo (V1 ids ``__feature_id__<id>``).

- Standard mode: the value is a "no variant" attribute line of the product template, shared by all its
  variants (one value per attribute).
- Advanced Variants mode (Splash setting of the company): the value belongs to the variant itself
  (``features_value_ids``), each variant has its own features.

Values are found by name or created on the fly; their translations are the value name translations.
"""

from __future__ import annotations

from typing import Any, Final

from splashpy.fields import FieldsFactory
from splashpy.objects import ObjectRequest, fields_group

from ...context import OdooContext
from ..base import OdooGroup
from .features import has_variants

PREFIX: Final = "__feature_id__"
"""Feature field id prefix (V1), followed by the Odoo attribute id."""

GROUP: Final = "Features"
"""Splash fields group."""

NO_VARIANT: Final = "no_variant"
"""Odoo attributes used as features: they never create variants."""

ADVANCED: Final = "product_advanced_variants"
"""Splash setting: features stored on the variants."""

VARIANT_VALUES: Final = "features_value_ids"
"""Variant features values (Advanced Variants mode)."""


@fields_group("features", priority=35, after=("core",))
class ProductFeatures(OdooGroup):
    """Features of the product: read & written on the template, or on the variant (Advanced Variants)."""

    @classmethod
    def available(cls, odoo: OdooContext) -> bool:
        """Only when the "Variants" setting of Odoo is enabled (attributes are hidden without it)."""
        return has_variants(odoo.env)

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare one field per feature attribute and language, with the known values as choices.

        Translations are the names of shared attribute values: written, but not tested (one product
        changes them for every product using the value).
        """
        if self.odoo is None:
            return
        languages = self.odoo.languages()
        factory.set_default_language(languages[0])
        for attribute in feature_attributes(self.odoo.env):
            field_id = encode(attribute)
            for lang in languages:
                factory.create("varchar", field_id, attribute.display_name).group(GROUP)
                factory.micro_data("http://schema.org/Product", attribute.name)
                factory.description(f"[{lang}] {attribute.display_name}")
                factory.set_multi_lang(lang)
                if lang != languages[0]:
                    factory.association(field_id).is_not_tested()
                    continue
                for value in attribute.value_ids:
                    factory.add_choice(value.name, value.name)

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a feature value (or one of its translations)."""
        attribute_id, lang = decode(field_id)
        value = self.current_value(req.object, attribute_id)
        if not value:
            return None
        return value.with_context(lang=lang).name if lang else value.name

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write a feature value; translations are staged on the value received with them."""
        attribute_id, lang = decode(field_id)
        attribute = req.object.env["product.attribute"].browse(attribute_id).exists()
        if not attribute:
            return False
        if lang:
            target = self.received_value(req, attribute)
            if target:
                return self.stage_translation(req, target, "name", lang, value)
            return True
        target = touch_value(attribute, str(value).strip()) if value not in (None, "") else None
        current = self.current_value(req.object, attribute_id)
        if (target.id if target else None) != (current.id if current else None):
            self.write_value(req.object, attribute, target)
            req.need_update()
        return True

    # ====================================================================#
    # Storage
    # ====================================================================#

    def is_advanced(self) -> bool:
        """Tell if features are stored on the variants (Advanced Variants setting of the company)."""
        return bool(self.odoo and self.odoo.setting(ADVANCED))

    def current_value(self, product: Any, attribute_id: int) -> Any:
        """Get the current value of a feature (``product.attribute.value``), or None."""
        if self.is_advanced():
            values = product[VARIANT_VALUES].filtered(lambda v: v.attribute_id.id == attribute_id)
        else:
            line = template_line(product.product_tmpl_id, attribute_id)
            values = line.value_ids if line else None
        return values[:1] if values else None

    def received_value(self, req: ObjectRequest, attribute: Any) -> Any:
        """Get the value a translation belongs to: the one received in the same request, else the current one."""
        field_id = encode(attribute)
        if field_id in req.inputs:
            received = req.inputs.get(field_id)
            return touch_value(attribute, str(received).strip()) if received not in (None, "") else None
        return self.current_value(req.object, attribute.id)

    def write_value(self, product: Any, attribute: Any, value: Any) -> None:
        """Replace the value of a feature (None: remove it)."""
        if self.is_advanced():
            others = product[VARIANT_VALUES].filtered(lambda v: v.attribute_id != attribute)
            product.write({VARIANT_VALUES: [(6, 0, (others | value).ids if value else others.ids)]})
            return
        template = product.product_tmpl_id
        line = template_line(template, attribute.id)
        if line and not value:
            template.write({"attribute_line_ids": [(2, line.id)]})
        elif line:
            line.write({"value_ids": [(6, 0, value.ids)]})
        elif value:
            template.write(
                {"attribute_line_ids": [(0, 0, {"attribute_id": attribute.id, "value_ids": [(6, 0, value.ids)]})]}
            )


# ====================================================================#
# Helpers
# ====================================================================#


def feature_attributes(env: Any) -> Any:
    """Odoo attributes used as features ("no variant"), by id."""
    return env["product.attribute"].search([("create_variant", "=", NO_VARIANT)], order="id")


def encode(attribute: Any) -> str:
    """Field id of a feature attribute."""
    return f"{PREFIX}{attribute.id}"


def decode(field_id: str) -> tuple[int, str | None]:
    """Attribute id & language of a feature field id (``__feature_id__12`` or ``__feature_id__12_fr_FR``)."""
    body = field_id.removeprefix(PREFIX)
    number, _sep, lang = body.partition("_")
    return int(number), lang or None


def is_feature(field_id: str) -> bool:
    """Tell if a field id is a feature field."""
    return field_id.startswith(PREFIX) and field_id.removeprefix(PREFIX).partition("_")[0].isdigit()


def template_line(template: Any, attribute_id: int) -> Any:
    """Get the "no variant" attribute line of a template for an attribute, or None."""
    lines = template.attribute_line_ids.filtered(lambda line: line.attribute_id.id == attribute_id)
    return lines[:1] or None


def touch_value(attribute: Any, name: str) -> Any:
    """Find (by name, case insensitive) or create a value of an attribute."""
    value = attribute.value_ids.filtered(lambda v: v.name.lower() == name.lower())[:1]
    return value or attribute.env["product.attribute.value"].create({"name": name, "attribute_id": attribute.id})
