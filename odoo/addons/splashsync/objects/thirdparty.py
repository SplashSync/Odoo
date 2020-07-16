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
# from .thirdparties import Relatives
from .thirdparties import Country
from .thirdparties import Name


# class ThirdParty(OdooObject, Relatives, Country, Name):
class ThirdParty(OdooObject, Country, Name):
    # ====================================================================#
    # Splash Object Definition
    name = "ThirdParty"
    desc = "Odoo Partner"
    icon = "fa fa-user"

    @staticmethod
    def getDomain():
        return 'res.partner'

    @staticmethod
    def objectsListFiltered():
        return [('parent_id', '=', None)]

    @staticmethod
    def get_listed_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['name', 'email', "is_company"]

    @staticmethod
    def get_required_fields():
        """Get List of Object Fields to Include in Lists"""
        return ["legal"]

    # @staticmethod
    # def get_composite_fields():
    #     """Get List of Fields NOT To Parse Automatically """
    #     return ['name']

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        return {

            "email": {"type": const.__SPL_T_EMAIL__, "group": "", "itemtype": "http://schema.org/ContactPoint",
                      "itemprop": "email"},
            "phone": {"type": const.__SPL_T_PHONE__, "group": "", "itemtype": "http://schema.org/Person",
                      "itemprop": "telephone"},

            "name": {"required": False, "write": False},
            "legal": {"group": "", "itemtype": "http://schema.org/Organization", "itemprop": "legalName"},

            "street": {"group": "Address", "itemtype": "http://schema.org/PostalAddress", "itemprop": "streetAddress"},
            # "street2": {"group": "Address", "itemtype": "http://schema.org/PostalAddress", "itemprop": "postOfficeBoxNumber"},
            "zip": {"group": "Address", "itemtype": "http://schema.org/PostalAddress", "itemprop": "postalCode"},
            "city": {"group": "Address", "itemtype": "http://schema.org/PostalAddress", "itemprop": "addressLocality"},
            "country_name": {"group": "Address"},
            "country_code": {"group": "Address"},

            "customer": {"group": "Meta", "itemtype": "http://schema.org/Organization", "itemprop": "customer"},
            "supplier": {"group": "Meta", "itemtype": "http://schema.org/Organization", "itemprop": "supplier"},
            "active": {"group": "Meta", "itemtype": "http://schema.org/Organization", "itemprop": "active"},
            "create_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateCreated"},
            "write_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateModified"},

            "website": {"group": "", "type": const.__SPL_T_URL__, "itemtype": "http://schema.org/Organization",
                        "itemprop": "url"},
            "activity_summary": {"write": False},

            "additional_info": {"notest": True},
            "message_follower_ids": {"notest": True},

            "image": {"group": "Images", "notest": True},
            "image_medium": {"group": "Images", "write": False},
            "image_small": {"group": "Images", "write": False},

        }

    def order_inputs(self):
        """Ensure Inputs are Correctly Ordered"""
        from collections import OrderedDict
        self._in = OrderedDict(sorted(self._in.items()))

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def create(self):
        """Create a New 3rdP"""
        if "name" not in self._in:
            self._in["name"] = self._in["legal"]
            self._in.__delitem__("legal")
        # ====================================================================#
        # Order Fields Inputs
        self.order_inputs()
        # ====================================================================#
        # Init List of required Fields
        # reqFields = self.collectRequiredCoreFields()
        reqFields = self._in
        Framework.log().dump(reqFields)
        if reqFields is False:
            return False
        # ====================================================================#
        # Create a New Simple 3rdP
        self.object.is_company = 1
        newthirdP = self.getModel().create(reqFields)

        if newthirdP is None:
            return False

        self._in.__delitem__("name")
        return newthirdP
