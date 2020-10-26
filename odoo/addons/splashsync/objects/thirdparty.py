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

from odoo.addons.splashsync.helpers import PartnersHelper
from odoo.addons.splashsync.objects.partners import PartnersCountry, PartnersParent
from splashpy import const, Framework
from .model import OdooObject
from .thirdparties import ThirdPartyName


class ThirdParty(OdooObject, PartnersParent, PartnersCountry, ThirdPartyName):
    # ====================================================================#
    # Splash Object Definition
    name = "ThirdParty"
    desc = "Odoo Partner"
    icon = "fa fa-user"

    # ====================================================================#
    # Object Default Configuration
    # ====================================================================#
    # Imports
    enable_pull_created = True
    enable_pull_updated = True
    enable_pull_deleted = True
    # Exports
    enable_push_created = True
    enable_push_updated = True
    enable_push_deleted = False

    @staticmethod
    def getDomain():
        return 'res.partner'

    @staticmethod
    def objectsListFiltered():
        """Filter on Search Query"""
        return PartnersHelper.thirdparty_filter()

    @staticmethod
    def get_listed_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['name', 'email', 'is_company', 'type']

    @staticmethod
    def get_required_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['name']

    @staticmethod
    def get_composite_fields():
        """Get List of Fields NOT To Parse Automatically """
        return ["id", 'message_follower_ids', 'image_medium', 'image_small']

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        return {

            "email": {"type": const.__SPL_T_EMAIL__, "group": "", "itemtype": "http://schema.org/ContactPoint", "itemprop": "email"},
            "phone": {"type": const.__SPL_T_PHONE__, "group": "", "itemtype": "http://schema.org/Person", "itemprop": "telephone"},

            "name": {"required": False, "write": False},
            "type": {"choices": {"contact": "Contact"}},

            "street": {"group": "Address", "itemtype": "http://schema.org/PostalAddress", "itemprop": "streetAddress"},
            "zip": {"group": "Address", "itemtype": "http://schema.org/PostalAddress", "itemprop": "postalCode"},
            "city": {"group": "Address", "itemtype": "http://schema.org/PostalAddress", "itemprop": "addressLocality"},
            "country_name": {"group": "Address"},
            "country_code": {"group": "Address"},
            "state_id": {"group": "Address"},

            "customer": {"group": "Meta", "itemtype": "http://schema.org/Organization", "itemprop": "customer"},
            "supplier": {"group": "Meta", "itemtype": "http://schema.org/Organization", "itemprop": "supplier"},

            "active": {"group": "Meta", "itemtype": "http://schema.org/Organization", "itemprop": "active"},
            "create_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateCreated"},
            "write_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateModified"},

            "website": {"group": "", "type": const.__SPL_T_URL__, "itemtype": "http://schema.org/Organization", "itemprop": "url"},
            "activity_summary": {"write": False},

            "additional_info": {"notest": True},
            "parent_id": {"notest": True},

            "image": {"group": "Images", "notest": True},
        }

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def create(self):
        """
        Create a New ThirdParty
        :return: ThirdParty Object
        """
        # ====================================================================#
        # Safety Check - Legal Name is Required
        if "legal" not in self._in:
            Framework.log().error("No Legal Name provided, Unable to create ThirdParty")
            return False
        # ====================================================================#
        # Load Legal Name Field in Name Field
        self._in["name"] = self._in["legal"]
        # ====================================================================#
        # Init List of required Fields
        req_fields = self.collectRequiredCoreFields()
        # ====================================================================#
        # Delete Name Field
        self._in.__delitem__("name")
        # ====================================================================#
        # Safety Check
        if req_fields.__len__() < 1:
            return False
        # ====================================================================#
        # Create a New Simple ThirdParty
        new_thirdparty = self.getModel().create(req_fields)
        # ====================================================================#
        # Safety Check - Error
        if new_thirdparty is None:
            Framework.log().error("ThirdParty is None")
            return False
        # ====================================================================#
        # Initialize ThirdParty Fullname buffer
        self.object = new_thirdparty
        self.initfullname()

        return new_thirdparty

    def load(self, object_id):
        """
        Load Odoo Object by Id
        :param object_id: str
        :return: ThirdParty Object
        """
        # ====================================================================#
        # Load Address
        model = super(ThirdParty, self).load(object_id)
        # ====================================================================#
        # Safety Check - Loaded Object is a ThirdParty
        if not PartnersHelper.is_thirdparty(model):
            Framework.log().warn('This Object is not a ThirdParty')
            return False
        # ====================================================================#
        # Initialize ThirdParty fullname_buffer
        if model:
            self.object = model
            self.initfullname()

        return model

    def update(self, needed):
        """
        Update Current Odoo Object
        :param needed: bool
        :return: Thirdparty Object
        """
        self._in["name"] = True
        self.setSimple("name", self.encodefullname())

        return super(ThirdParty, self).update(needed)
