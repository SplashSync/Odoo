# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) 2015-2019 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#


from odoo import api, models, fields
from splashpy import const


class AccountInvoice(models.Model):
    """Override for Odoo Invoice to Make it Work with Splash"""
    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)

        # ====================================================================#
        # Execute Splash Commit
        self.__do_splash_commit(const.__SPL_A_CREATE__)

        return res

    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)

        # ====================================================================#
        # Execute Splash Commit
        self.__do_splash_commit(const.__SPL_A_UPDATE__)

        return res

    def unlink(self):
        # ====================================================================#
        # Execute Splash Commit
        self.__do_splash_commit(const.__SPL_A_DELETE__)

        res = super(AccountInvoice, self).unlink()

        return res

    def __do_splash_commit(self, action):
        """
        Execute Splash Commit for this Invoice

        :param action: str
        :return: void
        """
        # ====================================================================#
        # Execute Splash Commit for this Product
        from odoo.addons.splashsync.objects import Invoice
        from odoo.addons.splashsync.client import OdooClient
        for invoice in self:
            OdooClient.commit(Invoice(), action, str(invoice.id))
