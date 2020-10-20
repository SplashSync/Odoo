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


class OrderRelations:
    """
    Access to Order Relational Fields
    """

    def buildRelationFields(self):
        # ==================================================================== #
        # Sale Person Name
        FieldFactory.create(const.__SPL_T_VARCHAR__, "user_id", "Salesperson Name")
        FieldFactory.microData("http://schema.org/Author", "name")
        FieldFactory.addChoices(M2OHelper.get_name_values("res.users"))
        FieldFactory.group("General")
        # ==================================================================== #
        # Sale Person Email
        FieldFactory.create(const.__SPL_T_VARCHAR__, "user_email", "Salesperson Email")
        FieldFactory.microData("http://schema.org/Author", "email")
        FieldFactory.group("General")
        FieldFactory.isNotTested()
        # ==================================================================== #
        # Sale Team Name
        FieldFactory.create(const.__SPL_T_VARCHAR__, "team_id", "Sales team Name")
        FieldFactory.microData("http://schema.org/Author", "memberOf")
        FieldFactory.addChoices(M2OHelper.get_name_values("crm.team"))
        FieldFactory.group("General")
        FieldFactory.isNotTested()

    def getRelationFields(self, index, field_id):
        # Check if Relation Field...
        if not self.isRelationFields(field_id):
            return
        # ==================================================================== #
        # Sale Person Name
        if field_id == "user_id":
            self._out[field_id] = M2OHelper.get_name(self.object, "user_id")
            self._in.__delitem__(index)
        # ==================================================================== #
        # Sale Person Email
        if field_id == "user_email":
            self._out[field_id] = M2OHelper.get_name(self.object, "user_id", "email")
            self._in.__delitem__(index)
        # ==================================================================== #
        # Sale Team Name
        if field_id == "team_id":
            self._out[field_id] = M2OHelper.get_name(self.object, "team_id")
            self._in.__delitem__(index)

    def setRelationFields(self, field_id, field_data):
        # Check if Relation Field...
        if not self.isRelationFields(field_id):
            return
        # ==================================================================== #
        # Sale Person Name
        if field_id == "user_id":
            M2OHelper.set_name(self.object, "user_id", field_data, domain="res.users")
            self._in.__delitem__(field_id)
        # ==================================================================== #
        # Sale Person Email
        if field_id == "user_email":
            M2OHelper.set_name(self.object, "user_id", field_data, 'email', domain="res.users")
            self._in.__delitem__(field_id)
        # ==================================================================== #
        # Sale Team Name
        if field_id == "team_id":
            M2OHelper.set_name(self.object, "team_id", field_data, domain="crm.team")
            self._in.__delitem__(field_id)

    @staticmethod
    def isRelationFields(field_id):
        if field_id in [
            "user_id", "user_email", "team_id"
        ]:
            return True
        return False


