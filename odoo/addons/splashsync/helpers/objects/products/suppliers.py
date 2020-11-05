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


class SupplierHelper:
    """Collection of Static Functions to manage Odoo Product Supplier Info"""

    vendorDomain = "res.partner"
    domain = "product.supplierinfo"
    filter = [("supplier", "=", True), ("is_company", "=", True)]

    @staticmethod
    def first(product):
        """
        Get Product First Supplier Info
        :param product: Product
        :return: None, product.supplierinfo
        """
        # ====================================================================#
        # Filter Product Suppliers
        productSuppliers = product.seller_ids.filtered(lambda r: r.product_id.id == product.id)
        # ====================================================================#
        # Return First Product Suppliers if Exists
        return productSuppliers[0] if len(productSuppliers) > 0 else None

    @staticmethod
    def create(product, vendor_name, vendor_price):
        """
        Create a Product Supplier Info Object
        :param product: Product
        :param vendor_name: str
        :param vendor_price: float
        :return: None, product.supplierinfo
        """
        from odoo.addons.splashsync.helpers import M2OHelper
        # ====================================================================#
        # Validate Supplier Partner
        vendor_id = M2OHelper.verify_name(vendor_name, "name", SupplierHelper.vendorDomain, SupplierHelper.filter)
        if vendor_id is None or vendor_id <= 0:
            return None
        try:
            # ====================================================================#
            # Create Supplier Info
            supplier = SupplierHelper.getModel().create({
                "name": vendor_id,
                "product_id": product.id,
                "min_qty": 1,
                "price": vendor_price,
            })
            # ====================================================================#
            # Connect Supplier Info
            product.seller_ids = [(6, 0, [supplier.id])]

            return supplier
        except Exception:
            return None

    # ====================================================================#
    # Odoo ORM Access
    # ====================================================================#

    @staticmethod
    def getModel():
        """Get Product Supplier Infos Model Class"""
        return http.request.env[SupplierHelper.domain].sudo()
