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

from splashpy import const, Framework
from splashpy.componants import FieldFactory


class Contact:
    """
    Manage type "contact" from Address class
    """

    def buildContactFields(self):
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_COUNTRY__, "street", "Street")
        FieldFactory.microData("http://schema.org/PostalAddress", "streetAddress")
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "zip", "ZIP Code")
        FieldFactory.microData("http://schema.org/PostalAddress", "postalCode")
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "city", "City Name")
        FieldFactory.microData("http://schema.org/PostalAddress", "addressLocality")

    def getContactFields(self, index, field_id):

        # ==================================================================== #
        # Filter on Field Id
        if field_id not in ["street", "zip", "city"]:
            return
        # ==================================================================== #
        # Read
        self._out[field_id] = self.object[field_id]
        self._in.__delitem__(index)


    def setContactFields(self, field_id, field_data):

        # ==================================================================== #
        # Filter on Field Id
        if field_id not in ["street", "zip", "city"]:
            return

        # ==================================================================== #
        # Detect Contact Types
        if self.is_a_contact():
            Framework.log().warn('Contact Address Type, field cannot be written!!')

        # ==================================================================== #
        if not self.is_a_contact() and (getattr(self.object, "parent_id") is not None):
            setattr(self.object, field_id, field_data)

        self._in.__delitem__(field_id)
        # ==================================================================== #

    def is_a_contact(self):
        ctc = str(getattr(self.object, "type"))
        if ctc == 'contact':
            return True
        return False
