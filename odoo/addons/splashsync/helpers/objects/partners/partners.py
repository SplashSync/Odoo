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

from splashpy import Framework


class PartnersHelper:
    """
    Access to Parent partners
    """
    # ==================================================================== #
    # Filters for Address Object & ThirdParty Object
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

    def is_partner(self):
        """
        Detect if Object is a Partner
        :return: bool
        """
        if not self._inherit == 'res.partner':
            Framework.log().warn('This Object is not a Partner')
            return False
        return True

    def is_address(self):
        """
        Detect if Object is an Address
        :return: bool
        """
        # ==================================================================== #
        # Safety Check - Partner
        if not PartnersHelper.is_partner(self):
            return False
        # ==================================================================== #
        # Check condition - Parent Id
        if self.parent_id.id is False:
            Framework.log().warn('This Object has no Parent')
            return False
        # ==================================================================== #
        # Check condition - No Child Ids
        if self.child_ids.ids:
            Framework.log().warn('This Object has one (or few) Child(s)')
            return False
        # ==================================================================== #
        # Check condition - Type <> 'private'
        if self.type == 'private':
            Framework.log().warn('This Object is Private')
            return False

        return True

    def is_thirdparty(self):
        """
        Detect if Object is a Thirdparty
        :return: bool
        """
        # ==================================================================== #
        # Safety Check - Partner
        if not PartnersHelper.is_partner(self):
            return False
        # ==================================================================== #
        # Check condition - No Parent Id
        if self.parent_id.id is not False:
            Framework.log().warn('This Object has a Parent')
            return False

        return True
