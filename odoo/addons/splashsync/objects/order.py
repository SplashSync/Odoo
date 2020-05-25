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
from splashpy import const


class Order(OdooObject):
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
        return ['name', 'display_name', 'client_order_ref', 'id']

    @staticmethod
    def get_required_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['company_id', 'currency_id', 'journal_id']

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        return {
                "name": {"group": "General", "itemtype": "http://schema.org/Invoice", "itemprop": "name"},
                "state": {"group": "General", "itemtype": "http://schema.org/Invoice", "itemprop": "paymentStatus"},

                "description": {"group": "General", "itemtype": "http://schema.org/Invoice", "itemprop": "description"},
                "date_due": {"group": "General", "itemtype": "http://schema.org/Invoice", "itemprop": "paymentDueDate"},
                "date_invoice": {"group": "General", "itemtype": "http://schema.org/Invoice", "itemprop": "dateCreated"},
                "reference": {"group": "General", "itemtype": "http://schema.org/Invoice", "itemprop": "confirmationNumber"},

                "create_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateCreated"},
                "__last_update": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateModified"},

                # "account.invoice.line[invoice_id]": {"group": "General", "itemtype": "http://schema.org/Invoice", "itemprop": "name"},
        }

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def create(self):
        """Create a New Invoice"""
        # ====================================================================#
        # Init List of required Fields
        reqFields = self.collectRequiredCoreFields()
        if reqFields is False:
            return False
        # ====================================================================#
        # Create a New Simple Product
        return self.getModel().create(reqFields)
