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


class AddrName:
    """
    Manage Encode/Decode Concatenated AddrName
    """

    addr_fullname_buffer = {}

    def buildAddrNameFields(self):
        FieldFactory.create(const.__SPL_T_VARCHAR__, "last", "Last Name")
        FieldFactory.microData("http://schema.org/Person", "givenName")
        FieldFactory.association('first')
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "first", "First Name")
        FieldFactory.microData("http://schema.org/Person", "familyName")
        FieldFactory.isRequired()

    def getAddrNameFields(self, index, field_id):
        # ==================================================================== #
        # Filter on Field Id
        if field_id not in ["first", "last"]:
            return
        # ==================================================================== #
        # Read & Decode Field Data
        self._out[field_id] = self.decodefullname()[field_id]
        self._in.__delitem__(index)

    def setAddrNameFields(self, field_id, field_data):
        # ==================================================================== #
        # Filter on Field Id
        if field_id not in ["first", "last"]:
            return
        # ==================================================================== #
        # Safety Check
        if field_data is None:
            field_data = ""
        # ==================================================================== #
        # WRITE Field Data in Buffer
        self.addr_fullname_buffer[field_id] = str(field_data).strip()
        self._in.__delitem__(field_id)
        # ==================================================================== #
        # Once all Fullname's Fields are Parsed, then Encode & Set Fullname
        if all(x not in self._in for x in ["first", "last"]):
            setattr(self.object, "name", self.encodefullname())

    def decodefullname(self):
        """
        Decode Last Name & First Name from Contact Name
        :return: dict
        """
        # ==================================================================== #
        # Init dict
        elements = {"first": "", "last": ""}
        # ==================================================================== #
        # Get Fullname to decode
        fullname = str(getattr(self.object, "name")).strip()
        # ==================================================================== #
        # Decode
        if ", " not in fullname:
            elements["first"] = fullname.strip()
        else:
            elements["first"] = fullname.split(", ")[0].strip()
            elements["last"] = fullname.split(", ")[-1].strip()

        return elements

    def encodefullname(self):
        """
        Encode Last Name & First Name from Buffer
        :return: str
        """
        # ==================================================================== #
        # Init return as empty str
        result = ""
        # ==================================================================== #
        # Get Data To Encode
        first = self.addr_fullname_buffer["first"]
        last = self.addr_fullname_buffer["last"]
        # ==================================================================== #
        # Encode
        if (isinstance(first, str)) and (len(first) > 0):
            if (isinstance(last, str)) and (len(last) > 0):
                result = first + ", " + last                    # first, last
            else:
                result = first                                  # first

        return result                                           # ""

    def initfullname(self):
        self.addr_fullname_buffer = self.decodefullname()

        return
