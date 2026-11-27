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

"""Order payments (ids of the V1 invoices payments ``<column>@payments``), as Odoo payment transactions.

A received payment is a confirmed transaction of the order, as the payments of the eCommerce
orders: no accounting entry until the order is invoiced. Transactions are booked on a "custom"
payment provider of the company: the one of the received method (wire transfer, cash on delivery,
pay on invoice), else the default one (wire transfer first). The received method code is kept on
the transaction and sent back as received.

Received payments are the complete list: matched by transaction id, else by date & amount; the
transactions not received are removed.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from odoo import fields as odoo_fields
from splashpy.fields import FieldsFactory
from splashpy.objects import ObjectRequest, fields_group

from ...taxes import Taxes
from ..accounting.lines import number, sorted_rows
from ..base import OdooGroup, build_fields

LIST: Final = "payments"
"""Payments list name (V1)."""

DATE: Final = "date"
"""Payment date column."""

AMOUNT: Final = "amount"
"""Payment amount column."""

NUMBER: Final = "ref"
"""Payment transaction id column."""

METHOD: Final = "journal_code"
"""Payment method column."""

TEMPLATES: Final = {
    f"{DATE}@{LIST}": "Splash.Templates.Accounting.Payments.PaymentDate",
    f"{AMOUNT}@{LIST}": "Splash.Templates.Accounting.Payments.PaymentAmount",
    f"{NUMBER}@{LIST}": "Splash.Templates.Accounting.Payments.PaymentNumber",
    f"{METHOD}@{LIST}": "Splash.Templates.Accounting.Payments.PaymentMode",
}
"""Fields: V1 field id => template code."""

FIELDS: Final = frozenset({LIST})
"""Lists of this group."""

MODES: Final = {
    "ByBankTransferInAdvance": "wire_transfer",
    "COD": "cash_on_delivery",
    "ByInvoice": "pay_on_invoice",
}
"""Splash payment method codes => Odoo custom providers mode."""

METHODS: Final = {
    "ByBankTransferInAdvance": "Bank Transfer",
    "CheckInAdvance": "Check",
    "Cash": "Cash",
    "COD": "Cash on Delivery",
    "ByInvoice": "By Invoice",
    "DirectDebit": "Direct Debit",
    "CreditCard": "Credit Card",
    "PayPal": "PayPal",
}
"""Splash normalized payment method codes (choices)."""

PROVIDER: Final = "custom"
"""Odoo code of the payment providers transactions are booked on."""

DONE: Final = "done"
"""Odoo state of a confirmed transaction."""

CANCEL: Final = "cancel"
"""Odoo state of a canceled transaction."""

SPLASH_METHOD: Final = "splash_payment_method"
"""Transaction field of the received method code."""


@fields_group("payments", priority=60, after=("lines",))
class OrderPayments(OdooGroup):
    """Payments of the order: date, amount, transaction id & method."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare payments columns."""
        main = (f"{DATE}@{LIST}", f"{AMOUNT}@{LIST}")
        flags: dict[str, tuple[str | tuple[Any, ...], ...]] = dict.fromkeys(TEMPLATES, (("association", *main),))
        build_fields(factory, TEMPLATES, flags=flags)
        factory.add_choices(METHODS)

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read one column of the order payments."""
        name = field_id.split("@", 1)[0]
        return [read(transaction, name) for transaction in transactions(req.object)]

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write the complete payments list: update matched transactions, create, remove the others."""
        order = req.object
        existing = transactions(order)
        kept = existing.browse()
        for row in sorted_rows(value):
            transaction = match(existing - kept, row)
            if transaction:
                kept |= transaction
                values = changes(transaction, row)
                if values:
                    transaction.write(values)
                    req.need_update()
                continue
            created = self.create_transaction(req, order, row)
            if created is None:
                return False
            kept |= created
            req.need_update()
        for transaction in existing - kept:
            remove(transaction)
            req.need_update()
        return True

    def create_transaction(self, req: ObjectRequest, order: Any, row: Mapping[str, Any]) -> Any:
        """Book a received payment as a confirmed transaction of the order; None (logged) when impossible."""
        method = str(row.get(METHOD) or "").strip()
        provider = self.provider(order, method)
        if not provider:
            req.logger.error(f"Order: no payment provider for company {order.company_id.name}, payment not saved.")
            return None
        transactions_model = self.context.model("payment.transaction")
        values = {
            "provider_id": provider.id,
            "payment_method_id": provider.payment_method_ids[:1].id,
            "reference": transactions_model._compute_reference(provider.code, prefix=order.name),
            "provider_reference": str(row.get(NUMBER) or "").strip() or False,
            "amount": number(row.get(AMOUNT)),
            "currency_id": order.currency_id.id,
            "partner_id": order.partner_invoice_id.id or order.partner_id.id,
            "sale_order_ids": [(6, 0, order.ids)],
            "state": DONE,
            "last_state_change": paid_at(row),
            SPLASH_METHOD: method or False,
        }
        return transactions_model.create(values)

    def provider(self, order: Any, method: str) -> Any:
        """Get the custom payment provider of the received method, else the default one (wire transfer first)."""
        providers = self.context.model("payment.provider").search(
            [("code", "=", PROVIDER), ("company_id", "=", order.company_id.id)], order="sequence, id"
        )
        mode = MODES.get(method, MODES["ByBankTransferInAdvance"])
        return providers.filtered(lambda provider: provider.custom_mode == mode)[:1] or providers[:1]


