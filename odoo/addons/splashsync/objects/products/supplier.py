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
from splashpy.helpers import PricesHelper
from odoo.addons.splashsync.helpers import M2OHelper, SettingsManager, TaxHelper, SupplierHelper

class ProductsSupplier:
    """
    Access to product First Supplier Fields
    """
    # Static List of First Supplier Field Ids
    supplierFields = [
        "supplier_name", "supplier_sku", "supplier_min_qty",
        "supplier_price", "supplier_price_dbl", "supplier_currency"
    ]

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
        # First Supplier Price as Double
        FieldFactory.create(const.__SPL_T_DOUBLE__, "supplier_price_dbl", "Supplier Price (Float)")
        FieldFactory.microData("http://schema.org/Product", "supplierPriceDbl")
        FieldFactory.association("supplier_name")
        # ==================================================================== #
        # First Supplier Price
        FieldFactory.create(const.__SPL_T_PRICE__, "supplier_price", "Supplier Price")
        FieldFactory.microData("http://schema.org/Product", "supplierPrice")
        FieldFactory.isNotTested()
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
        # ====================================================================#
        # First Supplier Currency
        FieldFactory.create(const.__SPL_T_CURRENCY__, "supplier_currency", "Supplier Currency")
        FieldFactory.microData("http://schema.org/Product", "supplierCurrency")
        FieldFactory.isNotTested()

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
            supplier = SupplierHelper.create(self.object, self._in["supplier_name"], self._in["supplier_price_dbl"])
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
        elif value_id == "supplier_price_dbl":
            return supplier.price
        elif value_id == "supplier_price":
            # ==================================================================== #
            # Load Product Configuration
            is_adv_taxes = SettingsManager.is_prd_adv_taxes()
            return PricesHelper.encode(
                float(supplier.price),
                TaxHelper.get_tax_rate(self.object.taxes_id, 'purchase') if not is_adv_taxes else float(0),
                None,
                supplier.currency_id.name
            )
        elif value_id == "supplier_currency":
            return supplier.currency_id.name

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
            new_currency = M2OHelper.verify_name(field_data, "name", SupplierHelper.vendorDomain, SupplierHelper.filter)
            if new_currency is not None and new_currency > 0:
                M2OHelper.set_name(
                    supplier, "name", field_data,
                    domain=SupplierHelper.vendorDomain, filters=SupplierHelper.filter
                )
        elif field_id == "supplier_sku":
            supplier.product_code = field_data
        elif field_id == "supplier_min_qty":
            supplier.min_qty = field_data
        elif field_id == "supplier_price_dbl":
            supplier.price = field_data
        elif field_id == "supplier_price":
            try:
                supplier.price = float(PricesHelper.taxExcluded(field_data))
            except TypeError:
                supplier.price = 0
        elif field_id == "supplier_currency":
            # ====================================================================#
            # Validate & Update Supplier Partner
            new_currency = M2OHelper.verify_name(field_data, "name", "res.currency")
            if new_currency is not None and new_currency > 0:
                M2OHelper.set_name(supplier, "currency_id", field_data, domain="res.currency")

    def __has_supplier_info(self):
        """
        Verify Product Supplier Info are Available on Input Fields
        :return: bool
        """
        # ====================================================================#
        # Check Supplier SKU is there
        if "supplier_name" not in self._in:
            return False
        if str(self._in["supplier_name"]).__len__() < 3:
            return False
        # ====================================================================#
        # Check Required Data are there
        if "supplier_price" in self._in:
            self._in["supplier_price_dbl"] = float(PricesHelper.taxExcluded(self._in["supplier_price"]))
        # ====================================================================#
        # Check Supplier Price is there
        if "supplier_price_dbl" not in self._in:
            return False
        try:
            if float(self._in["supplier_price_dbl"]) <= 0:
                return False
        except Exception:
            return False

        return True

    @staticmethod
    def isSupplierField(field_id):
        return field_id in ProductsSupplier.supplierFields
