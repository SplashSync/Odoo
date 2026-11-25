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

"""Product gallery, on the Odoo images only: main images and eCommerce extra images.

Splash sends and reads, for one variant, the complete gallery of the product with two flags per image:

- **visible**: hidden images belong to other variants, they are never put on this variant;
- **cover**: the main image of the product, whatever its position.

Odoo storage (nothing added in the database):

- main images: the template main image (``image_1920``) is the cover of the product; a variant with
  another cover gets its own main image (``image_variant_1920``);
- extra images (``product.image``, eCommerce module only): an image seen by every variant has no
  attribute values, an image seen by some variants only gets the attribute values of these
  variants, as the "variant images" of the Odoo screens. Without the eCommerce module, only the
  main images exist.

Odoo automatic main / extra images synchronisation is disabled while Splash writes, and the main
images Odoo resets when an extra image is removed are restored.
"""

from __future__ import annotations

import base64
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final

from splashpy.fields import FieldsFactory, Files, Images
from splashpy.objects import ObjectRequest, fields_group

from ..base import OdooGroup, build_fields
from .features import GALLERY_MODEL, has_gallery

LIST: Final = "Images"
"""Gallery list name (V1)."""

TEMPLATES: Final = {
    f"image@{LIST}": "Splash.Templates.Product.Gallery.Image",
    f"position@{LIST}": "Splash.Templates.Product.Gallery.Position",
    f"visible@{LIST}": "Splash.Templates.Product.Gallery.IsVisible",
    f"cover@{LIST}": "Splash.Templates.Product.Gallery.IsCover",
}
"""Fields: V1 field id => template code."""

FIELDS: Final = frozenset({LIST})
"""Lists of this group."""

SOURCES: Final = {
    GALLERY_MODEL: "image_1920",
    "product.template": "image_1920",
    "product.product": "image_variant_1920",
}
"""Odoo models & binary fields an image is read from (path given to Splash: ``<model>/<id>``)."""

QUIET: Final = {"skip_update_main_image": True, "from_extra_image": True}
"""Odoo context: no automatic main / extra images synchronisation."""


@dataclass(frozen=True)
class Entry:
    """One image of a variant gallery, as read by Splash."""

    record: Any
    """Odoo record holding the image."""

    visible: bool
    """Is the image shown on the variant?"""


# after the attributes when they exist (priority): the variant values are needed by its extra images
@fields_group("gallery", priority=40, after=("core",))
class ProductGallery(OdooGroup):
    """Images gallery: image, position, visible & cover flags (not tested here: Gallery Receiver scope)."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare gallery fields."""
        flags = dict.fromkeys(TEMPLATES, ("is_not_tested",))
        build_fields(factory, TEMPLATES, "Images", flags=flags)

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read one column of the variant gallery."""
        column = field_id.split("@", 1)[0]
        entries = read_gallery(req.object)
        main = binary_raw(req.object.with_context(bin_size=False).image_1920)
        cover = next((entry for entry in entries if main and raw_image(entry.record) == main), None)
        values: list[Any] = []
        for position, entry in enumerate(entries):
            if column == "image":
                values.append(encode(entry.record))
            elif column == "position":
                values.append(position)
            elif column == "visible":
                values.append(entry.visible)
            else:
                values.append(entry is cover)
        return values

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write the gallery of the variant: visible images, then the cover as main image."""
        variant = req.object.with_context(**QUIET)
        rows = sorted_rows(value)
        cover = write_extra_images(req, variant, rows) if has_gallery(variant.env) else None
        if cover is None:
            cover = find_cover(req, variant, rows)
        if cover is False:
            return False
        if isinstance(cover, bytes) and cover:
            set_cover(variant, cover)
        return True


# ====================================================================#
# Read
# ====================================================================#


def read_gallery(variant: Any) -> list[Entry]:
    """Complete gallery of the product, flagged for a variant: images of the other variants are hidden.

    The main image comes first when it is not one of the extra images.
    """
    entries: list[Entry] = []
    if has_gallery(variant.env):
        entries = [Entry(image, sees(variant, image)) for image in gallery(variant.product_tmpl_id)]
    main = binary_raw(variant.with_context(bin_size=False).image_1920)
    if main and all(raw_image(entry.record) != main for entry in entries):
        source = variant if variant.image_variant_1920 else variant.product_tmpl_id
        entries.insert(0, Entry(source, not any(entry.visible for entry in entries)))
    return entries


