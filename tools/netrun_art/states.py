"""states: the HQ room-state language (spec 8.1 `states`), pure part plus the PIL look-dev overlays.

Ports `hq_orbital/scripts/hq_kit/states.py` c47c67a9. Colours are 0..255 RGB. The two overlay functions draw into a PIL
image and import numpy / Pillow lazily, so importing this module needs neither.
"""
from typing import Dict, Optional, Sequence, Tuple

LIME = (212, 255, 0)
ORANGE = (255, 140, 26)
WHITE = (242, 246, 255)
GREY = (122, 118, 134)
RED = (255, 44, 52)
GOLD = (255, 196, 60)
STATE_COL: Dict[str, Tuple[int, int, int]] = {"option": ORANGE, "current": LIME, "walked": LIME, "reach": WHITE,
                                              "target": WHITE, "grey": GREY}
# 3D room light ladder (r3 jobs_aaa STATE_K)
STATE_K: Dict[str, float] = {"option": 0.9, "current": 0.6, "walked": 0.32, "reach": 0.34, "grey": 0.07, "target": 0.85}
LOCKDOWN_K = 2.2
LOCKDOWN_RGB = (1.0, 0.05, 0.08)
SCAN_ALPHA = 150          # scan line alpha at k = 1
SCAN_LINES = 11.0         # lines per opening height
SCAN_MIN_STEP = 4.0       # px
BADGE_FILL = (210, 20, 30, 255)
BADGE_EDGE = (10, 6, 8, 255)


def ring_colour(state: str, in_eye: bool) -> Tuple[int, int, int]:
    """Ring colour of a room state; RED for an option or room ahead that is in the eye."""
    return RED if in_eye and state in ("option", "reach") else STATE_COL.get(state, WHITE)


def rule_word(consequence: str) -> str:
    """The IN THE EYE chip text for a consequence (`spotted`, `blocked`, else the bare label)."""
    return {"spotted": "IN THE EYE: entering = SPOTTED (+1 enforcer)",
            "blocked": "IN THE EYE: LOCKED this step"}.get(consequence, "IN THE EYE")


def scan_lines(img, poly: Sequence[Sequence[float]], k: float = 1.0, phase: float = 0.0, size=None):
    """Red holo scan lines clipped to an opening polygon (PIL RGBA image in, same image out)."""
    import numpy as np
    from PIL import Image, ImageDraw
    W, H = size or img.size
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    ys = [q[1] for q in poly]
    y0, y1 = min(ys), max(ys)
    step = max(SCAN_MIN_STEP, (y1 - y0) / SCAN_LINES)
    y = y0 + (phase % 1.0) * step
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([tuple(q) for q in poly], fill=255)
    while y < y1:
        d.line([(0, y), (W, y)], fill=RED + (int(SCAN_ALPHA * k),), width=2)
        y += step
    a = lay.split()[3]
    lay.putalpha(Image.fromarray((np.asarray(a, np.float32) * np.asarray(m, np.float32) / 255).astype(np.uint8)))
    img.alpha_composite(lay)
    return img


def eye_badge(px: int, crest_mask: Optional[object] = None):
    """A red disc with the corp crest in white (PIL RGBA)."""
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([1, 1, px - 2, px - 2], fill=BADGE_FILL, outline=BADGE_EDGE, width=max(2, px // 12))
    if crest_mask is not None:
        m = crest_mask.resize((int(px * 0.78), int(px * 0.78)), Image.LANCZOS)
        w = Image.new("RGBA", m.size, (255, 255, 255, 255))
        w.putalpha(m)
        im.alpha_composite(w, ((px - m.width) // 2, (px - m.height) // 2))
    return im
