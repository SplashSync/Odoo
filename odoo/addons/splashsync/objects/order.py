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

from splashpy import Framework
from . import OdooObject
from .orders import Orderlines, OrderCore, OrderStatus, OrderCarrier, OrderDelivery, OrderRelations, OrderAddress
from odoo.exceptions import MissingError

class Order(OdooObject, OrderCore, OrderAddress, OrderRelations, OrderCarrier, OrderDelivery, OrderStatus, Orderlines):
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
        return ['partner_id', 'partner_invoice_id', 'partner_shipping_id']

    @staticmethod
    def get_composite_fields():
        """Get List of Fields NOT To Parse Automatically """
        return ['id', 'date_order', 'state']

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        return {
            "name": {"write": True, "group": "General", "itemtype": "http://schema.org/Order", "itemprop": "name"},
            "client_order_ref": {"write": True, "group": "General", "itemtype": "http://schema.org/Order", "itemprop": "orderNumber"},

            "description": {"group": "General", "itemtype": "http://schema.org/Order", "itemprop": "description"},
            "date_due": {"group": "General", "itemtype": "http://schema.org/Order", "itemprop": "paymentDueDate"},
            "date_invoice": {"group": "General", "itemtype": "http://schema.org/Order", "itemprop": "dateCreated"},
            "reference": {"group": "General", "itemtype": "http://schema.org/Order", "itemprop": "confirmationNumber"},

            "create_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateCreated"},
            "write_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateModified"},

            "activity_summary": {"write": False},
            "picking_policy": {"required": False},
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
        # Init List of required Fields
        req_fields = self.collectRequiredFields()
        if req_fields is False:
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

    def delete(self, object_id):
        """Delete Odoo Object with Id"""
        try:
            model = self.load(object_id)
            if model is False:
                return True
            # ====================================================================#
            # Safety Check - Order Delete Allowed
            if model.state != 'cancel':
                if Framework.isDebugMode():
                    model.state = 'cancel'
                else:
                    Framework.log().warn(
                        'You can not delete a sent quotation or a confirmed sales order. You must first cancel it.'
                    )
                    return True
            model.unlink()
        except MissingError:
            return True
        except Exception as exception:
            return Framework.log().fromException(exception)

        return True