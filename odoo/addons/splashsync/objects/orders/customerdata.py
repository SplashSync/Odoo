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

from odoo.addons.splashsync.helpers.objects.relations import M2OHelper
from splashpy import const
from splashpy.componants import FieldFactory
from splashpy.helpers import ObjectsHelper


class OrderCustomerData:
    """
    Access to Customer
    """

    def buildCustomerFields(self):
        FieldFactory.create(ObjectsHelper.encode("ThirdParty", const.__SPL_T_ID__), "partner_id", "Customer")
        FieldFactory.microData("http://schema.org/Organization", "ID")
        FieldFactory.isRequired()
        FieldFactory.create(ObjectsHelper.encode("Address", const.__SPL_T_ID__), "partner_invoice_id", "Invoice Address")
        FieldFactory.microData("http://schema.org/Order", "billingAddress")
        FieldFactory.isRequired()
        FieldFactory.create(ObjectsHelper.encode("Address", const.__SPL_T_ID__), "partner_shipping_id", "Shipping Address")
        FieldFactory.microData("http://schema.org/Order", "orderDelivery")
        FieldFactory.isRequired()

    def getCustomerFields(self, index, field_id):
        # ==================================================================== #
        # Filter on Field Id
        if field_id not in ["partner_id", "partner_invoice_id", "partner_shipping_id"]:
            return
        # ==================================================================== #
        # Read Field Data
        if field_id == "partner_id":
            self._out[field_id] = M2OHelper.get_object(self.object, "partner_id", "ThirdParty")
        # TODO: Filter on Address type ?
        if field_id == "partner_invoice_id":
            self._out[field_id] = M2OHelper.get_object(self.object, "partner_invoice_id", "Address")
        # TODO: Filter on Address type ?
        if field_id == "partner_shipping_id":
            self._out[field_id] = M2OHelper.get_object(self.object, "partner_shipping_id", "Address")

        self._in.__delitem__(index)

    def setCustomerFields(self, field_id, field_data):
        # ==================================================================== #
        # Filter on Field Id
        if field_id not in ["partner_id", "partner_invoice_id", "partner_shipping_id"]:
            return
        # ==================================================================== #
        # Write Field Data
        M2OHelper.set_object(self.object, field_id, field_data, domain="res.partner")

        self._in.__delitem__(field_id)
