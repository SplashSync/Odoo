#
#  This file is part of SplashSync Project.
#
#  Copyright (C) Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

"""Generic Odoo fields: every simple field of the model, field id = Odoo field name (as V1).

Fields owned by another group are skipped. Fields are sorted in functional groups (Sales,
Accounting, E-Invoicing...) from the Odoo module that defines them and their name. Fields
restricted by groups (``groups=``) are exposed only when the Splash user belongs to them, secrets
never. Computed fields without inverse are read-only.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar, Final

from odoo import fields as odoo_fields
from splashpy.fields import FieldsFactory, FieldType
from splashpy.objects import ObjectRequest, fields_group

from .base import OdooGroup

TYPES: Final = {
    "boolean": FieldType.BOOL,
    "char": FieldType.VARCHAR,
    "text": FieldType.TEXT,
    "html": FieldType.TEXT,
    "selection": FieldType.VARCHAR,
    "integer": FieldType.INT,
    "float": FieldType.DOUBLE,
    "monetary": FieldType.DOUBLE,
    "date": FieldType.DATE,
    "datetime": FieldType.DATETIME,
}
"""Odoo field types exposed, with their Splash type."""

EXCLUDED: Final = frozenset({"id", "create_uid", "write_uid"})
"""Technical fields never exposed."""

EINVOICING: Final = ("edi", "peppol", "pdp", "ubl", "routing")
"""Words of e-invoicing modules & fields (Peppol, French PDP, UBL / CII formats...)."""

GROUPS: Final = (
    ("account", "Accounting"),
    ("payment", "Accounting"),
    ("sale", "Sales"),
    ("product", "Sales"),
    ("crm", "Sales"),
    ("purchase", "Purchases"),
    ("stock", "Stock"),
    ("website", "Website"),
    ("mail", "Communication"),
    ("sms", "Communication"),
    ("phone", "Communication"),
    ("auth", "Communication"),
    ("base_address", "Address"),
    ("l10n", "Localization"),
)
"""Functional group of a field, by prefix of its Odoo module (first match); "General" otherwise."""

SECRETS: Final = ("token", "password", "secret")
"""Text fields never exposed when their name contains one of these words."""


@fields_group("odoo", priority=900)
class GenericFields(OdooGroup):
    """Every other simple field of the Odoo model (ids are the Odoo field names)."""

    owned_elsewhere: ClassVar[frozenset[str]] = frozenset()
    """Field ids declared by other groups of the object (set by each object)."""

    read_only: ClassVar[frozenset[str]] = frozenset({"name"})
    """Odoo fields only read: written through other fields (the name is encoded from the names)."""

    listed: ClassVar[Mapping[str, str]] = {}
    """Odoo fields shown in objects lists, with their group (set by each object)."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare generic fields; translatable texts once per language (``<name>_<lang>``, as V1)."""
        languages = self.odoo.languages() if self.odoo else ["en_US"]
        factory.set_default_language(languages[0])
        for name, field in self.exposed().items():
            for lang in languages if self.is_translated(field) else [None]:
                factory.create(TYPES[field.type], name, str(field.string or name))
                factory.group(self.listed.get(name) or group_label(name, field))
                factory.micro_data(f"http://schema.org/{req.object_type}", name)
                factory.description(str(field.help or field.string or name))
                if lang:
                    factory.set_multi_lang(lang)
                if name in self.read_only or self.is_read_only(field):
                    factory.is_read_only()
                else:
                    factory.is_not_tested()
                if field.type == "selection":
                    factory.add_choices(self.choices(field))
                if name in self.listed and not lang:
                    factory.is_listed()

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read a generic field (translations from the record owning the field)."""
        field_id, lang = self.split(req.object, field_id)
        field = req.object._fields[field_id]
        if lang:
            return self.owner(req.object, field_id).with_context(lang=lang)[field_id] or None
        value = req.object[field_id]
        if field.type == "boolean":
            return bool(value)
        if value is False or value is None:
            return None
        if field.type == "date":
            return odoo_fields.Date.to_string(value)
        if field.type == "datetime":
            return odoo_fields.Datetime.to_string(value)
        return value

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write a generic field (values are received as strings)."""
        field_id, lang = self.split(req.object, field_id)
        field = req.object._fields[field_id]
        if field_id in self.read_only or self.is_read_only(field):
            return True
        if lang:
            return self.stage_translation(req, self.owner(req.object, field_id), field_id, lang, value)
        return self.stage(req, field_id, _to_odoo(field.type, value))

    # ====================================================================#
    # Translations
    # ====================================================================#

    @staticmethod
    def is_translated(field: Any) -> bool:
        """Check if a field is translatable (texts only)."""
        return bool(field.translate) and field.type in ("char", "text", "html")

    def split(self, record: Any, field_id: str) -> tuple[str, str | None]:
        """Split a translation field id: (``name``, ``fr_FR``), or (field id, None)."""
        if field_id in record._fields:
            return field_id, None
        name, lang = field_id[:-6], field_id[-5:]
        return (
            (name, lang) if name in record._fields and len(field_id) > 6 and field_id[-6] == "_" else (field_id, None)
        )

    @staticmethod
    def owner(record: Any, name: str) -> Any:
        """Record owning a field: the parent record of inherited fields (product variant => template)."""
        for model, link in record._inherits.items():
            if name in record.env[model]._fields and record._fields[name].inherited:
                return record[link]
        return record

    # ====================================================================#
    # Discovery
    # ====================================================================#

    def exposed(self) -> dict[str, Any]:
        """Odoo fields exposed by this group."""
        if self.odoo is None:
            return {}
        model = self.odoo.model(self.model_name())
        user = self.odoo.env.user
        return {
            name: field
            for name, field in sorted(model._fields.items())
            if field.type in TYPES
            and name not in EXCLUDED
            and name not in self.owned_elsewhere
            and not name.startswith("_")
            and not (field.type in ("char", "text") and any(word in name for word in SECRETS))
            and (not field.groups or user.has_groups(field.groups))
        }

    def model_name(self) -> str:
        """Odoo model of the object (set by each object)."""
        raise NotImplementedError

    @staticmethod
    def is_read_only(field: Any) -> bool:
        """Read-only: readonly fields, computed fields without inverse, monetary amounts."""
        if field.type in ("monetary", "html") or field.readonly:
            return True
        return bool(field.compute) and not field.inverse

    def choices(self, field: Any) -> dict[str, str]:
        """Choices of a selection field."""
        if self.odoo is None:
            return {}
        try:
            selection = field._description_selection(self.odoo.env)
        except Exception:  # noqa: BLE001 - dynamic selections may need a record
            return {}
        return {str(key): str(label) for key, label in selection or []}


def group_label(name: str, field: Any) -> str:
    """Functional group of a generic field: e-invoicing first, then by Odoo module."""
    module = str(getattr(field, "_module", None) or "base")
    words = {*module.split("_"), *name.split("_")}
    if words.intersection(EINVOICING):
        return "E-Invoicing"
    return next((label for prefix, label in GROUPS if module.startswith(prefix)), "General")


def _to_odoo(field_type: str, value: Any) -> Any:
    """Convert a received value to an Odoo value."""
    if field_type == "boolean":
        return str(value) in ("1", "True", "true")
    if value is None or value == "":
        return False
    if field_type == "integer":
        return int(float(value))
    if field_type in ("float", "monetary"):
        return float(value)
    return value
