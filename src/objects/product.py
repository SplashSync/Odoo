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
from .products import ProductsVariants


class Product(OdooObject, ProductsVariants):
    # ====================================================================#
    # Splash Object Definition
    name = "Product"
    desc = "Odoo Product"
    icon = "fa fa-product-hunt"

    @staticmethod
    def getDomain():
        return 'product.product'

    @staticmethod
    def get_listed_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['code', 'name', 'qty_available']

    @staticmethod
    def get_required_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['name']

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        return {
            "code": {"itemtype": "http://schema.org/Product", "itemprop": "model"},

            "qty_at_date": {"group": "Inventory"},
            "qty_available": {"group": "Inventory"},
            "virtual_available": {"group": "Inventory"},
            "outgoing_qty	": {"group": "Inventory"},
            "incoming_qty": {"group": "Inventory"},

            "website": {"type": const.__SPL_T_URL__, "itemtype": "metadata", "itemprop": "metatype"},
            "activity_summary": {"write": False},
            "image": {"notest": True},
            "image_medium": {"write": False},
            "image_small": {"write": False},

            "valuation": {"write": False},

        }
