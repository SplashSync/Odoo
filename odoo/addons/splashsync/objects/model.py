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
from splashpy import Framework
from odoo import http
from odoo.exceptions import MissingError
from odoo.addons.splashsync.helpers.objects import BasicFields, BinaryFields, ListsHelper, ObjectConfigurator


class OdooObject(ListsHelper, BinaryFields, BaseObject, SimpleFields, BasicFields):

    configurator = None

    def __init__(self):
        self.model = None
        # ====================================================================#
        # Setup Configurator if Config Defined by Object
        object_type = self.getType()
        config = self.get_configuration()
        if isinstance(config, dict):
            self.configurator = ObjectConfigurator(object_type, config)

    # ====================================================================#
    # Functions that Parent Class MUST Implements
    # ====================================================================#

    @abstractmethod
    def getDomain(self):
        """Get Object Model Domain"""
        raise NotImplementedError("Not implemented yet.")

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        return None

    @staticmethod
    def get_composite_fields():
        """Get List of Fields NOT To Parse Automaticaly """
        return ["id"]

    # ====================================================================#
    # Odoo ORM Access
    # ====================================================================#

    def getModel(self):
        """Get Object Model Class"""
        if self.model is None:
            self.model = http.request.env[self.getDomain()]
            # self.model = http.request.env[self.getDomain()].sudo()

        return self.model

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def create(self):
        """Create a New Model Object """
        # ====================================================================#
        # Init List of required Fields
        reqFields = self.collectRequiredCoreFields()
        if reqFields is False:
            return False
        # ====================================================================#
        # Create new Model with Minimal Data
        return self.getModel().create(reqFields)

    def load(self, object_id):
        """Load Odoo Object by Id"""
        model = self.getModel().browse([int(object_id)])
        if len(model) != 1:
            return False

        return model

    def update(self, needed):
        """Update Current  Odoo Object"""
        if not needed:
            return self.getObjectIdentifier()
        try:
            self.object.flush()
        except Exception as exception:
            return Framework.log().fromException(exception)

        return self.getObjectIdentifier()

    def delete(self, object_id):
        """Delete Odoo Object with Id"""
        try:
            model = self.load(object_id)
            if model is False:
                return True
            model.unlink()
        except MissingError:
            return True
        except Exception as exception:
            return Framework.log().fromException(exception)

        return True

    def getObjectIdentifier(self):
        return self.object.id

    # ====================================================================#
    # OBJECT DEFINITION
    # ====================================================================#

    def fields(self):
        """Override Fields Definition if Configurator Defined"""
        fields = super(BaseObject, self).fields()
        if self.configurator is None:
            return fields

        return self.configurator.overrideFields(self.getType(), fields)

    # ====================================================================#
    # OBJECT DEBUG
    # ====================================================================#

    def dump(self, field_id):
        Framework.log().dump(getattr(self.object, field_id), field_id)
