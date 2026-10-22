"""Route node stickers for the three run-graph v2 kinds (REST, WORKSHOP, CACHE): direction C "Slap-tag" (designer pick,
DIRECTION_REVIEW), drawn as vectors by `icons.py` / `vec.py` (Pillow only) and exported next to round 37's five stickers.

    python tools/art_pipeline/route_nodes/export_route_nodes.py

Output: assets/netrun/route/node_{rest,workshop,cache}.png (130 x 130, the family's canvas), their `_past` cut-off looks (the
family's greyscale 0.7), `node_cache_legend.png` (the 16.8 px legend glyph: fewer, fatter bricks), `manifest_nodes.json`, and the
SVG sources in tools/art_pipeline/route_nodes/svg/. Each icon is a white contour die-cut round a saturated glyph (no field); the
state ring is the overlay's. The kind colours are the street room glow colours (street_route.tres rooms.colors, Palette.ROUTE_*).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from PIL import Image  # noqa: E402

import icons  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "assets" / "netrun" / "route"
GREY_MIX = 0.7  # the concept's `past` look (round 37 node_sd grey=True): colour -> luminance by 0.7


def past(img: Image.Image) -> Image.Image:
    px = img.convert("RGBA")
    a = px.split()[3]
    lum = px.convert("L").convert("RGB")
    rgb = Image.blend(px.convert("RGB"), lum, GREY_MIX)
    rgb.putalpha(a)
    return rgb


def main() -> int:
    items = []
    (HERE / "svg").mkdir(exist_ok=True)
    for kind in icons.KINDS:
        doc = icons.make("C", kind)
        (HERE / "svg" / ("C_%s.svg" % kind)).write_text(doc.svg(), encoding="utf-8")
        img = doc.render(scale=1.0, ss=8)
        img.save(OUT / ("node_%s.png" % kind))
        past(img).save(OUT / ("node_%s_past.png" % kind))
        items.append({"file": "node_%s.png" % kind, "made_by": "icons.make('C', '%s').render(1.0)" % kind, "size": [130, 130]})
        items.append({"file": "node_%s_past.png" % kind, "made_by": "past(node_%s.png)" % kind, "size": [130, 130], "note": "cut-off look: greyscale 0.7"})
    small = icons.c_cache_small()
    (HERE / "svg" / "C_cache_small.svg").write_text(small.svg(), encoding="utf-8")
    small.render(scale=1.0, ss=8).save(OUT / "node_cache_legend.png")
    items.append({"file": "node_cache_legend.png", "made_by": "icons.c_cache_small().render(1.0)", "size": [130, 130],
                  "note": "the legend's 16.8 px glyph: the same stack, fewer and fatter bricks, wider mortar"})
    man = {"schema": "rebel_cell.art_export/1", "asset": "route_node_stickers_v2",
           "about": "REST / WORKSHOP / CACHE route node stickers, direction C (slap-tag). Built by tools/art_pipeline/route_nodes/export_route_nodes.py.",
           "source": {"concept": "docs/concepts/solace_vertical/nodes", "driver": "tools/art_pipeline/route_nodes/export_route_nodes.py"},
           "items": items}
    (OUT / "manifest_nodes.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
    print("wrote", len(items), "files to", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
