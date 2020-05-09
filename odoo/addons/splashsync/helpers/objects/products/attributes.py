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

    # List of Attributes Modes used For Features
    attr_wnva = ['no_variant']

    # Names of Unit Tests Variants Codes
    attr_test = ['VariantA', 'VariantB']

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
    def is_wnva(attribute):
        """
        Check if Product Attributes is 'Without No Varriant Atrribute"
        :param attribute: product.attribute
        :return: bool
        """
        return attribute.create_variant in AttributesHelper.attr_wnva

    @staticmethod
    def touch(attr_code, is_wnva):
        """
        Find or Create a Product Attributes by Code

        :param attr_code: str       Attribute Code name
        :param is_wnva: bool        No Variant Attribute?

        :return: None, product.attribute
        """
        # ====================================================================#
        # Search for Attribute by Code
        attribute = AttributesHelper.find(attr_code, is_wnva)
        # ====================================================================#
        # Create Attribute if Not Found
        if attribute is None:
            attribute = AttributesHelper.create(attr_code, is_wnva)
        return attribute

    @staticmethod
    def find(attr_code, is_wnva):
        """
        Find Product Attributes by Code

        :param attr_code: str       Attribute Code name
        :param is_wnva: bool        No Variant Attribute?

        :return: None, product.attribute
        """
        # ==================================================================== #
        # Prepare Search Filters
        search_filters = [
            ("name", '=ilike', attr_code),
            ("create_variant", 'in' if is_wnva else 'not in', AttributesHelper.attr_wnva)
        ]
        # ==================================================================== #
        # Search For Attribute
        records = AttributesHelper.getModel().search(search_filters)
        if len(records) > 0:
            return records[0]
        return None

    @staticmethod
    def load(attr_id):
        """
        Find Product Attributes by Id
        :param attr_id: int       Attribute Id
        :return: None, product.attribute
        """
        # ==================================================================== #
        # Search For Attribute
        records = AttributesHelper.getModel().browse([attr_id])
        if len(records) == 1:
            return records[0]
        return None

    @staticmethod
    def create(attr_code, is_wnva):
        """
        Create a Product Attribute

        :param attr_code: str       Attribute Code name
        :param is_wnva: bool        No Variant Attribute?

        :return: None, product.attribute
        """
        return AttributesHelper.getModel().create({
            "name": attr_code,
            "type": "select",
            "create_variant": "no_variant" if is_wnva else "always"
        })

    # ====================================================================#
    # Odoo ORM Access
    # ====================================================================#

    @staticmethod
    def getModel():
        """Get Product Attributes Model Class"""
        return http.request.env["product.attribute"]


class ValuesHelper:
    """Collection of Static Functions to Manage Product Attributes Values"""

    @staticmethod
    def touch(attribute, attr_value, is_wnva):
        """
        Find or Create a Product Attributes Value by Code & Value

        :param attribute: str, product.attribute       Attribute Code Name or Product Attribute
        :param attr_value: None, str                Attribute Value
        :param is_wnva: bool        No Variant Attribute?

        :return: None, product.attribute.value
        """
        # ====================================================================#
        # Detect Empty Attribute Values
        if attr_value is None or len(str(attr_value)) < 1:
            return None
        # ====================================================================#
        # STR? Search or Create Attribute by Code
        if isinstance(attribute, str):
            attribute = AttributesHelper.touch(attribute, is_wnva)
        if attribute is None:
            Framework.log().error("An Error Occurred while Loading Attribute")
            return None
        # ====================================================================#
        # Search for Value in Attribute
        values = attribute.value_ids.filtered(lambda r: r.name.lower() == attr_value.lower())
        if len(values) > 0:
            return values[0]
        # ====================================================================#
        # Crate New Value for Attribute
        return ValuesHelper.create(attribute, attr_value)

    @staticmethod
    def create(attribute, attr_value):
        """
        Create a Product Attribute Value
        :param attribute: product.attribute
        :param attr_value: str
        :return: product.attribute.value
        """
        return ValuesHelper.getModel().create({
            "name": attr_value,
            "attribute_id": attribute.id,
        })

    # ====================================================================#
    # Odoo ORM Access
    # ====================================================================#

    @staticmethod
    def getModel():
        """Get Product Attributes Value Model Class"""
        return http.request.env["product.attribute.value"]


class LinesHelper:
    """Collection of Static Functions to Manage Product Templates Attributes Lines"""

    @staticmethod
    def add(template, new_value):
        """
        Add a Product Template Attribute Value Line
        :param template: product.product, product.template
        :param new_value: product.attribute.value
        :return: None
        """
        # ====================================================================#
        # Create Product Attributes Line
        new_line = {
            "attribute_id": new_value.attribute_id.id,
            "value_ids": [new_value.id],
            "product_tmpl_id": template.id
        }
        # ====================================================================#
        # Add Attribute Line
        template.attribute_line_ids = [(0, 0, new_line)]

    @staticmethod
    def set(template, attribute, value_ids):
        """
        Add a Product Template Attribute Value Line

        :param template: product.product, product.template
        :param attribute: product.attribute
        :param value_ids: dict
        """
        # ====================================================================#
        # Filter Attributes Line on Attribute For Id
        filtered_lines = template.attribute_line_ids.filtered(
            lambda l: l.attribute_id.id == attribute.id
        )
        # ====================================================================#
        # Line Found but Empty Values
        if len(value_ids) == 0 and len(filtered_lines) > 0:
            template.attribute_line_ids = [(2, filtered_lines[0].id, 0)]
            return
        # ====================================================================#
        # Line NOT Found => Add New Value
        if len(filtered_lines) == 0:
            # Add Attribute Line
            new_line = {"attribute_id": attribute.id, "value_ids": value_ids, "product_tmpl_id": template.id}
            template.attribute_line_ids = [(0, 0, new_line)]
            return
        # ====================================================================#
        # Update Attribute Line
        filtered_lines[0].value_ids = [(6, 0, value_ids)]