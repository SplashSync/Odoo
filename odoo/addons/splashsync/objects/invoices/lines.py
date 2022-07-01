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
from splashpy.helpers import ListHelper, ObjectsHelper


class InvoiceLines:
    """
    Access to Invoice Lines Fields
    """

    def buildLinesFields(self):
        """Build Invoice Lines Fields"""

        from odoo.addons.splashsync.helpers import SettingsManager, TaxHelper

        # ==================================================================== #
        # [CORE] Invoice Line Fields
        # ==================================================================== #

        # ==================================================================== #
        # Linked Product ID
        FieldFactory.create(ObjectsHelper.encode("Product", const.__SPL_T_ID__), "product_id", "Product ID")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/Product", "productID")
        FieldFactory.association("name@lines", "quantity@lines", "price_unit@lines")
        # ==================================================================== #
        # Description
        FieldFactory.create(const.__SPL_T_VARCHAR__, "name", "Product Desc.")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/partOfInvoice", "description")
        FieldFactory.association("name@lines", "quantity@lines", "price_unit@lines")
        # ==================================================================== #
        # Qty Invoiced
        FieldFactory.create(const.__SPL_T_INT__, "quantity", "Invoiced Qty")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/QuantitativeValue", "value")
        FieldFactory.association("name@lines", "quantity@lines", "price_unit@lines")
        # ==================================================================== #
        # Line Unit Price (HT)
        FieldFactory.create(const.__SPL_T_PRICE__, "price_unit", "Unit Price")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/PriceSpecification", "price")
        FieldFactory.association("name@lines", "quantity@lines", "price_unit@lines")
        # ==================================================================== #
        # Line Unit Price Reduction (Percent)
        FieldFactory.create(const.__SPL_T_DOUBLE__, "discount", "Discount")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/Order", "discount")
        FieldFactory.association("name@lines", "quantity@lines", "price_unit@lines")
        # ==================================================================== #
        # Sales Taxes (One)
        FieldFactory.create(const.__SPL_T_VARCHAR__, "tax_name", "Tax Name")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/PriceSpecification", "valueAddedTaxName")
        FieldFactory.addChoices(TaxHelper.get_name_values("sale"))
        FieldFactory.isReadOnly(not SettingsManager.is_sales_adv_taxes())
        FieldFactory.isNotTested()
        # ==================================================================== #
        # Sales Taxes (Multi)
        FieldFactory.create(const.__SPL_T_INLINE__, "tax_names", "Taxes")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/PriceSpecification", "valueAddedTaxNames")
        FieldFactory.addChoices(TaxHelper.get_name_values("sale"))
        FieldFactory.isReadOnly(not SettingsManager.is_sales_adv_taxes())
        FieldFactory.isNotTested()

        # ==================================================================== #
        # [EXTRA] Order Line Fields
        # ==================================================================== #

        # ==================================================================== #
        # Product reference
        FieldFactory.create(const.__SPL_T_VARCHAR__, "product_ref", "Product Ref.")
        FieldFactory.inlist("lines")
        FieldFactory.microData("http://schema.org/Product", "ref")
        FieldFactory.isReadOnly().isNotTested()

    def getLinesFields(self, index, field_id):
        """
        Get Invoice Lines List

        :param index: str
        :param field_id: str
        :return: None
        """
        from odoo.addons.splashsync.helpers import OrderLinesHelper

        # ==================================================================== #
        # Init Lines List...
        lines_list = ListHelper.initOutput(self._out, "lines", field_id)
        # ==================================================================== #
        # Safety Check
        if lines_list is None:
            return
        # ==================================================================== #
        # Read Lines Data
        lines_values = OrderLinesHelper.get_values(self.object.invoice_line_ids, lines_list)
        for pos in range(len(lines_values)):
            ListHelper.insert(self._out, "lines", field_id, "line-" + str(pos), lines_values[pos])
        # ==================================================================== #
        # Force Lines Ordering
        self._out["lines"] = OrderedDict(sorted(self._out["lines"].items()))
        self._in.__delitem__(index)

    def setLinesFields(self, field_id, field_data):
        """
        Set Invoice Lines List

        :param field_id: str
        :param field_data: hash
        :return: None
        """
        from odoo.addons.splashsync.helpers import OrderLinesHelper

        # ==================================================================== #
        # Safety Check - field_id is an Invoice lines List
        if field_id != "lines":
            return
        self._in.__delitem__(field_id)
        # ==================================================================== #
        # Safety Check - Received List is Valid
        if not isinstance(field_data, dict):
            return
        # ==================================================================== #
        # Walk on Received Invoice Lines...
        index = 0
        updated_invoice_line_ids = []
        for line_data in OrderedDict(sorted(field_data.items())).values():
            # ==================================================================== #
            # Complete Invoice Line values with computed Information
            line_data = OrderLinesHelper.complete_values(line_data)
            # ==================================================================== #
            # Load or Create Invoice Line
            try:
                invoice_line = self.object.invoice_line_ids[index]
            except:
                invoice_line = OrderLinesHelper.add_invoice_line(self.object, line_data)
                if invoice_line is None:
                    return
            # ==================================================================== #
            # Store Updated Invoice Line Id
            updated_invoice_line_ids.append(invoice_line.id)
            index += 1
            # ==================================================================== #
            # Check if Comment Invoice Line
            if OrderLinesHelper.is_comment(invoice_line):
                continue
            # ==================================================================== #
            # Update Invoice Line Values
            if not OrderLinesHelper.set_values(invoice_line, line_data):
                return
        # ==================================================================== #
        # Delete Remaining Invoice Lines...
        for invoice_line in self.object.invoice_line_ids:
            if invoice_line.id not in updated_invoice_line_ids:
                self.object.invoice_line_ids = [(3, invoice_line.id, 0)]
        # ==================================================================== #
        # Recompute Invoice Taxes
        if getattr(self.object, "_name") in ["account.move"]:
            self.object._recompute_tax_lines()
            self.object._compute_amount()
        else:
            self.object.compute_taxes()
