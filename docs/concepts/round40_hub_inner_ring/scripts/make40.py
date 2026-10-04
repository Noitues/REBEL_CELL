"""Round 40 -> hub_cores_v3.png, lockdown.gif, player_defeat_v2.gif, inner_ring_v3.png, status_stacks.png."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)

import textwrap
from PIL import Image, ImageDraw
import slicelib as SL
import slicekit as K
import hubkit as H
import hub39 as X
import hub40 as L
import ring2 as R
import overlays as O
import glyphs40 as G40
import make_glyphs as MG
from make_hubs import CLASS, CORE_NAME, RINGS, ENEMY, glyph_strip, grey, new_sheet, head, MANIFEST
from make39 import PS, BREAKER, MAN, save_gif as _sg, nearest
from slicelib import f_num, f_ui, f_mono, bloom


def save_gif(frames, name, ms):
    import make39
    make39.OUT = OUT
    make39.save_gif(frames, name, ms)


def cap(d, x, y, text, w=44, col=(185, 185, 198)):
    for k, ln in enumerate(textwrap.wrap(text, w)):
        d.text((x, y + k * 15), ln, font=f_mono(11, False), fill=col)


def hubs():
    W = 2400
    im, d = new_sheet(W, 1500, "HUB CORES v3  +  LOCKDOWN  +  PLAYER DEFEAT v2",
                      "Locked: Rigger, Overclocker, Ghost, Swarm, Hive, all enemy hubs. Redone: Breaker (spiderweb cracks only), Phantom (inner-ring pulsing removed). "
                      "Enemy Hub Breach becomes LOCKDOWN: a waterline of encrypted bits drains with the timer.")
    head(d, 40, 120, "BREAKER + PHANTOM", (255, 214, 64))
    br = [c for c in CLASS if c[1] == "breaker_core"][0]
    G40.BYPASS.add("CORE_breaker_core")
    SL._glyph_cache.clear()
    old = H.hub_closeup(dict(acc=br[2], emblem="CORE_breaker_core", name="BREAKER CORE", sub=br[4]), ring_segs=RINGS["breaker"], size=200)
    G40.BYPASS.discard("CORE_breaker_core")
    SL._glyph_cache.clear()
    im.alpha_composite(old, (40, 170))
    d.text((80, 372), "round 39", font=f_mono(11, False), fill=(200, 140, 140))
    d.text((250, 250), "->", font=f_num(30), fill=(200, 200, 210))
    new = H.hub_closeup(dict(acc=br[2], emblem="CORE_breaker_core", name="BREAKER CORE", sub=br[4]), ring_segs=RINGS["breaker"], size=280)
    im.alpha_composite(new, (300, 140))
    mk = H.hub_closeup(dict(acc=br[2], emblem="CORE_breaker_core", name="BREAKER CORE MK2", sub=br[5], mk2=True), ring_segs=RINGS["breaker"], size=180)
    im.alpha_composite(mk, (590, 190))
    glyph_strip(im, d, 300, 430, "CORE_breaker_core", br[2])
    sc, tw = nearest("CORE_breaker_core")
    d.text((460, 440), "16 px twin %.2f (%s)" % (sc, tw[:14]), font=f_mono(11, False), fill=(150, 225, 150) if sc < 0.62 else (255, 214, 120))
    cap(d, 460, 460, "crowbar + a spiderweb of glass cracks from the strike point; no pane, no fill", 40)
    ph = [c for c in CLASS if c[1] == "phantom_core"][0]
    hub = dict(acc=ph[2], emblem="CORE_phantom_core", name="PHANTOM CORE", sub=ph[4])
    x0 = 900
    for k, t in enumerate((0.0, 0.25, 0.5, 0.75)):
        f = X.phantom(hub, t, size=220, ring_segs=RINGS["ghost"])
        im.alpha_composite(f, (x0 + k * 230, 160))
        d.text((x0 + k * 230 + 80, 386), "t = %.2f" % t, font=f_mono(11, False), fill=(175, 175, 190))
    cap(d, x0, 410, "PHANTOM (phantom_echo_v2 frames): only the mask's echo trail moves; the inner ring and its glyphs now hold "
        "still (round 39's ring pulse was a bug: cached glyphs were being faded in place each frame).", 110)
    # lockdown
    y = 520
    head(d, 40, y, "ENEMY LOCKDOWN  (Hub Breach)", (92, 225, 255),
         "no cracks: a waterline of ENCRYPTED BITS fills the hub when Hub Breach lands and drains down in time with the lockdown timer; the passive is off "
         "while any water remains (lockdown.gif)")
    stages = [(1.0, "lands: full, 1 turn"), (0.66, "enemy turn: draining"), (0.33, "draining"), (0.05, "last bits"), (0.0, "empty: hub back online")]
    for i, (lv, txt) in enumerate(stages):
        f = L.lockdown(MAN, lv, t=i * 0.2, size=250)
        im.alpha_composite(f, (40 + i * 290, y + 50))
        d.text((60 + i * 290, y + 306), "level %.2f" % lv, font=f_ui(16, b"Bold SemiCondensed"), fill=(150, 230, 255))
        d.text((60 + i * 290, y + 326), txt, font=f_mono(11, False), fill=(175, 175, 190))
    sx = 40 + 5 * 290 + 10
    s2 = [L.lockdown(dict(MAN, name="PRIORITY ROUTING"), lv, t=0.3, size=200, turns=2) for lv in (1.0, 0.5)]
    for k, f in enumerate(s2):
        im.alpha_composite(f, (sx + k * 210, y + 70))
    d.text((sx, y + 280), "Short Circuit: 2 turns (2 -> 1)", font=f_mono(11, False), fill=(175, 175, 190))
    w60 = H.wheel(MANIFEST, None, MAN, r_px=60, ring=False)
    # small-wheel version: overlay the lockdown at the wheel centre size
    # (rendered via a closeup scaled to the hub)
    # defeat
    y2 = y + 370
    head(d, 40, y2, "PLAYER DEFEAT v2", (200, 200, 215), "bits fall and simply vanish when they reach the bottom of the core circle; no drain line (player_defeat_v2.gif)")
    for i, p in enumerate((0.0, 0.25, 0.45, 0.65, 0.85, 1.0)):
        f = X.defeat(BREAKER, p, size=250, ring_segs=RINGS["breaker"])
        im.alpha_composite(f, (40 + i * 280, y2 + 46))
        d.text((140 + i * 280, y2 + 296), "p = %.2f" % p, font=f_mono(12, False), fill=(175, 175, 190))
    out = bloom(im.convert("RGB"), 1, 0.25, 0.66).crop((0, 0, W, y2 + 320))
    out.save(os.path.join(OUT, "hub_cores_v3.png"))
    print("saved hub_cores_v3.png", out.size, flush=True)
    save_gif([L.lockdown(MAN, max(0.0, 1 - k / 26), t=k / 32 * 2, size=260) for k in range(32)], "lockdown.gif", 80)
    save_gif([X.defeat(BREAKER, min(1.0, k / 26), size=280, ring_segs=RINGS["breaker"]) for k in range(32)], "player_defeat_v2.gif", 70)
    save_gif([X.phantom(hub, k / 16, size=240, ring_segs=RINGS["ghost"]) for k in range(16)], "phantom_echo_v2.gif", 60)


def ring():
    W = 2400
    im, d = new_sheet(W, 1100, "INNER RING v3  (sub-needle + hangar)",
                      "Inner-ring textures and their extension into the slice are locked. Proposals (not in game): the sub-needle now uses the real pointer shape; "
                      "the hangar segment shown passive with TWO drones docked on its slice.")
    head(d, 40, 120, "SUB-NEEDLE  (Accelerator proposal)", (255, 214, 64), "proposal (not in game)")
    w = R.wheel(PS, ["SEG_x2", "SEG_sub_needle", "SEG_echo"], BREAKER, r_px=300, active=1, ext_slices=[(120, 1.0)], post=L.sub_needle_post(120))
    im.alpha_composite(w, (30, 160))
    w60 = R.wheel(PS, ["SEG_x2", "SEG_sub_needle", "SEG_echo"], BREAKER, r_px=60, active=1, ext_slices=[(120, 1.0)], post=L.sub_needle_post(120))
    im.alpha_composite(w60, (30 + w.width, 200))
    im.alpha_composite(grey(w60), (30 + w.width, 220 + w60.height))
    d.text((30 + w.width, 180), "r = 60 / grey", font=f_mono(11, False), fill=(175, 175, 190))
    cap(d, 40, 170 + w.height, "The sub-needle is the main pointer's cream blade with its ink outline, at 60 % size, rooted on the ring's outer lip and pointing out. "
        "It turns with the inner ring; the slice it points at also triggers (TRIGGERS tag).", 90)
    hx = 30 + w.width + w60.width + 60
    head(d, hx, 120, "HANGAR, TWO DRONES DOCKED", (176, 140, 255), "proposal (not in game)")
    w2 = R.wheel(PS, ["SEG_hangar", "SEG_x2", "SEG_echo"], BREAKER, r_px=300, post=L.hangar_post(0, 2))
    im.alpha_composite(w2, (hx, 160))
    w2s = R.wheel(PS, ["SEG_hangar", "SEG_x2", "SEG_echo"], BREAKER, r_px=60, post=L.hangar_post(0, 2))
    im.alpha_composite(w2s, (hx + w2.width, 200))
    im.alpha_composite(grey(w2s), (hx + w2.width, 220 + w2s.height))
    cap(d, hx, 170 + w2.height, "Two drone pods dock side by side on the slice's rim (clamps on the bezel, each pod with its own 3-pip HP). "
        "It stays readable: the pods sit above the value block, outside the screen. Three would crowd a 60-degree slice; "
        "beyond two, show '+n' on the second pod. OPEN QUESTION (designer): how is damage dealt with several drones on one slice? "
        "Each drone hits for its own value? They split the slice value? The slice fires once per drone?", 90, (255, 214, 120))
    out = bloom(im.convert("RGB"), 1, 0.25, 0.66).crop((0, 0, W, 170 + max(w.height, w2.height) + 120))
    out.save(os.path.join(OUT, "inner_ring_v3.png"))
    print("saved inner_ring_v3.png", out.size, flush=True)


def stacks():
    W = 2200
    im, d = new_sheet(W, 1000, "STATUS STACKS  (count indicator)",
                      "Status stacking is planned (not in game). Three indicator styles on the locked status badges; a stack count of 1 shows nothing extra. "
                      "Recommended: B (xN tab), it scales past 3 and reads at 16 px.")
    from glyph_catalog import STATUSES
    sts = [s for s in STATUSES if s[4] != "predicted" and s[0] != "ST_CLEANSE"]
    styles = [("A  PIPS", "pips", "one dot per stack under the badge; clean up to 3, ambiguous beyond"),
              ("B  xN TAB  (recommended)", "count", "a small ink tab with xN on the badge's top-right corner"),
              ("C  STACKED + TAB", "ghost", "fainter copies of the badge stacked behind, plus the xN tab")]
    y = 120
    for si, (title, st, txt) in enumerate(styles):
        d.text((40, y), title, font=f_num(26), fill=(255, 214, 64) if st == "count" else (220, 220, 230))
        d.text((40, y + 32), txt, font=f_mono(11, False), fill=(175, 175, 190))
        x = 40
        for it in sts:
            for n in (1, 2, 3, 5):
                b = L.stack_badge(it[0], 56, it[3], it[4], n, st)
                im.alpha_composite(b, (x, y + 50))
                x += b.width - 6
            x += 30
        sm = L.stack_badge(sts[0][0], 16, sts[0][3], sts[0][4], 3, st)
        sm2 = L.stack_badge(sts[0][0], 24, sts[0][3], sts[0][4], 3, st)
        im.alpha_composite(sm2, (x + 10, y + 70))
        im.alpha_composite(sm, (x + 60, y + 76))
        d.text((x + 10, y + 120), "24 / 16 px", font=f_mono(10, False), fill=(150, 150, 165))
        y += 170
    head(d, 40, y, "ON THE SLICE OVERLAYS  (style B)", (255, 214, 64), "the tab rides the overlay's corner badge; the value block is untouched")
    O.STACK_STYLE = "count"
    tiles = []
    for (st, prog, val, n) in (("CORRUPTED", "EXPLOIT", 6, 2), ("PARASITE", "PATCH", 3, 3), ("OVERCLOCKED", "ZERO-DAY", 12, 2), ("ENCRYPTED", "FIREWALL", 5, 3)):
        O.STACK.clear()
        O.STACK[st] = n
        tiles.append((st, n, K.tile(prog, val, t=0.3, tier=2, state=st, scale=0.62, seed=4)))
    O.STACK.clear()
    x = 40
    for st, n, t in tiles:
        im.alpha_composite(t, (x, y + 44))
        d.text((x + 20, y + 44 + t.height), "%s x%d" % (st, n), font=f_ui(16, b"Bold SemiCondensed"), fill=O.STATE_INFO[st][2])
        x += t.width + 10
    O.STACK["CORRUPTED"] = 3
    w = K.wheel([("EXPLOIT", 6, 2, "CORRUPTED"), ("FIREWALL", 5, 2, None), ("PROXY", 4, 2, None), ("VIRUS", 3, 2, None), ("ZERO-DAY", 12, 2, None), ("PATCH", 3, 2, None)], r_px=90)
    O.STACK.clear()
    im.alpha_composite(w, (x + 20, y + 60))
    d.text((x + 20, y + 60 + w.height), "r = 90: the tab is too small here; small wheels show the count in the forecast chip", font=f_mono(11, False), fill=(175, 175, 190))
    out = bloom(im.convert("RGB"), 1, 0.25, 0.66).crop((0, 0, W, max(y + 44 + tiles[0][2].height + 40, y + 80 + w.height + 20)))
    out.save(os.path.join(OUT, "status_stacks.png"))
    print("saved status_stacks.png", out.size, flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("hubs", "all"):
        hubs()
    if what in ("ring", "all"):
        ring()
    if what in ("stacks", "all"):
        stacks()
