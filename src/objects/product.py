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


class Product(OdooObject):
    # ====================================================================#
    # Splash Object Definition
    name = 'Product'
    desc = 'Odoo Partner Product'
    icon = 'fa fa-industry'

    @staticmethod
    def getDomain():
        return 'product.product'

    def get_listed_fields(self):
        """Get List of Object Fields to Include in Lists"""
        return ['name', 'lst_price', 'code']

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def create( self ):
        """Create a Faker Object """
        return False

    # ====================================================================#
    # Field Parsing Functions
    # ====================================================================#

    # def buildCoreFields( self ):
    #
    #     # Varchar
    #     FieldFactory.create(const.__SPL_T_VARCHAR__, "varchar", "Varchar 1")
    #     FieldFactory.isListed().isRequired()
    #     # Varchar 2
    #     FieldFactory.create(const.__SPL_T_VARCHAR__, "varchar2", "Varchar 2")
    #     # Bool
    #     FieldFactory.create(const.__SPL_T_BOOL__, "bool", "Bool")
    #     # Integer
    #     FieldFactory.create(const.__SPL_T_INT__, "integer", "Integer")
    #     # FieldFactory.isListed()
    #
    #     # Date
    #     FieldFactory.create(const.__SPL_T_DATE__, "date", "Date")
    #     # DateTime
    #     FieldFactory.create(const.__SPL_T_DATETIME__, "datetime", "Date Time")
    #
    # def getCoreFields( self, index, field_id):
    #
    #     if field_id in ['varchar', 'varchar2']:
    #         self.getSimpleStr(index, field_id)
    #
    #     if field_id in ['bool', 'integer']:
    #         self.getSimple(index, field_id)
    #
    #     if field_id in ['date']:
    #         self.getSimpleDate(index, field_id)
    #
    #     if field_id in ['datetime']:
    #         self.getSimpleDateTime(index, field_id)
    #
    # def setCoreFields( self, field_id, field_data ):
    #
    #     if field_id in ['varchar', 'varchar2', 'integer']:
    #         self.setSimple(field_id, field_data)
    #
    #     if field_id in ['bool']:
    #         self.setSimpleBool(field_id, field_data)
    #
    #     if field_id in ['date']:
    #         self.setSimpleDate(field_id, field_data)
    #
    #     if field_id in ['datetime']:
    #         self.setSimpleDateTime(field_id, field_data)