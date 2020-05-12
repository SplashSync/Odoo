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

from splashpy import const, Framework
from splashpy.componants import FieldFactory
from odoo.addons.splashsync.helpers import M2MHelper, M2OHelper


class ProductsRelations:
    """
    Access to product Relationnal Fields
    """

    def buildRelationFields(self):
        # ==================================================================== #
        # Product Main category
        FieldFactory.create(const.__SPL_T_VARCHAR__, "categ_id", "Categorie Id")
        FieldFactory.microData("http://schema.org/Product", "classificationId")
        FieldFactory.isNotTested()
        FieldFactory.create(const.__SPL_T_VARCHAR__, "categ", "Categorie")
        FieldFactory.microData("http://schema.org/Product", "classification")
        FieldFactory.isNotTested()

        # ==================================================================== #
        # Website category
        if "public_categ_ids" in self.getModel().fields_get():
            FieldFactory.create(const.__SPL_T_VARCHAR__, "public_categ_ids", "Categorie Id")
            FieldFactory.microData("http://schema.org/Product", "publicCategoryId")
            FieldFactory.isNotTested()
            FieldFactory.create(const.__SPL_T_VARCHAR__, "public_categ", "Public Categorie")
            FieldFactory.microData("http://schema.org/Product", "publicCategory")
            FieldFactory.isNotTested()

    def getRelationFields(self, index, field_id):
        # Check if Relation Field...
        if not self.isRelationFields(field_id):
            return
        # ==================================================================== #
        # Categorie
        if field_id == "categ_id":
            self._out[field_id] = M2OHelper.get_id(self.object, "categ_id")
            self._in.__delitem__(index)
        if field_id == "categ":
            self._out[field_id] = M2OHelper.get_name(self.object, "categ_id")
            self._in.__delitem__(index)
        # ==================================================================== #
        # Public Categories
        if field_id == "public_categ_ids":
            self._out[field_id] = M2MHelper.get_ids(self.object, "public_categ_ids")
            self._in.__delitem__(index)
        if field_id == "public_categ":
            self._out[field_id] = M2MHelper.get_names(self.object, "public_categ_ids")
            self._in.__delitem__(index)

    def setRelationFields(self, field_id, field_data):
        # Check if Relation Field...
        if not self.isRelationFields(field_id):
            return
        # ==================================================================== #
        # Categorie
        if field_id == "categ_id":
            M2OHelper.set_id(self.object, "categ_id", field_data, domain="product.category")
            self._in.__delitem__(field_id)
        if field_id == "categ":
            M2OHelper.set_name(self.object, "categ_id", field_data, domain="product.category")
            self._in.__delitem__(field_id)
        # ==================================================================== #
        # Public Categories
        if field_id == "public_categ_ids":
            M2MHelper.set_ids(self.object, "public_categ_ids", field_data, domain="product.public.category")
            self._in.__delitem__(field_id)
        if field_id == "public_categ":
            M2MHelper.set_names(self.object, "public_categ_ids", field_data, domain="product.public.category")
            self._in.__delitem__(field_id)

    @staticmethod
    def isRelationFields(field_id):
        if field_id in [
            "categ_id", "categ",
            "public_categ_ids", "public_categ"
        ]:
            return True
        return False


