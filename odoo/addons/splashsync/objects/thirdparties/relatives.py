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
from splashpy.helpers import ListHelper, ObjectsHelper
from odoo.addons.splashsync.helpers import SettingsManager, M2MHelper


class Relatives:
    """
    Access to relatives partners
    """
    def buildRelativesFields(self):

        # ==================================================================== #
        FieldFactory.create(ObjectsHelper.encode("ThirdParty", const.__SPL_T_ID__), "thirdP")
        FieldFactory.name("Thirdparty")
        FieldFactory.inlist("Relatives")
        FieldFactory.isNotTested()
        # ==================================================================== #
        # FieldFactory.create(ObjectsHelper.encode("ThirdParty", const.__SPL_T_ID__), "child", "Child")
        # FieldFactory.inlist("Relatives")
        # FieldFactory.isNotTested()
        # ==================================================================== #


    def getRelativesFields(self, index, field_id):
        base_field_id = ListHelper.initOutput(self._out, "Relatives", field_id)
        if base_field_id is None:
            return

        # ==================================================================== #
        # Read Parent Data
        field_values = self._get_parent_values(base_field_id)
        for pos in range(len(field_values)):
            ListHelper.insert(self._out, "Relatives", field_id, "parent-" + str(pos), field_values[pos])

        # ==================================================================== #
        # Read Child Data
        field_values = self._get_child_values(base_field_id)
        for pos in range(len(field_values)):
            ListHelper.insert(self._out, "Relatives", field_id, "child-" + str(pos), field_values[pos])
        self._in.__delitem__(index)


    def _get_parent_values(self, value_id):
        values = []

        for field_value in self.object.parent_id:
            # Collect Values

            if value_id == "thirdP":
                values += [ObjectsHelper.encode("ThirdParty", str(field_value.id))]
        return values

    def _get_child_values(self, value_id):
        values = []

        for field_value in self.object.child_ids:
            # Collect Values

            if value_id == "thirdP":
                values += [ObjectsHelper.encode("ThirdParty", str(field_value.id))]
        return values
