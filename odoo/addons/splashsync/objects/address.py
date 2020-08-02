#
#  This file is part of SplashSync Project.
#
#  Copyright (C) 2015-2020 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

import logging
from .model import OdooObject
from splashpy import const, Framework
from .thirdparties import Relatives
from .thirdparties import Country
from .thirdparties import AddrName


class Address(OdooObject, Country, AddrName, Relatives):
    # ====================================================================#
    # Splash Object Definition
    name = "Address"
    desc = "Odoo Address"
    icon = "fa fa-address-card-o"

    @staticmethod
    def getDomain():
        return 'res.partner'

    @staticmethod
    def objectsListFiltered():
        return [('parent_id', '<>', None), ('child_ids', '=', False)]

    @staticmethod
    def get_listed_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['name', 'email']

    @staticmethod
    def get_required_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['parent_id', 'type', 'name']

    @staticmethod
    def get_composite_fields():
        """Get List of Fields NOT To Parse Automatically """
        return ["id", 'message_follower_ids', 'image_medium', 'image_small', 'company_name', 'vat', "credit_limit", "street2"]

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        return {

            "email": {"type": const.__SPL_T_EMAIL__, "group": "", "itemtype": "http://schema.org/ContactPoint", "itemprop": "email"},
            "phone": {"type": const.__SPL_T_PHONE__, "group": "", "itemtype": "http://schema.org/Person", "itemprop": "telephone"},

            "name": {"required": False, "write": False},
            "type": {"notest": True},

            "street": {"group": "Address", "itemtype": "http://schema.org/PostalAddress", "itemprop": "streetAddress"},
            # "street2": {"group": "Address", "itemtype": "http://schema.org/PostalAddress", "itemprop": "postOfficeBoxNumber"},
            "zip": {"group": "Address", "itemtype": "http://schema.org/PostalAddress", "itemprop": "postalCode"},
            "city": {"notest": True, "group": "Address", "itemtype": "http://schema.org/PostalAddress", "itemprop": "addressLocality"},
            "country_name": {"notest": True, "group": "Address"},
            "country_code": {"notest": True, "group": "Address"},

            # "customer": {"group": "Meta", "itemtype": "http://schema.org/Organization", "itemprop": "customer"},
            # "supplier": {"group": "Meta", "itemtype": "http://schema.org/Organization", "itemprop": "supplier"},
            "active": {"group": "Meta", "itemtype": "http://schema.org/Organization", "itemprop": "active"},
            "create_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateCreated"},
            "write_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateModified"},

            "website": {"group": "", "type": const.__SPL_T_URL__, "itemtype": "http://schema.org/Organization", "itemprop": "url"},
            "activity_summary": {"write": False},

            "additional_info": {"notest": True},

            "image": {"group": "Images", "notest": True},
        }

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def create(self):
        """Create a New Address"""
        # ====================================================================#
        # Safety Check
        if "first" not in self._in:
            Framework.log().error("No Legal Name provided, Unable to create ThirdParty")
            return False
        # ====================================================================#
        # Init List of required Fields
        self._in["name"] = self._in["first"]
        req_fields = self.collectRequiredCoreFields()
        self._in.__delitem__("name")
        if req_fields.__len__() < 1:
            return False
        # ====================================================================#
        # Create a New Simple 3rdP
        newAddress = self.getModel().create(req_fields)
        if newAddress is None:
            Framework.log().error("Address is None")
            return False
        return newAddress
