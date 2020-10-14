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


class Partner(models.Model):
    """Override for Odoo Partners to Make it Work with Splash"""
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        res = super(Partner, self).create(vals)

        # ====================================================================#
        # Execute Splash Commit
        self.__do_splash_commit(const.__SPL_A_CREATE__)

        return res

    def write(self, vals):
        res = super(Partner, self).write(vals)

        # ====================================================================#
        # Execute Splash Commit
        self.__do_splash_commit(const.__SPL_A_UPDATE__)

        return res

    def unlink(self):
        res = super(Partner, self).unlink()

        # ====================================================================#
        # Execute Splash Commit
        self.__do_splash_commit(const.__SPL_A_DELETE__)

        return res

    def __do_splash_commit(self, action):
        """
        Execute Splash Commit for this Product
        :param action: str

        :rtype: void
        """
        # ====================================================================#
        # Safety Check
        if not self:
            pass
        # ====================================================================#
        # Import Required Classes
        from odoo.addons.splashsync.helpers.objects.partners import PartnersHelper
        from odoo.addons.splashsync.client import OdooClient
        # ====================================================================#
        # Object is a ThirdParty
        if PartnersHelper.is_thirdparty(self):
            from odoo.addons.splashsync.objects import ThirdParty
            OdooClient.commit(ThirdParty(), action, str(self.id))
            return
        # ====================================================================#
        # Object is an Address
        if PartnersHelper.is_address(self):
            from odoo.addons.splashsync.objects import Address
            OdooClient.commit(Address(), action, str(self.id))
            return