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
        # ====================================================================#
        # Walk on Available Languages
        for iso_code, lang_name in TransHelper.get_all().items():
            # ==================================================================== #
            # Product Description
            FieldFactory.create(const.__SPL_T_VARCHAR__, "description", "Description")
            FieldFactory.microData("http://schema.org/Product", "description")
            FieldFactory.description("[" + lang_name + "] Description")
            FieldFactory.setMultilang(iso_code)
            FieldFactory.addOption("isHtml", True)
            if iso_code != TransHelper.get_default_iso():
                FieldFactory.association("description")

    def getProductCoreFields(self, index, field_id):
        # ==================================================================== #
        # Filter on Field Id
        if field_id not in ProductsCore.__core_fields_ids:
            return
        # ==================================================================== #
        # Collect field value...
        self.getSimpleStr(index, field_id, self.template)
        for iso_code in TransHelper.get_extra_iso():
            iso_field_id = field_id+"_"+iso_code
            for key, val in self._in.copy().items():
                if iso_field_id != val:
                    continue
                self._out[iso_field_id] = TransHelper.get(self.template, field_id, iso_code)
                self._in.__delitem__(key)

    def setProductCoreFields(self, field_id, field_data):
        # ==================================================================== #
        # Filter on Field Id
        if field_id not in ProductsCore.__core_fields_ids:
            return
        # ==================================================================== #
        # Update field value...
        self.setSimple(field_id, field_data, self.template)
        for iso_code in TransHelper.get_extra_iso():
            iso_field_id = field_id+"_"+iso_code
            if iso_field_id not in self._in.keys():
                continue
            TransHelper.set(self.template, field_id, iso_code, self._in[iso_field_id])
            self._in.__delitem__(iso_field_id)
