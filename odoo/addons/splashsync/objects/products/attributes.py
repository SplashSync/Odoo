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
from odoo.addons.splashsync.helpers import AttributesHelper


class ProductsAttributes:
    """
    Access to product Attributes Fields
    """

    @staticmethod
    def buildAttributesFields():
        # ==================================================================== #
        # Product Variation Attribute Code
        FieldFactory.create(const.__SPL_T_VARCHAR__, "code", "Attr Code")
        FieldFactory.inlist("Attributes")
        FieldFactory.microData("http://schema.org/Product", "VariantAttributeCode")
        FieldFactory.isNotTested()

        # ==================================================================== #
        # Product Variation Attribute Code
        FieldFactory.create(const.__SPL_T_VARCHAR__, "name", "Attr Name")
        FieldFactory.inlist("Attributes")
        FieldFactory.microData("http://schema.org/Product", "VariantAttributeName")
        FieldFactory.isNotTested()

        # ==================================================================== #
        # Product Variation Attribute Code
        FieldFactory.create(const.__SPL_T_VARCHAR__, "value", "Attr Value")
        FieldFactory.inlist("Attributes")
        FieldFactory.microData("http://schema.org/Product", "VariantAttributeValue")
        FieldFactory.isNotTested()

    def getAttributesFields(self, index, field_id):
        """
        Get Product Attributes List
        :param index: str
        :param field_id: str
        :return: None
        """
        # ==================================================================== #
        # Check field_id this Attribute Field...
        value_id = ListHelper.initOutput(self._out, "Attributes", field_id)
        if value_id is None:
            return
        # ==================================================================== #
        # Check if Product has Variants
        if not AttributesHelper.has_attr(self.object):
            self._in.__delitem__(index)
            return
        # ==================================================================== #
        # Get Product Attributes Data
        attr_values = AttributesHelper.get_attr_values(self.object, value_id)
        for pos in range(len(attr_values)):
            ListHelper.insert(self._out, "Attributes", field_id, "attr-"+str(pos), attr_values[pos])
        # ==================================================================== #
        # Force Attributes Ordering
        self._out["Attributes"] = OrderedDict(sorted(self._out["Attributes"].items()))
        self._in.__delitem__(index)

    def setAttributesFields(self, field_id, field_data):
        """
        Update Product Attributes Values
        :param field_id: str
        :param field_data: hash
        :return: None
        """
        # ==================================================================== #
        # Check field_id this Attribute Field...
        if field_id != "Attributes":
            return
        # ==================================================================== #
        # Walk on Product Attributes Field...
        attr_ids = []
        if isinstance(field_data, dict):
            for key, value in field_data.items():
                try:
                    # Find or Create Attribute Value
                    attr_value = AttributesHelper.find_or_create_value(value["code"], value["value"])
                    # Store Attribute Value Id
                    attr_ids += [attr_value.id]
                except Exception as exception:
                    return Framework.log().fromException(exception)
        # ==================================================================== #
        # Update List of Product Attributes
        self.object.attribute_value_ids = [(6, 0, attr_ids)]
        self._in.__delitem__(field_id)
