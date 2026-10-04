"""Round 39 -> hub_cores_v2.png, phantom_echo.gif, player_core_defeat.gif, inner_ring_v2.png,
inner_ring_proposals.png (all in ..)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
CACHE = os.path.join(OUT, "scratch", "c")

import math
from PIL import Image, ImageDraw, ImageOps
import slicelib as SL
import hubkit as H
import hub39 as X
import ring2 as R
import glyphs39 as G39
import glyph_catalog as C
import make_glyphs as MG
from make_hubs import CLASS, CORE_NAME, RINGS, ENEMY, glyph_strip, grey, new_sheet, head, MANIFEST
from slicelib import f_num, f_ui, f_mono, bloom

PS = [("EXPLOIT", 6, 2, None), ("ZERO-DAY", 12, 3, None), ("FIREWALL", 5, 2, None), ("PROXY", 4, 1, None), ("VIRUS", 3, 2, None), ("PATCH", 3, 2, None)]
PINK = (255, 61, 168)
BREAKER = dict(acc=PINK, emblem="CORE_breaker_core", name="BREAKER CORE", sub="+1 SPIN // PERFECT x2")
MAN = dict(acc=(255, 140, 26), emblem="HUB_priority_routing", name="PRIORITY ROUTING", sub="+4 SHIELD / TURN", enemy=True)
CHANGED = ["breaker_core", "wrecker_core", "phantom_core", "rig_core", "overclock_core"]
NOTE = {"breaker_core": "crowbar strikes an empty glass pane; cracks spread from the hit",
        "wrecker_core": "speed lines dropped (they meant 'swing' but read as noise)",
        "phantom_core": "mask kept; the masks behind become a moving echo trail",
        "rig_core": "a firmware chip dropping into its socket (no power cord)",
        "overclock_core": "RPM gauge, needle buried in the red zone"}


def nearest(gid):
    ids = C.all_ids() + ["CORE_" + c[1] for c in CLASS] + ["HUB_" + e[1] for e in ENEMY] + \
        ["SEG_x2", "SEG_pierce", "SEG_corrupt", "SEG_anchor", "SEG_accelerator", "SEG_echo", "SEG_blank"]
    return C.nearest(C.cov(SL.glyph_mask(gid)), ids, exclude={gid})


# ------------------------------------------------------------------ hub cores v2
def hubs():
    W = 2400
    im, d = new_sheet(W, 2100, "HUB CORES v2  +  BREACH TIMER  +  PLAYER DEFEAT",
                      "Ghost, Swarm, Hive cores and all enemy hubs approved (round 38). Redone: Breaker, Wrecker, Phantom, Rigger, Overclocker. "
                      "BREACHED is an enemy-only 1-turn state; the player gets a DEFEAT state for the combat-loss screen.")
    head(d, 40, 120, "REDONE CORES  (round 38 -> round 39, base and Mk2)", (255, 214, 64))
    y = 166
    for i, cid in enumerate(CHANGED):
        cls = [c for c in CLASS if c[1] == cid][0]
        x = 40 + i * 470
        G39.BYPASS.add("CORE_" + cid)
        SL._glyph_cache.clear()
        old = H.hub_closeup(dict(acc=cls[2], emblem="CORE_" + cid, name=CORE_NAME[cid].upper(), sub=cls[4]), ring_segs=RINGS[cls[3]], size=170)
        G39.BYPASS.discard("CORE_" + cid)
        SL._glyph_cache.clear()
        im.alpha_composite(old, (x, y + 40))
        d.text((x + 50, y + 214), "round 38", font=f_mono(11, False), fill=(200, 140, 140))
        d.text((x + 176, y + 110), "->", font=f_num(30), fill=(200, 200, 210))
        hub = dict(acc=cls[2], emblem="CORE_" + cid, name=CORE_NAME[cid].upper(), sub=cls[4])
        new = X.phantom(hub, 0.35, size=250, ring_segs=RINGS[cls[3]]) if cid == "phantom_core" else H.hub_closeup(hub, ring_segs=RINGS[cls[3]], size=250)
        im.alpha_composite(new, (x + 210, y))
        hub2 = dict(hub, name=hub["name"] + " MK2", sub=cls[5], mk2=True)
        mk2 = X.phantom(hub2, 0.6, size=150, ring_segs=RINGS[cls[3]]) if cid == "phantom_core" else H.hub_closeup(hub2, ring_segs=RINGS[cls[3]], size=150)
        im.alpha_composite(mk2, (x + 260, y + 250))
        d.text((x, y), cls[0].upper(), font=f_ui(20, b"Bold SemiCondensed"), fill=cls[2])
        d.text((x, y + 410), NOTE[cid], font=f_mono(11, False), fill=(185, 185, 198))
        glyph_strip(im, d, x, y + 250, "CORE_" + cid if cid != "phantom_core" else "CORE_phantom_echo", cls[2])
        sc, tw = nearest("CORE_" + cid)
        d.text((x, y + 324), "16 px twin %.2f (%s)" % (sc, tw.replace("PI_", "").replace("ST_", "")[:16]), font=f_mono(11, False),
               fill=(150, 225, 150) if sc < 0.62 else (255, 214, 120))
        if cid == "phantom_core":
            d.text((x, y + 342), "icon form (static): mask + 2 echo outlines", font=f_mono(10, False), fill=(160, 160, 175))
    # approved row
    y2 = y + 450
    head(d, 40, y2, "APPROVED (unchanged)", (150, 225, 150), "Ghost, Swarm, Hive + the 6 enemy hubs")
    approved = [c for c in CLASS if c[1] in ("ghost_core", "swarm_core", "hive_core")]
    x = 40
    for cls in approved:
        h = H.hub_closeup(dict(acc=cls[2], emblem="CORE_" + cls[1], name=CORE_NAME[cls[1]].upper(), sub=cls[4]), ring_segs=RINGS[cls[3]], size=150)
        im.alpha_composite(h, (x, y2 + 44))
        x += 160
    for e in ENEMY:
        h = H.hub_closeup(dict(acc=e[4], emblem="HUB_" + e[1], name=e[0].upper(), sub=e[5], enemy=True), size=150)
        im.alpha_composite(h, (x, y2 + 44))
        x += 160
    # breach timer
    y3 = y2 + 220
    head(d, 40, y3, "ENEMY HUB BREACHED: A 1-TURN TIMER STATE", (255, 59, 48),
         "Hub Breach disables the target Hub's passive for 1 turn (Short Circuit: 2). A red timer ring drains over the enemy's turn, then the hub reboots.")
    stages = [("ONLINE", 0.3, 1.0, "passive on: +4 shield / turn"), ("BREACHED", 0.3, 1.0, "Hub Breach lands: timer full (1)"),
              ("BREACHED", 0.5, 0.45, "enemy turn: timer draining"), ("TIMER OUT", 0.7, 0.0, "end of turn: timer empty (0)"),
              ("REBOOT", 0.5, 0.0, "scan wipe: passive back on")]
    for i, (st, tt, left, cap) in enumerate(stages):
        x = 40 + i * 300
        f = X.breach_stage(MAN, st, t=tt, left=left, size=250)
        im.alpha_composite(f, (x, y3 + 50))
        d.text((x + 10, y3 + 306), "%d  %s" % (i + 1, st), font=f_ui(17, b"Bold SemiCondensed"), fill=(255, 150, 140) if "BREACH" in st or "TIMER" in st else (220, 220, 230))
        d.text((x + 10, y3 + 328), cap, font=f_mono(11, False), fill=(175, 175, 190))
        if i < 4:
            d.text((x + 258, y3 + 160), ">", font=f_num(34), fill=(200, 200, 210))
    sx = 40 + 5 * 300 + 20
    w_br = H.wheel(MANIFEST, None, dict(MAN, breached=True), r_px=60, ring=False)
    im.alpha_composite(w_br, (sx, y3 + 60))
    im.alpha_composite(grey(w_br), (sx + w_br.width + 10, y3 + 60))
    d.text((sx, y3 + 64 + w_br.height), "r = 60 breached: HARM ring; grey", font=f_mono(11, False), fill=(175, 175, 190))
    # player defeat
    y4 = y3 + 370
    head(d, 40, y4, "PLAYER DEFEAT: THE CORE TURNS TO BITS AND DRAINS", (200, 200, 215),
         "combat-loss screen (player_core_defeat.gif): bottom rows go first, bits fall into a slot at the bottom of the disc, the ring goes dark, FLATLINED")
    for i, p in enumerate((0.0, 0.3, 0.55, 0.8, 1.0)):
        x = 40 + i * 300
        f = X.defeat(BREAKER, p, size=260, ring_segs=RINGS["breaker"])
        im.alpha_composite(f, (x, y4 + 46))
        d.text((x + 100, y4 + 310), "p = %.2f" % p, font=f_mono(12, False), fill=(175, 175, 190))
    g = grey(X.defeat(BREAKER, 0.55, size=200, ring_segs=RINGS["breaker"]))
    im.alpha_composite(g, (40 + 5 * 300 + 20, y4 + 70))
    d.text((40 + 5 * 300 + 40, y4 + 274), "greyscale", font=f_mono(11, False), fill=(175, 175, 190))
    out = bloom(im.convert("RGB"), 1, 0.25, 0.66).crop((0, 0, W, y4 + 340))
    out.save(os.path.join(OUT, "hub_cores_v2.png"))
    print("saved hub_cores_v2.png", out.size, flush=True)
    # gifs
    cls = [c for c in CLASS if c[1] == "phantom_core"][0]
    ph = dict(acc=cls[2], emblem="CORE_phantom_core", name="PHANTOM CORE", sub=cls[4])
    save_gif([X.phantom(ph, k / 16, size=260, ring_segs=RINGS["ghost"]) for k in range(16)], "phantom_echo.gif", 60)
    fr = [X.defeat(BREAKER, min(1.0, k / 26), size=280, ring_segs=RINGS["breaker"]) for k in range(32)]
    save_gif(fr, "player_core_defeat.gif", 70)


def save_gif(frames, name, ms):
    rgb = []
    for f in frames:
        bg = Image.new("RGBA", f.size, (11, 10, 16, 255))
        bg.alpha_composite(f)
        rgb.append(bg.convert("RGB"))
    pal = rgb[len(rgb) // 2].quantize(colors=255, method=Image.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.FLOYDSTEINBERG) for f in rgb]
    q[0].save(os.path.join(OUT, name), save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=True)
    print("saved", name, os.path.getsize(os.path.join(OUT, name)) // 1024, "KB", flush=True)


# ------------------------------------------------------------------ inner ring v2
SEGS = [("SEG_x2", "x2", "doubled hairline pairs; the slice gets the same pairs rising"),
        ("SEG_pierce", "PIERCE", "chevrons stream outward, straight through the slice"),
        ("SEG_corrupt", "CORRUPT", "pink/green dead blocks climb into the slice"),
        ("SEG_anchor", "ANCHOR", "chain links; the chain reaches up into the slice"),
        ("SEG_accelerator", "ACCELERATOR", "tangential speed streaks running round"),
        ("SEG_echo", "ECHO", "ripples travel outward through the slice"),
        ("SEG_blank", "BLANK", "brushed steel; no extension")]


def ring_v2():
    W = 2400
    im, d = new_sheet(W, 1800, "INNER RING v2  (substantial ring + segment textures)",
                      "A machined ring: outer and inner lips with accent hairlines, a recessed gunmetal band, grooves with bolts between segments, a glass sheen. "
                      "Each segment has a full texture (+ its glyph on a plate); the segment under the pointer EXTENDS its texture into the slice it modifies.")
    head(d, 40, 120, "BEFORE / AFTER  (Breaker ring x2 / Pierce / -, r = 220)", (255, 214, 64))
    old = H.wheel(PS, RINGS["breaker"], BREAKER, r_px=220)
    new = R.wheel(PS, ["SEG_x2", "SEG_pierce", "SEG_blank"], BREAKER, r_px=220)
    im.alpha_composite(old, (30, 160))
    im.alpha_composite(new, (30 + old.width, 160))
    d.text((60, 160 + old.height - 8), "round 38: flat band, glyphs only", font=f_mono(12, False), fill=(200, 140, 140))
    d.text((60 + old.width, 160 + old.height - 8), "round 39: machined ring, textures, x2 extends into the 6", font=f_mono(12, False), fill=(150, 225, 150))
    # close-up crop of the ring
    big = R.wheel(PS, ["SEG_x2", "SEG_pierce", "SEG_blank"], BREAKER, r_px=520)
    cw_ = big.width
    crop = big.crop((int(cw_ * 0.22), int(cw_ * 0.12), int(cw_ * 0.78), int(cw_ * 0.62)))
    im.alpha_composite(crop, (60 + 2 * old.width, 150))
    d.text((70 + 2 * old.width, 150 + crop.height + 2), "close-up x2.4: lips, grooves + bolts, texture + glyph plate, extension", font=f_mono(12, False), fill=(175, 175, 190))
    sx = 80 + 2 * old.width + crop.width
    w60 = R.wheel(PS, ["SEG_x2", "SEG_pierce", "SEG_blank"], BREAKER, r_px=60)
    im.alpha_composite(w60, (sx, 170))
    im.alpha_composite(grey(w60), (sx, 180 + w60.height))
    im.alpha_composite(grey(new).resize((new.width // 2, new.height // 2), Image.LANCZOS), (sx, 200 + 2 * w60.height))
    d.text((sx, 160), "r = 60 / grey", font=f_mono(12, False), fill=(175, 175, 190))
    y = max(160 + old.height + 20, 150 + crop.height + 30)
    head(d, 40, y, "EVERY SEGMENT UNDER THE POINTER  (texture + extension into the slice it modifies)", (255, 214, 64))
    for i, (sg, nm, cap) in enumerate(SEGS):
        x = 30 + i * 335
        w = R.wheel(PS, [sg, "SEG_pierce" if sg != "SEG_pierce" else "SEG_x2", "SEG_echo" if sg != "SEG_echo" else "SEG_x2"], BREAKER, r_px=158, t=0.3)
        im.alpha_composite(w, (x, y + 44))
        d.text((x + 16, y + 44 + w.height - 4), nm, font=f_ui(18, b"Bold SemiCondensed"), fill=R.SEG_COL[sg])
        import textwrap
        for k, ln in enumerate(textwrap.wrap(cap, 40)):
            d.text((x + 16, y + 66 + w.height + k * 15), ln, font=f_mono(11, False), fill=(175, 175, 190))
    out = bloom(im.convert("RGB"), 1, 0.25, 0.66).crop((0, 0, W, y + 44 + w.height + 70))
    out.save(os.path.join(OUT, "inner_ring_v2.png"))
    print("saved inner_ring_v2.png", out.size, flush=True)


# ------------------------------------------------------------------ proposals
def _needle_post(angle):
    def post(img, c, ss, g):
        d = ImageDraw.Draw(img)
        a = math.radians(angle)
        base_r, tip_r = R.R1 - 4, R.R1 + 70
        bx, by = c[0] + base_r * ss * math.sin(a), c[1] - base_r * ss * math.cos(a)
        tx, ty = c[0] + tip_r * ss * math.sin(a), c[1] - tip_r * ss * math.cos(a)
        nx, ny = math.cos(a), math.sin(a)
        w = 8 * ss
        d.polygon([(bx + nx * w, by + ny * w), (bx - nx * w, by - ny * w), (tx, ty)], fill=(255, 190, 90, 255), outline=H.INK + (255,))
        d.line([(bx + nx * w, by + ny * w), (tx, ty), (bx - nx * w, by - ny * w)], fill=H.INK + (255,), width=int(2.5 * ss))
        d.ellipse([bx - 9 * ss, by - 9 * ss, bx + 9 * ss, by + 9 * ss], fill=(255, 190, 90, 255), outline=H.INK + (255,), width=int(2.5 * ss))
        # the slice it points at: bracket + TRIGGERS tag
        rr = (R.R1 + 245) * ss
        tx2, ty2 = c[0] + rr * math.sin(a), c[1] - rr * math.cos(a)
        f = f_ui(int(15 * ss), b"Bold SemiCondensed")
        s = "TRIGGERS"
        w2 = f.getlength(s) + 10 * ss
        d.rounded_rectangle([tx2 - w2 / 2, ty2 - 12 * ss, tx2 + w2 / 2, ty2 + 12 * ss], radius=4 * ss, fill=(255, 190, 90, 255), outline=H.INK + (255,), width=int(2 * ss))
        d.text((tx2 - f.getlength(s) / 2, ty2 - 10 * ss), s, font=f, fill=H.INK + (255,))
    return post


def _glyph_post(gid, angle, rr, size, tag=None, tagcol=(176, 140, 255)):
    def post(img, c, ss, g):
        a = math.radians(angle)
        x, y = c[0] + rr * ss * math.sin(a), c[1] - rr * ss * math.cos(a)
        gl = SL.glyph_rgba(gid, int(size * ss), max(2, size * ss * 0.08))
        img.alpha_composite(gl, (int(x - gl.width / 2), int(y - gl.height / 2)))
        if tag:
            d = ImageDraw.Draw(img)
            f = f_ui(int(13 * ss), b"Bold SemiCondensed")
            w2 = f.getlength(tag) + 10 * ss
            x = c[0] + 160 * ss * math.sin(a)  # the tag sits at the slice's inner edge, clear of the value
            ty = c[1] - 172 * ss * math.cos(a)
            d.rounded_rectangle([x - w2 / 2, ty, x + w2 / 2, ty + 20 * ss], radius=4 * ss, fill=tagcol + (255,), outline=H.INK + (255,), width=int(2 * ss))
            d.text((x - f.getlength(tag) / 2, ty + 1 * ss), tag, font=f, fill=H.INK + (255,))
    return post


def _multi(*posts):
    def post(img, c, ss, g):
        for p in posts:
            p(img, c, ss, g)
    return post


def proposals():
    W = 2400
    im, d = new_sheet(W, 1500, "INNER RING PROPOSALS  (concept only: rules are a designer to-do)",
                      "Every item here is a proposal (not in game). Same machined ring + textures as inner_ring_v2. Captions say what the art would mean; numbers are placeholders.")
    items = [
        ("ACCELERATOR -> SUB-NEEDLE", ["SEG_x2", "SEG_sub_needle", "SEG_echo"], dict(active=1, ext_slices=[(120, 1.0)], post=_needle_post(120)),
         ["A mini second needle rides the segment and", "points outward; whatever outer slice it points", "at ALSO triggers. It turns with the inner ring."]),
        ("HANGAR (drone)", ["SEG_hangar", "SEG_x2", "SEG_echo"], dict(post=_glyph_post("DRONE", 16, 330, 32, "DOCK +1", (176, 140, 255))),
         ["Drone-focused: when aligned, dock a drone on", "the slice it modifies (bay rails + dock", "lights; the drone lands at the slice rim)."]),
        ("DOUBLE STATUS (Corrupt rework)", ["SEG_double_status", "SEG_x2", "SEG_echo"], dict(post=_glyph_post("ST_CORRUPTED", 16, 330, 30, "STATUS x2", (200, 90, 255))),
         ["Status-themed: statuses this slice applies", "land twice (or stack 2). Paired diamonds;", "replaces / generalises CORRUPT."]),
        ("SPLASH (adjacent AOE)", ["SEG_splash", "SEG_x2", "SEG_echo"], dict(ext_slices=[(0, 1.0), (60, 0.7), (300, 0.7)]),
         ["AOE adjacent: the slice's effect also hits", "the neighbouring slices / adjacent enemies;", "bursts spread sideways into 3 slices."]),
        ("BROADCAST (global AOE)", ["SEG_broadcast", "SEG_x2", "SEG_echo"], dict(ext_slices=[(a, 0.45) for a in range(0, 360, 60)], post=_glyph_post("SEG_broadcast", 16, 330, 30, "ALL ENEMIES", (123, 224, 123))),
         ["AOE global: the slice hits every enemy.", "Waves leave the ring into all six slices;", "probably a rare, late segment."]),
        ("BLANK START", ["SEG_blank", "SEG_blank", "SEG_x2"], dict(ext=False),
         ["Operatives start with 1-2 BLANK segments", "(brushed steel, no extension) and earn real", "segments as they rank up."]),
    ]
    for i, (title, segs, kw, cap) in enumerate(items):
        x = 40 + (i % 3) * 790
        y = 120 + (i // 3) * 650
        w = R.wheel(PS, segs, BREAKER, r_px=230, t=0.3, **kw)
        im.alpha_composite(w, (x, y + 40))
        d.text((x, y), title, font=f_num(28), fill=(255, 214, 64))
        d.text((x + f_num(28).getlength(title) + 12, y + 10), "proposal (not in game)", font=f_mono(12, False), fill=(255, 150, 90))
        gx = x + w.width + 10
        glyph_strip(im, d, gx, y + 70, segs[kw.get("active", 0)], R.SEG_COL[segs[kw.get("active", 0)]])
        sc, tw = nearest(segs[kw.get("active", 0)])
        d.text((gx, y + 150), "16 px twin %.2f" % sc, font=f_mono(11, False), fill=(150, 225, 150) if sc < 0.62 else (255, 214, 120))
        d.text((gx, y + 166), tw.replace("PI_", "").replace("ST_", "")[:18], font=f_mono(10, False), fill=(160, 160, 175))
        import textwrap
        for k, ln in enumerate(textwrap.wrap(" ".join(cap), 33)):
            d.text((gx, y + 200 + k * 17), ln, font=f_mono(12, False), fill=(195, 195, 205))
    out = bloom(im.convert("RGB"), 1, 0.25, 0.66).crop((0, 0, W, 120 + 2 * 650))
    out.save(os.path.join(OUT, "inner_ring_proposals.png"))
    print("saved inner_ring_proposals.png", out.size, flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("hubs", "all"):
        hubs()
    if what in ("ring", "all"):
        ring_v2()
    if what in ("prop", "all"):
        proposals()
