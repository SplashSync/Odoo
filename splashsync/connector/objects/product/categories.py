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

"""Product category (V1 ids): its id (read-only) and its name, written by name or full path.

The category belongs to the product template: shared by its variants. Unknown names are refused
(categories are never created by Splash): a product always has a category in Odoo.
"""

from __future__ import annotations

from typing import Any, Final

from splashpy.fields import FieldsFactory, FieldType
from splashpy.objects import ObjectRequest, fields_group

from ..base import OdooGroup

GROUP: Final = "Relations"
"""Splash fields group."""

ID: Final = "categ_id"
"""Category id (read-only), also the Odoo field."""

NAME: Final = "categ"
"""Category name."""

MODEL: Final = "product.category"
"""Odoo model of categories."""

FIELDS: Final = frozenset({ID, NAME})
"""Field ids of this group."""


@fields_group("categories", priority=45, after=("core",))
class ProductCategories(OdooGroup):
    """Product category: id & name, the known categories as choices."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare category fields."""
        factory.create(FieldType.VARCHAR, ID, "Category Id").group(GROUP).is_read_only()
        factory.micro_data("http://schema.org/Product", "classificationId")
        factory.create(FieldType.VARCHAR, NAME, "Category").group(GROUP)
        factory.micro_data("http://schema.org/Product", "classification")
        if self.odoo is not None:
            for category in self.odoo.model(MODEL).search([], order="parent_path"):
                factory.add_choice(category.name, category.complete_name)

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read the category id or name."""
        category = req.object.categ_id
        if not category:
            return None
        return str(category.id) if field_id == ID else category.name

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write the category by name (or full path); unknown names are refused."""
        if field_id == ID:
            return True
        name = str(value or "").strip()
        if not name:
            return True
        # full path is not stored: matched among the categories of that name (last part of the path)
        candidates = req.object.env[MODEL].search([("name", "=ilike", name.rpartition("/")[2].strip())])
        candidates = candidates.sorted("parent_path")
        category = candidates.filtered(lambda c: c.complete_name.lower() == name.lower())[:1] or candidates[:1]
        if not category:
            req.logger.warning(f"Product: unknown category '{name}', not changed.")
            return True
        return self.stage(req, ID, category.id)
