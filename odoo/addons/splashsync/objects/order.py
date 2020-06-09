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

from . import OdooObject
from splashpy import const
from .orders import Orderslines


class Order(OdooObject, Orderslines):
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
            # 'name', 'date_order', 'currency_id',
            # 'partner_id', 'partner_invoice_id', 'partner_shipping_id',
            # 'pricelist_id', 'warehouse_id', 'picking_policy'
        ]

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        return {

            "activity_summary": {"write": False},

            "create_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateCreated"},
            "write_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateModified"},

         }

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def create(self):
        """Create a New Order"""
        # ====================================================================#
        # Init List of required Fields
        reqFields = self.collectRequiredCoreFields()
        if reqFields is False:
            return False

        # ====================================================================#
        # TODO FOR DEV
        reqFields["partner_id"] = 11
        # ====================================================================#
        # Create a New Simple Order
        return self.getModel().create(reqFields)
