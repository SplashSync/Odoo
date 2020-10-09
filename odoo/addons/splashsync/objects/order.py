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

from odoo.addons.splashsync.helpers import CustomerHelper
from splashpy import const, Framework
from . import OdooObject
from .orders import Orderlines


class Order(OdooObject, Orderlines, CustomerHelper):
    # ====================================================================#
    # Splash Object Definition
    name = "Order"
    desc = "Odoo Order"
    icon = "fa fa-shopping-cart"

    @staticmethod
    def getDomain():
        return 'sale.order'

    @staticmethod
    def get_listed_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['client_order_ref', 'name', 'date_order', 'type_name']

    @staticmethod
    def get_required_fields():
        """Get List of Object Fields to Include in Lists"""
        return [
            'partner_id', 'partner_invoice_id', 'partner_shipping_id',
        ]

    @staticmethod
    def get_composite_fields():
        """Get List of Fields NOT To Parse Automatically """
        return [
            "id", "partner_id", "partner_invoice_id", "partner_shipping_id"
        ]

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        return {
            "name": {"group": "General", "itemtype": "http://schema.org/Order", "itemprop": "name"},
            "state": {"group": "General", "itemtype": "http://schema.org/Order", "itemprop": "paymentStatus"},

            "description": {"group": "General", "itemtype": "http://schema.org/Order", "itemprop": "description"},
            "date_due": {"group": "General", "itemtype": "http://schema.org/Order", "itemprop": "paymentDueDate"},
            "date_invoice": {"group": "General", "itemtype": "http://schema.org/Order", "itemprop": "dateCreated"},
            "reference": {"group": "General", "itemtype": "http://schema.org/Order", "itemprop": "confirmationNumber"},

            "create_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateCreated"},
            "write_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateModified"},

            "date_order": {"type": const.__SPL_T_DATE__, "group": "", "itemtype": "http://schema.org/Order", "itemprop": "orderDate"},

         }

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def create(self):
        """
        Create a New Order
        :return: Order Object
        """
        # ====================================================================#
        # Safety Check - Customer, Invoice Address, Shipping Address are required
        if "partner_id" not in self._in:
            Framework.log().error("No Customer provided, Unable to create Order")
            return False
        if "partner_invoice_id" not in self._in:
            Framework.log().error("No Invoice Address provided, Unable to create Order")
            return False
        if "partner_shipping_id" not in self._in:
            Framework.log().error("No Shipping Address provided, Unable to create Order")
            return False
        # ====================================================================#
        # Init List of required Fields
        req_fields = self.collectRequiredCoreFields()
        # ====================================================================#
        # Safety Check
        if req_fields.__len__() < 1:
            return False
        # ====================================================================#
        # Create a New Simple Order
        new_order = self.getModel().create(req_fields)
        # ====================================================================#
        # Safety Check - Error
        if new_order is None:
            Framework.log().error("Order is None")
            return False

        return new_order

    # def load(self, object_id):
    #     """
    #     Load Odoo Object by Id
    #     :param object_id: str
    #     :return: Order Object
    #     """
    #     # ====================================================================#
    #     # Load Order
    #     model = super(Order, self).load(object_id)
    #     # ====================================================================#
    #     # TODO: Safety Check - Loaded Object is an Order
    #     # if not PartnersHelper.is_address(model):
    #     #     Framework.log().error('This Object is not an Address')
    #     #     return False
    #
    #     return model
    #
    # def update(self, needed):
    #     """
    #     Update Current Odoo Object
    #     :param needed: bool
    #     :return: Order Object
    #     """
    #
    #     return super(Order, self).update(needed)
