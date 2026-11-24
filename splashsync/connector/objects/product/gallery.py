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

"""Product gallery: the images of the template, with visible & cover flags per variant.

The gallery is the ordered list of the template images (``product.image``): positions are global,
the received list is complete (missing images are removed). Visible & cover flags apply to the
written variant only (``splash_hidden_variant_ids`` / ``splash_cover_variant_ids``); the cover is
also the variant main image. Odoo automatic main / extra images synchronisation is disabled
while Splash writes.
"""

from __future__ import annotations

import base64
from collections.abc import Mapping
from typing import Any, Final

from splashpy.fields import FieldsFactory, Files, Images
from splashpy.objects import ObjectRequest, fields_group

from ..base import OdooGroup, build_fields

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

PATH: Final = "product.image/"
"""Prefix of gallery images paths (``product.image/<id>``), given back by Splash to read them."""

QUIET: Final = {"skip_update_main_image": True, "from_extra_image": True}
"""Odoo context: no automatic main / extra images synchronisation."""


@fields_group("gallery", priority=40, after=("core", "attributes"))
class ProductGallery(OdooGroup):
    """Images gallery: image, position, visible & cover flags (not tested here: Gallery Receiver scope)."""

    def build(self, factory: FieldsFactory, req: ObjectRequest) -> None:
        """Declare gallery fields."""
        flags = dict.fromkeys(TEMPLATES, ("is_not_tested",))
        build_fields(factory, TEMPLATES, "Images", flags=flags)

    def get(self, req: ObjectRequest, field_id: str) -> Any:
        """Read one column of the gallery."""
        column = field_id.split("@", 1)[0]
        variant = req.object
        values: list[Any] = []
        for position, image in enumerate(gallery(variant.product_tmpl_id)):
            if column == "image":
                values.append(encode(image))
            elif column == "position":
                values.append(position)
            elif column == "visible":
                values.append(variant not in image.splash_hidden_variant_ids)
            else:
                values.append(variant in image.splash_cover_variant_ids)
        return values

    def set(self, req: ObjectRequest, field_id: str, value: Any) -> bool | None:
        """Write the complete gallery of the template, and the flags of the variant."""
        variant = req.object.with_context(**QUIET)
        template = variant.product_tmpl_id
        rows = [row for row in (value or []) if isinstance(row, Mapping) and isinstance(row.get("image"), Mapping)]
        rows.sort(
            key=lambda row: int(row.get("position") or 0) if str(row.get("position", "")).lstrip("-").isdigit() else 0
        )
        existing = {md5(image): image for image in gallery(template)}
        kept = template.env["product.image"]
        cover = None
        for sequence, row in enumerate(rows):
            image = existing.get(str(row["image"].get("md5"))) or self.download(req, template, row["image"])
            if image is None:
                return False
            image.write(self.flags(image, variant, row, sequence))
            kept |= image
            if truthy(row.get("cover")):
                cover = image
        (gallery(template) - kept).unlink()
        if cover is not None:
            (kept - cover).filtered(lambda image: variant in image.splash_cover_variant_ids).write(
                {"splash_cover_variant_ids": [(3, variant.id)]}
            )
        main = raw_image(cover) if cover is not None else b""
        if binary_raw(variant.with_context(bin_size=False).image_variant_1920) != main:
            variant.write({"image_variant_1920": binary_value(main) if main else False})
        return True

    @staticmethod
    def flags(image: Any, variant: Any, row: Mapping[str, Any], sequence: int) -> dict[str, Any]:
        """Image values: global position, visible & cover flags of the written variant."""
        values: dict[str, Any] = {"sequence": sequence}
        hidden = not truthy(row.get("visible", True))
        if hidden != (variant in image.splash_hidden_variant_ids):
            values["splash_hidden_variant_ids"] = [(4 if hidden else 3, variant.id)]
        cover = truthy(row.get("cover"))
        if cover != (variant in image.splash_cover_variant_ids):
            values["splash_cover_variant_ids"] = [(4 if cover else 3, variant.id)]
        return values

    @staticmethod
    def download(req: ObjectRequest, template: Any, value: Mapping[str, Any]) -> Any:
        """Download a received image from Splash (checked by md5) and add it to the gallery."""
        checksum = str(value.get("md5") or "")
        received = req.ctx.get_file(str(value.get("path") or value.get("file") or ""), checksum)
        raw = Files.decode_raw(received.get("raw")) if received else None
        if raw is None or Files.md5(raw) != checksum:
            req.logger.error(f"Product: unable to download image {value.get('filename')} ({checksum}).")
            return None
        return template.env["product.image"].create(
            {
                "name": str(value.get("name") or value.get("filename") or checksum),
                "product_tmpl_id": template.id,
                "image_1920": binary_value(raw),
            }
        )


def gallery(template: Any) -> Any:
    """Gallery images of a template, by position."""
    return template.product_template_image_ids.sorted(lambda image: (image.sequence, image.id))


def raw_image(image: Any) -> bytes:
    """Raw contents of a gallery image."""
    return binary_raw(image.with_context(bin_size=False).image_1920)


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


def md5(image: Any) -> str:
    """Checksum of a gallery image."""
    return Files.md5(raw_image(image))


def encode(image: Any) -> dict[str, Any] | None:
    """Splash image value of a gallery image."""
    raw = raw_image(image)
    kind = Images.kind(raw) or "png"
    base_url = image.get_base_url()
    url = f"{base_url}/web/image/product.image/{image.id}/image_1920" if base_url else None
    return Images.encode_image(
        str(image.name or image.id), f"{image.name or image.id}.{kind}", f"{PATH}{image.id}", raw, url
    )


def read_file(env: Any, path: str, checksum: str) -> dict[str, Any] | None:
    """Read a gallery image for Splash (``ReadFile``), when its checksum matches."""
    image_id = path.removeprefix(PATH)
    if not path.startswith(PATH) or not image_id.isdigit():
        return None
    image = env["product.image"].browse(int(image_id)).exists()
    raw = raw_image(image) if image else b""
    if not raw or Files.md5(raw) != checksum:
        return None
    return Files.read(f"{image.name or image.id}.{Images.kind(raw) or 'png'}", raw)


def truthy(value: Any) -> bool:
    """Received boolean."""
    return str(value) in ("1", "True", "true")
