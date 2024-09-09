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
        'name', 'state', 'customer_lead', 'discount',
        'product_uom_qty', 'qty_delivered_manual', 'qty_delivered', 'qty_invoiced', 'quantity'
    ]

    __float_fields = [
        'discount',
        'product_uom_qty', 'qty_delivered_manual', 'qty_invoiced', 'quantity'
    ]

    __qty_fields = [
        'product_uom_qty', 'qty_delivered_manual', 'qty_delivered', 'qty_invoiced', 'quantity'
    ]

    # ====================================================================#
    # Order & Invoice Line Management
    # ====================================================================#

    @staticmethod
    def get_values(lines, field_id):
        """
        Get List of Lines Values for given Field

        :param lines: recordset
        :param field_id: str
        :return: dict
        """
        values = []
        # ====================================================================#
        # Walk on Lines
        for order_line in lines.filtered(lambda r: r.display_type is False):
            # ====================================================================#
            # Check Line is Not a Comment Line
            if OrderLinesHelper.is_comment(order_line):
                continue
            # ====================================================================#
            # Collect Values
            values += [OrderLinesHelper.__get_raw_values(order_line, field_id)]

        return values

    @staticmethod
    def set_values(line, line_data):
        """
        Set values of Order Line

        :param line: sale.order.line
        :param line_data: dict
        :rtype: bool
        """
        # ====================================================================#
        # Update Taxes Names in Priority
        for field_id, field_data in line_data.items():
            if field_id in ["tax_name", "tax_names"]:
                try:
                    OrderLinesHelper.__set_raw_value(line, field_id, field_data)
                except Exception:
                    continue
        # ====================================================================#
        # Walk on Data to Update
        for field_id, field_data in line_data.items():
            try:
                # ====================================================================#
                # Update Order Line data
                OrderLinesHelper.__set_raw_value(line, field_id, field_data)
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
    def __get_raw_values(line, field_id):
        """
        Line Single Value for given Field

        :param line: sale.order.line
        :param field_id: str
        :return: dict
        """

        from odoo.addons.splashsync.helpers import CurrencyHelper, TaxHelper, SettingsManager, M2MHelper

        # ==================================================================== #
        # Detect Line Taxes Storage Field Id
        tax_field_id = OrderLinesHelper.get_tax_field_id(line)

        # ==================================================================== #
        # [CORE] Order Line Fields
        # ==================================================================== #

        # ==================================================================== #
        # Linked Product ID
        if field_id == "product_id":
            try:
                return ObjectsHelper.encode("Product", str(line.product_id[0].id))
            except:
                return None
        # ==================================================================== #
        # Description
        # Qty Ordered | Qty Shipped/Delivered | Qty Invoiced
        # Delivery Lead Time | Line Status
        # Line Unit Price Reduction (Percent)
        if field_id in OrderLinesHelper.__generic_fields:
            if field_id in OrderLinesHelper.__qty_fields:
                return int(getattr(line, field_id))
            return getattr(line, field_id)
        # ==================================================================== #
        # Line Unit Price (HT/TTC)
        if field_id == "price_unit":
            # ==================================================================== #
            # Encode Price
            return TaxHelper.encode_price(
                float(line.price_unit),
                getattr(line, tax_field_id),
                'sale'
            )

        # ==================================================================== #
        # Sales Taxes
        if field_id == "tax_name":
            try:
                return getattr(line, tax_field_id)[0].name
            except:
                return None
        if field_id == "tax_names":
            return M2MHelper.get_names(line, tax_field_id)

        # ==================================================================== #
        # [EXTRA] Order Line Fields
        # ==================================================================== #

        # ==================================================================== #
        # Product type
        if field_id == "detailed_type":
            try:
                if "detailed_type" in dir(line.product_id[0]):
                    # ==================================================================== #
                    # Odoo 15+
                    return str(line.product_id[0].detailed_type)
                elif "type" in dir(line.product_id[0]):
                    # ==================================================================== #
                    # Odoo 12/13/14
                    return str(line.product_id[0].type)

                return None
            except:
                return None

        # ==================================================================== #
        # Product reference
        if field_id == "product_ref":
            try:
                return str(line.product_id[0].default_code)
            except:
                return None

        # ==================================================================== #
        # Reserved Qty
        if field_id == "qty_reserved":
            from odoo.addons.splashsync.helpers import OrderPickingHelper
            return OrderPickingHelper.get_reserved_qty(line)

        return None

    @staticmethod
    def __set_raw_value(line, field_id, field_data):
        """
        Set simple value of Order Line

        :param line: sale.order.line
        :param field_id: str
        :param field_data: mixed
        """

        from odoo.addons.splashsync.helpers import TaxHelper, SettingsManager, M2MHelper

        # ==================================================================== #
        # Detect Line Taxes Storage Field Id
        tax_field_id = OrderLinesHelper.get_tax_field_id(line)

        # ==================================================================== #
        # [CORE] Order Line Fields
        # ==================================================================== #

        # ==================================================================== #
        # Linked Product ID
        if field_id == "product_id" and isinstance(ObjectsHelper.id(field_data), (int, str)):
            try:
                line.product_id = OrderLinesHelper.detect_product_id({
                    "product_id": field_data
                })
            except Exception as exception:
                Framework.log().error("Unable to Update Product ID.")
                Framework.log().fromException(exception, True)
                return None
        # ==================================================================== #
        # Description
        # Qty Ordered | Qty Shipped/Delivered | Qty Invoiced
        # Delivery Lead Time | Line Status
        # Line Unit Price Reduction (Percent)
        if field_id in OrderLinesHelper.__generic_fields:
            setattr(line, field_id, field_data)
        # ==================================================================== #
        # Line Unit Price (HT)
        if field_id == "price_unit":
            # ==================================================================== #
            # Update Line Tax using Price Tax Percent
            if not SettingsManager.is_sales_adv_taxes():
                setattr(
                    line,
                    tax_field_id,
                    TaxHelper.find_by_rate(PricesHelper.extract(field_data, "vat"), 'sale')
                )
            # ==================================================================== #
            # Update Line Unit Price with Tax Included / Excluded Detection
            line.price_unit = TaxHelper.decode_price(field_data, getattr(line, tax_field_id), 'sale')
        # ==================================================================== #
        # Sales Taxes
        if field_id == "tax_name" and SettingsManager.is_sales_adv_taxes():
            field_data = '["'+field_data+'"]' if isinstance(field_data, str) else "[]"
            M2MHelper.set_names(
                line, tax_field_id, field_data,
                domain=TaxHelper.tax_domain, filters=[("type_tax_use", "=", 'sale')]
            )
        if field_id == "tax_names" and SettingsManager.is_sales_adv_taxes():
            M2MHelper.set_names(
                line, tax_field_id, field_data,
                domain=TaxHelper.tax_domain, filters=[("type_tax_use", "=", 'sale')]
            )

        # ==================================================================== #
        # [EXTRA] Order Line Fields
        # ==================================================================== #

        return True

    @staticmethod
    def is_comment(line):
        """
        Check if Order Line is Section or Note
        :param line: sale.order.line|account.invoice.line
        :return: bool
        """
        return line.display_type is not False

    @staticmethod
    def is_order_line(line):
        """
        Check if Line is Order Line (or Invoice Line)

        :param line: sale.order.line|account.move.line|account.invoice.line
        :return: bool
        """
        return getattr(line, "_name") in ["sale.order.line"]

    @staticmethod
    def is_move_line(line):
        """
        Check if Line is Account Move Line (Invoice Line)

        :param line: sale.order.line|account.move.line|account.invoice.line
        :return: bool
        """
        return getattr(line, "_name") in ["account.move.line"]

    @staticmethod
    def get_tax_field_id(line):
        """
        Get Field Id for Line Tax Storage

        :return: str
        """
        if OrderLinesHelper.is_order_line(line):
            return "tax_id"
        elif OrderLinesHelper.is_move_line(line):
            return "tax_ids"
        else:
            return "invoice_line_tax_ids"

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
            req_fields["product_id"] = OrderLinesHelper.detect_product_id(line_data)
        except Exception as exception:
            Framework.log().error("Unable to create Order Line, Product Id is Missing")
            Framework.log().fromException(exception, False)
            Framework.log().dump(req_fields, "New Order Line")
            return None
        # ==================================================================== #
        # Description
        # Qty Ordered | Qty Shipped/Delivered | Qty Invoiced
        # Delivery Lead Time | Line Status
        for field_id in OrderLinesHelper.__generic_fields:
            try:
                if field_id in OrderLinesHelper.__float_fields:
                    req_fields[field_id] = float(line_data[field_id])
                else:
                    req_fields[field_id] = line_data[field_id]
            except Exception:
                pass
        # ====================================================================#
        # Unit Price
        try:
            req_fields["price_unit"] = PricesHelper.extract(line_data["price_unit"], "ht")
        except Exception:
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

    # ====================================================================#
    # Invoice Specific Methods
    # ====================================================================#

    @staticmethod
    def add_invoice_line(invoice, line_data):
        """
        Add a New Line to an Invoice

        :param invoice: account.invoice
        :param line_data: dict
        :return: account.invoice.line
        """
        from odoo.addons.splashsync.helpers import SystemManager
        # ====================================================================#
        # Load Account Id from Configuration
        account_id = OrderLinesHelper.detect_sales_account_id()
        # ====================================================================#
        # Safety Check
        if account_id is None or int(account_id) <= 0:
            Framework.log().error("Unable to detect Account Id, Add Invoice Line skipped.")
            Framework.log().error("Please check your configuration.")
            return None
        # ====================================================================#
        # Prepare Minimal Order Line Data
        req_fields = {
            "account_id": account_id,
            "sequence": 10 + len(invoice.invoice_line_ids),
        }
        # ====================================================================#
        # Link to Parent
        if SystemManager.compare_version(13) >= 0:
            req_fields["move_id"] = invoice.id
        else:
            req_fields["invoice_id"] = invoice.id

        # ====================================================================#
        # Link to Product
        try:
            req_fields["product_id"] = OrderLinesHelper.detect_product_id(line_data)
        except Exception as exception:
            Framework.log().error("Unable to create Invoice Line, please check inputs.")
            Framework.log().fromException(exception, False)
            Framework.log().dump(req_fields, "New Invoice Line")
            return None
        # ==================================================================== #
        # Description
        # Qty Invoiced
        for field_id in OrderLinesHelper.__generic_fields:
            try:
                if field_id in OrderLinesHelper.__float_fields:
                    req_fields[field_id] = float(line_data[field_id])
                else:
                    req_fields[field_id] = line_data[field_id]
            except:
                pass
        # ====================================================================#
        # Unit Price
        try:
            req_fields["quantity"] = float(req_fields["quantity"])
            req_fields["price_unit"] = PricesHelper.extract(line_data["price_unit"], "ht")
        except:
            pass
        # ====================================================================#
        # Create Order Line
        try:
            if SystemManager.compare_version(13) >= 0:
                return SystemManager.getModel("account.move.line").create(req_fields)
            else:
                return http.request.env["account.invoice.line"].create(req_fields)
        except Exception as exception:
            Framework.log().error("Unable to create Invoice Line, please check inputs.")
            Framework.log().fromException(exception, False)
            Framework.log().dump(req_fields, "New Invoice Line")
            return None

    @staticmethod
    def detect_sales_account_id():
        """
        Detect Account id for NEW Invoices Lines

        :return: int|None
        """
        from odoo.addons.splashsync.helpers import SettingsManager
        # ====================================================================#
        # Load Account Id from Configuration
        try:
            account_id = SettingsManager.get_sales_account_id()
            # ====================================================================#
            # FallBack to Demo Account Id
            if account_id is None or int(account_id) <= 0:
                from odoo.addons.splashsync.helpers import SystemManager
                accounts = SystemManager.getModel('account.account').search([
                    ('name', '=', "Product Sales")
                ])
                account_id = accounts.ids[0] if len(accounts.ids) > 0 else None
            return account_id
        except:
            return None

    @staticmethod
    def detect_product_id(line_data):
        """
        Detect Product ID for NEW Lines without Product ID

        :return: int|None
        """
        from odoo.addons.splashsync.helpers import SystemManager
        # ====================================================================#
        # Prepare Product
        empty_product = {
            "name": "Service",
            'default_code': "SPL"
        }
        # ==================================================================== #
        # Get Product ID From Line data
        if "product_id" in line_data and isinstance(ObjectsHelper.id(line_data["product_id"]), (int, str)):
            return int(ObjectsHelper.id(line_data["product_id"]))

        # ==================================================================== #
        # Search or Create for SPL Empty Product
        # ==================================================================== #

        # ====================================================================#
        # Search for Product by SKU
        model = SystemManager.getModel('product.product').search([('default_code', '=', empty_product['default_code'])])
        if len(model) == 1:
            return model[0][0].id
        # ====================================================================#
        # Ensure default type
        if SystemManager.compare_version(15) >= 0:
            empty_product['detailed_type'] = 'service'
        elif "type":
            empty_product['type'] = 'service'
        # ====================================================================#
        # Create Product
        new_product = SystemManager.getModel('product.product')\
            .with_context(create_product_product=True)\
            .create(empty_product)

        return new_product.id
