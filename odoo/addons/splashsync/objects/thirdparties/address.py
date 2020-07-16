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


class Address:
    """
    Access to relatives partners
    """
    def buildAddressFields(self):
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "strt", "Child Address")
        FieldFactory.inlist("Addresses")
        FieldFactory.isNotTested()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "adrsstype", "Address Type")
        FieldFactory.inlist("Addresses")
        FieldFactory.isNotTested()

    def getAddressFields(self, index, field_id):
        base_field_id = ListHelper.initOutput(self._out, "Addresses", field_id)
        if base_field_id is None:
            return

        field_values = self._get_address_values(base_field_id)
        for pos in range(len(field_values)):
            ListHelper.insert(self._out, "Addresses", field_id, "attr-" + str(pos), field_values[pos])
        self._in.__delitem__(index)

    def _get_address_values(self, value_id):
        values = []

        for field_value in self.object.child_ids:
            # Collect Values
            # if field_value.child_ids is None:
            #     return None
            if value_id == "strt":
                Framework.log().dump(field_value.street)
                values += [str(field_value.street)]
            elif value_id == "adrsstype":
                values += [str(field_value.type)]
        return values
