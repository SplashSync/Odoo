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
from odoo.addons.splashsync.helpers import ProductImagesHelper


class ProductsImages:
    """
    Access to product Images Fields
    """

    @staticmethod
    def buildImagesFields():
        # ==================================================================== #
        # Product Images
        FieldFactory.create(const.__SPL_T_IMG__, "image", "Image")
        FieldFactory.inlist("Images")
        FieldFactory.microData("http://schema.org/Product", "image")
        FieldFactory.isNotTested()

        # ==================================================================== #
        # Product Images => Image Position In List
        FieldFactory.create(const.__SPL_T_INT__, "position", "Position")
        FieldFactory.inlist("Images")
        FieldFactory.microData("http://schema.org/Product", "positionImage")
        FieldFactory.isNotTested()

        # ==================================================================== #
        # Product Images => Is Visible Image
        FieldFactory.create(const.__SPL_T_BOOL__, "visible", "Is Visible")
        FieldFactory.inlist("Images")
        FieldFactory.microData("http://schema.org/Product", "isVisibleImage")
        FieldFactory.isNotTested()

        # ==================================================================== #
        # Product Images => Is Cover
        FieldFactory.create(const.__SPL_T_BOOL__, "cover", "Is Cover")
        FieldFactory.inlist("Images")
        FieldFactory.microData("http://schema.org/Product", "isCover")
        FieldFactory.isNotTested()

    def getImagesFields(self, index, field_id):
        """
        Get Product Images List
        :param index: str
        :param field_id: str
        :return: None
        """
        # ==================================================================== #
        # Check field_id this Image Field...
        value_id = ListHelper.initOutput(self._out, "Images", field_id)
        if value_id is None:
            return
        # ==================================================================== #
        # Get Product Attributes Data
        img_values = ProductImagesHelper.get_values(self.object, value_id)
        for pos in range(len(img_values)):
            ListHelper.insert(self._out, "Images", field_id, "img-"+str(pos), img_values[pos])
        # # ==================================================================== #
        # # Force Attributes Ordering
        self._out["Images"] = OrderedDict(sorted(self._out["Images"].items()))
        self._in.__delitem__(index)

    def setImagesFields(self, field_id, field_data):
        """
        Update Product Images Values
        :param field_id: str
        :param field_data: hash
        :return: None
        """
        # Check if this field is Images List...
        if field_id != "Images":
            return
        # ====================================================================#
        # Sort Images List by Positions
        field_data = ProductImagesHelper.sort_images(field_data)

        # ====================================================================#
        # Update Main Image
        main_index, main_image = ProductImagesHelper.find_cover(field_data)
        self._in["image"] = main_image
        self.set_binary_data("image", self._in["image"], self.template)

        # ====================================================================#
        # Update Variant Image
        variant_index, self._in["image_variant"] = ProductImagesHelper.find_variant(field_data)
        self.set_binary_data("image_variant", self._in["image_variant"], self.object)

        # ====================================================================#
        # Fetch Current Product Images
        product_images = self.template.product_image_ids.sorted(key=lambda r: r.id)
        product_image_ids = []
        index_images = 0
        # ====================================================================#
        # Walk on Product Images
        if isinstance(field_data, dict):
            for index, spl_image in field_data.items():
                # ====================================================================#
                # Filter on Cover or Variant Images
                if index in [main_index, variant_index]:
                    continue
                # ====================================================================#
                # Filter on Visible Images
                if "visible" in spl_image and not bool(int(spl_image["visible"])):
                    continue
                # ====================================================================#
                # Load or Create Image
                try:
                    product_image = product_images[index_images]
                except:
                    product_image = ProductImagesHelper.create_image(self.template)
                # ====================================================================#
                # Update Image Name
                if str(spl_image["image"]["name"]).__len__() > 0:
                    product_image.name = spl_image["image"]["name"]
                else:
                    product_image.name = self.template.name
                # ====================================================================#
                # Update Image Contents
                self._in["image"] = spl_image["image"]
                self.set_binary_data("image", spl_image["image"], product_image)
                # Update loop metadata
                index_images += 1
                product_image_ids += [product_image.id]

        # ====================================================================#
        # Update Product Images
        self.template.product_image_ids = [(6, 0, product_image_ids)]

        self._in.__delitem__("Images")
