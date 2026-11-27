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

"""Order status (V1 ids): Splash status from the Odoo state, Odoo actions from a received status.

Odoo 20 states: quotation (draft), quotation sent, sales order, cancelled; a locked sales order is a
delivered (closed) order. Written after the lines and payments: a confirmed order is processed with
its received lines. A delivered order gets its deliveries validated, then is locked.
An empty status is never taken into account.
"""

from __future__ import annotations

from typing import Any, Final

from splashpy.fields import FieldsFactory, FieldType
from splashpy.objects import ObjectRequest, fields_group

from ..base import OdooGroup, build_fields

GROUP: Final = "Status"
"""Fields group label."""

STATUS: Final = "state"
"""Status field (V1), also the Odoo field."""


class Status:
    """Splash order statuses (Php-Core order status dictionary)."""

    DRAFT: Final = "OrderDraft"
    PAYMENT_DUE: Final = "OrderPaymentDue"
    PROCESSING: Final = "OrderProcessing"
    PROCESSED: Final = "OrderProcessed"
    OUT_OF_STOCK: Final = "OrderOutOfStock"
    TO_SHIP: Final = "OrderToShip"
    IN_TRANSIT: Final = "OrderInTransit"
    PICKUP: Final = "OrderPickupAvailable"
    DELIVERED: Final = "OrderDelivered"
    RETURNED: Final = "OrderReturned"
    PROBLEM: Final = "OrderProblem"
    CANCELED: Final = "OrderCanceled"


class State:
    """Odoo sales order states."""

    DRAFT: Final = "draft"
    SENT: Final = "sent"
    SALE: Final = "sale"
    CANCEL: Final = "cancel"


CHOICES: Final = {
    Status.DRAFT: "Quotation",
    Status.PAYMENT_DUE: "Quotation Sent",
    Status.PROCESSING: "Sales Order",
    Status.DELIVERED: "Locked",
    Status.CANCELED: "Cancelled",
}
"""Statuses sent by Odoo (choices)."""

TARGETS: Final = {
    Status.DRAFT: State.DRAFT,
    Status.PAYMENT_DUE: State.SENT,
    Status.PROCESSING: State.SALE,
    Status.PROCESSED: State.SALE,
    Status.OUT_OF_STOCK: State.SALE,
    Status.TO_SHIP: State.SALE,
    Status.CANCELED: State.CANCEL,
}
"""Received status => Odoo state (unlocked)."""

CLOSED: Final = frozenset({Status.DELIVERED, Status.IN_TRANSIT, Status.PICKUP, Status.RETURNED, Status.PROBLEM})
"""Received statuses of a delivered order: a locked sales order."""

TEMPLATES: Final = {
    STATUS: "Splash.Templates.Order.Status.Status",
    "isCanceled": "Splash.Templates.Order.Status.IsCanceled",
    "isValidated": "Splash.Templates.Order.Status.IsValidated",
    "isClosed": "Splash.Templates.Order.Status.IsClosed",
}
"""Fields: V1 field id => template code."""

PROCESSING: Final = "isProcessing"
"""Processing flag (V1, no template)."""

FIELDS: Final = frozenset({*TEMPLATES, PROCESSING})
"""Field ids of this group."""

QUIET: Final = {"disable_cancel_warning": True, "skip_backorder": True, "skip_sms": True, "skip_immediate": True}
"""Odoo context: no wizard while Splash changes a status."""


@fields_group("status", priority=95, after=("lines", "payments"))
class OrderStatus(OdooGroup):
    """Status & status flags; written after the lines and payments."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare status fields: the status (not tested: changes the order), read-only flags."""
        flags: dict[str, tuple[str | tuple[Any, ...], ...]] = dict.fromkeys(TEMPLATES, ("is_read_only",))
        flags[STATUS] = (("add_choices", CHOICES), "is_not_tested")
        build_fields(factory, TEMPLATES, GROUP, flags=flags)
        factory.create(FieldType.BOOL, PROCESSING, "Is Processing").group(GROUP)
        factory.micro_data("http://schema.org/OrderStatus", "OrderProcessing").is_read_only()

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read the status or a status flag."""
        order = req.object
        if field_id == STATUS:
            return status(order)
        if field_id == "isCanceled":
            return order.state == State.CANCEL
        if field_id == "isValidated":
            return order.state in (State.SENT, State.SALE)
        if field_id == PROCESSING:
            return order.state == State.SALE and not order.locked
        return order.state == State.SALE and bool(order.locked)

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Change the order status (flags are read only)."""
        if field_id != STATUS:
            return True
        received = str(value or "").strip()
        if not received or received == status(req.object):
            return True
        if received not in TARGETS and received not in CLOSED:
            req.logger.warning(f"Order: unknown status {received}, not changed.")
            return True
        order = req.object.with_context(**QUIET)
        try:
            with order.env.cr.savepoint():
                if received in CLOSED:
                    deliver(order)
                else:
                    change(order, TARGETS[received])
        except Exception as error:  # noqa: BLE001 - any Odoo refusal of the status change
            req.logger.error(f"Order: unable to change status to {received}: {error}")
            return False
        req.need_update()
        return True


def status(order: Any) -> str | None:
    """Splash status of an order."""
    if order.state == State.SALE:
        return Status.DELIVERED if order.locked else Status.PROCESSING
    return {
        State.DRAFT: Status.DRAFT,
        State.SENT: Status.PAYMENT_DUE,
        State.CANCEL: Status.CANCELED,
    }.get(order.state)


def change(order: Any, state: str) -> None:
    """Move an order to an Odoo state (unlocked)."""
    if order.locked:
        order.action_unlock()
    if state == State.CANCEL:
        order.action_cancel()
    elif state == State.DRAFT:
        if order.state == State.SALE:
            order.action_cancel()
        order.action_draft()
    elif state == State.SENT:
        if order.state != State.DRAFT:
            change(order, State.DRAFT)
        order.action_quotation_sent()
    elif order.state != State.SALE:
        order.action_confirm()


def deliver(order: Any) -> None:
    """Deliver an order: confirmed, deliveries validated, locked."""
    change(order, State.SALE)
    for picking in order.picking_ids.filtered(lambda picking: picking.state not in ("done", "cancel")):
        validate(picking)
    order.action_lock()


def validate(picking: Any) -> None:
    """Validate a delivery with its ordered quantities."""
    picking.action_confirm()
    picking.action_assign()
    for move in picking.move_ids.filtered(lambda move: move.state not in ("done", "cancel")):
        move.quantity = max(move.quantity, move.product_uom_qty)
        move.picked = True
    picking.button_validate()