def gallery(template: Any) -> Any:
    """Extra images of a template, by position."""
    return template.product_template_image_ids.sorted(lambda image: (image.sequence, image.id))


def sees(variant: Any, image: Any) -> bool:
    """Tell if an extra image is shown on a variant (Odoo rule: a matching value per attribute of the image)."""
    values = image.attribute_value_ids
    if not values:
        return True
    own = variant.product_template_attribute_value_ids
    return all(own & values.filtered_domain([("attribute_line_id", "=", line.id)]) for line in values.attribute_line_id)


# ====================================================================#
# Write
# ====================================================================#


def sorted_rows(value: Any) -> list[Mapping[str, Any]]:
    """Received images, by position."""
    items = value.values() if isinstance(value, Mapping) else (value or [])
    rows = [row for row in items if isinstance(row, Mapping) and isinstance(row.get("image"), Mapping)]

    def position(row: Mapping[str, Any]) -> int:
        text = str(row.get("position", ""))
        return int(text) if text.lstrip("-").isdigit() else 0

    return sorted(rows, key=position)


def write_extra_images(req: ObjectRequest, variant: Any, rows: Sequence[Mapping[str, Any]]) -> bytes | bool | None:
    """Show the visible images on the variant, hide the others; get the cover contents if received.

    Return the cover contents, None when no cover was received, False when an image failed.
    """
    template = variant.product_tmpl_id
    variants = template.product_variant_ids
    existing = {Files.md5(raw_image(image)): image for image in gallery(template)}
    touched = template.env[GALLERY_MODEL]
    cover: bytes | bool | None = None
    mains = main_images(template)
    for sequence, row in enumerate(rows):
        checksum = str(row["image"].get("md5") or "")
        visible = truthy(row.get("visible", True))
        image = existing.get(checksum)
        if image is None and visible:
            raw = download(req, row["image"])
            if raw is None:
                return False
            image = create_image(template, variant, row["image"], raw)
            existing[checksum] = image
        if cover is None and truthy(row.get("cover")):
            cover = raw_image(image) if image else download(req, row["image"])
            if cover is None:
                return False
        if image is None:
            continue
        touched |= image
        if image.sequence != sequence:
            image.write({"sequence": sequence})
        show(image, variants, variant, visible)
    for image in gallery(template) - touched:
        show(image, variants, variant, False)
    restore_main_images(mains)
    variants.env.add_to_compute(variants._fields["variant_image_ids"], variants)
    return cover


def create_image(template: Any, variant: Any, value: Mapping[str, Any], raw: bytes) -> Any:
    """Add a received image to the gallery, for this variant only when the product has several."""
    values: dict[str, Any] = {
        "name": str(value.get("name") or value.get("filename") or Files.md5(raw)),
        "product_tmpl_id": template.id,
        "image_1920": binary_value(raw),
    }
    if len(template.product_variant_ids) > 1:
        values["attribute_value_ids"] = [(6, 0, variant.product_template_attribute_value_ids.ids)]
    return template.env[GALLERY_MODEL].with_context(**QUIET).create(values)


def show(image: Any, variants: Any, variant: Any, visible: bool) -> None:
    """Show or hide an extra image on a variant: removed when no variant shows it any more."""
    viewers = variants.filtered(lambda other: sees(other, image))
    viewers = viewers | variant if visible else viewers - variant
    if not viewers:
        image.unlink()
        return
    values = variants.browse() if viewers == variants else viewers.product_template_attribute_value_ids
    if image.attribute_value_ids != values:
        image.write({"attribute_value_ids": [(6, 0, values.ids)]})


def find_cover(req: ObjectRequest, variant: Any, rows: Sequence[Mapping[str, Any]]) -> bytes | bool | None:
    """Cover contents: the image flagged as cover, else the first visible one (as Odoo)."""
    flagged = [row for row in rows if truthy(row.get("cover"))]
    visible = [row for row in rows if truthy(row.get("visible", True))]
    if not flagged and not visible:
        return None
    row = (flagged or visible)[0]
    current = binary_raw(variant.with_context(bin_size=False).image_1920)
    if current and Files.md5(current) == str(row["image"].get("md5") or ""):
        return current
    raw = download(req, row["image"])
    return False if raw is None else raw


