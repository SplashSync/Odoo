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


class Name:
    """
    Manage Encode/Decode Concatenated Name
    """
    # ==================================================================== #
    # Init Buffer
    fullname_buffer = {}

    def buildNameFields(self):
        FieldFactory.create(const.__SPL_T_VARCHAR__, "legal", "Legal Name")
        FieldFactory.microData("http://schema.org/Organization", "legalName")
        FieldFactory.isRequired()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "last", "Last Name")
        FieldFactory.microData("http://schema.org/Person", "givenName")
        FieldFactory.association('first')
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "first", "First Name")
        FieldFactory.microData("http://schema.org/Person", "familyName")

    def getNameFields(self, index, field_id):
        # ==================================================================== #
        # Filter on Field Id
        if field_id not in ["legal", "first", "last"]:
            return
        # ==================================================================== #
        # Read & Decode Field Data
        self._out[field_id] = self.decodefullname()[field_id]
        self._in.__delitem__(index)

    def setNameFields(self, field_id, field_data):
        # ==================================================================== #
        # Filter on Field Id
        if field_id not in ["legal", "first", "last"]:
            return
        # ==================================================================== #
        # Safety Check
        if field_data is None:
            field_data = ""
        # ==================================================================== #
        # WRITE Field Data in Buffer
        self.fullname_buffer[field_id] = str(field_data).strip()
        self._in.__delitem__(field_id)
        # ==================================================================== #
        # Once all Fullname's Fields are Parsed, then Encode & Set Fullname
        if all(x not in self._in for x in ["first", "last", "legal"]):
            setattr(self.object, "name", self.encodefullname())

    def decodefullname(self):
        """
        Decode Legal Name, Last Name & First Name from Thirdparty name
        :return: dict
        """
        # ==================================================================== #
        # Init dict
        elements = {"first": "", "last": "", "legal": ""}
        # ==================================================================== #
        # Get Fullname to decode
        fullname = str(getattr(self.object, "name")).strip()
        # ==================================================================== #
        # Saety Check
        if fullname is None:
            return
        # ==================================================================== #
        # Decode
        if " - " not in fullname:
            elements["legal"] = fullname
        if " - " in fullname:
            elements["legal"] = fullname.split(" - ")[-1].strip()
            residual = fullname.split(" - ")[0].strip()
            if ", " not in residual:
                elements["first"] = residual.strip()
            else:
                elements["first"] = residual.split(", ")[0].strip()
                elements["last"] = residual.split(", ")[-1].strip()

        return elements

    def encodefullname(self):
        """
        Encode First Name, Last Name & Legal Name from Buffer
        :return: str
        """
        # ==================================================================== #
        # Get Data To Encode
        first = self.fullname_buffer["first"]
        last = self.fullname_buffer["last"]
        legal = self.fullname_buffer["legal"]
        # ==================================================================== #
        # Safety Warn
        if legal == "":
            legal = "Legal Name not Defined"
            Framework.log().warn("Legal Name not defined")
        # ==================================================================== #
        # Encode
        if (isinstance(first, str)) and (len(first) > 0):
            if (isinstance(last, str)) and (len(last) > 0):
                result = first + ", " + last + " - " + legal   # first, last - legal
            else:
                result = first + " - " + legal                 # first - legal
        else:
            result = legal                                     # legal

        return result

    def initfullname(self):
        self.fullname_buffer = self.decodefullname()

        return
