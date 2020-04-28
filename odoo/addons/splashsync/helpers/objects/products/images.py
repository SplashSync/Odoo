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
from collections import OrderedDict
from splashpy import Framework
from splashpy.helpers import ImagesHelper
#


class ProductImagesHelper:
    """Collection of Static Functions to manage Product Images"""

    prd_domain = "product.product"
    tmpl_domain = "product.template"
    img_domain = "product.image"

    # ====================================================================#
    # Products Images Management
    # ====================================================================#

    @staticmethod
    def get_values(product, value_id):
        """
        Get List of Images Values for given Field
        :param product: product.product
        :param value_id: str
        :return: dict
        """
        position = 1
        values = []
        from odoo.addons.splashsync.helpers import OddoFilesHelper
        # ====================================================================#
        # Read Product Main Image
        tmpl = product.product_tmpl_id[0]
        if isinstance(tmpl.image, bytes):
            if value_id == "cover":
                values += [True]
            elif value_id == "visible":
                values += [not bool(isinstance(product.image_variant, bytes))]
            elif value_id == "position":
                values += [position]
                position += 1
            elif value_id == "image":
                values += [ImagesHelper.encodeFromRaw(
                    tmpl.image,
                    "Main Image",
                    "main_image." + str(ImagesHelper.get_extension(tmpl.image, True)),
                    OddoFilesHelper.encode_file_path(ProductImagesHelper.tmpl_domain, tmpl.id, "image"),
                    OddoFilesHelper.get_image_url(ProductImagesHelper.tmpl_domain, tmpl.id, "image"),
                    True
                )]
        # ====================================================================#
        # Walk on Product Variants Images
        for variant in product.product_variant_ids.sorted(key=lambda r: r.id):
            # Verify if Image Exist
            if not isinstance(variant.image_variant, bytes):
                continue
            # Add Image Value
            if value_id == "cover":
                values += [False]
            elif value_id == "visible":
                values += [bool(variant.id == product.id)]
            elif value_id == "position":
                values += [position]
                position += 1
            elif value_id == "image":
                values += [ImagesHelper.encodeFromRaw(
                    variant.image_variant,
                    "Variant Image",
                    "variant_image." + str(ImagesHelper.get_extension(variant.image, True)),
                    OddoFilesHelper.encode_file_path(ProductImagesHelper.prd_domain, variant.id, "image_variant"),
                    OddoFilesHelper.get_image_url(ProductImagesHelper.prd_domain, variant.id, "image_variant"),
                    True
                )]
        # ====================================================================#
        # Walk on Product Images
        for tmpl_image in product.product_image_ids.sorted(key=lambda r: r.id):
            if value_id == "cover":
                values += [False]
            elif value_id == "visible":
                values += [True]
            elif value_id == "position":
                values += [position]
                position += 1
            elif value_id == "image":
                values += [ImagesHelper.encodeFromRaw(
                    tmpl_image.image,
                    tmpl_image.name,
                    tmpl_image.name + "." + str(ImagesHelper.get_extension(tmpl_image.image, True)),
                    OddoFilesHelper.encode_file_path(ProductImagesHelper.img_domain, tmpl_image.id, "image"),
                    OddoFilesHelper.get_image_url(ProductImagesHelper.img_domain, tmpl_image.id, "image"),
                    True
                )]

        return values

    @staticmethod
    def sort_images(images_list):
        """Sort Product Images by Position if Defined"""
        # ====================================================================#
        # Safety Checks
        if not isinstance(images_list, dict):
            return images_list
        # ====================================================================#
        # Ensure Position Defined on All Items
        for index, spl_image in images_list.items():
            if "position" not in spl_image.keys():
                return OrderedDict(sorted(images_list.items()))
        # ====================================================================#
        # Sort Received Images by Position
        images_sorted = sorted(images_list.values(), key=lambda r: int(r["position"]))
        return {i: images_sorted[i] for i in range(0, len(images_sorted))}

    @staticmethod
    def find_cover(images_list):
        """
        Find Product Cover Image
        :param images_list: dict
        :return: None|dict
        """
        return ProductImagesHelper.__find_first(images_list, True, None)

    @staticmethod
    def find_variant(images_list):
        """
        Find Product Variant Image
        :param images_list: dict
        :return: None|dict
        """
        # ====================================================================#
        # Identify Cover & First Visible
        cover_index, cover_image = ProductImagesHelper.find_cover(images_list)
        visible_index, visible_image = ProductImagesHelper.__find_first(images_list, None, True)
        # ====================================================================#
        # One of Them NOT found
        if cover_index is None or visible_index is None:
            return None, None
        # First Visible is Cover
        if cover_index == visible_index:
            return None, None
        # First Cover is Visible
        if ProductImagesHelper.is_visible(images_list[cover_index]):
            Framework.log().warn("Cover is Not First Image")
            return None, None

        return visible_index, visible_image

    @staticmethod
    def __find_first(images_list, is_cover, is_visible):
        """
        Find First Product Image that Match Criteria
        :param images_list: dict
        :param is_cover: None|bool
        :param is_visible: None|bool
        :return: None|dict
        """
        # ====================================================================#
        # Safety Checks
        if not isinstance(images_list, dict):
            return None, None
        # ====================================================================#
        # Walk on Received Images
        for index, spl_image in images_list.items():
            keys = spl_image.keys()
            if "image" not in keys:
                continue
            if is_cover is not None:
                if ProductImagesHelper.is_cover(spl_image) != is_cover:
                    continue
            if is_visible is not None:
                if ProductImagesHelper.is_visible(spl_image) != is_visible:
                    continue
            return index, spl_image["image"]

        return None, None

    @staticmethod
    def is_visible(image_item):
        return ProductImagesHelper.__is_flagged(image_item, "visible")

    @staticmethod
    def is_cover(image_item):
        return ProductImagesHelper.__is_flagged(image_item, "cover")

    @staticmethod
    def __is_flagged(image_item, property_name):
        # Safety Checks
        if not isinstance(image_item, dict):
            return False
        if property_name not in image_item.keys():
            return False
        if bool(int(image_item[property_name])):
            return True

        return False

    # ====================================================================#
    # Products Images Management
    # ====================================================================#

    @staticmethod
    def create_image(template):
        """
        Create a Product Image
        :param template: product.template
        :return: product.image
        """
        img_data = {"product_tmpl_id": template.id, "name": template.name}

        return ProductImagesHelper.getImgModel().create(img_data)

    # ====================================================================#
    # Odoo ORM Access
    # ====================================================================#

    @staticmethod
    def getImgModel():
        """Get Product Image Model Class"""
        return http.request.env[ProductImagesHelper.img_domain].sudo()

