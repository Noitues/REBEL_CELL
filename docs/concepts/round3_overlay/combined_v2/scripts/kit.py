"""Combined overlay kit v2: vinyl stickers for ALL words and objects, grease pencil for plans,
light spill in the base. Spray is gone.

Layer order, bottom to top:
  base  ->  light spill (D)  ->  grease pencil + glass (A)  ->  vinyl stickers (C: objects, then words)

A (grease pencil) and B (only its font helper `marks.bahn` and `spraylib.fbm` noise) are imported in
place from their concept folders. The sticker library is a local copy (sticker_lib.py / pieces.py)
with thicker, crisper die-cut borders. The sticker palette is remapped to the kit colours at import.
"""
import importlib.util
import sys as _sys
_sys.dont_write_bytecode = True  # never leave caches in the other concept folders
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.abspath(os.path.join(HERE, "..", ".."))           # docs/concepts/round3_overlay
OUT = os.path.abspath(os.path.join(HERE, ".."))                # .../combined_v2
DOCS = os.path.abspath(os.path.join(R3, "..", ".."))           # docs/
BASE_COMBAT = os.path.join(DOCS, "concepts/round2/r2c_geo_vector_gritty/stills/04_combat.png")
BASE_CITY = os.path.join(DOCS, "concepts/round2/r2c_geo_vector_gritty/stills/02_city_night.png")
BASE_SHOP = os.path.join(DOCS, "concepts/round2/r2c_v2_modem/modem_shop.png")
BASE_SHOP_SIGN = os.path.join(DOCS, "concepts/round4_modem_sign/shop_with_sign.png")
W, H = 1920, 1080

for sub in ("o_b_stencil_spray/scripts", "o_a_tactical_glass/scripts"):
    p = os.path.join(R3, sub)
    if p not in sys.path:
        sys.path.append(p)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# --- B: only the font helper and noise (no spray is drawn)
import spraylib as SP          # noqa: E402
import marks as MK             # noqa: E402
# --- A: grease pencil on glass
import tg_lib as T             # noqa: E402
# --- C: vinyl stickers (local v2 copy)
import sticker_lib as SL       # noqa: E402
import pieces as PC            # noqa: E402
assert os.path.dirname(os.path.abspath(SL.__file__)) == HERE, SL.__file__


def _load_by_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- D: light pen (only the blur / tonemap / light model is used)
LP = _load_by_path("lightpen_d", os.path.join(R3, "o_d_light_pen/scripts/lightpen.py"))

# ------------------------------------------------------------------ kit palette
# One palette across all four materials. Nothing outside it.
K_PINK = (255, 36, 136)       # B spray face: the Cell's verbs
K_WHITE = (244, 242, 234)     # spray offset key, vinyl
K_BLACK = (10, 9, 12)         # stencil shadow, sticker ink
K_YELLOW = (255, 219, 41)     # grease pencil: plans and route (A yellow)
K_RED = (247, 33, 31)         # grease pencil: threats and targets (A red)
K_KRAFT = SL.KRAFT
PAL_F = {k: tuple(c / 255 for c in v) for k, v in
         dict(pink=K_PINK, white=K_WHITE, black=K_BLACK, yellow=K_YELLOW, red=K_RED).items()}

# remap the sticker library onto the kit palette (coral -> kit red, teal -> kit pink, yellow -> kit yellow)
_remap = dict(YELLOW=K_YELLOW, YELLOW_LO=(232, 176, 22), CORAL=K_RED, CORAL_LO=(196, 22, 26), TEAL=K_PINK,
              PEN_Y=K_YELLOW)
for mod in (SL, PC):
    for k, v in _remap.items():
        setattr(mod, k, v)


# ------------------------------------------------------------------ conversions
def f2pil(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")


def pil2f(im):
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


# ------------------------------------------------------------------ D: light spill (base layer)
def light_spill(base, region_masks, gain=1.0, threshold=0.55):
    """Glowing base elements throw coloured light on nearby facets.

    Emitters = bright, saturated base pixels inside the given emitter regions (neon signs,
    the MODEM sign, spinner rims). Uses D's projected-light model: the blurred emitter colour
    multiplies the base (lights the facets) plus a little fill, then D's tonemap.
    """
    mx = base.max(-1)
    mn = base.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-4)
    emit = np.clip((mx - threshold) / 0.30, 0, 1) * np.clip((sat - 0.20) / 0.30, 0, 1)
    region = np.zeros(mx.shape, np.float32)
    for m in region_masks:
        region = np.maximum(region, m)
    emit = emit * region
    col = base * emit[..., None]
    light = np.zeros_like(base)
    for c in range(3):
        light[..., c] = LP.gblur(col[..., c], 26) * 1.2 + LP.gblur(col[..., c], 80) * 1.5
    # emitters themselves are not re-lit (no blown-out signs), the facets around them are
    keep = 1 - np.clip(emit * 1.5, 0, 1)
    delta = (base * light * 1.9 + light * 0.28) * gain * keep[..., None]
    # D's tonemap shoulder, applied to the added light only so the base itself is not re-graded
    return np.clip(base + LP.tonemap(delta) * (1 - base), 0, 1)


