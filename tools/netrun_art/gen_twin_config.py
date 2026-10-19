"""Write `content/config/netrun_art.tres` (NetrunArtConfigData) from the Python oracle constants, so the GDScript twins and
the Python modules read the same numbers. Run from `tools/`:  `python -m netrun_art.gen_twin_config`  (NA-21)."""
import os
from typing import Any

from netrun_art import layout, lod, occlusion, rig, section, units
from netrun_art.derive import street
from netrun_art.hq import orbit, slots

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "content", "config", "netrun_art.tres")

# PIPELINE_SPEC 5.2b, defaults derived from the 5.2 bands (open number N1): [tier, d_far, d_near] in BU.
REVEAL = {
    "street_sign": [[1, 790.0, 466.0], [2, 466.0, 216.0], [3, 216.0, 152.0]],
    "billboard": [[2, 466.0, 216.0], [3, 216.0, 152.0]],
    "hero_sign": [[2, 466.0, 216.0], [3, 216.0, 152.0]],
    "shopfront": [[2, 466.0, 216.0], [3, 276.0, 152.0]],
    "roof_clutter": [[1, 790.0, 328.0], [2, 276.0, 152.0]],
    "kerb_lamp": [[1, 276.0, 152.0], [2, 194.0, 115.0]],
    "traffic": [[2, 663.0, 307.0], [3, 194.0, 115.0]],
    "steam_plume": [[1, 663.0, 307.0]],
    "fog_detail": [[2, 1594.0, 466.0], [3, 790.0, 328.0]],
}


def val(v: Any) -> str:
    """GDScript resource text of a JSON-like value (floats keep a decimal point)."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        s = repr(v)
        return s if any(c in s for c in ".en") else s + ".0"
    if isinstance(v, str):
        return '"' + v + '"'
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(val(e) for e in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f'"{k}": {val(e)}' for k, e in v.items()) + "}"
    raise TypeError(type(v).__name__)


def main() -> None:
    hq_rig = {k: v for k, v in orbit.HQ_RIG.items() if k != "dmin"}
    hq_rig["dmin_kit"] = 135.0
    assert orbit.HQ_RIG["dmin"] == units.kit(135.0)
    occ = dict(occlusion.OCC, front_fade_kit=6.0, clutter_kit=25.0, ease_s=occlusion.EASE_S, min_span=occlusion.MIN_SPAN)
    assert occlusion.FRONT_FADE == units.kit(6.0) and occlusion.CLUTTER == units.kit(25.0)
    lod_d = dict(d0=lod.D0, d1=lod.D1, bands={k: list(v) for k, v in lod.DEFAULT_BANDS.items()}, floors=dict(lod.FLOORS),
                 ramps={k: list(v) for k, v in lod.RAMPS.items()}, ramp_levels=dict(lod.RAMP_LEVELS))
    sec = dict(zcut=dict(section.ZCUT), look_blend=list(section.LOOK_BLEND), no_cut=section.NO_CUT, poche=list(section.POCHE),
               edge_col=list(section.EDGE_COL), band_overview_kit=30.0, band_rooms_kit=24.0, zref_margin_kit=1.5, plinth_kit=0.6,
               widen=0.45)
    assert section.CONSTS["widen"] == 0.45
    srules = {k: v for k, v in street.RULES.items() if k not in ("floor_bu", "front_band", "extend")}
    lay = dict(front_band=list(layout.FRONT_BAND), extend=list(layout.EXTEND), base_tol=layout.BASE_TOL, axis_tol=layout.AXIS_TOL)
    fields = [
        ("units", dict(floor_bu=units.FLOOR_BU, kit_storey=units.KIT_STOREY, k_fit=units.K_FIT)),
        ("rig", rig.RIG), ("look_bias_sign", rig.LOOK_BIAS_SIGN), ("dive", rig.DIVE), ("hq_page", rig.HQ_PAGE),
        ("hq_rig", hq_rig), ("occlusion", occ), ("lod", lod_d), ("section", sec), ("street_rules", srules), ("layout", lay),
        ("slot_params", slots.SLOT_PARAMS), ("landmark_entries", slots.LANDMARK_ENTRIES), ("reveal", REVEAL),
        ("frustum_tolerance", 1.0e-4)]
    lines = ['[gd_resource type="Resource" script_class="NetrunArtConfigData" load_steps=2 format=3]', "",
             '[ext_resource type="Script" path="res://scripts/data/netrun_art_config_data.gd" id="1_cfg"]', "", "[resource]",
             'script = ExtResource("1_cfg")']
    lines += [f"{k} = {val(v)}" for k, v in fields]
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
