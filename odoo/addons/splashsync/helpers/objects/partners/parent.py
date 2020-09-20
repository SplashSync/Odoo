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
from splashpy.helpers import ObjectsHelper
from odoo.addons.splashsync.helpers.objects.relations import M2OHelper


class ParentHelper:
    """
    Access to Parent partners
    """

    def buildParentFields(self):
        FieldFactory.create(ObjectsHelper.encode("ThirdParty", const.__SPL_T_ID__), "parent_id", "Parent")
        FieldFactory.microData("http://schema.org/Organization", "ID")
        if self.name is "Address":
            FieldFactory.isRequired()

    def getParentFields(self, index, field_id):
        # ==================================================================== #
        # Filter on Field Id
        if field_id != "parent_id":
            return
        # ==================================================================== #
        # Read Field Data
        self._out[field_id] = M2OHelper.get_object(self.object, "parent_id", "ThirdParty")
        self._in.__delitem__(index)

    def setParentFields(self, field_id, field_data):
        # ==================================================================== #
        # Filter on Field Id
        if field_id != "parent_id":
            return
        # ==================================================================== #
        # Write Field Data
        M2OHelper.set_object(self.object, "parent_id", field_data, domain="res.partner")
        self._in.__delitem__(field_id)

    # ==================================================================== #
    # Filters for Address Object & Thirdparty Object
    @staticmethod
    def address_filter():
        """
        Filter Address Objects (Parent, no Child, Address type except private)
        :return: list of tuples
        """
        return [('parent_id', '<>', None),
                ('child_ids', '=', False),
                ('type', '<>', 'private')
                ]

    @staticmethod
    def thirdparty_filter():
        """
        Filter Thirdparty Objects (No Parent)
        :return: list of tuples
        """
        return [('parent_id', '=', None)]

    # ==================================================================== #
    # Detect Class of Partner Object
    def is_address(self):
        """
        Detect if Object is an Address
        :return: bool
        """
        return (M2OHelper.get_object(self, "parent_id", "ThirdParty") is not None) and (self.type != 'private') and ((M2OHelper.get_object(self, "child_ids", "Address") is None) or (M2OHelper.get_object(self, "child_ids", "ThirdParty") is None))

    def is_thirdparty(self):
        """
        Detect if Object is a Thirdparty
        :return: bool
        """
        return M2OHelper.get_object(self, "parent_id", "ThirdParty") is None
