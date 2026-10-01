"""04_lifecycle.png: the SEND IT verb sprayed on, idling with crawling drips, wiped off with solvent."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from marks import load_base, stencil_word, bahn, OUT, W, H
from spraylib import (PINK, WHITE, BLACK, Layer, blur, fbm, spray, stencil_text, drip_mask, spray_drips, IMPACT)
from combat import wash_button

PW, PH = 600, 760          # panel size
SCALE = 1.5
CROP = (1520, 573, 1920, 1080)
SEED = 4401
VERB = dict(text="SEND\nIT", size=int(104 * SCALE), angle=-7, line_gap=-0.06, align="center")
CX, CY = (1748 - CROP[0]) * SCALE, (884 - CROP[1]) * SCALE


def hstreak(h, w, rng, scales=(30, 8), weights=(0.6, 0.4), stretch=8):
    """Noise stretched along x (rag weave / wipe streaks)."""
    n = fbm(h, max(4, w // stretch), rng, scales=scales, weights=weights)
    im = Image.fromarray((n * 255).astype(np.uint8), "L").resize((w, h), Image.BICUBIC)
    return np.asarray(im, np.float32) / 255


def panel_base():
    base = load_base("concepts/round2/r2c_geo_vector_gritty/stills/04_combat.png")
    base = wash_button(base, 1760, 895, 135, amount=0.30, desat=0.6)
    return base.crop(CROP).resize((PW, PH), Image.LANCZOS).convert("RGBA")


def verb_mask():
    rng = np.random.default_rng(SEED)
    return stencil_text(VERB["text"], VERB["size"], font=IMPACT, rng=rng, angle=VERB["angle"], slice_frac=0.56,
                        bridge=0.075, line_gap=VERB["line_gap"], align=VERB["align"], tracking=0.04)


def verb(reveal=None, drip_lengths=None):
    rng = np.random.default_rng(SEED)
    return stencil_word(VERB["text"], VERB["size"], PINK, rng, angle=VERB["angle"], drips=7, drip_len=140,
                        drip_w=(7, 12), line_gap=VERB["line_gap"], align=VERB["align"], sheen=0.5, halo=14,
                        reveal=reveal, drip_lengths=drip_lengths, return_parts=True, shadow_off=(8, 9),
                        keyline=(WHITE, 5, 5))


def put(panel, parts):
    img, mshape = parts[0], parts[1]
    x, y = int(CX - img.size[0] / 2), int(CY - mshape[0] / 2)
    lay = Image.new("RGBA", panel.size, (0, 0, 0, 0))
    lay.paste(img, (x, y))
    return Image.alpha_composite(panel, lay), (x, y)


def panel_spray_on():
    """Mid-spray: SEND is filled, the can is sweeping across IT; acetate stencil sheet still on the glass."""
    M = verb_mask()
    mh, mw = M.shape

    def reveal(shape):
        h, w = shape
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.zeros(shape, np.float32)
        split = mh * 0.50
        r[yy < split] = 1.0
        front = w * 0.56
        lower = (yy >= split)
        prog = np.clip((front - xx) / 60.0, 0, 1)
        # second coat still thin near the front
        r = np.where(lower, prog * (0.55 + 0.45 * np.clip((front - 90 - xx) / 80, 0, 1)), r)
        return r
    panel = panel_base()
    parts = verb(reveal=reveal)
    panel, (x, y) = put(panel, parts)
    # acetate stencil sheet with the cut letters, overspray built up on it
    arr = np.zeros((PH, PW), np.float32)
    arr[max(0, y):y + mh, max(0, x):x + mw] = M[: PH - max(0, y), : PW - max(0, x)]
    sheet = Image.new("L", (PW, PH), 0)
    ImageDraw.Draw(sheet).polygon([(x - 34, y + 26), (x + mw + 10, y - 12), (x + mw + 38, y + mh + 4), (x - 6, y + mh + 40)], fill=255)
    S = np.asarray(sheet, np.float32) / 255
    S = blur(S, 0.8) * (1 - np.clip(arr * 1.4, 0, 1))
    L = Layer(PW, PH)
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    frost = 0.16 + 0.05 * fbm(PH, PW, np.random.default_rng(5), scales=(120, 30), weights=(0.6, 0.4))
    L.over(np.array([0.86, 0.9, 0.92], np.float32), S * frost)
    # edge highlight and sheet shadow on the glass
    edge = np.clip(S - blur(S, 2.0), 0, 1) * 2.2
    L.over(WHITE, np.clip(edge, 0, 0.7))
    # pink buildup on the sheet around the holes (old coats from previous jobs too)
    rng = np.random.default_rng(9)
    build = np.clip(blur(arr, 9) * 1.4 - arr, 0, 1) * S
    spray(L, build * 1.0, PINK, rng, halo=6, halo_amt=0.3, core_soft=1.5, sheen=0)
    # live mist cloud at the nozzle front
    fx, fy = x + mw * 0.56, y + mh * 0.75
    cloud = np.exp(-(((xx - fx) / 70) ** 2 + ((yy - fy) / 55) ** 2))
    dots = (rng.random((PH, PW)) < cloud * 0.30).astype(np.float32) * (0.4 + 0.6 * rng.random((PH, PW)))
    L.over(PINK, np.clip(cloud * 0.22 + dots, 0, 1))
    panel = Image.alpha_composite(panel, L.to_image())
    sh = Image.new("RGBA", panel.size, (0, 0, 0, 0))
    return panel


def panel_idle():
    panel = panel_base()
    parts = verb(drip_lengths=[1.0] * 7)
    panel, (x, y) = put(panel, parts)
    return panel, parts, (x, y)


def panel_wipe(full_parts, xy):
    """Solvent wipe: the rag has crossed the left 55 %; paint there is smeared, thinned and running."""
    img = full_parts[0]
    a = np.asarray(img, np.float32) / 255
    rgb, al = a[..., :3], a[..., 3]
    h, w = al.shape
    rng = np.random.default_rng(77)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    front = w * 0.58 + (yy - h * 0.4) * 0.18 + (fbm(h, w, rng, scales=(40,), weights=(1,)) - 0.5) * 40
    wiped = np.clip((front - xx) / 45.0, 0, 1)
    # smear: paint dragged along the wipe direction, streaked by the rag weave
    sm = al.copy()
    acc = np.zeros_like(sm)
    for k in range(0, 90, 3):
        acc = np.maximum(acc, np.roll(sm, k, axis=1) * (1 - k / 90))
    streak = hstreak(h, w, rng, scales=(6, 2), weights=(0.6, 0.4), stretch=10)
    streak = np.clip((streak - 0.35) * 1.8, 0, 1)
    residue = blur(acc, 2.0) * streak * 0.42
    # dissolving edge: softened, thinner paint right at the front
    near = np.clip(1 - np.abs(front - xx) / 70.0, 0, 1)
    soft = blur(al, 3.0)
    keep = al * (1 - wiped)
    keep = keep * (1 - near * 0.45) + soft * near * 0.25 * (1 - wiped)
    out_a = np.clip(np.maximum(keep, residue * wiped), 0, 1)
    out_rgb = rgb.copy()
    # residue is diluted: lighter, cooler pink
    dil = np.clip(PINK * 0.8 + 0.18, 0, 1)
    mix = (residue * wiped / np.maximum(out_a, 1e-4))[..., None]
    smear_rgb = np.broadcast_to(dil, rgb.shape)
    out_rgb = out_rgb * (1 - np.clip(mix, 0, 1)) + smear_rgb * np.clip(mix, 0, 1)
    # where residue sits outside the old paint, rgb was undefined: use the smear colour
    out_rgb = np.where((al < 0.05)[..., None], smear_rgb, out_rgb)
    L = Layer(w, h)
    L.rgb, L.a = out_rgb.astype(np.float32), out_a.astype(np.float32)
    # solvent runs: thin, diluted, glossy
    band = (near > 0.4) & (al > 0.5)
    seeds = np.zeros_like(al)
    seeds[band] = 1
    D, _ = drip_mask(seeds, rng, n=6, max_len=170, width=(2.5, 4.5), clear=6, min_gap=22)
    run = Layer(w, h)
    spray_drips(run, D, dil, rng, gloss=0.8)
    L.over(run.rgb, run.a * 0.6)
    # wet rag sheen over the wiped glass
    wet = wiped * np.clip((hstreak(h, w, rng, scales=(8, 3), weights=(0.6, 0.4)) - 0.5) * 2.5, 0, 1)
    L.over(np.array([0.9, 0.95, 1.0], np.float32), wet * 0.10 * (blur(al, 30) > 0.02))
    panel = panel_base()
    lay = Image.new("RGBA", panel.size, (0, 0, 0, 0))
    lay.paste(L.to_image(), xy)
    return Image.alpha_composite(panel, lay)


def drip_ticks(panel, parts, xy):
    """Idle annotation: tick marks down the longest drip showing where its tip paused."""
    specs = parts[2]
    s = max(specs, key=lambda d: d["L"])
    x0, y0 = xy
    d = ImageDraw.Draw(panel)
    f = bahn(15, "SemiLight")
    tx = x0 + s["x"] + 22
    for i, fr in enumerate((0.45, 0.7, 1.0)):
        ty = y0 + s["y"] + s["L"] * fr
        d.line((tx - 8, ty, tx + 6, ty), fill=(235, 235, 235, 220), width=2)
        d.text((tx + 12, ty), ("t+1s", "t+3s", "t+6s")[i], font=f, fill=(235, 235, 235, 220), anchor="lm")
    d.line((tx, y0 + s["y"] + s["L"] * 0.45, tx, y0 + s["y"] + s["L"]), fill=(235, 235, 235, 120), width=1)
    return panel


def build():
    sheet = Image.new("RGB", (W, H), (12, 12, 16))
    nz = (fbm(H, W, np.random.default_rng(1), scales=(200, 40), weights=(0.6, 0.4)) * 10).astype(np.uint8)
    sheet = Image.fromarray(np.clip(np.asarray(sheet, np.int16) + nz[..., None], 0, 255).astype(np.uint8))
    p1 = panel_spray_on()
    p2, parts, xy = panel_idle()
    p2 = drip_ticks(p2, parts, xy)
    p3 = panel_wipe(parts, xy)
    d = ImageDraw.Draw(sheet)
    d.text((60, 58), "SEND IT  /  VERB LIFECYCLE", font=bahn(30, "Bold"), fill=(236, 236, 230))
    d.text((60, 98), "STENCIL & SPRAY OVERLAY  //  combat GO button, shown at 1.5x", font=bahn(18, "SemiLight"),
           fill=(150, 150, 158))
    caps = [("01  SPRAY ON", "0.00 - 0.45 s",
             "Acetate stencil snaps on. Three can sweeps fill it,\ntop line first. Mist settles; the sheet lifts away."),
            ("02  IDLE", "loop while waiting",
             "Drips crawl a few px, pause, crawl again.\nWet bulbs catch a slow glint. Overspray never moves."),
            ("03  LEAVE", "0.35 s with the page",
             "A solvent rag wipes with the transition: paint\nsmears, thins and runs, then clears from the glass.")]
    for i, p in enumerate([p1, p2, p3]):
        x = 45 + i * (PW + 30)
        y = 150
        sheet.paste(Image.new("RGB", (PW + 4, PH + 4), (40, 40, 48)), (x - 2, y - 2))
        sheet.paste(p.convert("RGB"), (x, y))
        t, tm, body = caps[i]
        d.rectangle((x, y + PH + 22, x + 6, y + PH + 52), fill=tuple(int(c * 255) for c in PINK))
        d.text((x + 18, y + PH + 18), t, font=bahn(26, "Bold"), fill=(240, 240, 236))
        d.text((x + PW, y + PH + 22), tm, font=bahn(18, "SemiLight"), fill=(160, 160, 168), anchor="ra")
        d.multiline_text((x + 18, y + PH + 60), body, font=bahn(17, "SemiLight"), fill=(175, 175, 182), spacing=6)
    sheet.save(os.path.join(OUT, "04_lifecycle.png"))
    print("saved 04_lifecycle.png")


if __name__ == "__main__":
    build()
