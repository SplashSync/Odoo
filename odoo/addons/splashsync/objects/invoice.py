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

# NOTES
#
# Since Oddo V13:
# - account.invoice deleted => Uses account.move instead

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
        from odoo.addons.splashsync.helpers import SystemManager
        if SystemManager.compare_version(13) >= 0:
            return 'account.move'
        return 'account.invoice'

    @staticmethod
    def objectsListFiltered():
        from odoo.addons.splashsync.helpers import SystemManager
        if SystemManager.compare_version(14) >= 0:
            return [('move_type', '=', "out_invoice")]
        """Filter on Search Query"""
        return [('type', '=', "out_invoice")]

    @staticmethod
    def get_listed_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['display_name', 'name', 'ref']

    @staticmethod
    def get_required_fields():
        """Get List of Object Fields to Include in Lists"""
        from odoo.addons.splashsync.helpers import SystemManager
        if SystemManager.compare_version(13) >= 0:
            return ['company_id', 'currency_id', 'journal_id', 'invoice_date']
        else:
            return ['company_id', 'currency_id', 'journal_id', 'date_invoice']

    @staticmethod
    def get_composite_fields():
        """Get List of Fields NOT To Parse Automatically """
        return [
            'id', 'state', 'activity_summary', 'date'
            'message_unread', 'message_unread_counter', 'move_name'
            'my_activity_date_deadline', 'amount_total_company_signed'
        ]

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        return {
            "name": {"group": "General", "write": True, "itemtype": "http://schema.org/Invoice", "itemprop": "name"},
            "ref": {"group": "General", "write": True, "itemtype": "http://schema.org/Invoice", "itemprop": "confirmationNumber"},
            "description": {"group": "General", "itemtype": "http://schema.org/Invoice", "itemprop": "description"},

            "date_due": {"group": "General", "write": False, "itemtype": "http://schema.org/Invoice", "itemprop": "paymentDueDate"},
            "create_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateCreated"},
            "__last_update": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateModified"},

            "date_invoice": {"group": "General", "itemtype": "http://schema.org/Order", "itemprop": "orderDate", "required": True, "write": True},
            "invoice_date": {"group": "General", "itemtype": "http://schema.org/Order", "itemprop": "orderDate", "required": True, "write": True},

            "payment_state":                    {"group": "General", "write": False},
            "payment_reference":                {"write": False},

            "access_token":                     {"write": False},
            "tax_totals_json":                  {"write": False},
            "user_id":                          {"write": False},
            "user_email":                       {"write": False},
            "invoice_sequence_number_next":     {"write": False},
            "sequence_number_next":             {"write": False},
            "sequence_number_next_prefix":      {"write": False},
            "posted_before":                    {"write": False},
            "qr_code_method":                   {"write": False},
            "show_name_warning":                {"write": False},

            "amount_residual":                  {"group": "Totals", "write": False},
            "amount_residual_signed":           {"group": "Totals", "write": False},
            "amount_tax":                       {"group": "Totals", "write": False},
            "amount_tax_signed":                {"group": "Totals", "write": False},
            "amount_total":                     {"group": "Totals", "write": False},
            "amount_total_in_currency_signed":  {"group": "Totals", "write": False},
            "amount_total_signed":              {"group": "Totals", "write": False},
            "amount_untaxed":                   {"group": "Totals", "write": False},
            "amount_untaxed_signed":            {"group": "Totals", "write": False},
            "amount_total_company_signed":      {"group": "Totals", "write": False},
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
        # DEBUG ONLY: Add Fake Line for Payments Test
        self.add_fake_line_for_payment_testing()
        # ====================================================================#
        # Order Fields Inputs
        self.order_inputs()
        Framework.log().dump(self._in)
        # ====================================================================#
        # Force Move type on Versions Above V14
        from odoo.addons.splashsync.helpers import SystemManager
        if SystemManager.compare_version(14) >= 0:
            self._in['move_type'] = "out_invoice"
            self._in['date'] = self._in['invoice_date']
        elif SystemManager.compare_version(13) >= 0:
            self._in['type'] = "out_invoice"
            self._in['date'] = self._in['invoice_date']
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

        self.object.move_type = "out_invoice"

        return super(Invoice, self).update(needed)

    def delete(self, object_id):
        """
        Delete Odoo Object with ID
        """
        try:
            invoice = self.load(object_id)
            if invoice is False:
                return True

            # ====================================================================#
            # Debug Mode => Force Order Delete
            if Framework.isDebugMode():
                self.get_helper().set_status(invoice, 'draft')
                if "move_name" in dir(invoice):
                    invoice.move_name = False
            invoice.ensure_one().unlink()
        except MissingError:
            return True
        except Exception as exception:
            return Framework.log().fromException(exception, True)

        return True

    def add_fake_line_for_payment_testing(self):
        """
        When Running Payment Tests, we add a fake Invoice Line
        in order to validate Invoice and Register Payments
        """
        # ====================================================================#
        # Only in Debug Mode
        if not Framework.isDebugMode() or not Framework.isServerMode():
            return
        # ====================================================================#
        # Only if NO Line but Payments
        if "lines" in self._in.keys() or "payments" not in self._in.keys():
            return

        self._in["lines"] = {
            "fake-item": {
                "name":     "This is a Fake Line",
                "quantity": 10,
                "price_unit": {"ht": 1000.0, "ttc": 1000.0, "vat": 0.0, "tax": 0.0}
            }
        }
