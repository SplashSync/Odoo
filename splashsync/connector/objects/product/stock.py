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

"""Product stock (V1 ids): quantity on hand (written), forecast & free quantities, free quantity per warehouse.

Quantities are the ones of the company warehouses. The quantity on hand is written as an inventory
adjustment on the stock location of the first warehouse of the company, only for products tracked
in stock (``is_storable``, true for products created by Splash, as in V1).
"""

from __future__ import annotations

from typing import Any, Final

from splashpy.fields import FieldsFactory, FieldType
from splashpy.objects import ObjectRequest, fields_group

from ...context import OdooContext
from ..base import OdooGroup

GROUP: Final = "Stocks"
"""Splash fields group."""

ON_HAND: Final = "qty_available"
"""Quantity on hand (written)."""

STORABLE: Final = "is_storable"
"""Product tracked in stock."""

READ_ONLY: Final = {
    "virtual_available": ("Forecast Quantity", "Splash.Templates.Product.Stock.ForecastLevel"),
    "free_qty": ("Free Quantity", None),
}
"""Read-only quantities: Odoo field => (label, template code)."""

WAREHOUSE: Final = "free_qty_wh_"
"""Free quantity per warehouse field id prefix, followed by the warehouse id."""

MAX_WAREHOUSES: Final = 50
"""Maximum warehouses exposed."""

PRECISION: Final = 0.001
"""Quantities compare precision."""

FIELDS: Final = frozenset({ON_HAND, STORABLE, *READ_ONLY})
"""Field ids of this group (warehouses fields apart)."""


@fields_group("stock", priority=50, after=("core",))
class ProductStock(OdooGroup):
    """Stock levels of the product, in the company warehouses."""

    @classmethod
    def available(cls, odoo: OdooContext) -> bool:
        """Only with the Inventory module."""
        return "stock.quant" in odoo.env

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare stock fields."""
        factory.create_from_template(ON_HAND, "Splash.Templates.Product.Stock.StockLevel").group(GROUP)
        factory.name("Quantity On Hand").description("Current quantity of products.")
        factory.create(FieldType.BOOL, STORABLE, "Track Inventory").group(GROUP).is_not_tested()
        factory.micro_data("http://schema.org/Product", "isStorable")
        for field_id, (label, template) in READ_ONLY.items():
            if template:
                factory.create_from_template(field_id, template).name(label)
            else:
                factory.create(FieldType.INT, field_id, label).micro_data("http://schema.org/Offer", "availableLevel")
            factory.group(GROUP).is_read_only()
        for warehouse in self.warehouses():
            factory.create(FieldType.INT, f"{WAREHOUSE}{warehouse.id}", f"Free Qty On {warehouse.code}")
            factory.description(f"Free quantity of product on Warehouse {warehouse.name}")
            factory.micro_data("http://schema.org/Offer", f"inventoryLevel{warehouse.code}")
            factory.group(GROUP).is_read_only()

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a stock level, or the stock tracking flag."""
        product = req.object
        if field_id == STORABLE:
            return bool(product.is_storable)
        if field_id.startswith(WAREHOUSE):
            warehouse = field_id.removeprefix(WAREHOUSE)
            product = product.with_context(warehouse_id=int(warehouse)) if warehouse.isdigit() else None
            return int(product.free_qty) if product else 0
        return int(product[field_id])

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write the stock tracking flag, or adjust the quantity on hand."""
        if field_id == STORABLE:
            return self.stage(req, STORABLE, str(value) in ("1", "True", "true"))
        if field_id != ON_HAND:
            return True
        product = req.object
        quantity = max(float(value or 0), 0.0)
        delta = quantity - float(product.qty_available)
        if abs(delta) < PRECISION:
            return True
        if not product.is_storable and self.current(req, STORABLE):
            # tracking received in the same request: needed before the adjustment
            product.write({STORABLE: True})
        if not product.is_storable:
            req.logger.warning("Product: stock is only adjusted for products tracked in stock.")
            return True
        location = self.location()
        if not location:
            req.logger.warning("Product: no warehouse in the company, stock not adjusted.")
            return True
        adjust(product, location, delta)
        req.need_update()
        return True

    # ====================================================================#
    # Warehouses
    # ====================================================================#

    def warehouses(self) -> Any:
        """Warehouses of the company."""
        if self.odoo is None:
            return []
        return self.odoo.model("stock.warehouse").search(
            [("company_id", "=", self.odoo.company_id)], order="sequence, id", limit=MAX_WAREHOUSES
        )

    def location(self) -> Any:
        """Stock location written by inventory adjustments: the one of the first warehouse."""
        return self.warehouses()[:1].lot_stock_id


def adjust(product: Any, location: Any, delta: float) -> None:
    """Change the quantity of a product on a location by an inventory adjustment."""
    quants = product.env["stock.quant"].with_context(inventory_mode=True)
    on_location = sum(
        quants.search([("product_id", "=", product.id), ("location_id", "=", location.id)]).mapped("quantity")
    )
    quant = quants.create(
        {"product_id": product.id, "location_id": location.id, "inventory_quantity": on_location + delta}
    )
    quant.action_apply_inventory()
