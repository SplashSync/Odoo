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

class InvoiceCore:
    """
    Access to Invoice Core Fields (Required)
    """

    __core_fields_ids = ['partner_id', 'partner_shipping_id']

    def buildInvCoreFields(self):
        from odoo.addons.splashsync.helpers import SystemManager
        # ==================================================================== #
        # Invoice Final Customer
        FieldFactory.create(ObjectsHelper.encode("ThirdParty", const.__SPL_T_ID__), "partner_id", "Customer")
        FieldFactory.microData("http://schema.org/Invoice", "customer")
        FieldFactory.group("General")
        FieldFactory.isRequired()
        # ==================================================================== #
        # Invoice Shipping Address
        FieldFactory.create(ObjectsHelper.encode("Address", const.__SPL_T_ID__), "partner_shipping_id", "Shipping Address")
        FieldFactory.microData("http://schema.org/Order", "orderDelivery")
        FieldFactory.group("General")
        FieldFactory.isRequired()

    def getInvCoreFields(self, index, field_id):
        # ==================================================================== #
        # Filter on Field Id
        if field_id not in InvoiceCore.__core_fields_ids:
            return
        # ==================================================================== #
        # Read Field Data
        # if field_id in ['date_invoice', 'invoice_date']:
        #     return self.getSimpleDate(index, field_id)
        if field_id == "partner_id":
            self._out[field_id] = M2OHelper.get_object(self.object, "partner_id", "ThirdParty")
        if field_id == "partner_shipping_id":
            self._out[field_id] = M2OHelper.get_object(self.object, "partner_shipping_id", "Address")

        self._in.__delitem__(index)

    def setInvCoreFields(self, field_id, field_data):
        # ==================================================================== #
        # Filter on Field Id
        if field_id not in InvoiceCore.__core_fields_ids:
            return
        # ==================================================================== #
        # Write Field Data
        M2OHelper.set_object(self.object, field_id, field_data, domain="res.partner")
        self._in.__delitem__(field_id)

    def is_ready_for_create(self):
        """
        Verify Received Data are Ok for Create a New Invoice

        :return: True if OK
        :rtype: True|str
        """
        # ====================================================================#
        # Safety Check - Customer, Shipping Address are required
        if "date_invoice" not in self._in and "invoice_date" not in self._in:
            return "No Invoice date provided, Unable to create Invoice"
        if "partner_id" not in self._in:
            return "No Customer provided, Unable to create Invoice"
        if "partner_shipping_id" not in self._in:
            return "No Shipping Address provided, Unable to create Invoice"

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
        # Safety Check - Name is Required
        if "name" not in self._in:
            self._in["name"] = "/"
        # ====================================================================#
        # Collect Basic Core Fields
        req_fields = self.collectRequiredCoreFields()
        if req_fields is False:
            return False
        # ====================================================================#
        # Collect Order Core Fields
        for field_id in InvoiceCore.__core_fields_ids:
            # ====================================================================#
            # Setup Order Relations
            req_fields[field_id] = int(ObjectsHelper.id(self._in[field_id]))
            object_filters = PartnersHelper.thirdparty_filter() if field_id == "partner_id" else PartnersHelper.address_filter()
            if not M2OHelper.verify_id(req_fields[field_id], "res.partner", object_filters):
                return Framework.log().error("Unable to Identify Pointed Object: "+str(self._in[field_id]))
        # ====================================================================#
        # Safety Check
        return req_fields
