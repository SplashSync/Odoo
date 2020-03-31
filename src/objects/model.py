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

from abc import abstractmethod
from splashpy.models.object import BaseObject
from splashpy.models.objects.parser import SimpleFields
from splashpy.core.framework import Framework

from odoo import http

from odoo.addons.splashsync.helpers.objects.basic import BasicFields
from odoo.addons.splashsync.helpers.objects.lists import ListsHelper


class OdooObject(BasicFields, ListsHelper, BaseObject, SimpleFields):

    def __init__(self):
        self.model = None

        pass

    # ====================================================================#
    # Functions that Parent Class MUST Implements
    # ====================================================================#

    @abstractmethod
    def getDomain(self):
        """Get Object Model Domain"""
        raise NotImplementedError("Not implemented yet.")

    # ====================================================================#
    # Odoo ORM Access
    # ====================================================================#

    def getModel(self):
        """Get Object Model Class"""
        if self.model is None:
            # self.model = http.request.env[self.getDomain()]
            self.model = http.request.env[self.getDomain()].sudo()

        return self.model

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def load( self, object_id ):
        """Load Odoo Object by Id"""
        # self.getModel().invalidate_cache([int(object_id)])
        # model = self.getModel().browse([object_id]).sudo()
        model = self.getModel().browse([int(object_id)])
        if len(model) != 1:
            return False

        return model

    def update( self, needed ):
        """Update Current  Odoo Object"""
        if not needed:
            return self.getObjectIdentifier()
        try:
            self.object.flush()
        except Exception as exception:
            return Framework.log().error(exception)

        return self.getObjectIdentifier()

    def delete( self, object_id ):
        """Delete Odoo Object with Id"""
        try:
            model = self.load(object_id)
            model.unlink()
        except Exception as exception:
            return Framework.log().error(exception)

        return True

    def getObjectIdentifier(self):
        return self.object.id


