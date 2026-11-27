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
"""Payment transactions: payment method received from Splash (orders payments)."""

from __future__ import annotations

from odoo import fields, models


class PaymentTransaction(models.Model):
    """Transaction: keeps the payment method code received from Splash.

    Odoo transactions are booked on one of its payment providers; the code received from the shop
    (``CreditCard``, ``PayPal``...) is kept as is, and sent back.
    """

    _inherit = "payment.transaction"

    splash_payment_method = fields.Char(
        help="Payment method code received from Splash (Splash normalized codes).",
        readonly=True,
        copy=False,
    )
