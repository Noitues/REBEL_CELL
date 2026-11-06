"""R2 actions glyph imports. Library (cards kglyph copy: KA_twist, KA_brace ...) + Breaker crest = cracked ring (same drawing as wheel_core hub_emblem WC2_CREST, name A2_CREST)."""
import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
import bb_lib  # noqa
import crests15
import kglyph2  # noqa: F401  (asm: master library)


def crest():
    S, SS = 512, 2
    m = Image.new('L', (S * SS, S * SS), 0)
    d = ImageDraw.Draw(m)
    k = SS
    d.ellipse([40 * k, 40 * k, 472 * k, 472 * k], fill=255)
    d.ellipse([132 * k, 132 * k, 380 * k, 380 * k], fill=0)
    zig = [(306, 14), (240, 188), (310, 226), (214, 334), (266, 372), (196, 500)]
    d.line([(x * k, y * k) for x, y in zig], fill=0, width=50 * k, joint='curve')
    for x, y in zig:
        d.ellipse([(x - 25) * k, (y - 25) * k, (x + 25) * k, (y + 25) * k], fill=0)
    d.ellipse([226 * k, 226 * k, 286 * k, 286 * k], fill=255)
    return m.resize((S, S), Image.LANCZOS)


crests15.CUSTOM['A2_CREST'] = crest
CREST, TWIST = 'A2_CREST', 'KA_twist'
