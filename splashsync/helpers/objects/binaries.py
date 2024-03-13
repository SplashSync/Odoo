# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) 2015-2019 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

from splashpy import const
from splashpy.componants import FieldFactory, Files
from splashpy.helpers import FilesHelper, ImagesHelper
from splashpy import Framework


class BinaryFields():

    __BinaryTypes__ = {
        "binary": const.__SPL_T_IMG__,
    }

    __BinaryFields__ = None

    def get_binary_fields_list(self):
        """Build & Store List of Binary Fields Definitions"""
        # List already in cache
        if self.__BinaryFields__ is not None:
            return self.__BinaryFields__
        # Init List Cache
        self.__BinaryFields__ = {}
        # Walk on Model Fields Definitions
        for fieldId in self.getModel().fields_get():
            # Get Fields Definitions
            field = self.getModel().fields_get([fieldId])
            # Filter Not Allowed Field
            if fieldId in self.get_composite_fields():
                continue
            # Filter on Binary Fields Types
            if field[fieldId]["type"] not in self.__BinaryTypes__.keys():
                continue
            # Add Definition to Cache
            self.__BinaryFields__[fieldId] = field[fieldId]

        return self.__BinaryFields__

    def buildBinaryFields(self):
        # Walk on Model Binary Fields Definitions
        for fieldId, field in self.get_binary_fields_list().items():
            # Build Splash Field Definition
            FieldFactory.create(self.__BinaryTypes__[field["type"]], fieldId, field["string"])
            FieldFactory.group("Others")
            FieldFactory.isReadOnly()
            if field["required"] or fieldId in self.get_required_fields():
                FieldFactory.isRequired()
            if field["readonly"]:
                FieldFactory.isReadOnly()
            if 'help' in field:
                FieldFactory.description(field["help"])

    def getBinaryFields(self, index, field_id):
        # Load Binary Fields Definitions
        fields_def = self.get_binary_fields_list()
        # Check if this field is Binary...
        if field_id not in fields_def.keys():
            return
        # ====================================================================#
        # Fetch Field Definition
        field = self.__BinaryFields__[field_id]
        # ====================================================================#
        # Fetch Binary raw Contents
        base64_contents = getattr(self.object, field_id)
        if not isinstance(base64_contents, bytes):
            self._out[field_id] = None
        else:
            from odoo.addons.splashsync.helpers import OddoFilesHelper
            self._out[field_id] = OddoFilesHelper.encode(
                self.getDomain(),
                self.object.id,
                field["string"],
                field_id,
                field_id,
                getattr(self.object, field_id)
            )

        self._in.__delitem__(index)

    def setBinaryFields( self, field_id, field_data ):
        # Load Binary Fields Definitions
        fields_def = self.get_binary_fields_list()
        # Check if this field is Binary...
        if field_id not in fields_def.keys():
            return

        self.set_binary_data(field_id, field_data, self.object)

    def set_binary_data(self, field_id, field_data, target):
        # ====================================================================#
        # Empty Value Received
        if not isinstance(field_data, dict) or field_data is None:
            self.setSimple(field_id, None, target)

            return
        # ====================================================================#
        # Compare Md5
        if field_data['md5'] == FilesHelper.md5(getattr(target, field_id), True):
            self._in.__delitem__(field_id)

            return
        # ====================================================================#
        # Read File from Server
        new_file = Files.getFile(
            field_data['file'] if not Framework.isDebugMode() else field_data['path'],
            field_data['md5']
        )
        if isinstance(new_file, dict) and "raw" in new_file:
            self.setSimple(field_id, new_file["raw"], target)
        else:
            Framework.log().error("Unable to read file from Server")

    def getFile(self, path, md5):
        """
        Custom Reading of a File from Local System (Database or any else)
        """
        from odoo.addons.splashsync.helpers import OddoFilesHelper
        return OddoFilesHelper.getFile(path, md5)



