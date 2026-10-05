"""Single upright slice tiles (with specials) for the corp kits."""
import math
import numpy as np
from PIL import Image
import slicelib as SL
from slicelib import R_OUT, R_IN, render_slice
import roster_wheel as RW
import screens10 as S10

S10.select(virus="OOZE", proxy="TURN")

TIER_COLS = {  # round 16: (primary, secondary / threat) per corp
    "player": ((255, 205, 90), (255, 240, 200)),
    "meridian": ((255, 140, 26), (255, 46, 40)),
    "solace": ((150, 255, 70), (255, 70, 150)),
    "halcyon": ((176, 110, 255), (255, 170, 40)),
    "orbital": ((205, 240, 255), (255, 255, 255)),
    "rebel_cell": ((255, 40, 52), (255, 200, 210)),
}
KIT_TYPES = {  # (program, value, special) per corp: the slice types its roster actually uses
    "meridian": [("EXPLOIT", 14, None), ("ZERO-DAY", 24, None), ("FIREWALL", 12, None), ("SANDBOX", 8, None),
                 ("VIRUS", 3, "tariff"), ("NULL", None, None)],
    "solace": [("EXPLOIT", 14, None), ("ZERO-DAY", 24, None), ("FIREWALL", 12, None), ("PATCH", 4, None),
               ("VIRUS", None, "dose"), ("NULL", None, None)],
    "halcyon": [("EXPLOIT", 14, None), ("ZERO-DAY", 24, None), ("SANDBOX", 8, None), ("PATCH", 6, None),
                ("VIRUS", None, "citation"), ("NULL", None, None)],
    "orbital": [("EXPLOIT", 14, None), ("ZERO-DAY", 24, None), ("FIREWALL", 12, None), ("PROXY", 1, None),
                ("VIRUS", None, "solar_flare"), ("NULL", None, None)],
    "rebel_cell": [("EXPLOIT", 14, None), ("ZERO-DAY", 24, None), ("FIREWALL", 12, None), ("SANDBOX", 5, None),
                   ("VIRUS", None, "dose"), ("NULL", None, None)],
}


def tile(prog, value, special, theme, ss=2, scale=0.5, seed=1, tier="regular", boss=False, phase=1, motifs=True, t=0.4, scene_kind=None, corp_tier=None):
    span = 60
    pad = 8
    Ro = R_OUT * ss
    half = math.radians(span / 2)
    w = int(2 * Ro * math.sin(half) + 2 * pad * ss)
    h = int(Ro - R_IN * ss * math.cos(half) + 2 * pad * ss)
    canvas = np.zeros((h, w, 4), np.float32)
    opts = dict(upright=True, tier=tier, motifs=motifs, scene_kind=scene_kind)
    if corp_tier and theme in TIER_COLS:
        opts.update(corp_tier=corp_tier, tier_cols=TIER_COLS[theme])
    if boss:
        opts.update(boss=True, phase=phase)
    render_slice(canvas, w / 2, Ro + pad * ss, prog, -span / 2, span, value, t, theme, ss, opts, seed,
                 glyph=RW.SPECIAL_GLYPH.get(special), special=special)
    rgb, a = canvas[..., :3], canvas[..., 3:]
    st = np.where(a > 1e-4, rgb / np.maximum(a, 1e-4), 0)
    im = Image.fromarray((np.clip(np.concatenate([st, a], 2), 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
    return im.resize((int(w / ss * scale), int(h / ss * scale)), Image.LANCZOS)
