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
import logging


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # ====================================================================#
    # !!! Odoo Core Features Overrides !!!
    # ====================================================================#

    def create_variant_ids(self):
        _logger = logging.getLogger("SPLASH SYNC")
        _logger.warning("Variants Auto-creation is disabled when Splash Module is Active")
        return True

    def _create_variant_ids(self):
        return self.create_variant_ids()

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)

        # ====================================================================#
        # Execute Splash Commit
        self.__do_splash_commit(const.__SPL_A_CREATE__)

        return res

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)

        # ====================================================================#
        # Execute Splash Commit
        self.__do_splash_commit(const.__SPL_A_UPDATE__)

        return res

    def unlink(self):
        # ====================================================================#
        # Execute Splash Commit
        self.__do_splash_commit(const.__SPL_A_DELETE__)

        res = super(ProductTemplate, self).unlink()

        return res

    def __do_splash_commit(self, action):
        """
        Execute Splash Commit for All Child Products

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
        for template in self:
            OdooClient.commit(Product(), action, list(map(str, template.product_variant_ids.ids)))
