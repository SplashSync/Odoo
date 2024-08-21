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

import json
from splashpy import const, Framework
from splashpy.componants import FieldFactory
from odoo.addons.splashsync.helpers import M2MHelper, M2OHelper


class CompanyRelations:
    """
    Access to Object Company Allocations
    """

    def buildCompanyRelationsFields(self):
        # ==================================================================== #
        # Check if Model is Company Dependant
        fieldsIds = self.getModel().fields_get().keys()
        if "company_ids" not in fieldsIds and "company_id" not in fieldsIds:
            return
        # ==================================================================== #
        # Register Company Field
        FieldFactory.create(const.__SPL_T_INLINE__, "company", "Companies")
        FieldFactory.group("Meta")
        FieldFactory.isReadOnly()

    def getCompanyRelationsFields(self, index, field_id):
        if field_id != "company":
            return
        fieldsIds = self.getModel().fields_get().keys()
        # ==================================================================== #
        # M2M Company Relation
        if "company_ids" in fieldsIds:
            self._out[field_id] = M2MHelper.get_names(self.object, "company_ids")
        # ==================================================================== #
        # O2M Company Relation
        elif "company_id" in fieldsIds:
            if self.object.company_id.id > 0:
                data = [self.object.company_id.name]
            else:
                data = []
            self._out[field_id] = json.dumps(data, sort_keys=False)
        self._in.__delitem__(index)
