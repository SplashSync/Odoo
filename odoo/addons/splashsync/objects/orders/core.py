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
from odoo.addons.splashsync.helpers.objects.partners import PartnersHelper
from splashpy import const
from splashpy.componants import FieldFactory
from splashpy.helpers import ObjectsHelper
from datetime import date, datetime

class OrderCore:
    """
    Access to Order Core Fields (Required)
    """

    __core_fields_ids = ['partner_id', 'partner_invoice_id', 'partner_shipping_id', 'date_order']

    def buildOrderCoreFields(self):
        # ==================================================================== #
        # Order Final Customer
        FieldFactory.create(ObjectsHelper.encode("ThirdParty", const.__SPL_T_ID__), "partner_id", "Customer")
        FieldFactory.microData("http://schema.org/Organization", "ID")
        FieldFactory.group("General")
        FieldFactory.isRequired()
        # ==================================================================== #
        # Order Billing Address
        FieldFactory.create(ObjectsHelper.encode("Address", const.__SPL_T_ID__), "partner_invoice_id", "Invoice Address")
        FieldFactory.microData("http://schema.org/Order", "billingAddress")
        FieldFactory.group("General")
        FieldFactory.isRequired()
        # ==================================================================== #
        # Order Shipping Address
        FieldFactory.create(ObjectsHelper.encode("Address", const.__SPL_T_ID__), "partner_shipping_id", "Shipping Address")
        FieldFactory.microData("http://schema.org/Order", "orderDelivery")
        FieldFactory.group("General")
        FieldFactory.isRequired()
        # ==================================================================== #
        # Order Date
        FieldFactory.create(const.__SPL_T_DATE__, "date_order", "Order Date")
        FieldFactory.microData("http://schema.org/Order", "orderDate")
        FieldFactory.group("General")
        FieldFactory.isRequired()

    def getOrderCoreFields(self, index, field_id):
        # ==================================================================== #
        # Filter on Field Id
        if field_id not in OrderCore.__core_fields_ids:
            return
        # ==================================================================== #
        # Read Field Data
        if field_id == "date_order":
            if isinstance(self.object.date_order, datetime):
                self._out[field_id] = self.object.date_order.strftime(const.__SPL_T_DATECAST__)
            else:
                self._out[field_id] = ""
        if field_id == "partner_id":
            self._out[field_id] = M2OHelper.get_object(self.object, "partner_id", "ThirdParty")
        # TODO: Filter on Address type ?
        if field_id == "partner_invoice_id":
            self._out[field_id] = M2OHelper.get_object(self.object, "partner_invoice_id", "Address")
        # TODO: Filter on Address type ?
        if field_id == "partner_shipping_id":
            self._out[field_id] = M2OHelper.get_object(self.object, "partner_shipping_id", "Address")

        self._in.__delitem__(index)

    def setOrderCoreFields(self, field_id, field_data):
        # ==================================================================== #
        # Filter on Field Id
        if field_id not in OrderCore.__core_fields_ids:
            return
        # ==================================================================== #
        # Write Order Date
        if field_id == "date_order":
            self.setSimple(field_id, field_data)
            return
        # ==================================================================== #
        # Write Field Data
        M2OHelper.set_object(self.object, field_id, field_data, domain="res.partner")

        self._in.__delitem__(field_id)

    def is_ready_for_create(self):
        """
        Verify Received Data are Ok for Create a New Order

        :return: True if OK
        :rtype: True|str
        """
        # ====================================================================#
        # Safety Check - Customer, Invoice Address, Shipping Address are required
        if "date_order" not in self._in:
            return "No Order date provided, Unable to create Order"
        if "partner_id" not in self._in:
            return "No Customer provided, Unable to create Order"
        if "partner_invoice_id" not in self._in:
            return "No Invoice Address provided, Unable to create Order"
        if "partner_shipping_id" not in self._in:
            return "No Shipping Address provided, Unable to create Order"

        return True

    def collectRequiredFields(self):
        """
        Collect All Required Fields from Inputs

        :return: False|hash
        """
        from splashpy import Framework
        # ====================================================================#
        # Safety Check - All required fields are there
        if self.is_ready_for_create() is not True:
            return Framework.log().error(self.is_ready_for_create())
        # ====================================================================#
        # Safety Check - Tracking Policy is Required
        if "picking_policy" not in self._in:
            self._in["picking_policy"] = "one"
        # ====================================================================#
        # Collect Basic Core Fields
        req_fields = self.collectRequiredCoreFields()
        self._in.__delitem__("picking_policy")
        if req_fields is False or req_fields.__len__() < 1:
            return False
        # ====================================================================#
        # Collect Order Core Fields
        for field_id in OrderCore.__core_fields_ids:
            # ====================================================================#
            # Setup Order Date
            if field_id == "date_order":
                req_fields[field_id] = self._in[field_id]
                continue
            # ====================================================================#
            # Setup Order Relations
            req_fields[field_id] = int(ObjectsHelper.id(self._in[field_id]))
            object_filters = PartnersHelper.thirdparty_filter() if field_id is "partner_id" else PartnersHelper.address_filter()
            if not M2OHelper.verify_id(req_fields[field_id], "res.partner", object_filters):
                return Framework.log().error("Unable to Identify Pointed Object: "+str(self._in[field_id]))
        # ====================================================================#
        # Safety Check
        return req_fields
