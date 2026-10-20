"""Write `content/config/street_r2.tres` (StreetR2ConfigData): the street-look parity rule numbers (P2-P4 step 1).

The numbers are the art-pass `street_r2/scripts/r2_config.py` (art-pass c8d2f67e), copied as they are, plus the few table constants
the ported modules carry (one-city frame, kit widths and colours, sign texture sizes). The Python port (`netrun_art/r2/`) and
the GDScript twin (`scripts/netrun_art/street_r2_*.gd`) both read the generated `.tres`, so there is one copy of every number.
Run from `tools/`:  `python -m netrun_art.gen_street_r2_config`."""
import os
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "content", "config", "street_r2.tres")

# ---- r2_config.RULES_R2, one block per rule (field name = rule name with the dot as an underscore)
RULES_R2 = {
    "frontage_silhouette": dict(
        frontage_min_floors=6, floors_low=(6, 8), floors_mid=(9, 13), floors_tall=(14, 21),
        rhythm_p=dict(low=0.34, mid=0.33, tall=0.33), height_step_min=2, triple_span_min=6, max_equal_tops=2, crown_share=0.34,
        crown_kinds=("setback", "spire", "roof_box", "sign_frame"), route_sign_floors=3, sightline_floors=7, sightline_pad=0.035,
        both_sides=True, roof_rim=True, band_gap_p=0.22, band_every=(3, 5), p_corner=0.45),
    "horizon_break": dict(
        spikes_min=3, spikes_max=5, spike_k=2.0, spike_spacing=1.0 / 6.0, spike_top=(0.04, 0.24), backdrop_band=(24.0, 170.0),
        spike_min_w=4.0, coast_amp=None),
    "materials_mix": dict(
        kits=("concrete_band", "glass_curtain", "panel_grille", "lit_atrium"), material_kinds=4, kit_radius=260.0,
        district_weights={"meridian": (0.30, 0.15, 0.40, 0.15), "halcyon": (0.20, 0.40, 0.15, 0.25), "": (0.35, 0.25, 0.25, 0.15)},
        roof_clutter_kinds=("ac", "tank", "vent_stack", "antenna", "dish"), roof_clutter_min_kinds=3),
    "repetition_guard": dict(
        max_same_module_adjacent=2, bay_mults=(0.55, 0.7, 0.85, 1.0, 1.25, 1.6, 2.1, 2.8), motif_len=(2, 4), bay_jitter=0.3,
        feature_bay_p=0.12, floor_mults=(0.8, 0.9, 1.0, 1.0, 1.15, 1.35), p_double=0.08, double_mult=1.9, ground_mult=(1.3, 1.7),
        top_mult=(0.75, 0.95), band_floors=(2, 4),
        window_tone_pool=((1.0, 0.68, 0.28), (1.0, 0.8, 0.5), (0.45, 0.9, 1.0), (0.9, 0.9, 1.0), (1.0, 0.42, 0.72)),
        window_tones=2, cell_tone=(0.8, 1.2), cell_relief=0.22, p_mixed_modules=0.8, p_setback=0.65, setback_min_floors=8,
        setback_from=(0.4, 0.75), setback_depth=(0.6, 1.4), p_balcony_floor=0.3, balcony_w=(1.5, 5.5), balcony_depth=(0.45, 0.7),
        rhythm_radius=90.0),
    "props_facade": dict(
        density=0.105, p_quiet=0.22, quiet_k=0.2, min_per_face=5, max_per_face=26,
        kinds={"ac": 0.12, "pipe": 0.07, "awning": 0.12, "small_sign": 0.55, "lit_room": 0.14},
        opening_margin=0.15, second_row_band=40.0, lamp_shift_max=2.4),
    "dressing_signs": dict(
        hero_kinds=("blade", "wall"), hero_lum_ratio=(1.5, 2.0), hero_central_frac=2.0 / 3.0, p_secondary=0.5, p_shop_sign=0.75,
        megastructures=1, mega_kinds=("globe", "arch", "holo"), signs_on_screen_min=6, legible_px=12.0, backdrop_sign_p=0.6,
        p_roof_board=0.16, mega_headroom=0.03, sign_off=0.12, hero_emit=4.0, sec_emit=2.6, shop_emit=1.5, mega_emit=3.0,
        backdrop_emit=2.4),
    "lod_signs": dict(t1_shape=466.0, t2_full=216.0, t3_detail=70.0, fade_margin=0.15),
    "streets_light": dict(
        lamp_step=6.0, lamp_jit=0.6, lamp_post_h=4.6, lamp_arm=1.1, kerb_off=3.3, p_shopfront=0.55, shopfront_frontage=1.0,
        lanes=4, lane_period=80.0, section_spill=14.0, facade_wash=2400.0),
    "foreground_street": dict(
        fg_band=0.20, zcut_street=0.15, fill_albedo=0.045, fg_lanes=(-6.5, -9.5, -13.0, -17.5), edge_silhouettes=0),
    "atmosphere_layers": dict(
        sky_max_share=0.25, beam_fog_min=0.6, planes=3, plane_step=0.03, back_haze=0.0040, back_haze_band=(30.0, 120.0),
        back_haze_top=2.4, sky_haze=0.0014, plumes=4, plume_h=(7.0, 15.0), plume_r=(1.4, 2.4), plume_k=0.09),
    "palette_districts": dict(
        district_hue_min=0.04, hue_cluster_max=0.45,
        hues={"meridian": (1.0, 0.549, 0.102), "halcyon": (0.549, 0.482, 1.0), "solace": (0.239, 1.0, 0.545),
              "orbital": (0.498, 0.659, 1.0), "rebel_cell": (0.91, 0.078, 0.118), "": (0.16, 0.8, 1.0)},
        sign_pal={
            "meridian": [(1.0, 0.55, 0.10), (1.0, 0.78, 0.25), (1.0, 0.22, 0.20), (0.16, 0.80, 1.0), (1.0, 0.16, 0.6)],
            "halcyon": [(0.62, 0.45, 1.0), (1.0, 0.16, 0.6), (0.16, 0.80, 1.0), (0.85, 0.85, 1.0), (0.25, 1.0, 0.75)],
            "": [(1.0, 0.16, 0.6), (0.16, 0.80, 1.0), (0.20, 1.0, 0.70), (1.0, 0.85, 0.20), (1.0, 0.40, 0.18)]},
        scatter=(0.88, 0.86, 0.90)),
}
SEEDS = {"s1": 1, "s2": 2}
WORDS = {
    "meridian": ["MERIDIAN", "FREIGHT", "DOCK 9", "CARGO", "CRANE", "SODIUM", "RAMEN", "PAWN", "BAR", "REPAIR"],
    "halcyon": ["HALCYON", "CLINIC", "PHARMA", "CLEAN AIR", "HOTEL", "SLEEP", "KARAOKE", "TEA", "DATA", "ORBITAL"],
    "": ["NOODLE", "OPEN 24", "CAPSULES", "VOLTA", "SOLACE", "ARCADE", "SUSHI", "PAWN", "BAR", "DATA"],
}
SUBS = ["24 H", "OPEN", "NO CREDIT", "LIVE", "B1", "2F", "ALL NIGHT", "FAST", "DOSE+", "NEW"]
# ad plate names of the storyboard's ad library (dressing only): hero wall posters, crown / roof boards, the megastructure
ADS = {"hero": {"meridian": ["meridian", "noodle", "volta"], "halcyon": ["halcyon", "orbital", "solace"], "": ["volta", "noodle", "solace"]},
       "board": ["volta", "noodle", "solace", "orbital", "halcyon", "meridian"],
       "mega": ["volta", "orbital", "halcyon", "solace", "meridian"]}
