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

from odoo.addons.splashsync.helpers.objects.relations import M2OHelper
from splashpy import const
from splashpy.componants import FieldFactory


class PartnersCountry:
    """
    Access to Country Fields
    """
    def buildCountryFields(self):
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_COUNTRY__, "country_code", "Country Code")
        FieldFactory.microData("http://schema.org/PostalAddress", "addressCountry")
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "country_name", "Country Name")
        FieldFactory.microData("http://schema.org/PostalAddress", "addressCountryName")
        FieldFactory.addChoices(M2OHelper.get_name_values("res.country"))
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_STATE__, "state_id", "State Code")
        FieldFactory.microData("http://schema.org/PostalAddress", "addressRegion")

    def getCountryFields(self, index, field_id):
        # ==================================================================== #
        # Filter on Field Id
        if not self.isCountryFields(field_id):
            return
        # ==================================================================== #
        # Read Field Data
        if field_id == "country_code":
            self._out[field_id] = M2OHelper.get_name(self.object, "country_id", index="code")
            self._in.__delitem__(index)
        if field_id == "country_name":
            self._out[field_id] = M2OHelper.get_name(self.object, "country_id")
            self._in.__delitem__(index)
        if field_id == "state_id":
            self._out[field_id] = M2OHelper.get_name(self.object, "state_id", index="code")
            self._in.__delitem__(index)

    def setCountryFields(self, field_id, field_data):
        # ==================================================================== #
        # Filter on Field Id
        if not self.isCountryFields(field_id):
            return
        # ==================================================================== #
        # WRITE Field Data
        if field_id == "country_code":
            M2OHelper.set_name(self.object, "country_id", field_data, domain="res.country", index="code")
            self._in.__delitem__(field_id)
        if field_id == "state_id":
            M2OHelper.set_name(self.object, "state_id", field_data, domain="res.country.state", index="code")
            self._in.__delitem__(field_id)
        if field_id == "country_name":
            M2OHelper.set_name(self.object, "country_id", field_data, domain="res.country")
            self._in.__delitem__(field_id)

    @staticmethod
    def isCountryFields(field_id):
        """
        Check if Field is a Country Field
        :param field_id: str
        :return: bool
        """
        return field_id in [
            "country_name", "country_code", "state_id"
        ]
