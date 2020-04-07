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

class ThirdParty(OdooObject):
    # ====================================================================#
    # Splash Object Definition
    name = "ThirdParty"
    desc = "Odoo Partner"
    icon = "fa fa-user"

    @staticmethod
    def getDomain():
        return 'res.partner'

    @staticmethod
    def get_listed_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['ref', 'name', 'email']

    @staticmethod
    def get_required_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['name']

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        return {
            "website": {"type": const.__SPL_T_URL__, "itemtype": "metadata", "itemprop": "metatype"},
            "activity_summary": {"write": False},
            "image": {"notest": True},
            "image_medium": {"write": False},
            "image_small": {"write": False},
        }
