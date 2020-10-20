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
from odoo.addons.splashsync.helpers import TaxHelper, SettingsManager, M2MHelper, M2OHelper

class OrderDelivery:
    """
    Access to Order Delivery Fields
    """

    def buildDeliveryFields(self):
        # ====================================================================#
        # Delivery Carrier Name
        FieldFactory.create(const.__SPL_T_VARCHAR__, "carrier_id", "Carrier Name")
        FieldFactory.microData("http://schema.org/ParcelDelivery", "identifier")
        FieldFactory.addChoices(M2OHelper.get_name_values("delivery.carrier"))
        FieldFactory.group("Tracking")
        # ====================================================================#
        # Delivery Carrier Description
        FieldFactory.create(const.__SPL_T_VARCHAR__, "carrier_desc", "Carrier Description")
        FieldFactory.microData("http://schema.org/ParcelDelivery", "provider")
        FieldFactory.group("Tracking")
        FieldFactory.isReadOnly()

    def getDeliveryFields(self, index, field_id):
        # ====================================================================#
        # Delivery Carrier Name
        if field_id == "carrier_id":
            self._out[field_id] = M2OHelper.get_name(self.object, field_id)
            self._in.__delitem__(index)
        # ====================================================================#
        # Delivery Carrier Description
        if field_id == "carrier_desc":
            self._out[field_id] = self.object.carrier_id.name if self.object.carrier_id.id else None
            self._in.__delitem__(index)

    def setDeliveryFields(self, field_id, field_data):
        # ====================================================================#
        # Delivery Carrier Name
        if field_id == "carrier_id":
            M2OHelper.set_name(self.object, field_id, field_data, domain="delivery.carrier")
            self._in.__delitem__(field_id)

