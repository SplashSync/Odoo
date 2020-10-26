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
from .addresses import AddresseName, AddresseContact
from .model import OdooObject


class Address(OdooObject, PartnersCountry, AddresseName, PartnersParent, AddresseContact):
    # ====================================================================#
    # Splash Object Definition
    name = "Address"
    desc = "Odoo Address"
    icon = "fa fa-envelope-o"

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
        return PartnersHelper.address_filter()

    @staticmethod
    def get_listed_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['name', 'email', 'type']

    @staticmethod
    def get_required_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['parent_id', 'type', 'name']

    @staticmethod
    def get_composite_fields():
        """Get List of Fields NOT To Parse Automatically """
        return [
            "id", 'message_follower_ids', 'image_medium', 'image_small',
            'company_name', 'vat', "credit_limit", "street2", "street", "zip", "city"
        ]

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        configuration = {
            "function": {"group": "", "itemtype": "http://schema.org/Person", "itemprop": "jobTitle"},

            "email": {"type": const.__SPL_T_EMAIL__, "group": "", "itemtype": "http://schema.org/ContactPoint", "itemprop": "email"},
            "mobile": {"type": const.__SPL_T_PHONE__, "group": "", "itemtype": "http://schema.org/Person", "itemprop": "telephone"},
            "phone": {"type": const.__SPL_T_PHONE__, "group": "", "itemtype": "http://schema.org/PostalAddress", "itemprop": "telephone"},

            "name": {"required": False, "write": False},
            "type": {"required": False},

            "street": {"group": "Address", "itemtype": "http://schema.org/PostalAddress", "itemprop": "streetAddress"},
            "zip": {"group": "Address", "itemtype": "http://schema.org/PostalAddress", "itemprop": "postalCode"},
            "city": {"group": "Address", "itemtype": "http://schema.org/PostalAddress", "itemprop": "addressLocality"},
            "country_name": {"group": "Address"},
            "country_code": {"group": "Address"},
            "state_id": {"group": "Address"},

            "active": {"group": "Meta", "itemtype": "http://schema.org/Person", "itemprop": "active"},
            "create_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateCreated"},
            "write_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateModified"},

            "website": {"group": "", "type": const.__SPL_T_URL__, "itemtype": "http://schema.org/Organization", "itemprop": "url"},
            "activity_summary": {"write": False},

            "additional_info": {"notest": True},

            "image": {"group": "Images", "notest": True},
        }

        # ====================================================================#
        # Type Configuration for DebugMode
        if Framework.isDebugMode():
            configuration["type"]["choices"] = {
                "contact": "Contact",
                "delivery": "Delivery Address",
                "invoice": "Invoice Address",
                "other": "Other Address"
            }

        return configuration

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def create(self):
        """
        Create a New Address
        :return: Address Object
        """
        # ====================================================================#
        # Safety Check - First Name is Required
        if "first" not in self._in:
            Framework.log().error("No Legal Name provided, Unable to create Address")
            return False
        # ====================================================================#
        # Load First Name Field in Name Field
        self._in["name"] = self._in["first"]
        # ====================================================================#
        # Safety Check - Address Type is Required (Auto-provide if needed)
        if "type" not in self._in:
            self._in["type"] = "other"
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
        # Create a New Simple Address
        new_address = self.getModel().create(req_fields)
        # ====================================================================#
        # Safety Check - Error
        if new_address is None:
            Framework.log().error("Address is None")
            return False
        # ====================================================================#
        # Initialize Address Fullname buffer
        self.object = new_address
        self.initfullname()

        return new_address

    def load(self, object_id):
        """
        Load Odoo Object by Id
        :param object_id: str
        :return: Address Object
        """
        # ====================================================================#
        # Load Address
        model = super(Address, self).load(object_id)
        # ====================================================================#
        # Safety Check - Loaded Object is an Address
        if not PartnersHelper.is_address(model):
            Framework.log().error('This Object is not an Address')
            return False
        # ====================================================================#
        # Initialize Address Fullname buffer
        if model:
            self.object = model
            self.initfullname()

        return model

    def update(self, needed):
        """
        Update Current Odoo Object
        :param needed: bool
        :return: Address Object
        """
        self._in["name"] = True
        self.setSimple("name", self.encodefullname())

        return super(Address, self).update(needed)
