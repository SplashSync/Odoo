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


class FeaturesHelper:
    """Collection of Static Functions to manage Product Features"""

    prefix = "feature_id_"

    @staticmethod
    def find_all():
        """ 
        Get List of All Available Attributes Types
        :return: dict
        """
        return http.request.env["product.attribute"].sudo().search([], order="id")

    # ====================================================================#
    # Products Feature Field Ids Management
    # ====================================================================#

    @staticmethod
    def encode_id(attribute):
        """
        Decode Filed Id to Extract Pointed Attribute Id
        :param attribute: product.attribute
        :return: string
        """
        return FeaturesHelper.prefix + str(attribute.id)

    @staticmethod
    def decode_id(field_id):
        """
        Decode Filed Id to Extract Pointed Attribute Id
        :param field_id: str
        :return: None|int
        """
        if not isinstance(field_id, str) or field_id.find(FeaturesHelper.prefix) != 0:
            return None
        try:
            return int(field_id[len(FeaturesHelper.prefix): len(field_id)])
        except:
            return None

    # ====================================================================#
    # Products Attributes Lines Management
    # ====================================================================#

    @staticmethod
    def add(template, new_value):
        """
        Add a Product Attribute Value
        :param template: product.template
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
    def update(template, new_value):
        """
        Update a Product Attribute Line
        :param template: product.template
        :param new_value: product.attribute.value
        :return: None
        """
        # ====================================================================#
        # Safety Check
        if new_value is None:
            Framework.log().error("Attribute Value is None!")
            return
        # ====================================================================#
        # Walk on Product Attributes Values
        for attribute_line in template.attribute_line_ids:
            # Filter Same Attribute
            if new_value.attribute_id.id != attribute_line.attribute_id.id:
                continue
            # If Values are Similar => Nothing to Do => Exit
            if new_value.id == attribute_line.value_ids[0].id:
                return
            # Update Attribute Value => Remove Old Value => Add New Value
            attribute_line.value_ids = [(3, attribute_line.value_ids[0].id, 0), (4, new_value.id, 0)]

            return

        # ====================================================================#
        # Attributes Value NOT Found => Add New Value
        template.product_template_attribute_value_ids = [(4, new_value.id, 0)]

    @staticmethod
    def remove(template, attribute_id):
        """
        Remove a Product Attribute Line
        :param template: product.template
        :param attribute_id: int
        :return: None
        """
        # ====================================================================#
        # Safety Check
        if not isinstance(attribute_id, int):
            Framework.log().error("Removed Attribute Id must be an Int!")
            return
        # ====================================================================#
        # Walk on Product Attributes Lines
        for attr_line in template.attribute_line_ids:
            # Filter Same Attribute
            if attribute_id != attr_line.attribute_id.id:
                continue
            # Update Attribute Value => Remove Old Value
            template.attribute_line_ids = [(3, attr_line.id, 0)]
