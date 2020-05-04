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
from splashpy import Framework


class AttributesHelper:
    """Collection of Static Functions to manage Product Attributes"""

    attr_domain = "product.attribute"
    values_domain = "product.attribute.value"

    # ====================================================================#
    # Products Attributes Management
    # ====================================================================#

    @staticmethod
    def has_attr(product):
        """
        Check if Product has Variant Attributes
        :param product: product.product
        :return: bool
        """
        if len(product.attribute_value_ids) > 0:
            return True
        return False

    @staticmethod
    def get_attr_values(product, value_id):
        """
        Get List of Attributes Values for given Field
        :param product: product.product
        :param value_id: str
        :return: dict
        """
        values = []
        attr_ids = AttributesHelper.get_variation_attr_ids(product)
        # ====================================================================#
        # Verify if Product has Attributes
        if len(product.attribute_value_ids) == 0:
            return values
        # ====================================================================#
        # Walk on Product Attributes Values
        for attribute in product.attribute_value_ids.sorted(key=lambda r: r.attribute_id[0].id):
            # Filter Attributes that are NOT Variants Attributes
            if attribute.attribute_id[0].id not in attr_ids:
                continue
            # Collect Values
            if value_id == "value":
                values += [attribute.name]
            elif value_id == "code":
                values += [attribute.attribute_id[0].name]
            elif value_id == "name":
                values += [attribute.attribute_id[0].display_name]

        return values

    @staticmethod
    def get_variation_attr_ids(product):
        """
        Get List of Product Attributes Used for Variations
        :param product: product.product
        :return: list
        """
        attr_ids = []
        # ====================================================================#
        # Walk on Product Attributes Values to Collect Attributes Ids
        for value in product.attribute_value_ids:
            attr_ids += [value.attribute_id.id]

        # for line in product.valid_product_template_attribute_line_ids:
        #     if Framework.isDebugMode() or len(line.value_ids.ids) > 1:
        #         attr_ids += [line.attribute_id.id]

        return attr_ids

    @staticmethod
    def find_or_create_attr(attr_code):
        """Find or Create a Product Attributes by Code"""
        # ====================================================================#
        # Search for Attribute by Code
        attribute = AttributesHelper.find_attr(attr_code)
        # ====================================================================#
        # Create Attribute if Not Found
        if attribute is None:
            attribute = AttributesHelper.create_attr(attr_code)

        return attribute

    @staticmethod
    def find_attr(attr_code):
        """
        Find Product Attributes by Code
        :param attr_code: str
        :return: product.attribute
        """
        records = AttributesHelper.getAttrModel().name_search(attr_code, operator='=ilike')
        if len(records) > 0:
            for record in records:
                model = AttributesHelper.getAttrModel().browse([int(record[0])])
                if len(model) == 1:
                    return model

        return None

    @staticmethod
    def create_attr(attr_code):
        """
        Create a Product Attribute
        :param attr_code: str
        :return: product.attribute
        """
        attr_data = {"name": attr_code, "type": "select", "create_variant": "no_variant"}
        # if attr_code.find("color") > 0:
        #     attr_data["type"] = "color"

        return AttributesHelper.getAttrModel().create(attr_data)

    # ====================================================================#
    # Products Attributes Values Management
    # ====================================================================#

    @staticmethod
    def find_or_create_value(attr_code, attr_value):
        """
        Find or Create a Product Attributes Value by Code & Value
        :param attr_code: str
        :param attr_value: str
        :return: None, product.attribute.value
        """
        # ====================================================================#
        # Detect Empty Attribute Values
        if attr_value is None or len(str(attr_value)) < 1:
            Framework.log().warn("Empty Attribute Detected")
            return None
        # ====================================================================#
        # Search or Create Attribute by Code
        attribute = AttributesHelper.find_or_create_attr(attr_code)
        if attribute is None:
            Framework.log().error("An Error Occurred while Loading Attribute")
            return None
        # ====================================================================#
        # Search for Value in Attribute
        values = attribute.value_ids.filtered(lambda r: r.name.lower() == attr_value.lower())
        if len(values) > 0:
            for value in values:
                return value
        # ====================================================================#
        # Crate New Value for Attribute
        return AttributesHelper.create_value(attribute, attr_value)

    @staticmethod
    def create_value(attribute, attr_value):
        """
        Create a Product Attribute Value
        :param attribute: product.attribute
        :param attr_value: str
        :return: product.attribute.value
        """
        value_data = {
            "name": attr_value,
            "attribute_id": attribute.id,
        }
        return AttributesHelper.getValueModel().create(value_data)

    # ====================================================================#
    # Products Attributes Values Management
    # ====================================================================#

    @staticmethod
    def update_value(product, new_value):
        """
        Update a Product Attribute Value
        :param product: product.product
        :param new_value: product.attribute.value
        :return: None
        """
        # ====================================================================#
        # Safety Check
        if new_value is None:
            Framework.log().error("Attribute Value is None!")
            return
        # ====================================================================#
        # Walk on Product Current Attributes Values
        for current_value in product.attribute_value_ids:
            # Filter Same Attribute
            if new_value.attribute_id.id != current_value.attribute_id.id:
                continue
            # If Values are Similar => Nothing to Do => Exit
            if new_value.id == current_value.id:
                return
            # Update Attribute Value => Remove Old Value => Add New Value
            product.attribute_value_ids = [(3, current_value.id, 0), (4, new_value.id, 0)]

            return

        # ====================================================================#
        # Attributes Value NOT Found => Add New Value
        product.attribute_value_ids = [(4, new_value.id, 0)]

    # ====================================================================#
    # Odoo ORM Access
    # ====================================================================#

    @staticmethod
    def getAttrModel():
        """Get Product Attributes Model Class"""
        return http.request.env[AttributesHelper.attr_domain].sudo()

    @staticmethod
    def getValueModel():
        """Get Product Attributes Value Model Class"""
        return http.request.env[AttributesHelper.values_domain].sudo()

