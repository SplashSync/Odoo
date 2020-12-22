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

from splashpy import const, Framework
from splashpy.componants import FieldFactory
from odoo.addons.splashsync.helpers import M2MHelper, M2OHelper


class SafeName:
    """
    Access to Safe Names Field: A Sanitized Version of Object Name
    """

    def buildSafeNameFields(self):
        # ==================================================================== #
        # Sale Person Name
        FieldFactory.create(const.__SPL_T_VARCHAR__, "safe_name", "Sanitized Name")
        FieldFactory.group("General")
        FieldFactory.isReadOnly()

    def getSafeNameFields(self, index, field_id):
        if field_id == "safe_name":
            try:
                import re
                self._out[field_id] = re.sub("[^a-zA-Z0-9]", "-", self.object.name)
            except Exception:
                self._out[field_id] = self.object.name
            self._in.__delitem__(index)
