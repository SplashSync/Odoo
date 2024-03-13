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


from odoo import api, models
from splashpy import const


class StockMoveLine(models.Model):
    """
    Override for Odoo Stock Move to Make it Work with Splash
    """
    _inherit = 'stock.move.line'

    def unlink(self):
        # ====================================================================#
        # Execute Splash Commit
        self.__do_splash_commit(const.__SPL_A_UPDATE__)

        res = super(StockMoveLine, self).unlink()

        return res

    def __do_splash_commit(self, action):
        """
        Execute Splash Commit for this Product

        :param action: str
        :return: void
        """
        # ====================================================================#
        # Check if Splash Commit is Allowed
        from odoo.addons.splashsync.helpers import SettingsManager
        if SettingsManager.is_no_commits():
            return
        # ====================================================================#
        # Execute Splash Commit for this Product
        from odoo.addons.splashsync.objects import Product
        from odoo.addons.splashsync.client import OdooClient
        for move_line in self:
            OdooClient.commit(Product(), action, str(move_line.product_id.id))