def set_cover(variant: Any, raw: bytes) -> None:
    """Write the main image from the cover: the template one (product cover), else the variant own one.

    A single variant product (or a template without main image) takes the cover as template main
    image. Another variant with a different cover gets its own main image. Written
    ``from_extra_image`` (Odoo would copy them in the gallery), never cleared (Odoo would remove
    the first extra image).
    """
    template = variant.product_tmpl_id.with_context(bin_size=False, **QUIET)
    variant = variant.with_context(bin_size=False, **QUIET)
    template_main = binary_raw(template.image_1920)
    own = binary_raw(variant.image_variant_1920)
    if not own and (len(template.product_variant_ids) <= 1 or not template_main):
        if template_main != raw:
            template.write({"image_1920": binary_value(raw)})
        return
    if own != raw and (own or raw != template_main):
        variant.write({"image_variant_1920": binary_value(raw)})


def main_images(template: Any) -> dict[Any, bytes]:
    """Get the main images of a template & its variants (Odoo resets them when extra images are removed)."""
    template = template.with_context(bin_size=False)
    mains = {template: binary_raw(template.image_1920)}
    for variant in template.product_variant_ids:
        mains[variant] = binary_raw(variant.image_variant_1920)
    return mains


def restore_main_images(mains: Mapping[Any, bytes]) -> None:
    """Put back main images Odoo changed while extra images were removed (never cleared: see above)."""
    for record, raw in mains.items():
        name = SOURCES[record._name]
        if raw and record.exists() and binary_raw(record.with_context(bin_size=False)[name]) != raw:
            record.with_context(**QUIET).write({name: binary_value(raw)})


def download(req: ObjectRequest, value: Mapping[str, Any]) -> bytes | None:
    """Download a received image from Splash, checked by md5."""
    checksum = str(value.get("md5") or "")
    received = req.ctx.get_file(str(value.get("path") or value.get("file") or ""), checksum)
    raw = Files.decode_raw(received.get("raw")) if received else None
    if raw is None or Files.md5(raw) != checksum:
        req.logger.error(f"Product: unable to download image {value.get('filename')} ({checksum}).")
        return None
    return raw


# ====================================================================#
# Images contents
# ====================================================================#


def raw_image(record: Any) -> bytes:
    """Raw contents of an image record (extra image, template or variant main image)."""
    if not record:
        return b""
    return binary_raw(record.with_context(bin_size=False)[SOURCES[record._name]])


def binary_raw(value: Any) -> bytes:
    """Raw bytes of an Odoo binary value (Odoo 20: ``BinaryValue``, before: base64 bytes)."""
    if not value:
        return b""
    if hasattr(value, "content"):
        return bytes(value.content)
    return base64.b64decode(value)


def binary_value(raw: bytes) -> Any:
    """Odoo binary value from raw bytes (Odoo 20: ``BinaryBytes``, before: base64 bytes)."""
    try:
        from odoo.tools import BinaryBytes  # noqa: PLC0415 - Odoo 20+
    except ImportError:  # pragma: no cover - Odoo <= 19
        return base64.b64encode(raw)
    return BinaryBytes(raw)


def encode(record: Any) -> dict[str, Any] | None:
    """Splash image value of an image record."""
    raw = raw_image(record)
    kind = Images.kind(raw) or "png"
    name = str(record.name or record.id) if record._name == GALLERY_MODEL else f"{record.display_name}"
    base_url = record.get_base_url()
    field = SOURCES[record._name]
    url = f"{base_url}/web/image/{record._name}/{record.id}/{field}" if base_url else None
    return Images.encode_image(name, f"{name}.{kind}", f"{record._name}/{record.id}", raw, url)


def read_file(env: Any, path: str, checksum: str) -> dict[str, Any] | None:
    """Read a gallery image for Splash (``ReadFile``), when its checksum matches."""
    model, _, record_id = path.rpartition("/")
    if model not in SOURCES or model not in env or not record_id.isdigit():
        return None
    record = env[model].browse(int(record_id)).exists()
    raw = raw_image(record) if record else b""
    if not raw or Files.md5(raw) != checksum:
        return None
    return Files.read(f"{record.id}.{Images.kind(raw) or 'png'}", raw)


def truthy(value: Any) -> bool:
    """Received boolean."""
    return str(value) in ("1", "True", "true")
