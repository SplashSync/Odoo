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

    varfullname = {"first": "", "last": ""}

    def buildAddrNameFields(self):
        FieldFactory.create(const.__SPL_T_VARCHAR__, "last", "Last Name")
        FieldFactory.microData("http://schema.org/Person", "givenName")
        FieldFactory.association('first')
        # FieldFactory.isNotTested()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "first", "First Name")
        FieldFactory.microData("http://schema.org/Person", "familyName")
        FieldFactory.isRequired()
        # FieldFactory.isNotTested()

    def getAddrNameFields(self, index, field_id):
        if field_id == "first":
            self._out[field_id] = AddrName.decodefullname(self)[field_id]
            self._in.__delitem__(index)
        if field_id == "last":
            self._out[field_id] = AddrName.decodefullname(self)[field_id]
            self._in.__delitem__(index)

    def setAddrNameFields(self, field_id, field_data):
        if field_data is None:
            field_data = ""
        if field_id == "first":
            AddrName.varfullname[field_id] = AddrName.decodefullname(self)[field_id]
            if AddrName.isactualdatadifferent(self, field_id, field_data):
                AddrName.varfullname[field_id] = str(field_data).strip()
            self._in.__delitem__(field_id)
        if field_id == "last":
            AddrName.varfullname[field_id] = AddrName.decodefullname(self)[field_id]
            if AddrName.isactualdatadifferent(self, field_id, field_data):
                AddrName.varfullname[field_id] = str(field_data).strip()
            self._in.__delitem__(field_id)
        if all(x not in self._in for x in ["first", "last"]):
            setattr(self.object, "name", AddrName.encodefullname(AddrName.varfullname["first"], AddrName.varfullname["last"]))

    def decodefullname(self):
        elements = {"first": "", "last": ""}
        fullname = str(getattr(self.object, "name")).strip()
        if fullname is None:
            return
        if ", " not in fullname:
            elements["first"] = fullname.strip()
        else:
            elements["first"] = fullname.split(", ")[0].strip()
            elements["last"] = fullname.split(", ")[-1].strip()
        return elements

    @staticmethod
    def encodefullname(first, last):
        result = ""
        if (isinstance(first, str)) and (len(first) > 0):
            if (isinstance(last, str)) and (len(last) > 0):
                result = first + ", " + last   # first, last
            else:
                result = first                 # first
        return result

    def isactualdatadifferent(self, field_id, field_data):
        actualfield = AddrName.decodefullname(self)[field_id]
        return field_data != actualfield
