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

"""Order invoice (read only, scope Invoicing Provider): number, date and PDF of the first posted invoice.

The PDF is the legal document of the invoice, as Odoo "Send & Print" stores it: generated once on
first read when the invoice was never sent nor printed, then read from its attachment. It is a
stream field: Splash downloads it on demand (``ReadFile``), empty until the order is invoiced.
"""

from __future__ import annotations

from typing import Any, Final

from splashpy.fields import FieldsFactory, Files
from splashpy.objects import ObjectRequest, fields_group

from ..base import OdooGroup, build_fields

GROUP: Final = "Invoicing"
"""Fields group label."""

TEMPLATES: Final = {
    "invoice_number": "Splash.Templates.Accounting.Invoicing.InvoiceNumber",
    "invoice_date": "Splash.Templates.Accounting.Invoicing.InvoiceDate",
    "invoice_pdf": "Splash.Templates.Accounting.Invoicing.InvoicePdf",
}
"""Fields: field id => template code."""

FIELDS: Final = frozenset(TEMPLATES)
"""Field ids of this group."""

MODEL: Final = "account.move"
"""Odoo model of invoices (path of the PDF files: ``account.move/<id>``)."""

TTL: Final = 3
"""Days Splash keeps the PDF."""


@fields_group("invoicing", priority=90)
class OrderInvoicing(OdooGroup):
    """First invoice of the order: number, date, PDF."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare invoice fields (read only)."""
        build_fields(factory, TEMPLATES, GROUP, flags=dict.fromkeys(TEMPLATES, ("is_read_only",)))

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read the number, date or PDF of the first invoice."""
        invoice = first_invoice(req.object)
        if not invoice:
            return None
        if field_id == "invoice_number":
            return invoice.name or None
        if field_id == "invoice_date":
            return invoice.invoice_date.isoformat() if invoice.invoice_date else None
        raw = invoice_pdf(invoice)
        if not raw:
            return None
        filename = f"{str(invoice.name).replace('/', '_')}.pdf"
        file = Files.encode(str(invoice.name), filename, f"{MODEL}/{invoice.id}", raw)
        if file is not None:
            file["ttl"] = TTL
        return file


def first_invoice(order: Any) -> Any:
    """First posted customer invoice of an order."""
    invoices = order.invoice_ids.filtered(lambda move: move.move_type == "out_invoice" and move.state == "posted")
    return invoices.sorted(lambda move: (move.invoice_date or move.date, move.id))[:1]


def invoice_pdf(invoice: Any) -> bytes:
    """Legal PDF of a posted invoice: generated & stored once (as Odoo "Send & Print"), the "sent" flag kept."""
    if not invoice.invoice_pdf_report_id:
        sent = invoice.is_move_sent
        invoice.env["account.move.send"]._generate_and_send_invoices(invoice, sending_methods=["manual"])
        if invoice.is_move_sent != sent:
            invoice.write({"is_move_sent": sent})
    return attachment_raw(invoice.invoice_pdf_report_id)


def attachment_raw(attachment: Any) -> bytes:
    """Raw contents of an attachment (Odoo 20: ``LocalBinaryFile``, before: bytes)."""
    if not attachment:
        return b""
    raw = attachment.raw
    return bytes(raw.content if hasattr(raw, "content") else raw or b"")


def read_file(env: Any, path: str, checksum: str) -> dict[str, Any] | None:
    """Read an invoice PDF for Splash (``ReadFile``), when its checksum matches."""
    model, _, record_id = path.rpartition("/")
    if model != MODEL or not record_id.isdigit():
        return None
    invoice = env[MODEL].browse(int(record_id)).exists()
    raw = attachment_raw(invoice.invoice_pdf_report_id) if invoice else b""
    if not raw or Files.md5(raw) != checksum:
        return None
    return Files.read(f"{str(invoice.name).replace('/', '_')}.pdf", raw)