def transactions(order: Any) -> Any:
    """Transactions of an order (canceled excluded), by creation."""
    return order.transaction_ids.filtered(lambda transaction: transaction.state != CANCEL).sorted("id")


def read(transaction: Any, name: str) -> Any:
    """Read a payment column."""
    if name == DATE:
        moment = transaction.last_state_change or transaction.create_date
        return moment.date().isoformat() if moment else None
    if name == AMOUNT:
        return float(transaction.amount)
    if name == NUMBER:
        return transaction.provider_reference or transaction.reference or None
    received = transaction[SPLASH_METHOD]
    if received:
        return received
    mode = transaction.provider_id.custom_mode
    return next((code for code, odoo_mode in MODES.items() if odoo_mode == mode), None)


def match(candidates: Any, row: Mapping[str, Any]) -> Any:
    """Transaction of a received payment: same transaction id, else same date & amount."""
    reference = str(row.get(NUMBER) or "").strip()
    if reference:
        found = candidates.filtered(lambda transaction: transaction.provider_reference == reference)
        if found:
            return found[:1]
    date = str(row.get(DATE) or "")[:10]
    amount = number(row.get(AMOUNT))
    return candidates.filtered(
        lambda transaction: (
            not (reference and transaction.provider_reference)
            and read(transaction, DATE) == date
            and abs(float(transaction.amount) - amount) <= Taxes.PRECISION
        )
    )[:1]


def changes(transaction: Any, row: Mapping[str, Any]) -> dict[str, Any]:
    """Values of a matched transaction that changed."""
    values: dict[str, Any] = {}
    if AMOUNT in row and abs(float(transaction.amount) - number(row[AMOUNT])) > Taxes.PRECISION:
        values["amount"] = number(row[AMOUNT])
    if DATE in row and read(transaction, DATE) != str(row[DATE] or "")[:10]:
        values["last_state_change"] = paid_at(row)
    if NUMBER in row and (str(row[NUMBER] or "").strip() or False) != (transaction.provider_reference or False):
        values["provider_reference"] = str(row[NUMBER] or "").strip() or False
    if METHOD in row and (str(row[METHOD] or "").strip() or False) != (transaction[SPLASH_METHOD] or False):
        values[SPLASH_METHOD] = str(row[METHOD] or "").strip() or False
    return values


def remove(transaction: Any) -> None:
    """Remove a transaction no more received: deleted, else canceled (linked to accounting)."""
    try:
        with transaction.env.cr.savepoint():
            transaction.unlink()
    except Exception:  # noqa: BLE001 - Odoo refuses to delete transactions with payments
        transaction.write({"state": CANCEL})


def paid_at(row: Mapping[str, Any]) -> Any:
    """Date-time of a received payment (its date, at midnight; now when not received)."""
    date = str(row.get(DATE) or "")[:10]
    return f"{date} 00:00:00" if date else odoo_fields.Datetime.now()