def ring_mask(cx, cy, r0, r1, feather=6):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot(xx - cx, yy - cy)
    return np.clip((r - r0) / feather, 0, 1) * np.clip((r1 - r) / feather, 0, 1)


def box_mask(x0, y0, x1, y1, feather=8):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    return (np.clip((xx - x0) / feather, 0, 1) * np.clip((x1 - xx) / feather, 0, 1) *
            np.clip((yy - y0) / feather, 0, 1) * np.clip((y1 - yy) / feather, 0, 1))


# ------------------------------------------------------------------ A: glass (a touch more visible than A)
def glass(img, rng, smudges, band_pos=0.30, band_gain=1.7, corner="tr"):
    """A's acrylic pass, with a stronger sheen band and visible smudges."""
    out = T.acrylic(img, rng, smudges, corner, band_pos)
    h, w, _ = out.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = (xx / w * 0.72 + yy / h * 0.28)
    band = T.smoothstep(band_pos - 0.16, band_pos, t) * (1 - T.smoothstep(band_pos, band_pos + 0.035, t))
    band *= 0.055 * (band_gain - 1) * (0.55 + 0.45 * (1 - yy / h))
    out = out + band[..., None] * np.array([0.85, 0.92, 1.0], np.float32)
    return np.clip(out, 0, 1)


def pencil_composite(base_f, layer):
    """A's composite: darken under the wax a little, 4/6 px cast shadow onto the screen."""
    return T.composite(base_f, layer, darken=0.26, shadow=0.42)


# ------------------------------------------------------------------ C: sticker objects in kit form
def note_card(text, w=262, h=134, seed=9, curl=None, cap=19, width=4.6):
    """Kraft note card (C) whose text is grease pencil (A), written before it was stuck down."""
    S = SL.SS
    P = 40
    Wc, Hc = (w + 2 * P) * S, (h + 2 * P) * S
    body = Image.new("L", (Wc, Hc), 0)
    ImageDraw.Draw(body).rounded_rectangle([P * S, P * S, Wc - P * S, Hc - P * S], radius=16 * S, fill=255)
    hole = 8 * S
    ImageDraw.Draw(body).ellipse([(P + 18) * S - hole, (P + 20) * S - hole, (P + 18) * S + hole, (P + 20) * S + hole], fill=0)
    rng = np.random.default_rng(seed)
    L = T.Layer(rng, 0, 0, w + 2 * P, h + 2 * P)
    st = T.letter_strokes(text, P + w / 2 + 6, P + h / 2 + 8, cap, width, PAL_F["black"], rng,
                          angle=-0.03, align="left", line_gap=1.5, slant=0.14)
    L.strokes(st)
    L.light(spec_gain=0.7)
    a = np.clip(L.a, 0, 1)
    rgb = np.where(a[..., None] > 1e-4, L.rgb / np.maximum(a[..., None], 1e-4), 0)
    art = Image.fromarray((np.dstack([np.clip(rgb, 0, 1), a]) * 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(art)
    SL.text_img(d, (Wc - P * S - 14 * S, P * S + 16 * S), "CELL//NOTE", SL.MONO, 11, (90, 60, 34, 255), anchor="rm")
    return SL.build_sticker(art, material="kraft", body=body, curl=curl, seed=seed)


def place_sticker(img_f, sd, cx, cy, **kw):
    """Place a C sticker onto a float RGB image."""
    c = f2pil(img_f).convert("RGBA")
    c = SL.place(c, sd, cx, cy, **kw)
    return pil2f(c)


# ------------------------------------------------------------------ C: word stickers
FILL_PINK = ("grad", (255, 96, 172), (222, 18, 112))
FILL_RED = ("grad", (255, 88, 80), (204, 20, 22))
FILL_YELLOW = ("grad", (255, 238, 96), (232, 176, 22))


def word_sticker(lines, size, fills, seed=1, border=20, curl=None, gloss_pos=0.32, holo_phase=0.0,
                 key_w=5, extrude=8, jitter=4.0):
    """Bold die-cut lettering: black keyline, chunky extrude, thick crisp white border, gloss."""
    if isinstance(lines, str):
        lines = [lines]
    art = SL.lettering(lines, size, fills, key_w=key_w, extrude=extrude, seed=seed, jitter=jitter, track=1,
                       holo_seed=seed + 40, holo_phase=holo_phase)
    return SL.build_sticker(art, border=border, material="gloss", gloss_pos=gloss_pos, curl=curl, seed=seed,
                            close=border * 1.25)


def verb_sticker(word, size, holo=True, **kw):
    """Verbs: holo foil on the primary verb, kit pink on the rest."""
    return word_sticker([word], size, ["holo" if holo else FILL_PINK], **kw)
