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
        # ====================================================================#
        # Verify if Product has Attributes
        if len(product.attribute_value_ids) == 0:
            return values
        # ====================================================================#
        # Walk on Product Attributes Values
        for attribute in product.attribute_value_ids.sorted(key=lambda r: r.attribute_id[0].id):
            if value_id == "value":
                values += [attribute.name]
            elif value_id == "code":
                values += [attribute.attribute_id[0].name]
            elif value_id == "name":
                values += [attribute.attribute_id[0].display_name]

        return values

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
        :return: ProductAttribute
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
        """Find or Create a Product Attributes Value by Code & Value"""
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

