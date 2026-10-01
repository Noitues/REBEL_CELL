"""The two wheat-paste posters: crew photo and Heat poster."""
import numpy as np
from PIL import Image
from paste import photocopy, portrait_gray, wheatpaste, text_ink
from spraylib import IMPACT, COUR, BAHN, PINK, YELLOW, BLACK, Layer, spray, stencil_shadow, stencil_text, drip_mask, spray_drips, icon_eye_crossed, blur


def crew_poster(rng, w=210, h=272):
    """Photocopied operative portrait pasted as an ID slip."""
    ph = int(h * 0.80)
    g = portrait_gray(w, ph, rng)
    ink = photocopy(g, rng, cell=4.2)
    content = np.ones((h, w), np.float32)
    content[:ph] = 1 - ink
    cap = text_ink(w, h - ph, [("OPERATIVE // CELL-9", COUR, 13.5, (w / 2, (h - ph) * 0.40), "mm"),
                               ("KNOWN AS: WREN", COUR, 11.5, (w / 2, (h - ph) * 0.78), "mm")])
    capink = photocopy(cap, rng, cell=3, lo=0.45, hi=0.75, streaks=False)
    content[ph:] = 1 - capink
    rgb = np.repeat(content[..., None], 3, axis=2)
    rgb = 0.07 + 0.93 * rgb  # toner is never pure black
    return wheatpaste(rgb, rng, peel="tr", peel_size=0.22, bites=1, wrinkles=4)


def heat_poster(rng, w=250, h=330):
    """Heat poster: photocopied surveillance sheet, FLAGGED sprayed across it."""
    items = [("HEAT", IMPACT, 54, (w / 2, 46), "mm"),
             ("62", IMPACT, 150, (w / 2, 158), "mm"),
             ("SECTOR 9 // CELL ACTIVITY", COUR, 12, (w / 2, 296), "mm"),
             ("KEEP MOVING.", COUR, 10.5, (w / 2, 312), "mm")]
    g = text_ink(w, h, items)
    # surveillance eye band (halftone grey) behind the number
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    eye = np.clip(1 - np.abs(((xx - w / 2) / (w * 0.46)) ** 2 + ((yy - 160) / 62) ** 2 - 0.7) * 2.2, 0, 1)
    g = np.minimum(g, 1 - eye * 0.45)
    # frame rule
    g[12:16, 14:w - 14] = 0
    g[h - 48:h - 45, 14:w - 14] = 0
    ink = photocopy(g, rng, cell=4.5, lo=0.32, hi=0.7)
    rgb = np.repeat((1 - ink)[..., None], 3, axis=2) * 0.93 + 0.07
    poster = wheatpaste(rgb, rng, peel="tr", peel_size=0.24, bites=1, wrinkles=5)
    # spray FLAGGED across the pasted poster
    M = stencil_text("FLAGGED", 54, rng=rng, angle=8, slice_frac=None, bridge=0.06)
    Mp = np.pad(M, ((0, 60), (0, 0)))
    L = Layer(Mp.shape[1], Mp.shape[0])
    stencil_shadow(L, Mp, rng, dx=3, dy=4, amt=0.7)
    spray(L, Mp, PINK, rng, halo=7, sheen=0.4)
    D, _ = drip_mask(Mp, rng, n=4, max_len=46, width=(3, 5))
    spray_drips(L, D, PINK, rng)
    return poster, L.to_image()