# the one-city frame (sb_onecity.RULES / layout36 constants): lot size, model centre, the height factor KH = U / kh[0] * kh[1]
ONECITY = dict(u=6.0, cx=6.0, cy=6.0, kh=(41.64, 1.15), floor_bu=1.9, front_band=(0.8, 6.5), min_width=2.5, extend=(12.0, 60.0),
               w=1920, h=1080, base_tol=0.05)
# r2_kits constants and the mainline window colours (target_corps.WIN_COLS) the kit falls back to
KITS = dict(kit_w={"glass_curtain": (1.4, 1.7, 2.2), "panel_grille": (1.6, 1.9, 2.4), "lit_atrium": (1.7, 2.0, 2.6)},
            glass_col=(0.22, 0.26, 0.34), metal_col=(0.20, 0.20, 0.24),
            win_cols=((1.0, 0.68, 0.28), (1.0, 0.68, 0.28), (1.0, 0.8, 0.5), (0.45, 0.9, 1.0), (1.0, 0.42, 0.72), (0.9, 0.9, 1.0)),
            red=(1.0, 0.15, 0.12))
# r2_signs constants: texture size by the long side (box / blade / holo, poster / shop), the fit-to-sign font search, the pale ink
SIGN_TEX = dict(long_px=768, long_px_big=1024, fit_lo=6, fit_hi=600, pale=(235, 230, 245), min_px=64)


def val(v: Any) -> str:
    """GDScript resource text of a JSON-like value (floats keep a decimal point; None is null)."""
    if v is None:
        return "null"
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


def fields() -> list:
    """`(name, value)` of every exported field of StreetR2ConfigData, in file order."""
    out = list(RULES_R2.items())
    out += [("seeds", SEEDS), ("words", WORDS), ("subs", SUBS), ("ads", ADS), ("onecity", ONECITY), ("kits", KITS), ("sign_tex", SIGN_TEX)]
    return out


def main() -> None:
    """Write content/config/street_r2.tres."""
    lines = ['[gd_resource type="Resource" script_class="StreetR2ConfigData" load_steps=2 format=3]', "",
             '[ext_resource type="Script" path="res://scripts/data/street_r2_config_data.gd" id="1_cfg"]', "", "[resource]",
             'script = ExtResource("1_cfg")']
    lines += [f"{k} = {val(v)}" for k, v in fields()]
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
