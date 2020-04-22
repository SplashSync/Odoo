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
from .products import ProductsVariants, ProductsAttributes, ProductsPrices


class Product(OdooObject, ProductsAttributes, ProductsVariants, ProductsPrices):
    # ====================================================================#
    # Splash Object Definition
    name = "Product"
    desc = "Odoo Product"
    icon = "fa fa-product-hunt"

    template = None

    @staticmethod
    def getDomain():
        return 'product.product'

    @staticmethod
    def get_listed_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['code', 'name', 'qty_available', 'list_price']

    @staticmethod
    def get_required_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['name']

    @staticmethod
    def get_composite_fields():
        """Get List of Fields NOT To Parse Automaticaly """
        return [
            "id", "valuation", "image_small", "image_medium", "cost_method",
            "rating_last_image", "rating_last_feedback",
            "message_unread_counter",
            "price",
            "lst_price",
            "list_price",
            # "price", "lst_price", "list_price", 
            "standard_price"
        ]

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        return {
            "code": {"group": "General", "itemtype": "http://schema.org/Product", "itemprop": "model"},
            "name": {"group": "General", "itemtype": "http://schema.org/Product", "itemprop": "name"},
            "description": {"group": "General", "itemtype": "http://schema.org/Product", "itemprop": "description"},

            "active": {"group": "General", "itemtype": "http://schema.org/Product", "itemprop": "active", "notest": True},
            "sale_ok": {"group": "General", "itemtype": "http://schema.org/Product", "itemprop": "offered"},
            "purchase_ok": {"group": "General", "itemtype": "http://schema.org/Product", "itemprop": "ordered"},

            "qty_available": {"group": "General"},
            "qty_at_date": {"group": "General"},
            "virtual_available": {"group": "General"},
            "outgoing_qty	": {"group": "General"},
            "incoming_qty": {"group": "General"},

            "website": {"type": const.__SPL_T_URL__, "itemtype": "metadata", "itemprop": "metatype"},
            "activity_summary": {"write": False},
            "image": {"group": "General", "notest": True},

            "create_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateCreated"},
            "write_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateModified"},
        }

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def create(self):
        """Create a New Product with Variants Detection"""
        # ====================================================================#
        # Init List of required Fields
        reqFields = self.collectRequiredCoreFields()
        if reqFields is False:
            return False
        # ====================================================================#
        # Create a New Simple Product
        if not self.is_new_variable_product():
            return self.getModel().create(reqFields)
        # ====================================================================#
        # Detect Product Variant Template
        template_id = self.detect_variant_template()
        if template_id is not None:
            reqFields["product_tmpl_id"] = template_id

        return self.getModel().create(reqFields)

    def load(self, object_id):
        """Load Odoo Object by Id"""
        # ====================================================================#
        # Load Product Variant
        model = self.getModel().browse([int(object_id)])
        if len(model) != 1:
            return False
        # ====================================================================#
        # Load Product Template
        self.template = model[0].product_tmpl_id[0]

        return model

