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
from splashpy.helpers import ObjectsHelper, ListHelper, FieldsHelper
from odoo.addons.splashsync.helpers.objects import AttributesHelper


class ProductsVariants:
    """
    Access to product Variation Fields
    """

    def buildVariantsFields(self):

        # ==================================================================== #
        # Product Variation Parent Link
        FieldFactory.create(const.__SPL_T_VARCHAR__, "variant_template", "Template ID")
        FieldFactory.name("Template ID")
        FieldFactory.group("Meta")
        FieldFactory.microData("http://schema.org/Product", "isVariationOf")
        FieldFactory.isReadOnly()

        # ==================================================================== #
        # CHILD PRODUCTS INFORMATION
        # ==================================================================== #

        # ==================================================================== #
        # Product Variation List - Product Link
        FieldFactory.create(ObjectsHelper.encode("Product", const.__SPL_T_ID__), "id")
        FieldFactory.name("Variant ID")
        FieldFactory.inlist("variants")
        FieldFactory.microData("http://schema.org/Product", "Variants")
        FieldFactory.isNotTested()

        FieldFactory.create(const.__SPL_T_VARCHAR__, "sku")
        FieldFactory.name("Variant SKU")
        FieldFactory.inlist("variants")
        FieldFactory.isReadOnly()

    def getVariantsMetaFields(self, index, field_id):
        # ==================================================================== #
        # Read Product Template Id
        if field_id == "variant_template":
            if len(self.object.product_tmpl_id) == 0:
                self._out[field_id] = None
            else:
                self._out[field_id] = str(self.object.product_tmpl_id[0].id)
            self._in.__delitem__(index)
            return

    def getVariantsFields(self, index, field_id):
        # ==================================================================== #
        # Check if this Variant Field...
        base_field_id = ListHelper.initOutput(self._out, "variants", field_id)
        if base_field_id is None:
            return
        # ==================================================================== #
        # Check if Product has Variants
        if not AttributesHelper.has_attr(self.object):
            self._in.__delitem__(index)
            return
        # ==================================================================== #
        # List Product Variants Ids
        for variant in self.object.with_context(active_test=False).product_variant_ids:
            # ==================================================================== #
            # Debug Mode => Filter Current Product From List
            if Framework.isDebugMode() and variant.id == self.object.id:
                continue
            # ==================================================================== #
            # Read Variant Data
            if base_field_id == "id":
                value = ObjectsHelper.encode("Product", str(variant.id))
            elif base_field_id == "sku":
                value = str(variant.code)
            ListHelper.insert(self._out, "variants", field_id, "var-"+str(variant.id), value)

        self._in.__delitem__(index)

    def setVariantsFields(self, field_id, field_data):
        """Update of Product Variants Not Allowed"""
        if field_id == "variants":
            self.detect_variant_template()
            self._in.__delitem__(field_id)

    def is_new_variable_product(self):
        """
        Detect if New Product is Variable => Has Attributes
        :return: bool
        """
        # ====================================================================#
        # Check if Inputs Contains Attributes
        if "attributes" not in self._in.keys() or not isinstance(self._in["attributes"], dict):
            return False
        return True

    def detect_variant_template(self):
        """
        Detect if Product Template for New Product
        :return: None|int
        """
        # ====================================================================#
        # Check if Inputs Contains Variants Ids
        if "variants" not in self._in.keys() or not isinstance(self._in["variants"], dict):
            return None
        # ====================================================================#
        # Walk on Variants Items
        for key, variant in self._in["variants"].items():
            # Variant Object Splash Id is Here
            if "id" not in variant.keys() or not isinstance(variant["id"], str):
                continue
            # Variant Object Splash Id is Valid
            product_id = ObjectsHelper.id(variant["id"])
            if not isinstance(product_id, str) or int(product_id) <= 0:
                continue
            # Load Variant Product
            product = self.load(int(product_id))
            if product is False or not isinstance(product.product_tmpl_id[0].id, int):
                continue
            # Return product Template Id
            return product.product_tmpl_id[0].id

        return None



