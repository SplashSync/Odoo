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
"""Product attributes: the variant attributes values, declared on the fly.

Odoo would create every combination of the template attribute lines; Splash creates one variant
at a time. Splash writes run with ``create_product_product=False`` (no automatic variant): values
are added to the template lines, then assigned to the variant, and the lines are cleaned from
values no active variant uses anymore. No-variant attributes are not exposed here.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from splashpy.fields import FieldsFactory
from splashpy.objects import ObjectRequest, fields_group

from ..base import OdooGroup

LIST: Final = "attributes"
"""Attributes list name."""

CODE: Final = "Splash.Templates.Product.Variants.AttributeCode"
"""Attribute code (Odoo attribute name)."""

NAME: Final = "Splash.Templates.Product.Variants.AttributeName"
"""Attribute name (read-only, Odoo attribute display name)."""

VALUE: Final = "Splash.Templates.Product.Variants.AttributeValue"
"""Attribute value (translated Odoo attribute value name)."""

LANGUAGE: Final = "language"
"""Field option: language of a translated field."""

NO_VARIANT: Final = "no_variant"
"""Odoo attributes that never create variants."""

FIELDS: Final = frozenset({LIST})
"""Lists of this group."""


@fields_group("attributes", priority=30, after=("core", "variants"))
class ProductAttributes(OdooGroup):
    """Variant attributes: code, name and translated value of each attribute of the variant."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare attributes fields (not tested here: the Variants Receiver scope tests them)."""
        languages = self.odoo.languages() if self.odoo else ["en_US"]
        factory.set_default_language(languages[0])
        factory.create_from_template(f"code@{LIST}", CODE).group("Attributes").is_not_tested()
        factory.create_from_template(f"name@{LIST}", NAME).group("Attributes").is_read_only()
        for lang in languages:
            # translated list columns: "value_fr_FR@attributes" (V1 & Php-Core ids)
            field_id = f"value@{LIST}" if lang == languages[0] else f"value_{lang}@{LIST}"
            factory.create_from_template(field_id, VALUE).group("Attributes").is_not_tested()
            factory.add_option(LANGUAGE, lang)
            if lang != languages[0]:
                factory.micro_data(f"http://schema.org/Product/{lang}", "VariantAttributeValue")

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read one column of the attributes list."""
        column = field_id.split("@", 1)[0]
        values = []
        for ptav in variant_values(req.object):
            if column == "code":
                values.append(ptav.attribute_id.name)
            elif column == "name":
                values.append(ptav.attribute_id.display_name)
            elif column == "value":
                values.append(ptav.product_attribute_value_id.name)
            else:
                lang = column.removeprefix("value_")
                values.append(ptav.product_attribute_value_id.with_context(lang=lang).name)
        return values

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write the attributes of the variant (the whole list)."""
        product = req.object
        rows = [row for row in (value or []) if isinstance(row, Mapping) and row.get("code") and row.get("value")]
        ptavs = product.env["product.template.attribute.value"]
        for row in rows:
            attribute_value = self.touch_value(product.env, str(row["code"]), str(row["value"]), row)
            ptavs |= self.touch_template_value(product.product_tmpl_id, attribute_value)
        kept = product.product_template_attribute_value_ids.filtered(
            lambda v: v.attribute_id.create_variant == NO_VARIANT
        )
        if set((ptavs | kept).ids) != set(product.product_template_attribute_value_ids.ids):
            product.write({"product_template_attribute_value_ids": [(6, 0, (ptavs | kept).ids)]})
            req.need_update()
        clean_lines(product.product_tmpl_id)
        return True

    # ====================================================================#
    # Attributes & values
    # ====================================================================#

    @staticmethod
    def touch_value(env: Any, code: str, name: str, row: Mapping[str, Any]) -> Any:
        """Find or create an attribute (by name) and its value (by name), with value translations."""
        attributes = env["product.attribute"]
        attribute = attributes.search([("name", "=ilike", code), ("create_variant", "!=", NO_VARIANT)], limit=1)
        if not attribute:
            attribute = attributes.create({"name": code, "display_type": "select", "create_variant": "always"})
        value = attribute.value_ids.filtered(lambda v: v.name.lower() == name.lower())[:1]
        if not value:
            value = env["product.attribute.value"].create({"name": name, "attribute_id": attribute.id})
        translations = {
            key.removeprefix("value_"): str(text) for key, text in row.items() if key.startswith("value_") and text
        }
        if translations:
            value.update_field_translations("name", translations)
        return value

    @staticmethod
    def touch_template_value(template: Any, value: Any) -> Any:
        """Add a value to the template line of its attribute (no variant created), get its PTAV."""
        line = template.attribute_line_ids.filtered(lambda line: line.attribute_id == value.attribute_id)[:1]
        if not line:
            template.write(
                {
                    "attribute_line_ids": [
                        (0, 0, {"attribute_id": value.attribute_id.id, "value_ids": [(6, 0, value.ids)]})
                    ]
                }
            )
            line = template.attribute_line_ids.filtered(lambda line: line.attribute_id == value.attribute_id)[:1]
        elif value not in line.value_ids:
            line.write({"value_ids": [(4, value.id)]})
        return line.product_template_value_ids.filtered(lambda v: v.product_attribute_value_id == value)[:1]


def variant_values(product: Any) -> Any:
    """Attribute values of a variant (variant attributes only), by attribute sequence."""
    values = product.product_template_attribute_value_ids.filtered(
        lambda v: v.attribute_id.create_variant != NO_VARIANT
    )
    return values.sorted(lambda v: (v.attribute_id.sequence, v.attribute_id.id))


def clean_lines(template: Any) -> None:
    """Keep on the template lines only the values used by its variants (no variant created).

    Variants are searched in database (archived ones included): the cached variants of the template
    may miss a variant created in the same request, and Odoo deletes the variants of removed values.
    """
    template.env.flush_all()
    variants = (
        template.env["product.product"].with_context(active_test=False).search([("product_tmpl_id", "=", template.id)])
    )
    used = variants.product_template_attribute_value_ids.product_attribute_value_id
    commands: list[tuple[Any, ...]] = []
    for line in template.attribute_line_ids.filtered(lambda line: line.attribute_id.create_variant != NO_VARIANT):
        values = line.value_ids & used
        if not values:
            commands.append((2, line.id))
        elif values != line.value_ids:
            commands.append((1, line.id, {"value_ids": [(6, 0, values.ids)]}))
    if commands:
        template.write({"attribute_line_ids": commands})
