"""hq_kit.states: the HQ room-state language (one place for the colours, the 3D light ladder and the 2D marks).

States (the locked netrun grammar + the HQ scan state):
  current   lime ring + lime cut frame, the token            walked   lime, the room desaturated to 70 %
  option    orange ring + number chip, orange wax link       reach    white ring, white dashed wax ("ahead")
  grey      past / cut off: grey ring at 26 %, ghost tint    target   the red pencil TARGET circle
  IN THE EYE (scanned, an HQ addition, proposal): on an option or a room ahead -> RED ring + red cut frame (glow),
            a small red EYE badge on the sticker, red holo scan lines over the opening, the "IN THE EYE" chip on
            options; in 3D the room light turns lockdown red (x LOCKDOWN_K) and a translucent red scan-line plane +
            a red frame close the opening. The rule word (SPOTTED / LOCKED) is a config choice; the visual is the same.
  x-ray     a room on a face turned away: a faint ring in its state colour (OVERVIEW / legend hover only)

    from hq_kit import states as ST
    ST.STATE_COL, ST.STATE_K, ST.RED, ST.GOLD, ST.LOCKDOWN_K
    ST.scan_lines(img, poly, k, phase, size)  ->  img (RGBA, PIL)
    ST.eye_badge(px, crest_mask=None)        ->  RGBA sticker badge (the corp crest, white on red)
    ST.ring_colour(state, in_eye) / ST.rule_word(consequence)
"""



LIME = (212, 255, 0)
ORANGE = (255, 140, 26)
WHITE = (242, 246, 255)
GREY = (122, 118, 134)
RED = (255, 44, 52)
GOLD = (255, 196, 60)
STATE_COL = {"option": ORANGE, "current": LIME, "walked": LIME, "reach": WHITE, "target": WHITE, "grey": GREY}
# 3D room light ladder (r3 jobs_aaa STATE_K): options 0.9, TARGET 0.85, current 0.6, ahead 0.34, walked 0.32, past 0.07
STATE_K = {"option": 0.9, "current": 0.6, "walked": 0.32, "reach": 0.34, "grey": 0.07, "target": 0.85}
LOCKDOWN_K = 2.2
LOCKDOWN_RGB = (1.0, 0.05, 0.08)


def ring_colour(state, in_eye):
    return RED if in_eye and state in ("option", "reach") else STATE_COL.get(state, WHITE)


def rule_word(consequence):
    return {"spotted": "IN THE EYE: entering = SPOTTED (+1 enforcer)",
            "blocked": "IN THE EYE: LOCKED this step"}.get(consequence, "IN THE EYE")


def scan_lines(img, poly, k=1.0, phase=0.0, size=None):
    """Red holo scan lines clipped to a room's opening polygon (the 2D twin of the 3D lockdown plane)."""
    import numpy as np
    from PIL import Image, ImageDraw
    W, H = size or img.size
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    ys = [q[1] for q in poly]
    y0, y1 = min(ys), max(ys)
    step = max(4.0, (y1 - y0) / 11.0)
    y = y0 + (phase % 1.0) * step
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([tuple(q) for q in poly], fill=255)
    while y < y1:
        d.line([(0, y), (W, y)], fill=RED + (int(150 * k),), width=2)
        y += step
    a = lay.split()[3]
    lay.putalpha(Image.fromarray((np.asarray(a, np.float32) * np.asarray(m, np.float32) / 255).astype(np.uint8)))
    img.alpha_composite(lay)
    return img


_BADGE = {}


def eye_badge(px, crest_mask=None):
    """A red disc with the corp crest in white (Halcyon: the eye, crests15.eye()). crest_mask: a 512 'L' mask."""
    from PIL import Image, ImageDraw
    key = (px, id(crest_mask))
    if key not in _BADGE:
        im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse([1, 1, px - 2, px - 2], fill=(210, 20, 30, 255), outline=(10, 6, 8, 255), width=max(2, px // 12))
        if crest_mask is not None:
            m = crest_mask.resize((int(px * 0.78), int(px * 0.78)), Image.LANCZOS)
            w = Image.new("RGBA", m.size, (255, 255, 255, 255))
            w.putalpha(m)
            im.alpha_composite(w, ((px - m.width) // 2, (px - m.height) // 2))
        _BADGE[key] = im
    return _BADGE[key]
