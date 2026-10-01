"""05_lifecycle.png: the three materials moving together on the combat screen.

APPEAR  SEND IT sprays on through an acetate stencil, the note card slaps on, the pencil circle draws.
IDLE    drips crawl, the card corner flutters, a glint runs across the wax.
EXIT    solvent wipe on the spray, the card peels away, a palm smears the pencil.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from kit import *  # noqa
import s01_combat as C

CROP = (1320, 380, 1920, 1080)        # 600 x 700
PW, PH = 600, 700
VERB_SEED = 1104


def verb_mask():
    return SP.stencil_text("SEND\nIT", 100, font=SP.IMPACT, rng=np.random.default_rng(VERB_SEED), angle=-7,
                           slice_frac=0.56, bridge=0.075, line_gap=-0.06, align="center", tracking=0.04)


def hstreak(h, w, rng, scales=(6, 2), stretch=10):
    n = SP.fbm(h, max(4, w // stretch), rng, scales=scales, weights=(0.6, 0.4))
    return np.asarray(Image.fromarray((n * 255).astype(np.uint8), "L").resize((w, h), Image.BICUBIC), np.float32) / 255


def solvent_wipe(img, front_frac=0.58, seed=77):
    """B's solvent wipe on a sprayed RGBA image: smear along the rag, thin, run, wet sheen."""
    a = np.asarray(img, np.float32) / 255
    rgb, al = a[..., :3], a[..., 3]
    h, w = al.shape
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    front = w * front_frac + (yy - h * 0.4) * 0.18 + (SP.fbm(h, w, rng, scales=(40,), weights=(1,)) - 0.5) * 40
    wiped = np.clip((front - xx) / 45.0, 0, 1)
    acc = np.zeros_like(al)
    for k in range(0, 90, 3):
        acc = np.maximum(acc, np.roll(al, k, axis=1) * (1 - k / 90))
    streak = np.clip((hstreak(h, w, rng) - 0.35) * 1.8, 0, 1)
    residue = SP.blur(acc, 2.0) * streak * 0.42
    near = np.clip(1 - np.abs(front - xx) / 70.0, 0, 1)
    keep = al * (1 - wiped)
    keep = keep * (1 - near * 0.45) + SP.blur(al, 3.0) * near * 0.25 * (1 - wiped)
    out_a = np.clip(np.maximum(keep, residue * wiped), 0, 1)
    dil = np.clip(SP.PINK * 0.8 + 0.18, 0, 1)
    mix = np.clip(residue * wiped / np.maximum(out_a, 1e-4), 0, 1)[..., None]
    out_rgb = rgb * (1 - mix) + dil * mix
    out_rgb = np.where((al < 0.05)[..., None], np.broadcast_to(dil, rgb.shape), out_rgb)
    L = SP.Layer(w, h)
    L.rgb, L.a = out_rgb.astype(np.float32), out_a.astype(np.float32)
    seeds = ((near > 0.4) & (al > 0.5)).astype(np.float32)
    D, _ = SP.drip_mask(seeds, rng, n=5, max_len=120, width=(2.5, 4.0), clear=6, min_gap=22)
    run = SP.Layer(w, h)
    SP.spray_drips(run, D, dil, rng, gloss=0.8)
    L.over(run.rgb, run.a * 0.6)
    return L.to_image()


def acetate(img_f, cx, cy, img_w):
    """The stencil sheet still on the glass while the can sweeps: holes where the letters are."""
    M = verb_mask()
    mh, mw = M.shape
    x, y = int(cx - img_w / 2), int(cy - mh / 2)
    arr = np.zeros((H, W), np.float32)
    ww = min(mw, W - x)
    arr[y:y + mh, x:x + ww] = M[:, :ww]
    sheet = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sheet).polygon([(x - 26, y + 22), (x + mw + 6, y - 10), (x + mw + 30, y + mh + 4), (x - 4, y + mh + 32)],
                                  fill=255)
    S = SP.blur(np.asarray(sheet, np.float32) / 255, 0.8) * (1 - np.clip(arr * 1.4, 0, 1))
    frost = 0.16 + 0.05 * SP.fbm(H, W, np.random.default_rng(5), scales=(120, 30), weights=(0.6, 0.4))
    out = img_f * (1 - (S * frost)[..., None]) + np.array([0.86, 0.9, 0.92]) * (S * frost)[..., None]
    edge = np.clip(S - SP.blur(S, 2.0), 0, 1) * 2.2
    out = out * (1 - np.clip(edge, 0, 0.7)[..., None]) + SP.WHITE * np.clip(edge, 0, 0.7)[..., None]
    build_up = np.clip(SP.blur(arr, 7) * 1.4 - arr, 0, 1) * S * 0.7
    out = out * (1 - build_up[..., None]) + SP.PINK * build_up[..., None]
    # live mist at the nozzle front
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    fx, fy = x + mw * 0.56, y + mh * 0.75
    cloud = np.exp(-(((xx - fx) / 55) ** 2 + ((yy - fy) / 42) ** 2))
    rng = np.random.default_rng(9)
    dots = (rng.random((H, W)) < cloud * 0.3).astype(np.float32) * (0.4 + 0.6 * rng.random((H, W)))
    m = np.clip(cloud * 0.22 + dots, 0, 1)[..., None]
    return np.clip(out * (1 - m) + SP.PINK * m, 0, 1)


