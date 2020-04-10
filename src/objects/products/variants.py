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

import logging
from splashpy import const, Framework
from splashpy.componants import FieldFactory
from splashpy.helpers import ObjectsHelper, ListHelper, FieldsHelper

class ProductsVariants:

    def buildVariantsFields(self):
        # ==================================================================== #
        # Is Default Product Variant

        # ==================================================================== #
        # CHILD PRODUCTS INFORMATION
        # ==================================================================== #

        # ==================================================================== #
        # Product Variation List - Product Link
        FieldFactory.create(ObjectsHelper.encode("Product", const.__SPL_T_ID__), "id")
        FieldFactory.name("Variant ID")
        FieldFactory.inlist("Variants")
        FieldFactory.microData("http://schema.org/Product", "Variants")
        FieldFactory.isNotTested()

        FieldFactory.create(const.__SPL_T_VARCHAR__, "sku")
        FieldFactory.name("Variant SKU")
        FieldFactory.inlist("Variants")
        FieldFactory.isReadOnly()

    def getVariantsFields(self, index, field_id):
        # ==================================================================== #
        # Check if this Variant Field...
        base_field_id = ListHelper.initOutput(self._out, "Variants", field_id)
        if base_field_id is None:
            return
        # ==================================================================== #
        # Check if Product has Variants
        if not self.object.is_product_variant:
            self._in.__delitem__(index)
            return
        # ==================================================================== #
        # List Product Variants Ids
        for variant in self.object.product_variant_ids:
            if base_field_id == "id":
                value = ObjectsHelper.encode("Product", str(variant.id))
            elif base_field_id == "sku":
                value = str(variant.code)
            ListHelper.insert(self._out, "Variants", field_id, "var-"+str(variant.id), value)

        self._in.__delitem__(index)


    def setVariantsFields( self, field_id, field_data ):
        pass
        # # Load Basic Fields Definitions
        # fields_def = self.get_basic_fields_list()
        # # Check if this field is Basic...
        # if field_id not in fields_def.keys():
        #     return
        # # Update field value...
        # field_type = fields_def[field_id]['type']
        #
        # if field_type in ['char', 'integer', 'float']:
        #     self.setSimple(field_id, field_data)
        #
        # if field_type in ['boolean']:
        #     self.setSimpleBool(field_id, field_data)
        #
        # if field_type in ['date']:
        #     self.setSimpleDate(field_id, field_data)
        #
        # if field_type in ['datetime']:
        #     self.setSimpleDateTime(field_id, field_data)
