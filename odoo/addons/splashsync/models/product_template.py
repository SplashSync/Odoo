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
import logging


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # ====================================================================#
    # !!! Odoo Core Features Overrides !!!
    # ====================================================================#

    @api.multi
    def create_variant_ids(self):
        _logger = logging.getLogger("SPLASH SYNC")
        _logger.warning("Variants Auto-creation is disabled when Splash Module is Active")
        return True
