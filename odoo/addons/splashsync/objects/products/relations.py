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
    Access to product Relational Fields
    """

    # Product Many2One Attributes Definition
    m2o_rel = {
        # ==================================================================== #
        # Product Brand
        "product_brand": {
            "item_type": "http://schema.org/Product",
            "item_prop": "brand",
            "model": "product.brand",
            "nullable": True,
        },
        # ==================================================================== #
        # Product Inventory Stock
        "property_stock_inventory": {
            "item_type": "http://schema.org/Product",
            "item_prop": "stockInventory",
            "model": "stock.location",
            "nullable": True,
        },
        # ==================================================================== #
        # Product Production Stock
        "property_stock_production": {
            "item_type": "http://schema.org/Product",
            "item_prop": "stockProduction",
            "model": "stock.location",
            "nullable": True,
        }
    }

    # Product Many2Many Attributes Definition
    m2m_rel = {
        # ==================================================================== #
        # Product Routes
        "route": {
            "item_type": "http://schema.org/Product",
            "item_prop": "routes",
            "model": "stock.location.route",
        },
        # ==================================================================== #
        # Public Categories
        "public_categ": {
            "item_type": "http://schema.org/Product",
            "item_prop": "publicCategory",
            "model": "product.public.category",
        }
    }

    def buildProductsM2ORelationsFields(self):
        """
        Product Many2One Attributes Automatic Links
        :return: none
        """
        allFields = self.getModel().fields_get()
        for autoId in self.m2o_rel:
            if autoId in allFields:
                FieldFactory.create(const.__SPL_T_VARCHAR__, autoId+"_id", allFields[autoId]["string"]+" ID")
                FieldFactory.microData(self.m2o_rel[autoId]["item_type"], self.m2o_rel[autoId]["item_prop"] + "Id")
                FieldFactory.group("Relations")
                FieldFactory.isReadOnly()
                FieldFactory.create(const.__SPL_T_VARCHAR__, autoId, allFields[autoId]["string"])
                FieldFactory.group("Relations")
                FieldFactory.addChoices(M2OHelper.get_name_values(self.m2o_rel[autoId]["model"]))
                FieldFactory.microData(self.m2o_rel[autoId]["item_type"], self.m2o_rel[autoId]["item_prop"])
                FieldFactory.isNotTested()

    def buildProductsM2MRelationsFields(self):
        """
        Product Many2Many Attributes Automatic Links
        :return: none
        """
        allFields = self.getModel().fields_get()
        for autoId in self.m2m_rel:
            autoIds = autoId+"_ids"
            if autoIds in allFields:
                FieldFactory.create(const.__SPL_T_INLINE__, autoId+"_ids", allFields[autoIds]["string"]+" IDS")
                FieldFactory.microData(self.m2m_rel[autoId]["item_type"], self.m2m_rel[autoId]["item_prop"] + "Id")
                FieldFactory.group("Relations")
                FieldFactory.isReadOnly()
                FieldFactory.create(const.__SPL_T_INLINE__, autoId, allFields[autoIds]["string"])
                FieldFactory.group("Relations")
                FieldFactory.addChoices(M2OHelper.get_name_values(self.m2m_rel[autoId]["model"]))
                FieldFactory.microData(self.m2m_rel[autoId]["item_type"], self.m2m_rel[autoId]["item_prop"])
                FieldFactory.isNotTested()

    def buildProductsRelationsFields(self):
        # ==================================================================== #
        # Product Main category
        FieldFactory.create(const.__SPL_T_VARCHAR__, "categ_id", "Categorie Id")
        FieldFactory.microData("http://schema.org/Product", "classificationId")
        FieldFactory.isReadOnly()
        FieldFactory.create(const.__SPL_T_VARCHAR__, "categ", "Categorie")
        FieldFactory.microData("http://schema.org/Product", "classification")
        FieldFactory.addChoices(M2OHelper.get_name_values("product.category"))
        FieldFactory.isNotTested()
        allFields = self.getModel().fields_get()
        # ==================================================================== #
        # Website Alternate Products
        if "alternative_product_ids" in allFields:
            FieldFactory.create(const.__SPL_T_VARCHAR__, "alternative_products", "Alternate Products Names")
            FieldFactory.microData("http://schema.org/Product", "alternateModels")
            FieldFactory.isNotTested()
        # ==================================================================== #
        # Website Accessory Products
        if "accessory_product_ids" in allFields:
            FieldFactory.create(const.__SPL_T_VARCHAR__, "accessory_products", "Accessory Products Names")
            FieldFactory.microData("http://schema.org/Product", "crossellModels")
            FieldFactory.isNotTested()
        # ==================================================================== #
        # Allowed Companies
        if "ons_allowed_company_ids" in allFields:
            FieldFactory.create(const.__SPL_T_VARCHAR__, "company_ids", "Companies IDs")
            FieldFactory.microData("http://schema.org/Product", "allowedCompanies")
            FieldFactory.isNotTested()
            FieldFactory.create(const.__SPL_T_VARCHAR__, "company_names", "Companies Names")
            FieldFactory.microData("http://schema.org/Product", "allowedCompaniesNames")
            FieldFactory.isNotTested()
        # ==================================================================== #
        # [Point of Sale] POS Category
        if "pos_categ_id" in allFields:
            FieldFactory.create(const.__SPL_T_VARCHAR__, "pos_categ_id", "POS Category Id")
            FieldFactory.microData("http://schema.org/Product", "posCategoryId")
            FieldFactory.isReadOnly()
            FieldFactory.create(const.__SPL_T_VARCHAR__, "pos_categ", "POS Category")
            FieldFactory.microData("http://schema.org/Product", "posCategory")
            FieldFactory.addChoices(M2OHelper.get_name_values("pos.category"))
            FieldFactory.isNotTested()
        # ==================================================================== #
        # [MY LED] Product Tags
        if "tag_ids" in allFields:
            FieldFactory.create(const.__SPL_T_VARCHAR__, "tag_id", "Tag Id")
            FieldFactory.microData("http://schema.org/Product", "tagId")
            FieldFactory.addChoices(M2OHelper.get_name_values("product.tag"))
            FieldFactory.isWriteOnly()
            FieldFactory.isNotTested()
            FieldFactory.create(const.__SPL_T_VARCHAR__, "tag_id", "Tag Ids")
            FieldFactory.microData("http://schema.org/Product", "tagIds")
            FieldFactory.addChoices(M2OHelper.get_name_values("product.tag"))
            FieldFactory.isNotTested()
        # ==================================================================== #
        # [MY LED] ONS Product Type
        if "ons_product_type" in allFields:
            FieldFactory.create(const.__SPL_T_VARCHAR__, "ons_product_type", "ONS Product Type")
            FieldFactory.microData("http://schema.org/Product", "onsProductTypeCodeName")
            FieldFactory.addChoices(M2OHelper.get_name_values("product.category"))
            FieldFactory.isNotTested()

    def getProductsM2ORelationsFields(self, index, field_id):
        """
        Read Product Many2One Relation
        """
        for autoId in self.m2o_rel:
            if field_id == autoId+"_id":
                self._out[field_id] = M2OHelper.get_id(self.object, autoId)
                self._in.__delitem__(index)
            if field_id == autoId:
                self._out[field_id] = M2OHelper.get_name(self.object, autoId)
                self._in.__delitem__(index)

    def getProductsM2MRelationsFields(self, index, field_id):
        """
        Read Product Many2Many Relation
        """
        for autoId in self.m2m_rel:
            autoIds = autoId + "_ids"
            if field_id == autoIds:
                self._out[field_id] = M2MHelper.get_ids(self.object, autoIds)
                self._in.__delitem__(index)
            if field_id == autoId:
                self._out[field_id] = M2MHelper.get_names(self.object, autoIds)
                self._in.__delitem__(index)

    def getProductsRelationsFields(self, index, field_id):
        # Check if Relation Field...
        if not self.isProductRelationFields(field_id):
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
        # [Point of Sale] POS Category
        if field_id == "pos_categ_id":
            self._out[field_id] = M2OHelper.get_id(self.object, "pos_categ_id")
            self._in.__delitem__(index)
        if field_id == "pos_categ":
            self._out[field_id] = M2OHelper.get_name(self.object, "pos_categ_id")
            self._in.__delitem__(index)
        # ==================================================================== #
        # [MY LED] Product Tags
        if field_id == "tag_ids":
            self._out[field_id] = M2OHelper.get_name(self.object, "tag_ids")
            self._in.__delitem__(index)
        # ==================================================================== #
        # [MY LED] ONS Product Type
        if field_id == "ons_product_type":
            self._out[field_id] = M2OHelper.get_name(self.object, "ons_product_type")
            self._in.__delitem__(index)

    def setProductsM2ORelationsFields(self, field_id, field_data):
        """
        Write Product Many2One Relation
        """
        for autoId in self.m2o_rel:
            config = self.m2o_rel[autoId]
            if field_id == autoId+"_id":
                M2OHelper.set_id(self.object, autoId, field_data, domain=config["model"], nullable=config["nullable"])
                self._in.__delitem__(field_id)
            if field_id == autoId:
                M2OHelper.set_name(self.object, autoId, field_data, domain=config["model"], nullable=config["nullable"])
                self._in.__delitem__(field_id)

    def setProductsM2MRelationsFields(self, field_id, field_data):
        """
        Write Product Many2Many Relation
        """
        for autoId in self.m2m_rel:
            autoIds = autoId + "_ids"
            config = self.m2m_rel[autoId]
            if field_id == autoIds:
                M2MHelper.set_ids(self.object, autoIds, field_data, domain=config["model"])
                self._in.__delitem__(field_id)
            if field_id == autoId:
                M2MHelper.set_names(self.object, autoIds, field_data, domain=config["model"])
                self._in.__delitem__(field_id)

    def setProductsRelationsFields(self, field_id, field_data):
        # Check if Relation Field...
        if not self.isProductRelationFields(field_id):
            return
        # ==================================================================== #
        # Category
        if field_id == "categ_id":
            M2OHelper.set_id(self.object, "categ_id", field_data, domain="product.category", nullable=False)
            self._in.__delitem__(field_id)
        if field_id == "categ":
            M2OHelper.set_name(self.object, "categ_id", field_data, domain="product.category", nullable=False)
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
        # [Point of Sale] POS Category
        if field_id == "pos_categ_id":
            M2OHelper.set_id(self.object, "pos_categ_id", field_data, domain="pos.category")
            self._in.__delitem__(field_id)
        if field_id == "pos_categ":
            M2OHelper.set_name(self.object, "pos_categ_id", field_data, domain="pos.category")
            self._in.__delitem__(field_id)
        # ==================================================================== #
        # [MY LED] Product Tags
        if field_id == "tag_id":
            M2MHelper.set_names(
                self.object,
                "tag_ids",
                '["'+field_data+'"]' if isinstance(field_data, str) else None,
                domain="product.tag"
            )
            self._in.__delitem__(field_id)
        if field_id == "tag_ids":
            M2MHelper.set_names(self.object, "tag_ids", field_data, domain="product.tag")
            self._in.__delitem__(field_id)
        # ==================================================================== #
        # [MY LED] ONS Product Type
        if field_id == "ons_product_type":
            M2OHelper.set_name(self.template, "ons_product_type", field_data, domain="product.category")
            self._in.__delitem__(field_id)

    @staticmethod
    def isProductRelationFields(field_id):
        if field_id in [
            "categ_id", "categ",
            "pos_categ_id", "pos_categ",
            "alternative_products", "accessory_products",
            "company_ids", "company_names",
            "tag_id", "tag_ids",
            "ons_product_type"
        ]:
            return True

        return False


