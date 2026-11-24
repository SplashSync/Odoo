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

"""Fields correspondence report: V1 manifest vs Gen 3 manifest, as JSON rows for review.

Usage: python3 tools/fields_report.py ThirdParty > report.json
Reads docs/plan/v1-legacy-manifest.json (V1) and splash.json (Gen 3, ``make manifest``).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
V1 = ROOT / "docs" / "plan" / "v1-legacy-manifest.json"
GEN3 = ROOT / "splash.json"


def fields(path: Path, object_type: str) -> dict[str, dict[str, Any]]:
    """Fields of an object type in a manifest, by id."""
    manifest = json.loads(path.read_text())
    return {field["id"]: field for field in manifest["objects"].get(object_type, {}).get("fields", [])}


def flags(field: dict[str, Any] | None) -> str:
    """Compact flags of a field: R(equired) W(rite) / RO, L(ist), P(rimary), NT (not tested)."""
    if not field:
        return ""
    parts = ["Req"] if field.get("required") == "1" else []
    parts.append("RW" if field.get("write") == "1" else "RO")
    parts += [name for key, name in (("inlist", "List"), ("primary", "Primary"), ("notest", "NoTest")) if field.get(key) == "1"]
    return " ".join(parts)


def microdata(field: dict[str, Any] | None) -> str:
    """Microdata of a field, short form."""
    if not field:
        return ""
    item_type = str(field.get("itemtype") or "").replace("https://", "").replace("http://", "").replace("schema.org/", "")
    return f"{item_type} / {field.get('itemprop') or ''}"


def kind(object_type: str, template: str, field: dict[str, Any] | None) -> str:
    """Kind of a Gen 3 field: from a template, generic Odoo field, or custom (explicit, no template)."""
    if template:
        return "template"
    if field and str(field.get("itemtype") or "").endswith(f"schema.org/{object_type}"):
        return "odoo"
    return "custom"


def rows(object_type: str) -> list[dict[str, Any]]:
    """Report rows: one per field id of V1 or Gen 3."""
    old, new = fields(V1, object_type), fields(GEN3, object_type)
    result = []
    for field_id in [*new, *[key for key in old if key not in new]]:
        before, after = old.get(field_id), new.get(field_id)
        template = str(((after or {}).get("options") or {}).get("tmpl") or "") if isinstance((after or {}).get("options"), dict) else ""
        if after is None:
            status = "removed"
        elif before is None:
            status = "new"
        elif microdata(before) != microdata(after) or before["type"] != after["type"]:
            status = "changed"
        else:
            status = "same"
        result.append(
            {
                "id": field_id,
                "status": status,
                "kind": kind(object_type, template, after),
                "template": template.replace("Splash.Templates.", ""),
                "group": (after or before or {}).get("group") or "",
                "name": (after or before or {}).get("name") or "",
                "v1_type": (before or {}).get("type", ""),
                "v3_type": (after or {}).get("type", ""),
                "v1_micro": microdata(before),
                "v3_micro": microdata(after),
                "v1_flags": flags(before),
                "v3_flags": flags(after),
            }
        )
    return result


if __name__ == "__main__":
    print(json.dumps(rows(sys.argv[1] if len(sys.argv) > 1 else "ThirdParty"), indent=1))
