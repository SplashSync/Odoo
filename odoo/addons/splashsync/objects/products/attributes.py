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
        FieldFactory.inlist("attributes")
        FieldFactory.microData("http://schema.org/Product", "VariantAttributeCode")
        FieldFactory.isNotTested()

        # ==================================================================== #
        # Product Variation Attribute Code
        FieldFactory.create(const.__SPL_T_VARCHAR__, "name", "Attr Name")
        FieldFactory.inlist("attributes")
        FieldFactory.microData("http://schema.org/Product", "VariantAttributeName")
        FieldFactory.isReadOnly()
        FieldFactory.isNotTested()

        # ==================================================================== #
        # Product Variation Attribute Code
        FieldFactory.create(const.__SPL_T_VARCHAR__, "value", "Attr Value")
        FieldFactory.inlist("attributes")
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
        value_id = ListHelper.initOutput(self._out, "attributes", field_id)
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
            ListHelper.insert(self._out, "attributes", field_id, "attr-"+str(pos), attr_values[pos])
        # ==================================================================== #
        # Force Attributes Ordering
        self._out["attributes"] = OrderedDict(sorted(self._out["attributes"].items()))
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
        if field_id != "attributes":
            return
        new_attributes_ids = []
        # ==================================================================== #
        # Walk on Product Attributes Field...
        if isinstance(field_data, dict):
            # Force Attributes Ordering
            field_data = OrderedDict(sorted(field_data.items()))
            # Walk on Product Attributes Field...
            for key, value in field_data.items():
                try:
                    # Find or Create Attribute Value
                    attr_value = AttributesHelper.find_or_create_value(value["code"], value["value"])
                    # Update Product Attribute
                    if attr_value is not None:
                        new_attributes_ids += [attr_value.attribute_id.id]
                        AttributesHelper.update_value(self.object, attr_value)
                except Exception as exception:
                    return Framework.log().fromException(exception)
        # ==================================================================== #
        # Delete Remaining Product Attributes Values...
        for current_value in self.object.attribute_value_ids:
            if current_value.attribute_id.id not in new_attributes_ids:
                self.object.attribute_value_ids = [(3, current_value.id, 0)]

        self._in.__delitem__(field_id)
