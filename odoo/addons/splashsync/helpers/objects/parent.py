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

from splashpy import const, Framework
from splashpy.componants import FieldFactory
from splashpy.helpers import ObjectsHelper
from .relations import M2OHelper


class Parent:
    """
    Access to Parent partners
    """
    def buildParentFields(self):
        FieldFactory.create(ObjectsHelper.encode("ThirdParty", const.__SPL_T_ID__), "parent_id", "Parent")
        if self.name is "Address":
            FieldFactory.isRequired()

    def getParentFields(self, index, field_id):
        # Check is Requested Field
        if field_id != "parent_id":
            return

        self._out[field_id] = M2OHelper.get_object(self.object, "parent_id", "ThirdParty")
        self._in.__delitem__(index)

    def setParentFields(self, field_id, field_data):
        # Check is Requested Field
        if field_id != "parent_id":
            return

        M2OHelper.set_object(self.object, "parent_id", field_data, domain="res.partner")
        self._in.__delitem__(field_id)
