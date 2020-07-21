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
from odoo.addons.splashsync.helpers import M2OHelper
from odoo.addons.splashsync.helpers import SupplierHelper

class ProductsSupplier:
    """
    Access to product First Supplier Fields
    """
    # Static List of First Supplier Field Ids
    supplierFields = ["supplier_name", "supplier_sku", "supplier_min_qty", "supplier_price"]

    def buildSupplierFields(self):
        # ==================================================================== #
        # Safety Check
        if "seller_ids" not in self.getModel().fields_get():
            return
        # ====================================================================#
        # First Supplier Name
        FieldFactory.create(const.__SPL_T_VARCHAR__, "supplier_name", "Supplier Name")
        FieldFactory.microData("http://schema.org/Product", "supplierName")
        FieldFactory.addChoices(M2OHelper.get_name_values(SupplierHelper.vendorDomain, SupplierHelper.filter))
        FieldFactory.isNotTested()
        # ====================================================================#
        # First Supplier Price
        FieldFactory.create(const.__SPL_T_DOUBLE__, "supplier_price", "Supplier Price")
        FieldFactory.microData("http://schema.org/Product", "supplierPrice")
        FieldFactory.association("supplier_name")
        # ====================================================================#
        # First Supplier SKU
        FieldFactory.create(const.__SPL_T_VARCHAR__, "supplier_sku", "Supplier SKU")
        FieldFactory.microData("http://schema.org/Product", "mpn")
        FieldFactory.association("supplier_name", "supplier_price")
        # ====================================================================#
        # First Supplier MOQ
        FieldFactory.create(const.__SPL_T_INT__, "supplier_min_qty", "Supplier MOQ")
        FieldFactory.microData("http://schema.org/Product", "supplierMinQty")
        FieldFactory.association("supplier_name", "supplier_price")

    def getSupplierFields(self, index, field_id):
        """
        Get Product First Supplier Fields
        :param index: str
        :param field_id: str
        :return: None
        """
        # ==================================================================== #
        # Check field_id this First Supplier Field...
        if not self.isSupplierField(field_id):
            return
        # ==================================================================== #
        # Read First Supplier Value
        self._out[field_id] = self.__get_supplier_values(field_id)
        self._in.__delitem__(index)

    def setSupplierFields(self, field_id, field_data):
        """
        Set Product First Supplier Fields
        :param field_id: str
        :param field_data: hash
        :return: None
        """
        # ==================================================================== #
        # Check field_id this First Supplier Field...
        if not self.isSupplierField(field_id):
            return
        # ====================================================================#
        # Try to fetch Current First Supplier
        supplier = SupplierHelper.first(self.object)
        # ====================================================================#
        # Try to Create if Valid Supplier Info Provided
        if supplier is None and self.__has_supplier_info():
            supplier = SupplierHelper.create(self.object, self._in["supplier_name"], self._in["supplier_price"])
        # ====================================================================#
        # Unable to Load/Create Supplier Info
        if supplier is None:
            self._in.__delitem__(field_id)
            return
        # ====================================================================#
        # Update Supplier Info
        return self.__set_supplier_values(field_id, field_data, supplier)

    def __get_supplier_values(self, value_id):
        """
        Get List of Attributes Values for given Field
        :param value_id: str
        :return: dict
        """
        # ====================================================================#
        # Load First Product Supplier Info
        supplier = SupplierHelper.first(self.object)
        if supplier is None:
            return None
        # ====================================================================#
        # Get Value
        if value_id == "supplier_name":
            return supplier.name.name
        elif value_id == "supplier_sku":
            return supplier.product_code
        elif value_id == "supplier_min_qty":
            return supplier.min_qty
        elif value_id == "supplier_price":
            return supplier.price

        return None

    def __set_supplier_values(self, field_id, field_data, supplier):
        """
        Set Product Supplier Fields
        :param field_id: str
        :param field_data: hash
        :param supplier: product.supplierinfo
        :return: None
        """
        # ====================================================================#
        # Set Value
        self._in.__delitem__(field_id)
        if field_id == "supplier_name":
            # ====================================================================#
            # Validate & Update Supplier Partner
            new_partner = M2OHelper.verify_name(field_data, "name", SupplierHelper.vendorDomain, SupplierHelper.filter)
            if new_partner is not None and new_partner > 0:
                M2OHelper.set_name(
                    supplier, "name", field_data,
                    domain=SupplierHelper.vendorDomain, filters=SupplierHelper.filter
                )
        elif field_id == "supplier_sku":
            supplier.product_code = field_data
        elif field_id == "supplier_min_qty":
            supplier.min_qty = field_data
        elif field_id == "supplier_price":
            supplier.price = field_data

    def __has_supplier_info(self):
        """
        Verify Product Supplier Info are Available on Input Fields
        :return: bool
        """
        # ====================================================================#
        # Check Required Data are there
        if "supplier_name" not in self._in:
            return False
        if str(self._in["supplier_name"]).__len__() < 3:
            return False
        if "supplier_price" not in self._in:
            return False
        try:
            if float(self._in["supplier_price"]) <= 0:
                return False
        except Exception:
            return False

        return True

    @staticmethod
    def isSupplierField(field_id):
        return field_id in ProductsSupplier.supplierFields
