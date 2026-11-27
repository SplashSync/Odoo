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

"""Invoice payments (V1 ids ``<column>@payments``), as Odoo payments reconciled with the invoice.

Payments are only registered on posted invoices (as Odoo "Register Payment"). The method is the name
of a manual payment method or of a bank / cash journal of the company, else the first bank journal.
Received payments are the complete list: matched by reference, else by date & amount; changed or
missing payments are removed (unreconciled, cancelled). An amount within the rounding margin of
the residual amount pays the invoice in full. With "Check Payments Amounts" (Splash setting), the
payments are refused when their total is not the invoice total.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final

from splashpy.fields import FieldsFactory, FieldType
from splashpy.objects import ObjectRequest, fields_group

from ..accounting.lines import number, sorted_rows
from ..base import OdooGroup, build_fields

LIST: Final = "payments"
"""Payments list name (V1)."""

METHOD: Final = "journal_code"
"""Payment method column."""

TEMPLATES: Final = {
    f"{METHOD}@{LIST}": "Splash.Templates.Accounting.Payments.PaymentMode",
    f"date@{LIST}": "Splash.Templates.Accounting.Payments.PaymentDate",
    f"ref@{LIST}": "Splash.Templates.Accounting.Payments.PaymentNumber",
    f"amount@{LIST}": "Splash.Templates.Accounting.Payments.PaymentAmount",
}
"""Fields: V1 field id => template code."""

READ_ONLY: Final = {
    "journal_name": "Journal",
    "journal_type": "Journal Type",
    "payment_type": "Type",
    "state": "Status",
    "name": "Name",
}
"""Read-only columns (V1): column => name."""

FIELDS: Final = frozenset({LIST})
"""Lists of this group."""

JOURNALS: Final = ("bank", "cash")
"""Odoo journal types of payments."""

MANUAL: Final = "manual"
"""Odoo code of the manual payment methods."""

MARGIN: Final = 0.01
"""Accepted rounding error per invoice line."""

CHECK: Final = "sales_check_payments"
"""Splash setting: payments total must be the invoice total."""


@fields_group("payments", priority=80, after=("status",))
class InvoicePayments(OdooGroup):
    """Payments of the invoice: method, date, reference, amount (not tested: posted invoices only)."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare payments columns."""
        flags: dict[str, tuple[str | tuple[Any, ...], ...]] = dict.fromkeys(
            TEMPLATES, (("association", *TEMPLATES), "is_not_tested")
        )
        flags[f"{METHOD}@{LIST}"] = (("association", *TEMPLATES), "is_not_tested", ("add_choices", self.choices()))
        build_fields(factory, TEMPLATES, flags=flags)
        for column, name in READ_ONLY.items():
            factory.create(FieldType.VARCHAR, column, name).in_list(LIST).is_read_only()

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read one column of the invoice payments."""
        name = field_id.split("@", 1)[0]
        return [read(payment, name) for payment in payments(req.object)]

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write the complete payments list of a posted invoice."""
        invoice = req.object
        rows = [row for row in sorted_rows(value) if row.get("date") and row.get("amount") is not None]
        if invoice.state != "posted":
            if rows:
                req.logger.warning(f"Invoice: {invoice.display_name} is not posted, payments not registered.")
            return True
        if not self.check_total(req, invoice, rows):
            return True
        existing = payments(invoice)
        kept = existing.browse()
        new: list[Mapping[str, Any]] = []
        for row in rows:
            payment = match(existing - kept, row, margin(invoice))
            if payment:
                kept |= payment
            else:
                new.append(row)
        # payments not received first: the invoice residual is then free for the new ones
        for payment in existing - kept:
            remove(invoice, payment)
            req.need_update()
        for row in new:
            if self.register(req, invoice, row) is None:
                return False
            req.need_update()
        return True

    # ====================================================================#
    # Write
    # ====================================================================#

    def check_total(self, req: ObjectRequest, invoice: Any, rows: Sequence[Mapping[str, Any]]) -> bool:
        """Check the received payments total is the invoice total (Check Payments Amounts setting)."""
        if not self.context.setting(CHECK):
            return True
        total = sum(number(row.get("amount")) for row in rows)
        if abs(float(invoice.amount_total) - total) <= margin(invoice):
            return True
        req.logger.error(f"Invoice: payments total {total} is not the invoice total {invoice.amount_total}.")
        return False

    def register(self, req: ObjectRequest, invoice: Any, row: Mapping[str, Any]) -> Any:
        """Register a received payment on the invoice; None (logged) when impossible."""
        amount = number(row.get("amount"))
        method = self.method(str(row.get(METHOD) or ""), amount)
        if not method:
            req.logger.error(f"Invoice: no payment journal for company {invoice.company_id.name}.")
            return None
        if abs(float(invoice.amount_residual) - amount) <= margin(invoice):
            amount = float(invoice.amount_residual)
        wizard = (
            self.context.model("account.payment.register")
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "journal_id": method.journal_id.id,
                    "payment_method_line_id": method.id,
                    "amount": abs(amount),
                    "communication": str(row.get("ref") or "").strip() or invoice.name,
                    "payment_date": str(row.get("date"))[:10],
                }
            )
        )
        return wizard._create_payments()

    def method(self, code: str, amount: float) -> Any:
        """Find the manual payment method of a code: method name, else journal name, else first bank journal."""
        journals = self.journals()
        lines = journals.mapped(
            "inbound_payment_method_line_ids" if amount >= 0 else "outbound_payment_method_line_ids"
        )
        lines = lines.filtered(lambda line: line.code == MANUAL)
        code = code.strip().lower()
        return (
            lines.filtered(lambda line: line.name.lower() == code)[:1]
            or lines.filtered(lambda line: line.journal_id.name.lower() == code)[:1]
            or lines.filtered(lambda line: line.journal_id.type == "bank")[:1]
            or lines[:1]
        )

    def journals(self) -> Any:
        """Bank & cash journals of the company."""
        return self.context.model("account.journal").search(
            [("type", "in", JOURNALS), ("company_id", "=", self.context.company_id)], order="sequence, id"
        )

    def choices(self) -> dict[str, str]:
        """Payment methods choices: journals names & manual methods names."""
        if self.odoo is None:
            return {}
        choices: dict[str, str] = {}
        for journal in self.journals():
            choices[journal.name] = f"[{journal.code}] {journal.name}"
            for line in journal.inbound_payment_method_line_ids.filtered(lambda line: line.code == MANUAL):
                choices.setdefault(line.name, f"[{journal.code}] {line.name}")
        return choices


