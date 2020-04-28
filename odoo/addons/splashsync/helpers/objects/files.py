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

from odoo import http
from splashpy.helpers import FilesHelper, ImagesHelper
from odoo.addons.splashsync.models.configuration import ResConfigSettings
from splashpy.core.framework import Framework


class OddoFilesHelper:

    @staticmethod
    def encode(domain, object_id, name, filename, field_id, base64_contents):
        """Encode Odoo Binary to Splash Field Data"""
        # ====================================================================#
        # Detect Images
        if ImagesHelper.is_image(base64_contents, True):
            # ====================================================================#
            # Encode as Splash Images
            return ImagesHelper.encodeFromRaw(
                base64_contents,
                name,
                filename + "." + str(ImagesHelper.get_extension(base64_contents, True)),
                OddoFilesHelper.encode_file_path(domain, object_id, field_id),
                OddoFilesHelper.get_image_url(domain, object_id, field_id),
                True
            )
        # ====================================================================#
        # Encode as Splash File
        return FilesHelper.encodeFromRaw(
            base64_contents,
            name,
            field_id,
            OddoFilesHelper.encode_file_path(domain, object_id, field_id),
            True
        )

    # ====================================================================#
    #  Object IMAGES Management
    # ====================================================================#

    @staticmethod
    def get_image_url(domain, object_id, field_id):
        """Get Public Image Preview Url"""
        url = ResConfigSettings.get_base_url()
        url += "/web/image?model=" + domain
        url += "&id=" + str(object_id) + "&field=" + str(field_id)

        return url

    # ====================================================================#
    #  Object FILES Management
    # ====================================================================#

    @staticmethod
    def encode_file_path(domain, object_id, field_id):
        """Build Virtual File Path for this Binary File"""
        return str(domain) + "::" + str(object_id) + "::" + str(field_id)

    @staticmethod
    def decode_file_path(path):
        """Decode Virtual File Path for this Binary File"""
        # Try to Explode Virtual Path
        try:
            domain, object_id, field_id = list(path.split('::'))
        except Exception:
            return None
        # Return Path Info
        return {
            "domain": str(domain),
            "id": int(object_id),
            "field": field_id
        }

    @staticmethod
    def getFile(path, md5):
        """
        Custom Reading of a File from Local System (Database or any else)
        """
        # ====================================================================#
        # Decode Path Info
        info = OddoFilesHelper.decode_file_path(path)
        if info is None:
            return None
        # ====================================================================#
        # Load Object by Id
        odoo_object = OddoFilesHelper.load(info["domain"], info["id"])
        if odoo_object is False:
            return None
        # ====================================================================#
        # Load Object Field Contents
        b64_data = getattr(odoo_object, info["field"])
        if b64_data is None:
            return None
        # ====================================================================#
        # Verify Md5
        if md5 != FilesHelper.md5(b64_data, True):
            return None
        # ====================================================================#
        # Encode Splash File
        field_id = info["field"]
        splashFile = OddoFilesHelper.encode(info["domain"], info["id"], field_id, field_id, field_id, b64_data)
        if splashFile is None or not isinstance(splashFile, dict):
            return None
        # Add Raw Contents to Splash File
        splashFile["raw"] = b64_data

        return splashFile

    # ====================================================================#
    # Odoo ORM Access
    # ====================================================================#

    @staticmethod
    def load(domain, object_id):
        """Load Odoo Object by Domain & Id"""
        model = http.request.env[domain].sudo().browse([int(object_id)])
        if len(model) != 1:
            return False
        return model

