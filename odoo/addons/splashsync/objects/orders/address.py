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

from splashpy import const
from splashpy.componants import FieldFactory
from odoo.addons.splashsync.helpers import M2OHelper


class OrderAddress:
    """
    Access to Order delivery Address Fields
    """

    def buildAddressFields(self):
        # ====================================================================#
        # Delivery Address Legal Name
        FieldFactory.create(const.__SPL_T_VARCHAR__, "__shipping__name", "Legal Name")
        FieldFactory.microData("http://schema.org/Organization", "legalName")
        FieldFactory.group("Address")
        FieldFactory.isReadOnly()
        # # ====================================================================#
        # # Delivery Address Legal Name
        FieldFactory.create(const.__SPL_T_VARCHAR__, "__shipping__contact", "Contact Name")
        FieldFactory.microData("http://schema.org/PostalAddress", "alternateName")
        FieldFactory.group("Address")
        FieldFactory.isReadOnly()
        # ====================================================================#
        # Delivery Address Street
        FieldFactory.create(const.__SPL_T_VARCHAR__, "__shipping__street", "Street")
        FieldFactory.microData("http://schema.org/PostalAddress", "streetAddress")
        FieldFactory.group("Address")
        FieldFactory.isReadOnly()
        # ====================================================================#
        # Delivery Address Zip Code
        FieldFactory.create(const.__SPL_T_VARCHAR__, "__shipping__zip", "Zip Code")
        FieldFactory.microData("http://schema.org/PostalAddress", "postalCode")
        FieldFactory.group("Address")
        FieldFactory.isReadOnly()
        # ====================================================================#
        # Delivery Address City Name
        FieldFactory.create(const.__SPL_T_VARCHAR__, "__shipping__city", "City Name")
        FieldFactory.microData("http://schema.org/PostalAddress", "addressLocality")
        FieldFactory.group("Address")
        FieldFactory.isReadOnly()
        # ====================================================================#
        # Delivery Address State Name
        FieldFactory.create(const.__SPL_T_VARCHAR__, "__shipping__state_name", "State Name")
        FieldFactory.group("Address")
        FieldFactory.isReadOnly()
        # ====================================================================#
        # Delivery Address State Code
        FieldFactory.create(const.__SPL_T_STATE__, "__shipping__state_id", "State Code")
        FieldFactory.microData("http://schema.org/PostalAddress", "addressRegion")
        FieldFactory.group("Address")
        FieldFactory.isReadOnly()

    def buildAddressTwoFields(self):
        # ====================================================================#
        # Delivery Address Country Name
        FieldFactory.create(const.__SPL_T_VARCHAR__, "__shipping__country_name", "Country")
        FieldFactory.group("Address")
        FieldFactory.isReadOnly()
        # ====================================================================#
        # Delivery Address Country Code
        FieldFactory.create(const.__SPL_T_COUNTRY__, "__shipping__country_code", "Country Code")
        FieldFactory.microData("http://schema.org/PostalAddress", "addressCountry")
        FieldFactory.group("Address")
        FieldFactory.isReadOnly()
        # ====================================================================#
        # Delivery Address Phone
        FieldFactory.create(const.__SPL_T_VARCHAR__, "__shipping__phone", "Phone")
        FieldFactory.microData("http://schema.org/PostalAddress", "telephone")
        FieldFactory.group("Address")
        FieldFactory.isReadOnly()
        # ====================================================================#
        # Delivery Address Mobile Phone
        FieldFactory.create(const.__SPL_T_VARCHAR__, "__shipping__mobile", "Mobile")
        FieldFactory.microData("http://schema.org/Person", "telephone")
        FieldFactory.group("Address")
        FieldFactory.isReadOnly()

    def getAddressFields(self, index, field_id):
        # ====================================================================#
        # Shipping Address Field Requested
        if field_id.find("__shipping__") < 0:
            return
        # ====================================================================#
        # Remove Pattern from Field Id
        real_field_id = field_id.replace("__shipping__", "")
        # ====================================================================#
        # Detect Shipping Address
        if len(self.object.partner_shipping_id) > 0:
            self.Address = self.object.partner_shipping_id[0]
        elif len(self.object.partner_id) > 0:
            self.Address = self.object.partner_id[0]
        else:
            return
        # ==================================================================== #
        # Non Generic Data
        if real_field_id == "name" and len(self.Address.parent_id) > 0:
            self._out[field_id] = getattr(self.Address.parent_id, real_field_id)
        elif real_field_id == "contact":
            self._out[field_id] = getattr(self.Address, "name") if len(self.Address.parent_id) > 0 else ""
        elif real_field_id == "country_code":
            self._out[field_id] = M2OHelper.get_name(self.Address, "country_id", index="code")
        elif real_field_id == "country_name":
            self._out[field_id] = M2OHelper.get_name(self.Address, "country_id")
        elif real_field_id == "state_id":
            self._out[field_id] = M2OHelper.get_name(self.Address, "state_id", index="code")
        elif real_field_id == "state_name":
            self._out[field_id] = M2OHelper.get_name(self.Address, "state_id")
        # ====================================================================#
        # Parse generic Fields
        else:
            self._out[field_id] = getattr(self.Address, real_field_id)

        self._in.__delitem__(index)