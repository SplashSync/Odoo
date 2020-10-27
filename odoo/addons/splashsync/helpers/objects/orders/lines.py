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
from splashpy.helpers import PricesHelper, ObjectsHelper
from splashpy import Framework


class OrderLinesHelper:
    """Collection of Static Functions to manage Order & Invoices Lines content"""

    __generic_fields = [
        'name', 'product_uom_qty', 'qty_delivered_manual',
        'qty_invoiced', 'state', 'customer_lead', 'discount'
    ]

    __qty_fields = [
        'product_uom_qty', 'qty_delivered_manual', 'qty_invoiced'
    ]

    # ====================================================================#
    # Order & Invoice Line Management
    # ====================================================================#

    @staticmethod
    def get_values(order_lines, field_id):
        """
        Get List of Lines Values for given Field

        :param order_lines: recordset
        :param field_id: str
        :return: dict
        """
        values = []
        # ====================================================================#
        # Walk on Lines
        for order_line in order_lines.filtered(lambda r: r.display_type is False):
            # ====================================================================#
            # Check Line is Not a Comment Line
            if OrderLinesHelper.is_comment(order_line):
                continue
            # ====================================================================#
            # Collect Values
            values += [OrderLinesHelper.__get_raw_values(order_line, field_id)]

        return values

    @staticmethod
    def set_values(order_line, line_data):
        """
        Set values of Order Line

        :param order_line: sale.order.line
        :param line_data: dict
        :rtype: bool
        """
        # ====================================================================#
        # Walk on Data to Update
        for field_id, field_data in line_data.items():
            try:
                # ====================================================================#
                # Update Order Line data
                OrderLinesHelper.__set_raw_value(order_line, field_id, field_data)
            except Exception as ex:
                # ====================================================================#
                # Update Failed => Line may be protected
                return Framework.log().error(ex)

        return True

    @staticmethod
    def complete_values(line_data):
        """
        Complete Order Line values with computed Information
        - Detect Product ID based on Line Name


        :param line_data: dict
        :rtype: dict
        """
        from odoo.addons.splashsync.helpers import M2OHelper

        # ====================================================================#
        # Detect Wrong or Empty Product ID
        # ====================================================================#
        try:
            if not M2OHelper.verify_id(ObjectsHelper.id(line_data["product_id"]), 'product.product'):
                raise Exception("Invalid Product ID")
        except Exception:
            # ====================================================================#
            # Try detection based on Line Description
            try:
                product_id = M2OHelper.verify_name(line_data["name"], 'default_code', 'product.product')
                if int(product_id) > 0:
                    line_data["product_id"] = ObjectsHelper.encode("Product", str(product_id))
            except Exception:
                pass

        return line_data


    # ====================================================================#
    # RAW Order & Invoice Line Management
    # ====================================================================#

    @staticmethod
    def __get_raw_values(order_line, field_id):
        """
        Line Single Value for given Field

        :param order_line: sale.order.line
        :param field_id: str
        :return: dict
        """

        from odoo.addons.splashsync.helpers import CurrencyHelper, TaxHelper, SettingsManager, M2MHelper

        # ==================================================================== #
        # [CORE] Order Line Fields
        # ==================================================================== #

        # ==================================================================== #
        # Linked Product ID
        if field_id == "product_id":
            try:
                return ObjectsHelper.encode("Product", str(order_line.product_id[0].id))
            except:
                return None
        # ==================================================================== #
        # Description
        # Qty Ordered | Qty Shipped/Delivered | Qty Invoiced
        # Delivery Lead Time | Line Status
        # Line Unit Price Reduction (Percent)
        if field_id in OrderLinesHelper.__generic_fields:
            if field_id in OrderLinesHelper.__qty_fields:
                return int(getattr(order_line, field_id))
            return getattr(order_line, field_id)
        # ==================================================================== #
        # Line Unit Price (HT)
        if field_id == "price_unit":
            return PricesHelper.encode(
                float(order_line.price_unit),
                TaxHelper.get_tax_rate(order_line.tax_id, 'sale'),
                None,
                CurrencyHelper.get_main_currency_code()
            )

        # ==================================================================== #
        # Sales Taxes
        if field_id == "tax_name":
            try:
                return order_line.tax_id[0].name
            except:
                return None
        if field_id == "tax_names":
            return M2MHelper.get_names(order_line, "tax_id")

        # ==================================================================== #
        # [EXTRA] Order Line Fields
        # ==================================================================== #

        # ==================================================================== #
        # Product reference
        if field_id == "product_ref":
            try:
                return str(order_line.product_id[0].default_code)
            except:
                return None

        return None

    @staticmethod
    def __set_raw_value(order_line, field_id, field_data):
        """
        Set simple value of Order Line

        :param order_line: sale.order.line
        :param field_id: str
        :param field_data: mixed
        """

        from odoo.addons.splashsync.helpers import TaxHelper, SettingsManager, M2MHelper

        # ==================================================================== #
        # [CORE] Order Line Fields
        # ==================================================================== #

        # ==================================================================== #
        # Linked Product ID
        if field_id == "product_id" and isinstance(ObjectsHelper.id(field_data), (int, str)):
            order_line.product_id = int(ObjectsHelper.id(field_data))
        # ==================================================================== #
        # Description
        # Qty Ordered | Qty Shipped/Delivered | Qty Invoiced
        # Delivery Lead Time | Line Status
        # Line Unit Price Reduction (Percent)
        if field_id in OrderLinesHelper.__generic_fields:
            setattr(order_line, field_id, field_data)
        # ==================================================================== #
        # Line Unit Price (HT)
        if field_id == "price_unit":
            order_line.price_unit = PricesHelper.extract(field_data, "ht")
            if not SettingsManager.is_sales_adv_taxes():
                order_line.tax_id = TaxHelper.find_by_rate(PricesHelper.extract(field_data, "vat"), 'sale')
        # ==================================================================== #
        # Sales Taxes
        if field_id == "tax_name" and SettingsManager.is_sales_adv_taxes():
            field_data = '["'+field_data+'"]' if isinstance(field_data, str) else "[]"
            M2MHelper.set_names(
                order_line, "tax_id", field_data,
                domain=TaxHelper.tax_domain, filters=[("type_tax_use", "=", 'sale')]
            )
        if field_id == "tax_names" and SettingsManager.is_sales_adv_taxes():
            M2MHelper.set_names(
                order_line, "tax_id", field_data,
                domain=TaxHelper.tax_domain, filters=[("type_tax_use", "=", 'sale')]
            )

        # ==================================================================== #
        # [EXTRA] Order Line Fields
        # ==================================================================== #

        return True

    @staticmethod
    def is_comment(order_line):
        """
        Check if Order Line is Section or Note
        :param order_line: sale.order.line
        :return: bool
        """
        return order_line.display_type is not False

    # ====================================================================#
    # Order Specific Methods
    # ====================================================================#

    @staticmethod
    def add_order_line(order, line_data):
        """
        Add a New Line to an Order
        :param order: sale.order
        :return: sale.order.line
        """
        # ====================================================================#
        # Prepare Minimal Order Line Data
        req_fields = {
            "order_id": order.id,
            "sequence": 10 + len(order.order_line),
            "qty_delivered_method": 'manual',
        }
        # ====================================================================#
        # Link to Product
        try:
            req_fields["product_id"] = int(ObjectsHelper.id(line_data["product_id"]))
        except:
            Framework.log().error("Unable to create Order Line, Product Id is Missing")
            return None
        # ==================================================================== #
        # Description
        # Qty Ordered | Qty Shipped/Delivered | Qty Invoiced
        # Delivery Lead Time | Line Status
        for field_id in OrderLinesHelper.__generic_fields:
            try:
                req_fields[field_id] = line_data[field_id]
            except:
                pass
        # ====================================================================#
        # Unit Price
        try:
            req_fields["price_unit"] = PricesHelper.extract(line_data["price_unit"], "ht")
        except:
            pass
        # ====================================================================#
        # Create Order Line
        try:
            return http.request.env["sale.order.line"].create(req_fields)
        except Exception as exception:
            Framework.log().error("Unable to create Order Line, please check inputs.")
            Framework.log().fromException(exception, False)
            Framework.log().dump(req_fields, "New Order Line")
            return None

