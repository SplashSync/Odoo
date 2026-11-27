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

"""Invoice status (V1 ids): Splash payment status from the Odoo state & payment state, Odoo actions from a status.

Odoo states: draft, posted, cancelled; a posted invoice is paid when its payment state says so.
Written after the lines, before the payments (payments are only registered on posted invoices).
An empty status is never taken into account.
"""

from __future__ import annotations

from typing import Any, Final

from splashpy.fields import FieldsFactory
from splashpy.objects import ObjectRequest, fields_group

from ..base import OdooGroup, build_fields

STATUS: Final = "state"
"""Status field (V1), also the Odoo field."""

GROUP: Final = "Status"
"""Fields group label."""


class Status:
    """Splash invoice statuses (Php-Core invoice status dictionary)."""

    DRAFT: Final = "PaymentDraft"
    DUE: Final = "PaymentDue"
    COMPLETE: Final = "PaymentComplete"
    CANCELED: Final = "PaymentCanceled"


class State:
    """Odoo invoice states."""

    DRAFT: Final = "draft"
    POSTED: Final = "posted"
    CANCEL: Final = "cancel"


PAID: Final = ("paid", "in_payment")
"""Odoo payment states of a paid invoice."""

CHOICES: Final = {
    Status.DRAFT: "Draft",
    Status.DUE: "Posted",
    Status.COMPLETE: "Paid",
    Status.CANCELED: "Cancelled",
}
"""Statuses sent by Odoo (choices)."""

TARGETS: Final = {
    Status.DRAFT: State.DRAFT,
    Status.DUE: State.POSTED,
    Status.COMPLETE: State.POSTED,
    Status.CANCELED: State.CANCEL,
}
"""Received status => Odoo state (paid by its payments)."""

TEMPLATES: Final = {
    STATUS: "Splash.Templates.Invoice.Status.Status",
    "isDraft": "Splash.Templates.Invoice.Status.IsDraft",
    "isCanceled": "Splash.Templates.Invoice.Status.IsCanceled",
    "isValidated": "Splash.Templates.Invoice.Status.IsValidated",
    "isPaid": "Splash.Templates.Invoice.Status.IsPaid",
}
"""Fields: V1 field id => template code."""

FIELDS: Final = frozenset(TEMPLATES)
"""Field ids of this group."""


@fields_group("status", priority=70, after=("lines",))
class InvoiceStatus(OdooGroup):
    """Status & status flags; written after the lines."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare status fields: the status (not tested: posts the invoice), read-only flags."""
        flags: dict[str, tuple[str | tuple[Any, ...], ...]] = dict.fromkeys(TEMPLATES, ("is_read_only",))
        flags[STATUS] = (("add_choices", CHOICES), "is_not_tested")
        build_fields(factory, TEMPLATES, GROUP, flags=flags)

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read the status or a status flag."""
        invoice = req.object
        if field_id == STATUS:
            return status(invoice)
        if field_id == "isDraft":
            return invoice.state == State.DRAFT
        if field_id == "isCanceled":
            return invoice.state == State.CANCEL
        if field_id == "isValidated":
            return invoice.state == State.POSTED
        return is_paid(invoice)

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Change the invoice state (flags are read only)."""
        if field_id != STATUS:
            return True
        received = str(value or "").strip()
        if not received or received not in TARGETS:
            if received:
                req.logger.warning(f"Invoice: unknown status {received}, not changed.")
            return True
        invoice = req.object
        if TARGETS[received] == invoice.state:
            return True
        try:
            with invoice.env.cr.savepoint():
                change(invoice, TARGETS[received])
        except Exception as error:  # noqa: BLE001 - any Odoo refusal of the state change
            req.logger.error(f"Invoice: unable to change status to {received}: {error}")
            return False
        req.need_update()
        return True


def is_paid(invoice: Any) -> bool:
    """Tell if an invoice is posted & paid."""
    return invoice.state == State.POSTED and invoice.payment_state in PAID


def status(invoice: Any) -> str | None:
    """Splash status of an invoice."""
    if is_paid(invoice):
        return Status.COMPLETE
    return {State.DRAFT: Status.DRAFT, State.POSTED: Status.DUE, State.CANCEL: Status.CANCELED}.get(invoice.state)


def change(invoice: Any, state: str) -> None:
    """Move an invoice to an Odoo state (only drafts are posted or cancelled)."""
    if invoice.state != State.DRAFT:
        invoice.button_draft()
    if state == State.POSTED:
        invoice.action_post()
    elif state == State.CANCEL:
        invoice.button_cancel()
