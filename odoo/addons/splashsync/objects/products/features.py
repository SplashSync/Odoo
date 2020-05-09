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

from odoo import http
from splashpy import const, Framework
from splashpy.componants import FieldFactory
from odoo.addons.splashsync.helpers import AttributesHelper, LinesHelper, ValuesHelper


class ProductsFeatures:
    """
    Access to product Features Fields
    """

    # Static Prefix for Feature Attributes
    prefix = "__feature_id__"

    def buildFeaturesFields(self):
        from odoo.addons.splashsync.helpers import TransHelper
        # ====================================================================#
        # Set default System Language
        FieldFactory.setDefaultLanguage(TransHelper.get_default_iso())
        # ====================================================================#
        # Walk on Available Attributes
        for attribute in ProductsFeatures.find_all():
            # ====================================================================#
            # Walk on Available Languages
            for iso_code, lang_name in TransHelper.get_all().items():
                # ==================================================================== #
                # Product Feature Field
                FieldFactory.create(const.__SPL_T_VARCHAR__, self.encode(attribute), attribute.display_name)
                FieldFactory.group("Features")
                FieldFactory.microData("http://schema.org/Product", attribute.name)
                # ==================================================================== #
                # Add Language Params
                FieldFactory.description("["+lang_name+"] "+attribute.display_name)
                FieldFactory.setMultilang(iso_code)
                # ==================================================================== #
                # Filter Variants Attributes During Tests
                if Framework.isDebugMode() and attribute.name in AttributesHelper.attr_test:
                    FieldFactory.isNotTested()
                if iso_code != TransHelper.get_default_iso():
                    FieldFactory.association(self.encode(attribute))

    def getFeaturesFields(self, index, field_id):
        """
        Get Product Attributes List
        :param index: str
        :param field_id: str
        :return: None
        """
        # ==================================================================== #
        # Check field_id this Feature Field...
        attr_id = self.decode(field_id)
        if attr_id is None:
            return
        self._in.__delitem__(index)
        self._out[field_id] = None
        # ==================================================================== #
        # Check if Product has Attribute Value
        for attr_value in self.object.attribute_value_ids:
            if attr_value.attribute_id.id == attr_id:
                self._out[field_id] = attr_value.name
                self.__getFeatureTranslatedFields(field_id, attr_value)
                return
        # ==================================================================== #
        # Check if Product has Feature Value
        for attr_value in self.template.valid_product_attribute_value_ids:
            if attr_value.attribute_id.id == attr_id:
                self._out[field_id] = attr_value.name
                self.__getFeatureTranslatedFields(field_id, attr_value)
                return
        # ==================================================================== #
        # Complete Not Found Feature Translations
        self.__isEmptyFeatureTranslatedFields(field_id)

    def setFeatureFields(self, field_id, field_data):
        """
        Update Product Attributes Values
        :param field_id: str
        :param field_data: hash
        :return: None
        """
        # ==================================================================== #
        # Check field_id this Feature Field...
        attr_id = self.decode(field_id)
        if attr_id is None:
            return
        self._in.__delitem__(field_id)
        # ==================================================================== #
        # Check if Product has Feature Value
        attr_lines = self.template.attribute_line_ids.filtered(
            lambda l: l.attribute_id.create_variant == "no_variant" and l.attribute_id.id == attr_id
        )
        for attr_line in attr_lines:
            # ==================================================================== #
            # Find or Create Attribute Value
            new_value = ValuesHelper.touch(attr_line.attribute_id, field_data, True)
            # ==================================================================== #
            # Empty Value or Creation Fail => Remove Product Attribute
            if new_value is None:
                self.template.attribute_line_ids = [(3, attr_line.id, 0)]
                self.__isEmptyFeatureTranslatedFields(field_id)
                return
            # ====================================================================#
            # If Values are Different => Update Values
            if len(attr_line.value_ids) != 1 or new_value.id != attr_line.value_ids[0].id:
                attr_line.value_ids = [(6, 0, [new_value.id])]
            # ====================================================================#
            # Update Product Attribute Translations
            self.__setFeatureTranslatedFields(field_id, new_value)
            return
        # ==================================================================== #
        # Add Product Feature Value
        if field_data is not None and len(str(field_data)) > 0:
            # Find or Create Attribute Value
            new_value = ValuesHelper.touch(AttributesHelper.load(attr_id), str(field_data), True)
            # for variant in self.object.product_variant_ids:
            LinesHelper.add(self.template, new_value)
            self.__setFeatureTranslatedFields(field_id, new_value)
        # ==================================================================== #
        # Complete Empty Feature Translations
        else:
            self.__isEmptyFeatureTranslatedFields(field_id)

    # ====================================================================#
    # Products Feature Field Ids Management
    # ====================================================================#

    @staticmethod
    def find_all():
        """
        Get List of All Available Attributes Types
        :return: dict
        """
        return http.request.env["product.attribute"].search([("create_variant", "=", "no_variant")], order="id")

    # ====================================================================#
    # Products Feature Field Ids Management
    # ====================================================================#

    def encode(self, attribute):
        """
        Decode Filed Id to Extract Pointed Attribute Id
        :param attribute: product.attribute
        :return: string
        """
        return ProductsFeatures.prefix + str(attribute.id)

    def decode(self, field_id):
        """
        Decode Filed Id to Extract Pointed Attribute Id
        :param field_id: str
        :return: None|int
        """
        if not isinstance(field_id, str) or field_id.find(ProductsFeatures.prefix) != 0:
            return None
        try:
            return int(field_id[len(ProductsFeatures.prefix): len(field_id)])
        except:
            return None

    # ====================================================================#
    # Products Feature Translations Management
    # ====================================================================#

    def __getFeatureTranslatedFields(self, field_id, attr_value):
        from odoo.addons.splashsync.helpers import TransHelper
        for iso_code in TransHelper.get_extra_iso():
            iso_field_id = field_id+"_"+iso_code
            for key, val in self._in.copy().items():
                if iso_field_id != val:
                    continue
                self._out[iso_field_id] = TransHelper.get(attr_value, 'name', iso_code, attr_value.name)
                self._in.__delitem__(key)

    def __setFeatureTranslatedFields(self, field_id, attr_value):
        from odoo.addons.splashsync.helpers import TransHelper
        for iso_code in TransHelper.get_extra_iso():
            iso_field_id = field_id+"_"+iso_code
            if iso_field_id not in self._in.keys():
                continue
            TransHelper.set(attr_value, 'name', iso_code, self._in[iso_field_id])
            self._in.__delitem__(iso_field_id)

    def __isEmptyFeatureTranslatedFields(self, field_id):
        from odoo.addons.splashsync.helpers import TransHelper
        for iso_code in TransHelper.get_extra_iso():
            iso_field_id = field_id+"_"+iso_code
            # Read Mode
            for key, val in self._in.copy().items():
                if iso_field_id != val:
                    continue
                self._out[iso_field_id] = ""
                self._in.__delitem__(key)
            # Write Mode
            if iso_field_id in self._in.keys():
                self._in.__delitem__(iso_field_id)
