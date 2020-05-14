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
from odoo.addons.splashsync.helpers import AttributesHelper, LinesHelper, TransHelper, ValuesHelper


class ProductsAttributes:
    """
    Access to product Attributes Fields
    """

    @staticmethod
    def buildAttributesFields():
        # ====================================================================#
        # Set default System Language
        FieldFactory.setDefaultLanguage(TransHelper.get_default_iso())
        # ==================================================================== #
        # Product Variation Attribute Code
        FieldFactory.create(const.__SPL_T_VARCHAR__, "code", "Attr Code")
        FieldFactory.inlist("attributes")
        FieldFactory.microData(
            "http://schema.org/Product",
            "VariantAttributeCode" if Framework.isDebugMode() else "VariantAttributeName"
        )
        FieldFactory.isNotTested()
        # ==================================================================== #
        # Product Variation Attribute Name
        FieldFactory.create(const.__SPL_T_VARCHAR__, "name", "Attr Name")
        FieldFactory.inlist("attributes")
        FieldFactory.isReadOnly()
        FieldFactory.isNotTested()
        if Framework.isDebugMode():
            FieldFactory.microData("http://schema.org/Product", "VariantAttributeName")
        # ====================================================================#
        # Walk on Available Languages
        for iso_code, lang_name in TransHelper.get_all().items():
            # ==================================================================== #
            # Product Variation Attribute Code
            FieldFactory.create(const.__SPL_T_VARCHAR__, "value", "Attr Value")
            FieldFactory.description("[" + lang_name + "] Attr Value")
            FieldFactory.microData("http://schema.org/Product", "VariantAttributeValue")
            FieldFactory.setMultilang(iso_code)
            FieldFactory.inlist("attributes")
            FieldFactory.isNotTested()
        # ==================================================================== #
        # Product Variation Attribute Extra Price
        FieldFactory.create(const.__SPL_T_DOUBLE__, "price_extra", "Extra Price")
        FieldFactory.inlist("attributes")
        FieldFactory.microData(
            "http://schema.org/Product",
            "VariantAttributeCode" if Framework.isDebugMode() else "VariantExtraPrice"
        )
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
        # Get Product Attributes Data
        attr_values = self._get_attributes_values(value_id)
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
                # Find or Create Attribute Value
                attr_value = ValuesHelper.touch(value["code"], value["value"], False)
                # Unable to Create Attribute...
                if attr_value is None:
                    continue
                # Update Product Attribute
                new_attributes_ids += [attr_value.attribute_id.id]
                self._set_attribute_value(attr_value)
                self._set_attribute_value_langs(attr_value, value)
                self._set_attribute_extra_price(attr_value.attribute_id.id, value)
        # ==================================================================== #
        # Delete Remaining Product Attributes Values...
        to_delete_values = self.object.attribute_value_ids.filtered(
            lambda v: not AttributesHelper.is_wnva(v.attribute_id) and v.attribute_id.id not in new_attributes_ids
        )
        for attr_value in to_delete_values:
            # Remove Attribute from Values
            self.object.attribute_value_ids = [(3, attr_value.id, 0)]
            # Update Template Attribute Values with Variants Values
            self._set_variants_value_ids(attr_value.attribute_id)
        self._in.__delitem__(field_id)

    def _get_attributes_values(self, value_id):
        """
        Get List of Attributes Values for given Field
        :param value_id: str
        :return: dict
        """
        values = []
        # ====================================================================#
        # Walk on Product Attributes Values
        for attr_value in self.object.attribute_value_ids:
            # Filter Attributes that are NOT Variants Attributes
            if AttributesHelper.is_wnva(attr_value.attribute_id):
                continue
            # Collect Values
            if value_id == "value":
                values += [attr_value.name]
            elif value_id == "code":
                values += [attr_value.attribute_id[0].name]
            elif value_id == "name":
                values += [attr_value.attribute_id[0].display_name]
            # Attribute Extra Price
            elif value_id == "price_extra":
                values += [self._get_attribute_extra_price(attr_value.attribute_id[0].id)]
            # Walk on Extra Languages
            for iso_code in TransHelper.get_extra_iso():
                if value_id != "value_"+iso_code:
                    continue
                values += [TransHelper.get(attr_value, 'name', iso_code, attr_value.name)]

        return values

    def _get_attribute_extra_price(self, attr_id):
        """
        Get Extra Price for an Attribute
        :param attr_id: str
        :return: float
        """
        # ====================================================================#
        # Walk on Template Attributes Values
        for attr_value in self.object.product_template_attribute_value_ids:
            # Filter Attribute Id
            if attr_value.attribute_id.id != attr_id:
                continue
            # Collect Values
            return float(attr_value.price_extra)
        return float(0)

    def _set_attribute_value(self, new_value):
        """
        Update a Product Attribute Value
        :param new_value: product.attribute.value
        """
        # ====================================================================#
        # Find Product Current Attributes Values
        current_value = self.object.attribute_value_ids.filtered(lambda v: v.attribute_id.id == new_value.attribute_id.id)
        # ====================================================================#
        # If Values are Similar => Nothing to Do => Exit
        if len(current_value) == 1 and new_value.id == current_value.id:
            return
        # ====================================================================#
        # Update Attribute Value => Remove Old Value => Add New Value
        if len(current_value):
            self.object.attribute_value_ids = [(3, current_value.id, 0), (4, new_value.id, 0)]
        else:
            self.object.attribute_value_ids = [(4, new_value.id, 0)]
        # ====================================================================#
        # Update Template Attribute Values with Variants Values
        self._set_variants_value_ids(new_value.attribute_id)

    def _set_attribute_extra_price(self, attr_id, value):
        """
        Get Extra Price for an Attribute
        :param attr_id: str
        :param value: dict
        :return: void
        """
        # ====================================================================#
        # Check if a Value was Received
        if "price_extra" not in value.keys():
            return
        extra_price = float(value["price_extra"])
        # ====================================================================#
        # Walk on Template Attributes Values
        for attr_value in self.object.product_template_attribute_value_ids:
            # Filter Attribute Id
            if attr_value.attribute_id.id != attr_id:
                continue
            # Compare Values
            if abs(attr_value.price_extra - extra_price) < 1e-03:
                continue
            # Update Value
            attr_value.price_extra = extra_price

    @staticmethod
    def _set_attribute_value_langs(attr_value, field_values):
        """
        Update a Product Attribute Value Translations
        :param attr_value: product.attribute.value
        :param field_values: dict
        """
        for iso_code in TransHelper.get_extra_iso():
            iso_field_id = "value_" + iso_code
            if iso_field_id in field_values.keys():
                TransHelper.set(attr_value, 'name', iso_code, field_values[iso_field_id])

    def _set_variants_value_ids(self, attribute, active_test=True):
        """
        Get List of Product Value Ids for product Variants
        :param attribute: product.attribute
        :param active_test: bool
        :return: list
        """
        # ====================================================================#
        # Collect Variants Product Values Ids
        values_ids = []
        for variant in self.template.with_context(active_test=active_test).product_variant_ids:
            for value in variant.attribute_value_ids.filtered(lambda v: v.attribute_id.id == attribute.id):
                values_ids += [value.id]
        # ====================================================================#
        # Update Product Template Attribute Values Ids
        LinesHelper.set(self.template, attribute, values_ids)
        return values_ids