def payments(invoice: Any) -> Any:
    """Payments reconciled with an invoice, by creation."""
    return invoice._get_reconciled_payments().sorted("id")


def read(payment: Any, name: str) -> Any:
    """Read a payment column."""
    if name == METHOD:
        return payment.payment_method_line_id.name or None
    if name == "date":
        return payment.date.isoformat() if payment.date else None
    if name == "ref":
        return payment.memo or None
    if name == "amount":
        return float(payment.amount)
    if name == "journal_name":
        return payment.journal_id.name or None
    if name == "journal_type":
        return payment.journal_id.type or None
    return payment[name] or None


def match(candidates: Any, row: Mapping[str, Any], accepted: float) -> Any:
    """Payment of a received row: same reference, date & amount (else it is registered again)."""
    reference = str(row.get("ref") or "").strip()
    date = str(row.get("date") or "")[:10]
    amount = number(row.get("amount"))
    return candidates.filtered(
        lambda payment: (
            (not reference or payment.memo == reference)
            and read(payment, "date") == date
            and abs(float(payment.amount) - abs(amount)) <= accepted
        )
    )[:1]


def remove(invoice: Any, payment: Any) -> None:
    """Remove a payment from an invoice: unreconciled, cancelled, deleted."""
    partials = invoice._get_reconciled_invoices_partials()[0]  # (partial, amount, counterpart line)
    for partial, _amount, counterpart in partials:
        if counterpart.payment_id == payment:
            invoice.js_remove_outstanding_partial(partial.id)
    payment.action_cancel()
    payment.unlink()


def margin(invoice: Any) -> float:
    """Get the accepted rounding error of an invoice amount: one cent per line (as V1)."""
    return max(1, len(invoice.invoice_line_ids)) * MARGIN
