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

from splashpy import const
from splashpy.componants import FieldFactory
from odoo.addons.splashsync.helpers import TransHelper

class ProductsCore:
    """
    Access to Order Core Fields (Required or NOT)
    """

    __core_fields_ids = ['description']

    def buildProductCoreFields(self):
        # ==================================================================== #
        # Product Description
        FieldFactory.create(const.__SPL_T_VARCHAR__, "description", "Description")
        FieldFactory.microData("http://schema.org/Product", "description")
        FieldFactory.description("Description")
        FieldFactory.setMultilang(TransHelper.get_default_iso())
        FieldFactory.addOption("isHtml", True)

    def getProductCoreFields(self, index, field_id):
        # ==================================================================== #
        # Filter on Field Id
        if field_id not in ProductsCore.__core_fields_ids:
            return
        # ==================================================================== #
        # Collect field value...
        self.getSimpleStr(index, field_id, self.template)

    def setProductCoreFields(self, field_id, field_data):
        # ==================================================================== #
        # Filter on Field Id
        if field_id not in ProductsCore.__core_fields_ids:
            return
        # ==================================================================== #
        # Update field value...
        self.setSimple(field_id, field_data, self.template)
