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

from collections import OrderedDict
from splashpy import const, Framework
from splashpy.componants import FieldFactory
from splashpy.helpers import ListHelper
from odoo.addons.splashsync.helpers import AttributesHelper, FeaturesHelper


class ProductsFeatures:
    """
    Access to product Features Fields
    """

    @staticmethod
    def buildFeaturesFields():
        for attribute in FeaturesHelper.find_all():
            # ==================================================================== #
            # Product Feature Field
            FieldFactory.create(const.__SPL_T_VARCHAR__, FeaturesHelper.encode_id(attribute), attribute.display_name)
            FieldFactory.group("Features")
            FieldFactory.microData("http://schema.org/Product", attribute.name)

    def getFeaturesFields(self, index, field_id):
        """
        Get Product Attributes List
        :param index: str
        :param field_id: str
        :return: None
        """
        # ==================================================================== #
        # Check field_id this Feature Field...
        attr_id = FeaturesHelper.decode_id(field_id)
        if attr_id is None:
            return
        self._in.__delitem__(index)
        # ==================================================================== #
        # Check if Product has Attribute Value
        for attr_value in self.object.attribute_value_ids:
            if attr_value.attribute_id.id == attr_id:
                self._out[field_id] = attr_value.name
                return
        # ==================================================================== #
        # Check if Product has Feature Value
        for attr_value in self.template.valid_product_attribute_value_ids:
            if attr_value.attribute_id.id == attr_id:
                self._out[field_id] = attr_value.name
                return

    def setFeatureFields(self, field_id, field_data):
        """
        Update Product Attributes Values
        :param field_id: str
        :param field_data: hash
        :return: None
        """
        # ==================================================================== #
        # Check field_id this Feature Field...
        attr_id = FeaturesHelper.decode_id(field_id)
        if attr_id is None:
            return
        self._in.__delitem__(field_id)
        # ==================================================================== #
        # Load List of Variation Attribute Ids
        var_attr_ids = AttributesHelper.get_variation_attr_ids(self.object)
        if attr_id in var_attr_ids:
            return
        # ==================================================================== #
        # Check if Product has Feature Value
        for attr_line in self.template.attribute_line_ids:
            # Check if Attribute Found & NOT a Variation Attribute
            if attr_line.attribute_id.id != attr_id or attr_line.attribute_id.id in var_attr_ids:
                continue
            # Detect Empty Product Attribute
            if field_data is None or len(str(field_data)) < 1:
                # for variant in self.object.product_variant_ids:
                FeaturesHelper.remove(self.template, attr_line.attribute_id.id)
                break
            # Find or Create Attribute Value
            new_value = AttributesHelper.find_or_create_value(
                attr_line.attribute_id.name,
                str(field_data)
            )
            # Remove Product Attribute
            if new_value is None:
                FeaturesHelper.remove(self.template, attr_line.attribute_id.id)
            # Update Product Attribute
            else:
                FeaturesHelper.update(self.template, new_value)
            return

        # ==================================================================== #
        # Add Product Feature Value
        if field_data is not None and len(str(field_data)) > 0:
            # Find or Create Attribute Value
            new_value = AttributesHelper.find_or_create_value(
                AttributesHelper.getAttrModel().browse([attr_id]).name,
                str(field_data)
            )
            # for variant in self.object.product_variant_ids:
            FeaturesHelper.add(self.template, new_value)










