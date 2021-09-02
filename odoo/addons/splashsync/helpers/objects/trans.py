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


class TransHelper:
    """Collection of Static Functions to manage Translations"""

    df_iso = None
    df_name = "English"

    model = None
    langs = None
    extra_langs = None
    extra_iso = None

    langs_domain = "res.lang"
    trans_domain = "ir.translation"

    # ====================================================================#
    # Products Translations Management
    # ====================================================================#

    @staticmethod
    def for_factory(translatable=False):
        """
        Get Languages For Fields Factory
        :param translatable: bool, dict
        :return: dict
        """
        if isinstance(translatable, bool) and translatable:
            return TransHelper.get_all()
        if isinstance(translatable, dict) and "translate" in translatable and translatable["translate"]:
            return TransHelper.get_all()
        return TransHelper.get_default()

    @staticmethod
    def get(model, field_name, iso_lang, default=""):
        """
        Get Translation for a Model Field
        :param model: model
        :param field_name: str
        :param iso_lang: str
        :return: str
        """
        try:
            translations = TransHelper.getModel()._get_ids(
                model.__class__.__name__ + "," + field_name,
                "model",
                iso_lang,
                [model.id]
            )
            if model.id in translations and isinstance(translations[model.id], str):
                return translations[model.id]
        except Exception as exception:
            from splashpy import Framework
            Framework.log().fromException(exception)
            return "Translation Error"
        return default

    @staticmethod
    def set(model, field_name, iso_lang, value):
        """
        Set Translation for a Model Field
        :param model: model
        :param field_name: str
        :param iso_lang: str
        :param value: str
        :return: void
        """
        try:
            TransHelper.getModel()._set_ids(
                model.__class__.__name__ + "," + field_name,
                "model",
                iso_lang,
                [model.id],
                value
            )
        except Exception as exception:
            from splashpy import Framework
            Framework.log().fromException(exception)

    # ====================================================================#
    # Languages Management
    # ====================================================================#

    @staticmethod
    def get_extra_iso():
        """
        Get List of Extra Installed Languages ISO Codes
        :return: list
        """
        return TransHelper.get_extra().keys()

    @staticmethod
    def get_extra():
        """
        Get List of Extra Installed Languages
        :return: dict
        """
        if TransHelper.extra_langs is None:
            TransHelper.extra_langs = {}
            for code, name in TransHelper.get_all().items():
                if code == TransHelper.get_default_iso():
                    continue
                TransHelper.extra_langs[code] = name
        return TransHelper.extra_langs

    @staticmethod
    def get_all():
        """
        Get List of All Installed Languages
        :return: dict
        """
        if TransHelper.langs is None:
            TransHelper.langs = dict(http.request.env[TransHelper.langs_domain].get_installed())
        return TransHelper.langs

    @staticmethod
    def get_default():
        """
        Get Default Language
        :return: dict
        """

        iso_code = TransHelper.get_default_iso()

        return {iso_code: iso_code}

    @staticmethod
    def get_default_iso():
        """
        Get Default Language Iso Code
        :return: string
        """
        if TransHelper.df_iso is None:
            try:
                import json
                TransHelper.df_iso = json.loads(http.request.env['ir.default'].search([('display_name', '=', 'lang')]).json_value)
            except Exception as exception:
                TransHelper.df_iso = "en_US"

        return TransHelper.df_iso

    # ====================================================================#
    # Odoo ORM Access
    # ====================================================================#

    @staticmethod
    def getModel():
        """Get Translations Model Class"""
        return http.request.env[TransHelper.trans_domain].sudo()
