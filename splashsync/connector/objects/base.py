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

"""Base of Odoo objects: CRUD on an Odoo model, values written in one ``write()`` per request.

Every write runs in a database savepoint: a refused write never aborts the Splash request.

Fields groups never write on the record: they stage Odoo values (``stage()``), then the object
creates the record with them (``create()``) or writes them once (``update()``).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import partial
from typing import Any, ClassVar, cast

from splashpy.core.context import RequestContext
from splashpy.fields import FieldsFactory
from splashpy.objects import BaseObject, FieldsGroup, ObjectRequest

from ..context import OdooContext

VALUES = "odoo_values"
"""Stash key of the Odoo values to write."""

TRANSLATIONS = "odoo_translations"
"""Stash key of the translations to write: {(model, id): {field: {lang: value}}}."""


class OdooGroup(FieldsGroup):
    """Base of Odoo fields groups: read the record, stage values to write."""

    def __init__(self, odoo: OdooContext | None = None) -> None:
        """Keep the Odoo context of the request (optional)."""
        self.odoo = odoo

    @classmethod
    def available(cls, odoo: OdooContext) -> bool:  # noqa: ARG003 - used by the overrides
        """Tell if this group is available in the Odoo database (modules, settings): default, always."""
        return True

    # ====================================================================#
    # Read
    # ====================================================================#

    @staticmethod
    def current(req: ObjectRequest, name: str) -> Any:
        """Get the current Odoo value: staged value first, then the record (None while creating)."""
        staged = req.stash.get(VALUES) or {}
        if name in staged:
            return staged[name]
        if req.object is None:
            return None
        return req.object[name]

    # ====================================================================#
    # Write
    # ====================================================================#

    @staticmethod
    def stage(req: ObjectRequest, name: str, value: Any) -> bool:
        """Stage an Odoo value when it differs from the current one."""
        staged = req.stash.get(VALUES) or {}
        if req.object is not None and name not in staged and _same(req.object[name], value):
            return True
        req.stash.setdefault(VALUES, {})[name] = value
        req.need_update()
        return True

    @staticmethod
    def stage_translation(req: ObjectRequest, record: Any, name: str, lang: str, value: Any) -> bool:
        """Stage a translation of a translatable field, written after the main values."""
        if record and record.with_context(lang=lang)[name] == (value or False):
            return True
        key = (record._name, record.id)
        req.stash.setdefault(TRANSLATIONS, {}).setdefault(key, {}).setdefault(name, {})[lang] = value or ""
        req.need_update()
        return True


class OdooObject(BaseObject):
    """Splash object on an Odoo model."""

    model: ClassVar[str] = ""
    """Odoo model name."""

    listed_fields: ClassVar[Sequence[str]] = ("name",)
    """Odoo fields returned in lists (same ids as the Splash fields)."""

    def __init__(self, odoo: OdooContext) -> None:
        """Use the Odoo context of the request; groups are built with it."""
        self.odoo = odoo
        # groups are built by splashpy without arguments: bind them to the request context
        vars(self)["groups"] = tuple(
            cast("type[FieldsGroup]", partial(cast("type[OdooGroup]", group), odoo))
            for group in type(self).groups
            if cast("type[OdooGroup]", group).available(odoo)
        )

    # ====================================================================#
    # Model & Filters
    # ====================================================================#

    def records(self) -> Any:
        """Odoo model, as the Splash user."""
        return self.odoo.model(self.model)

    def domain(self) -> list[Any]:
        """Get the records exposed to Splash (base filter of every operation)."""
        return []

    def search_domain(self, text: str) -> list[Any]:
        """Free text search of lists."""
        return [("display_name", "ilike", text)]

    def create_values(self, req: ObjectRequest) -> dict[str, Any]:
        """Default values of new records (staged values win)."""
        return {}

    def list_values(self, record: Any) -> dict[str, Any]:
        """Values of a record in lists (listed fields, by field id)."""
        return {name: _plain(record[name]) for name in self.listed_fields}

    # ====================================================================#
    # CRUD
    # ====================================================================#

    def load(self, req: ObjectRequest, object_id: str) -> Any:
        """Load a record, only when exposed to Splash."""
        if not str(object_id).isdigit():
            return None
        record = self.records().search([("id", "=", int(object_id)), *self.domain()], limit=1)
        return record or None

    def create(self, req: ObjectRequest) -> Any:  # pylint: disable=method-required-super
        """Create the record with the values staged in the create phase."""
        values = {**self.create_values(req), **(req.stash.pop(VALUES, None) or {})}
        req.set_updated()
        with self.odoo.env.cr.savepoint():
            return self.records().create(values)

    def object_id(self, req: ObjectRequest) -> str | None:
        """Record id."""
        return str(req.object.id) if req.object else None

    def update(self, req: ObjectRequest, needed: bool) -> str | None:
        """Write staged values once."""
        values = req.stash.pop(VALUES, None)
        translations = req.stash.pop(TRANSLATIONS, None) or {}
        if needed and (values or translations):
            with self.odoo.env.cr.savepoint():
                if values:
                    req.object.write(values)
                for (model, record_id), fields in translations.items():
                    record = self.odoo.env[model].browse(record_id)
                    for name, langs in fields.items():
                        write_translations(record, name, langs)
        return self.object_id(req)

    def delete(self, ctx: RequestContext, object_id: str) -> bool:
        """Delete a record (True also when already deleted)."""
        if not str(object_id).isdigit():
            return True
        record = self.records().search([("id", "=", int(object_id)), *self.domain()], limit=1)
        if not record:
            return True
        try:
            with self.odoo.env.cr.savepoint():
                self.delete_record(record)
        except Exception as error:  # noqa: BLE001 - any Odoo refusal (constraints, links...)
            ctx.logger.error(f"{self.object_type()}: unable to delete {object_id}: {error}")
            return False
        return True

    def delete_record(self, record: Any) -> None:
        """Delete an Odoo record."""
        record.unlink()

    def objects_list(self, ctx: RequestContext, filter: str | None, params: Mapping[str, Any]) -> dict[str, Any]:
        """List records with their listed fields, newest first."""
        domain = [*self.domain(), *(self.search_domain(filter) if filter else [])]
        limit, offset = self.list_params(params)
        model = self.records()
        records = model.search(domain, limit=limit, offset=offset, order="id desc")
        items = [{"id": str(record.id), **self.list_values(record)} for record in records]
        return self.list_result(items, model.search_count(domain))


def write_translations(record: Any, name: str, langs: Mapping[str, Any]) -> None:
    """Write translations of a field: whole value, or term by term for HTML fields (Odoo terms)."""
    field = record._fields[name]
    if not callable(field.translate):
        for lang, text in langs.items():
            record.with_context(lang=lang).write({name: text})
        return
    source = terms(field, record[name] or "")
    if len(source) != 1:
        # no single source term to translate (empty source...): write the value in its language
        for lang, text in langs.items():
            record.with_context(lang=lang).write({name: text})
        return
    translations = {lang: {source[0]: (terms(field, str(text or "")) or [""])[0]} for lang, text in langs.items()}
    record.update_field_translations(name, translations)


def terms(field: Any, value: str) -> list[str]:
    """Get the translatable terms of a value of a term translated field (HTML, XML)."""
    found: list[str] = []

    def collect(term: str) -> str:
        """Collect a term, unchanged."""
        found.append(term)
        return term

    field.translate(collect, value)
    return found


def build_fields(
    factory: FieldsFactory,
    templates: Mapping[str, str],
    group: str | None = None,
    flags: Mapping[str, Sequence[str | tuple[Any, ...]]] | None = None,
) -> None:
    """Declare fields from templates (field id => template code).

    :param flags: factory calls per field id: a method name, or a tuple (method name, *arguments),
        e.g. ``{"legal": ("is_required",), "website": (("add_option", "Url_Prefix", "http://"),)}``.
    """
    for field_id, template in templates.items():
        factory.create_from_template(field_id, template)
        if group:
            factory.group(group)
        for flag in (flags or {}).get(field_id, ()):
            method, *arguments = (flag,) if isinstance(flag, str) else flag
            getattr(factory, method)(*arguments)


def _same(current: Any, value: Any) -> bool:
    """Compare an Odoo value with a staged one (records by id, empty values as None)."""
    if hasattr(current, "_name") and hasattr(current, "ids"):
        current = current.id or None
    return (current or None) == (value or None) if not isinstance(value, bool) else bool(current) == value


def _plain(value: Any) -> Any:
    """Odoo value as a plain value (records by display name, False as None)."""
    if hasattr(value, "_name") and hasattr(value, "ids"):
        return value.display_name or None
    return None if value is False else value