def reveal_sweep(mh):
    def reveal(shape):
        h, w = shape
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.where(yy < mh * 0.5, 1.0, 0.0).astype(np.float32)
        front = w * 0.56
        prog = np.clip((front - xx) / 50.0, 0, 1) * (0.55 + 0.45 * np.clip((front - 70 - xx) / 60, 0, 1))
        return np.where(yy >= mh * 0.5, prog, r).astype(np.float32)
    return reveal


def frame(stage, base):
    img = C.pencil_composite(base, C.pencil_layer(np.random.default_rng(101), **{
        "appear": dict(progress=0.55), "idle": dict(progress=1.0, glint=0.80), "exit": dict(wipe=0.76)}[stage]))
    img = glass(img, np.random.default_rng(11), C.SMUDGES, band_pos=0.30)
    note = lambda **kw: note_card("SLICE 6 CRACKED\nBACKDOOR FIRST\nTHEN BRUTE IT", **kw)  # noqa: E731
    nx, ny, na = C.NOTE_POS
    if stage == "appear":
        # slap: a ghost in the air, then the squash on contact
        img = place_sticker(img, note(), nx - 30, ny - 50, angle=na - 12, scale=1.2, hover=1.0, opacity=0.3, shadow=0.6)
        img = place_sticker(img, note(), nx, ny + 4, angle=na - 2, squash=(1.12, 0.86), shadow=1.2)
    elif stage == "idle":
        img = place_sticker(img, note(curl=dict(corner="tr", amount=0.20)), nx, ny, angle=na, opacity=0.35, shadow=0.0)
        img = place_sticker(img, note(curl=dict(corner="tr", amount=0.08)), nx, ny, angle=na)
    else:
        img = place_sticker(img, note(curl=dict(corner="tr", amount=0.6, bend=0.25, flap_shadow=0.6)),
                            nx - 26, ny + 40, angle=na - 12, scale=0.96, hover=0.7)
    cx, cy = C.SEND_C
    if stage == "appear":
        mh = verb_mask().shape[0]
        parts = C.send_it(reveal=reveal_sweep(mh))
        img = spray_verbs(img, [(parts, cx, cy)])
        img = acetate(img, cx, cy, parts[0].size[0])
    elif stage == "idle":
        parts = C.send_it(drip_lengths=[1.25] * 7)
        img = spray_verbs(img, [(parts, cx, cy)])
    else:
        parts = C.send_it()
        img = spray_verbs(img, [((solvent_wipe(parts[0]),) + tuple(parts[1:]), cx, cy)])
    x0, y0, x1, y1 = CROP
    return f2pil(img[y0:y1, x0:x1])


def build():
    base = C.combat_base()
    sheet = Image.new("RGB", (W, H), (13, 13, 17))
    d = ImageDraw.Draw(sheet)
    d.text((45, 40), "SEND IT  /  KIT LIFECYCLE", font=MK.bahn(32, "Bold"), fill=(236, 236, 230))
    d.text((45, 84), "spray verb + vinyl note card + grease pencil target, moving together on the combat screen",
           font=MK.bahn(19, "SemiLight"), fill=(150, 150, 158))
    caps = [("01  APPEAR", "0.00 - 0.55 s",
             "SEND IT sprays on through an acetate stencil, top line first.\nThe note card slaps on (squash 1.12 / 0.86, one overshoot).\nThe red pencil circle draws in writing order."),
            ("02  IDLE", "loop",
             "Drips crawl a few px, pause, crawl again.\nThe card's top corner flutters 0.08 <-> 0.20.\nA thin glint runs across the wax every ~3 s."),
            ("03  EXIT", "0.35 s with the page",
             "A solvent rag wipes the spray: smear, thin, run.\nThe card peels from its lifted corner and drops away.\nA palm drags the pencil into a red haze.")]
    for i, st in enumerate(("appear", "idle", "exit")):
        x = 45 + i * (PW + 30)
        y = 130
        sheet.paste(Image.new("RGB", (PW + 4, PH + 4), (44, 44, 52)), (x - 2, y - 2))
        sheet.paste(frame(st, base), (x, y))
        t, tm, body = caps[i]
        d.rectangle((x, y + PH + 22, x + 6, y + PH + 52), fill=K_PINK)
        d.text((x + 18, y + PH + 18), t, font=MK.bahn(26, "Bold"), fill=(240, 240, 236))
        d.text((x + PW, y + PH + 22), tm, font=MK.bahn(18, "SemiLight"), fill=(160, 160, 168), anchor="ra")
        d.multiline_text((x + 18, y + PH + 60), body, font=MK.bahn(17, "SemiLight"), fill=(175, 175, 182), spacing=6)
    sheet.save(os.path.join(OUT, "05_lifecycle.png"))
    print("saved 05_lifecycle.png")


if __name__ == "__main__":
    build()
