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
        FieldFactory.isReadOnly()
        FieldFactory.create(const.__SPL_T_VARCHAR__, "categ", "Categorie")
        FieldFactory.microData("http://schema.org/Product", "classification")
        FieldFactory.addChoices(M2OHelper.get_name_values("product.category"))
        FieldFactory.isNotTested()
        # ==================================================================== #
        # Product Routes
        FieldFactory.create(const.__SPL_T_VARCHAR__, "route_ids", "Routes Ids")
        FieldFactory.microData("http://schema.org/Product", "routesId")
        FieldFactory.isReadOnly()
        FieldFactory.create(const.__SPL_T_VARCHAR__, "routes", "Routes")
        FieldFactory.microData("http://schema.org/Product", "routes")
        FieldFactory.isNotTested()
        # ==================================================================== #
        # Website category
        if "public_categ_ids" in self.getModel().fields_get():
            FieldFactory.create(const.__SPL_T_VARCHAR__, "public_categ_ids", "Categorie Id")
            FieldFactory.microData("http://schema.org/Product", "publicCategoryId")
            FieldFactory.isReadOnly()
            FieldFactory.create(const.__SPL_T_INLINE__, "public_categ", "Public Categorie")
            FieldFactory.microData("http://schema.org/Product", "publicCategory")
            FieldFactory.addChoices(M2OHelper.get_name_values("product.public.category"))
            FieldFactory.isNotTested()
        # ==================================================================== #
        # Website Alternate Products
        if "alternative_product_ids" in self.getModel().fields_get():
            FieldFactory.create(const.__SPL_T_VARCHAR__, "alternative_products", "Alternate Products Names")
            FieldFactory.microData("http://schema.org/Product", "alternateModels")
            FieldFactory.isNotTested()
        # ==================================================================== #
        # Website Accessory Products
        if "accessory_product_ids" in self.getModel().fields_get():
            FieldFactory.create(const.__SPL_T_VARCHAR__, "accessory_products", "Accessory Products Names")
            FieldFactory.microData("http://schema.org/Product", "crossellModels")
            FieldFactory.isNotTested()
        # ==================================================================== #
        # Allowed Companies
        if "ons_allowed_company_ids" in self.getModel().fields_get():
            FieldFactory.create(const.__SPL_T_VARCHAR__, "company_ids", "Companies IDs")
            FieldFactory.microData("http://schema.org/Product", "allowedCompanies")
            FieldFactory.isNotTested()
            FieldFactory.create(const.__SPL_T_VARCHAR__, "company_names", "Companies Names")
            FieldFactory.microData("http://schema.org/Product", "allowedCompaniesNames")
            FieldFactory.isNotTested()
        # ==================================================================== #
        # Product Brand
        if "product_brand_id" in self.getModel().fields_get():
            FieldFactory.create(const.__SPL_T_VARCHAR__, "product_brand_id", "Brand Id")
            FieldFactory.microData("http://schema.org/Product", "brandId")
            FieldFactory.isReadOnly()
            FieldFactory.create(const.__SPL_T_VARCHAR__, "product_brand", "Brand")
            FieldFactory.microData("http://schema.org/Product", "brand")
            FieldFactory.addChoices(M2OHelper.get_name_values("product.brand"))
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
        # Routes
        if field_id == "route_ids":
            self._out[field_id] = M2MHelper.get_ids(self.object, "route_ids")
            self._in.__delitem__(index)
        if field_id == "routes":
            self._out[field_id] = M2MHelper.get_names(self.object, "route_ids")
            self._in.__delitem__(index)
        # ==================================================================== #
        # Public Categories
        if field_id == "public_categ_ids":
            self._out[field_id] = M2MHelper.get_ids(self.object, "public_categ_ids")
            self._in.__delitem__(index)
        if field_id == "public_categ":
            self._out[field_id] = M2MHelper.get_names(self.object, "public_categ_ids")
            self._in.__delitem__(index)
        # ==================================================================== #
        # Website Alternate Products
        if field_id == "alternative_products":
            self._out[field_id] = M2MHelper.get_names(self.object, "alternative_product_ids")
            self._in.__delitem__(index)
        # ==================================================================== #
        # Website Accessory Products
        if field_id == "accessory_products":
            self._out[field_id] = M2MHelper.get_names(self.object, "accessory_product_ids")
            self._in.__delitem__(index)
        # ==================================================================== #
        # Allowed Companies
        if field_id == "company_ids":
            self._out[field_id] = M2MHelper.get_ids(self.object, "ons_allowed_company_ids")
            self._in.__delitem__(index)
        if field_id == "company_names":
            self._out[field_id] = M2MHelper.get_names(self.object, "ons_allowed_company_ids")
            self._in.__delitem__(index)
        # ==================================================================== #
        # Product Brand
        if field_id == "product_brand_id":
            self._out[field_id] = M2OHelper.get_id(self.object, "product_brand_id")
            self._in.__delitem__(index)
        if field_id == "product_brand":
            self._out[field_id] = M2OHelper.get_name(self.object, "product_brand_id")
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
        # Routes
        if field_id == "route_ids":
            M2MHelper.set_ids(self.object, "route_ids", field_data, domain="stock.location.route")
            self._in.__delitem__(field_id)
        if field_id == "routes":
            M2MHelper.set_names(self.object, "route_ids", field_data, domain="stock.location.route")
            self._in.__delitem__(field_id)
        # ==================================================================== #
        # Public Categories
        if field_id == "public_categ_ids":
            M2MHelper.set_ids(self.object, "public_categ_ids", field_data, domain="product.public.category")
            self._in.__delitem__(field_id)
        if field_id == "public_categ":
            M2MHelper.set_names(self.object, "public_categ_ids", field_data, domain="product.public.category")
            self._in.__delitem__(field_id)
        # ==================================================================== #
        # Website Alternate Products
        if field_id == "alternative_products":
            M2MHelper.set_names(self.object, "alternative_product_ids", field_data, domain="product.template")
            self._in.__delitem__(field_id)
        # ==================================================================== #
        # Website Alternate Products
        if field_id == "accessory_products":
            M2MHelper.set_names(self.object, "accessory_product_ids", field_data, domain="product.product")
            self._in.__delitem__(field_id)
        # ==================================================================== #
        # Allowed Companies
        if field_id == "company_ids":
            M2MHelper.set_ids(self.object, "ons_allowed_company_ids", field_data, domain="res.company")
            self._in.__delitem__(field_id)
        if field_id == "company_names":
            M2MHelper.set_names(self.object, "ons_allowed_company_ids", field_data, domain="res.company")
            self._in.__delitem__(field_id)
        # ==================================================================== #
        # Product Brand
        if field_id == "product_brand_id":
            M2OHelper.set_id(self.object, "product_brand_id", field_data, domain="product.brand")
            self._in.__delitem__(field_id)
        if field_id == "product_brand":
            M2OHelper.set_name(self.object, "product_brand_id", field_data, domain="product.brand")
            self._in.__delitem__(field_id)

    @staticmethod
    def isRelationFields(field_id):
        if field_id in [
            "categ_id", "categ",
            "route_ids", "routes",
            "public_categ_ids", "public_categ",
            "alternative_products", "accessory_products",
            "company_ids", "company_names",
            "product_brand_id", "product_brand",
        ]:
            return True
        return False


