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

    @staticmethod
    def is_partner(model):
        """
        Detect if Object is a Partner
        :param model: Object
        :return: bool
        """
        return model._inherit == 'res.partner'

    @staticmethod
    def is_address(model):
        """
        Detect if Object is an Address
        :param model: Object
        :return: bool
        """
        # ==================================================================== #
        # Safety Check - Partner
        if not PartnersHelper.is_partner(model):
            return False
        # ==================================================================== #
        # Check condition - Parent Id
        if model.parent_id.id is False:
            Framework.log().warn('This Object has no Parent')
            return False
        # ==================================================================== #
        # Check condition - No Child Ids
        if model.child_ids.ids:
            Framework.log().warn('This Object has one (or few) Child(s)')
            return False
        # ==================================================================== #
        # Check condition - Type <> 'private'
        if model.type == 'private':
            Framework.log().warn('This Object is Private')
            return False

        return True

    @staticmethod
    def is_thirdparty(model):
        """
        Detect if Object is a Thirdparty
        :param model: Object
        :return: bool
        """
        # ==================================================================== #
        # Safety Check - Partner
        if not PartnersHelper.is_partner(model):
            return False
        # ==================================================================== #
        # Check condition - No Parent Id
        if len(model.parent_id) > 0:
            Framework.log().warn('This Object has a Parent')
            return False

        return True

    @staticmethod
    def is_contact(model):
        """
        Detect if Address Type is Contact
        :param model: Object
        :return: bool
        """
        try:
            return str(getattr(model, "type")) == 'contact'
        except Exception:
            return False
