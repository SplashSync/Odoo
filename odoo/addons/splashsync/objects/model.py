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
from .core import SalesRelations


class OdooObject(ListsHelper, BinaryFields, BaseObject, SimpleFields, BasicFields, SalesRelations):

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
        """Get List of Fields NOT To Parse Automatically"""
        return ["id"]

    # ====================================================================#
    # Odoo ORM Access
    # ====================================================================#

    def getModel(self):
        """Get Object Model Class"""
        if self.model is None:
            from odoo.addons.splashsync.helpers import SystemManager
            self.model = SystemManager.getModel(self.getDomain())

        return self.model

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def create(self):
        """Create a New Model Object """
        # ====================================================================#
        # Order Fields Inputs
        self.order_inputs()
        # ====================================================================#
        # Init List of required Fields
        req_fields = self.collectRequiredCoreFields()
        if req_fields is False:
            return False
        # ==================================================================== #
        # Pre-Setup Default Team Id
        req_fields = self.setup_default_team(req_fields)
        # ====================================================================#
        # Create new Model with Minimal Data
        return self.getModel().create(req_fields)

    def load(self, object_id):
        """
        Load Odoo Object by Id

        :param object_id: str
        :rtype: odoo.BaseModel
        """
        # ====================================================================#
        # Order Fields Inputs
        self.order_inputs()
        # ====================================================================#
        # Load Requested Objects
        try:
            model = self.getModel().browse([int(object_id)])
            if len(model) != 1:
                return False
        except MissingError:
            return False

        return model

    def update(self, needed):
        """
        Update Current Odoo Object
            - This function is useless on Odoo as Data is saved upon changes
            - It's kept for compatibility & Overrides

        :return:    Objects Id of False if Error
        :rtype: int | False
        """
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

    def order_inputs(self):
        """Ensure Inputs are Correctly Ordered"""
        from collections import OrderedDict
        self._in = OrderedDict(sorted(self._in.items()))

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
