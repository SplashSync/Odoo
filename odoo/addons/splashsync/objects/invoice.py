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

from .model import OdooObject
from splashpy import Framework
from .invoices import InvoiceCore, InvoiceLines, InvoiceStatus, InvoicePayments
from .orders import OrderAddress
from odoo.exceptions import MissingError


class Invoice(OdooObject, InvoiceCore, InvoiceLines, OrderAddress, InvoiceStatus, InvoicePayments):
    # ====================================================================#
    # Splash Object Definition
    name = "Invoice"
    desc = "Odoo Invoice"
    icon = "fa fa-money"

    @staticmethod
    def getDomain():
        return 'account.invoice'

    @staticmethod
    def objectsListFiltered():
        """Filter on Search Query"""
        return [('type', '=', "out_invoice")]

    @staticmethod
    def get_listed_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['display_name', 'vendor_display_name', 'date_invoice', 'name', 'number']

    @staticmethod
    def get_required_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['company_id', 'currency_id', 'journal_id']

    @staticmethod
    def get_composite_fields():
        """Get List of Fields NOT To Parse Automatically """
        return [
            'id', 'state', 'activity_summary', 'date_invoice',
            'message_unread', 'message_unread_counter', 'move_name'
        ]

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        return {
            "name": {"group": "General", "write": True, "itemtype": "http://schema.org/Invoice", "itemprop": "confirmationNumber"},
            "description": {"group": "General", "itemtype": "http://schema.org/Invoice", "itemprop": "description"},

            "date_due": {"group": "General", "write": False, "itemtype": "http://schema.org/Invoice", "itemprop": "paymentDueDate"},
            "create_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateCreated"},
            "__last_update": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateModified"},

            "access_token": {"write": False},
            "sequence_number_next": {"write": False},
            "sequence_number_next_prefix": {"write": False},
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
        # Order Fields Inputs
        self.order_inputs()
        # ====================================================================#
        # Init List of required Fields
        req_fields = self.collectRequiredFields()
        if req_fields is False:
            return False
        # ==================================================================== #
        # Pre-Setup Default Team Id
        req_fields = self.setup_default_team(req_fields)
        # ====================================================================#
        # Create a New Simple Order
        new_invoice = self.getModel().create(req_fields)
        # ====================================================================#
        # Safety Check - Error
        if new_invoice is None:
            Framework.log().error("Invoice creation failed")
            return False

        return new_invoice

    def update(self, needed):
        """
        Update Current Odoo Object
        :param needed: bool
        :return: ThirdParty Object
        """
        # ====================================================================#
        # Post Update of Invoice Status
        if not self.post_set_status():
            return False

        return super(Invoice, self).update(needed)

    def delete(self, object_id):
        """Delete Odoo Object with Id"""
        try:
            invoice = self.load(object_id)
            if invoice is False:
                return True
            # ====================================================================#
            # Debug Mode => Force Order Delete
            if Framework.isDebugMode():
                if invoice.state not in ['draft', 'cancel']:
                    invoice.journal_id.update_posted = True
                    invoice.action_invoice_cancel()
                    invoice.action_invoice_draft()
                invoice.move_name = False
            invoice.unlink()
        except MissingError:
            return True
        except Exception as exception:
            return Framework.log().fromException(exception, False)

        return True
