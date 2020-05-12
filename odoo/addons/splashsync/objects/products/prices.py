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
from splashpy.helpers import PricesHelper
from odoo.addons.splashsync.models.configuration import ResConfigSettings
from odoo.addons.splashsync.helpers import CurrencyHelper, TaxHelper, SettingsManager, M2MHelper


class ProductsPrices:
    """
    Access to product Prices Fields
    """

    def buildPricesFields(self):
        # ==================================================================== #
        # Load Product Configuration
        is_adv_taxes = SettingsManager.is_prd_adv_taxes()
        # ==================================================================== #
        # Product Selling Price
        FieldFactory.create(const.__SPL_T_PRICE__, "list_price", "Sell Price")
        FieldFactory.microData("http://schema.org/Product", "price")
        if is_adv_taxes:
            FieldFactory.create(const.__SPL_T_VARCHAR__, "list_price_tax_ids", "Sell Taxes Ids")
            FieldFactory.microData("http://schema.org/Product", "priceTaxIds")
            FieldFactory.isNotTested()
            FieldFactory.create(const.__SPL_T_VARCHAR__, "list_price_tax_names", "Sell Taxes Names")
            FieldFactory.microData("http://schema.org/Product", "priceTaxNames")
            FieldFactory.isNotTested()
        # ==================================================================== #
        # Product Cost Price
        FieldFactory.create(const.__SPL_T_PRICE__, "standard_price", "Buy Price")
        FieldFactory.microData("http://schema.org/Product", "wholesalePrice")
        if is_adv_taxes:
            FieldFactory.create(const.__SPL_T_VARCHAR__, "standard_price_tax_ids", "Buy Taxes Ids")
            FieldFactory.microData("http://schema.org/Product", "wholesalePriceTaxIds")
            FieldFactory.isNotTested()
            FieldFactory.isReadOnly()
            FieldFactory.create(const.__SPL_T_VARCHAR__, "standard_price_tax_names", "Buy Taxes Names")
            FieldFactory.microData("http://schema.org/Product", "priceTaxNames")
            FieldFactory.isNotTested()

    def getPricesFields(self, index, field_id):
        # Check if Price Field...
        if not self.isPricesFields(field_id):
            return
        # ==================================================================== #
        # Load Product Configuration
        is_adv_taxes = SettingsManager.is_prd_adv_taxes()
        # ==================================================================== #
        # Read Sell Price
        if field_id == "list_price":
            self._out[field_id] = PricesHelper.encode(
                float(self.object.lst_price),
                TaxHelper.get_tax_rate(self.object.taxes_id, 'sale') if not is_adv_taxes else float(0),
                None,
                CurrencyHelper.get_main_currency_code()
            )
            self._in.__delitem__(index)
        # ==================================================================== #
        # Read Buy Price
        if field_id == "standard_price":
            self._out[field_id] = PricesHelper.encode(
                float(self.object.standard_price),
                TaxHelper.get_tax_rate(self.object.supplier_taxes_id, 'purchase') if not is_adv_taxes else float(0),
                None,
                CurrencyHelper.get_main_currency_code()
            )
            self._in.__delitem__(index)

    def getPricesTaxFields(self, index, field_id):
        # Check if Price Field...
        if not self.isPricesTaxFields(field_id):
            return
        # ==================================================================== #
        # Read Sell Price Taxes
        if field_id == "list_price_tax_ids":
            self._out[field_id] = M2MHelper.get_ids(self.object, "taxes_id")
            self._in.__delitem__(index)
        if field_id == "list_price_tax_names":
            self._out[field_id] = M2MHelper.get_names(self.object, "taxes_id")
            self._in.__delitem__(index)
        # ==================================================================== #
        # Read Buy Price Taxes
        if field_id == "standard_price_tax_ids":
            self._out[field_id] = M2MHelper.get_ids(self.object, "supplier_taxes_id")
            self._in.__delitem__(index)
        if field_id == "standard_price_tax_names":
            self._out[field_id] = M2MHelper.get_names(self.object, "supplier_taxes_id")
            self._in.__delitem__(index)

    def setPricesFields(self, field_id, field_data):
        # Check if Price Field...
        if not self.isPricesFields(field_id):
            return
        # ==================================================================== #
        # Update Price
        self.setSimple(field_id, PricesHelper.taxExcluded(field_data) - self.object.price_extra)
        # ==================================================================== #
        # Load Product Configuration
        if SettingsManager.is_prd_adv_taxes():
            return
        # ==================================================================== #
        # Update Product Sell Taxes
        if field_id == "list_price":
            tax_rate = PricesHelper.taxPercent(field_data)
            if tax_rate > 0:
                tax = TaxHelper.find_by_rate(tax_rate, 'sale')
                if tax is None:
                    return Framework.log().error("Unable to Identify Tax ID for Rate "+str(tax_rate))
                else:
                    self.object.taxes_id = [(6, 0, [tax.id])]
            else:
                self.object.taxes_id = [(6, 0, [])]
        # ==================================================================== #
        # Update Product Buy Taxes
        if field_id == "standard_price":
            tax_rate = PricesHelper.taxPercent(field_data)
            if tax_rate > 0:
                tax = TaxHelper.find_by_rate(tax_rate, 'purchase')
                if tax is None:
                    return Framework.log().error("Unable to Identify Tax ID for Rate "+str(tax_rate))
                else:
                    self.object.supplier_taxes_id = [(6, 0, [tax.id])]
            else:
                self.object.supplier_taxes_id = [(6, 0, [])]

    def setPricesTaxFields(self, field_id, field_data):
        # Check if Price Field...
        if not self.isPricesTaxFields(field_id):
            return
        # ==================================================================== #
        # Write Sell Price Taxes
        if field_id == "list_price_tax_ids":
            M2MHelper.set_ids(
                self.object, "taxes_id", field_data,
                domain=TaxHelper.tax_domain, filters=[("type_tax_use", "=", 'sale')]
            )
            self._in.__delitem__(field_id)
        if field_id == "list_price_tax_names":
            M2MHelper.set_names(
                self.object, "taxes_id", field_data,
                domain=TaxHelper.tax_domain, filters=[("type_tax_use", "=", 'sale')]
            )
            self._in.__delitem__(field_id)
        # ==================================================================== #
        # Write Buy Price Taxes
        if field_id == "standard_price_tax_ids":
            M2MHelper.set_ids(
                self.object, "supplier_taxes_id", field_data,
                domain=TaxHelper.tax_domain, filters=[("type_tax_use", "=", 'purchase')]
            )
            self._in.__delitem__(field_id)
        if field_id == "standard_price_tax_names":
            M2MHelper.set_names(
                self.object, "supplier_taxes_id", field_data,
                domain=TaxHelper.tax_domain, filters=[("type_tax_use", "=", 'purchase')]
            )
            self._in.__delitem__(field_id)

    @staticmethod
    def isPricesFields(field_id):
        if field_id in ["list_price", "standard_price"]:
            return True
        return False

    @staticmethod
    def isPricesTaxFields(field_id):
        if field_id in [
            "list_price_tax_ids", "list_price_tax_names",
            "standard_price_tax_ids", "standard_price_tax_names"
        ] and SettingsManager.is_prd_adv_taxes():
            return True
        return False

