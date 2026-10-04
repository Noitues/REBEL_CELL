"""Round 38 -> ../hub_cores.png, ../inner_ring.png, ../hub_breach.gif

Real names: content/hub_cores/*.tres, content/enemies/* (hub sub-resources), content/rings/*.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)

from PIL import Image, ImageDraw, ImageOps
import slicelib as SL
import hubkit as H
import glyph_catalog as C
import make_glyphs as MG
from slicelib import f_num, f_ui, f_mono, bloom

PINK = (255, 61, 168)
CLASS = [  # class, core id, accent (ART_BIBLE 7.1), base ring (content/rings), base / Mk2 passive (content)
    ("Breaker", "breaker_core", PINK, "breaker", "+1 SPIN // PERFECT x2", "+2 SPIN // PERFECT x2 +RAM"),
    ("Wrecker", "wrecker_core", (255, 122, 26), "breaker", "PERFECT +1.5x", "+1 SPIN // PERFECT +1.5x"),
    ("Ghost", "ghost_core", (159, 232, 255), "ghost", "1st NUDGE IGNORES RES", "2 NUDGES IGNORE RES"),
    ("Phantom", "phantom_core", (200, 182, 255), "ghost", "FREE NUDGE / TURN", "2 FREE NUDGES / TURN"),
    ("Rigger", "rig_core", (255, 210, 77), "rigger", "+1 MAX RAM", "+2 MAX RAM"),
    ("Overclocker", "overclock_core", (255, 79, 216), "rigger", "+2 MAX RAM", "+3 MAX RAM"),
    ("Botnet", "swarm_core", (123, 224, 123), "botnet", "3 DRONES, PERSIST", "4 DRONES, PERSIST"),
    ("Hivemind", "hive_core", (176, 77, 255), "botnet", "4 DRONES (FIGHT)", "5 DRONES (FIGHT)"),
]
CORE_NAME = {"breaker_core": "Breaker Core", "wrecker_core": "Wrecker Core", "ghost_core": "Ghost Core", "phantom_core": "Phantom Core",
             "rig_core": "Rig Core", "overclock_core": "Overclock Core", "swarm_core": "Swarm Core", "hive_core": "Hive Core"}
RINGS = {  # content/rings/*.tres
    "breaker": ["SEG_x2", "SEG_pierce", "SEG_blank"],
    "ghost": ["SEG_pierce", "SEG_x2", "SEG_echo"],
    "rigger": ["SEG_accelerator", "SEG_x2", "SEG_echo"],
    "botnet": ["SEG_echo", "SEG_corrupt", "SEG_x2"],
}
ENEMY = [  # hub name, enemy (content/enemies), corporation, accent, passive (content description)
    ("Compliance Lock", "compliance_lock", "Compliance Officer (elite)", "Solace", (61, 255, 139), "SPIN RESISTANCE 3"),
    ("Priority Routing", "priority_routing", "The Manifest (boss)", "Meridian", (255, 140, 26), "+4 SHIELD / TURN"),
    ("Emergency Powers", "emergency_powers", "The Civic Core (boss)", "Halcyon", (140, 123, 255), "HEAL 4 + BLOCK 4 / TURN"),
    ("Station Keeping", "station_keeping", "The Commons Array (boss)", "Orbital", (127, 168, 255), "REPAIR 3 + SHIELD 3 / TURN"),
    ("Auto-Renew", "auto_renew", "Renewal Engine (boss)", "Solace", (61, 255, 139), "HEAL 10 / TURN"),
    ("Root Access", "root_access", "DISPATCH (final boss)", "REBEL_CELL", (232, 20, 30), "REPAIR 4 + SHIELD 4 / TURN"),
]
SEGS = [("SEG_x2", "x2", "Outer slice output doubled."), ("SEG_pierce", "Pierce", "Ignore block and shield."),
        ("SEG_corrupt", "Corrupt", "Target's resolved slice becomes CORRUPTED."), ("SEG_anchor", "Anchor", "On Perfect: your wheel skips its next respin."),
        ("SEG_accelerator", "Accelerator", "Nudge cards next turn trigger twice."), ("SEG_echo", "Echo", "Outer slice triggers again at half output."),
        ("SEG_blank", "- (blank)", "No modifier.")]
PLAYER_SLICES = [("EXPLOIT", 6, 2, None), ("ZERO-DAY", 12, 3, None), ("FIREWALL", 5, 2, None), ("PROXY", 4, 1, None), ("VIRUS", 3, 2, None), ("PATCH", 3, 2, None)]
MANIFEST = [("EXPLOIT", 14, 2, None, "meridian"), ("FIREWALL", 12, 2, None, "meridian"), ("ZERO-DAY", 24, 2, None, "meridian"),
            ("EXPLOIT", 14, 2, None, "meridian"), ("NULL", None, 1, None, "meridian"), ("FIREWALL", 12, 2, None, "meridian")]


def grey(im):
    a = im.split()[3]
    g = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
    g.putalpha(a)
    return g


def new_sheet(W, H, title, sub):
    im = Image.new("RGBA", (W, H), (11, 10, 16, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        d.line([(0, y), (W, y)], fill=(14, 13, 20))
    d.text((40, 18), title, font=f_num(54), fill=(255, 255, 255))
    d.text((44, 82), sub, font=f_mono(14, False), fill=(190, 190, 200))
    return im, d


def head(d, x, y, t, c, sub=""):
    d.rectangle([x - 14, y + 4, x - 8, y + 30], fill=c)
    d.text((x, y), t, font=f_num(30), fill=c)
    if sub:
        d.text((x + f_num(30).getlength(t) + 16, y + 12), sub, font=f_mono(13, False), fill=(170, 170, 185))


def glyph_strip(im, d, x, y, gid, col):
    t = MG.tile(64, col)
    g = SL.glyph_rgba(gid, 50, 4)
    t.alpha_composite(g, ((64 - g.width) // 2, (64 - g.height) // 2))
    im.alpha_composite(t, (x, y))
    for k, px in enumerate((24, 16)):
        t = MG.tile(px + 6, col)
        g = SL.glyph_rgba(gid, px, max(1, px * 0.075))
        t.alpha_composite(g, ((t.width - g.width) // 2, (t.height - g.height) // 2))
        im.alpha_composite(t, (x + 70 + k * 34, y + 2))
        gg = grey(t)
        im.alpha_composite(gg, (x + 70 + k * 34, y + 34))


# ------------------------------------------------------------------ hub_cores.png
def hub_sheet():
    W, Hh = 2400, 2000
    im, d = new_sheet(W, Hh, "HUB CORES  +  BREACHED HUB",
                      "The locked D4 hub: a dark CRT disc in a machined rim, the core emblem, the core name and its passive. Player hubs sit inside the inner ring; "
                      "enemy hubs fill the centre. Names and passives from content/hub_cores and content/enemies.")
    head(d, 40, 120, "CLASS CORES  (base / Mk2)", (255, 214, 64), "Mk2 = Rank 2 'Upgraded Hub Core': a second notched rim + MK2 tab; same emblem")
    x0, y0, cw = 40, 166, 292
    for i, (cls, cid, acc, ring, p1, p2) in enumerate(CLASS):
        x = x0 + i * cw
        for k, mk2 in enumerate((False, True)):
            hub = dict(acc=acc, emblem="CORE_" + cid, name=CORE_NAME[cid].upper() + (" MK2" if mk2 else ""), sub=p2 if mk2 else p1, mk2=mk2)
            h = H.hub_closeup(hub, ring_segs=RINGS[ring], size=272)
            im.alpha_composite(h, (x, y0 + k * 300))
        d.text((x + 6, y0 + 600), cls.upper(), font=f_ui(20, b"Bold SemiCondensed"), fill=acc)
        d.text((x + 6, y0 + 626), "%s / %s_mk2" % (cid, cid), font=f_mono(11, False), fill=(160, 160, 175))
        glyph_strip(im, d, x + 6, y0 + 648, "CORE_" + cid, acc)
    y1 = y0 + 740
    head(d, 40, y1, "ENEMY HUBS", (255, 214, 64), "no inner ring: the hub fills the centre; a slow corp-colour chevron sweep marks it hostile")
    for i, (nm, hid, enemy, corp, acc, passive) in enumerate(ENEMY):
        x = 40 + i * 392
        hub = dict(acc=acc, emblem="HUB_" + hid, name=nm.upper(), sub=passive, enemy=True)
        h = H.hub_closeup(hub, size=270)
        im.alpha_composite(h, (x, y1 + 46))
        d.text((x + 6, y1 + 320), nm, font=f_ui(19, b"Bold SemiCondensed"), fill=acc)
        d.text((x + 6, y1 + 346), enemy, font=f_mono(11, False), fill=(190, 190, 200))
        d.text((x + 6, y1 + 362), corp, font=f_mono(11, False), fill=(160, 160, 175))
        glyph_strip(im, d, x + 200, y1 + 320, "HUB_" + hid, acc)
    y2 = y1 + 420
    head(d, 40, y2, "BREACHED", (255, 59, 48), "Hub Breach (1 turn) / Short Circuit (2 turns) / Shatter: the glass cracks from the hit, static tears the screen, "
         "sparks spit from the cracks, the passive is struck out, a red BREACHED plate counts the turns")
    acc = (255, 140, 26)
    on = dict(acc=acc, emblem="HUB_priority_routing", name="PRIORITY ROUTING", sub="+4 SHIELD / TURN", enemy=True)
    br = dict(on, breached=True)
    wy = y2 + 50
    w_on = H.wheel(MANIFEST, None, on, r_px=220, ring=False)
    w_br = H.wheel(MANIFEST, None, br, r_px=220, ring=False)
    im.alpha_composite(w_on, (30, wy))
    im.alpha_composite(w_br, (30 + w_on.width, wy))
    d.text((60, wy + w_on.height - 10), "The Manifest r = 220, hub online", font=f_mono(12, False), fill=(170, 170, 182))
    d.text((60 + w_on.width, wy + w_on.height - 10), "hub BREACHED (shield-per-turn off)", font=f_mono(12, False), fill=(255, 150, 140))
    sx = 60 + 2 * w_on.width
    for k in range(3):
        f = H.hub_closeup(dict(br), t=k / 3, size=200)
        im.alpha_composite(f, (sx + k * 210, wy + 10))
    d.text((sx, wy + 216), "breach loop  t = 0 / 0.33 / 0.67  (hub_breach.gif)", font=f_mono(12, False), fill=(170, 170, 182))
    s60 = [H.wheel(MANIFEST, None, on, r_px=60, ring=False), H.wheel(MANIFEST, None, br, r_px=60, ring=False)]
    for k, w in enumerate(s60):
        im.alpha_composite(w, (sx + k * (w.width + 10), wy + 250))
        im.alpha_composite(grey(w), (sx + 2 * (w.width + 10) + 20 + k * (w.width + 10), wy + 250))
    d.text((sx, wy + 250 + s60[0].height), "r = 60 online / breached        greyscale", font=f_mono(12, False), fill=(170, 170, 182))
    gb = grey(w_br).resize((w_br.width // 2, w_br.height // 2), Image.LANCZOS)
    im.alpha_composite(gb, (sx + 640, wy + 10))
    d.text((sx + 650, wy + 10 + gb.height), "breached, greyscale", font=f_mono(12, False), fill=(170, 170, 182))
    out = bloom(im.convert("RGB"), 1, 0.25, 0.66)
    out = out.crop((0, 0, W, wy + w_on.height + 20))
    out.save(os.path.join(OUT, "hub_cores.png"))
    print("saved hub_cores.png", out.size, flush=True)
    frames = []
    for k in range(12):
        f = H.hub_closeup(dict(br), t=k / 12, size=240)
        bg = Image.new("RGBA", f.size, (11, 10, 16, 255))
        bg.alpha_composite(f)
        frames.append(bg.convert("RGB"))
    pal = frames[6].quantize(colors=255, method=Image.MEDIANCUT)
    q = [fr.quantize(palette=pal, dither=Image.FLOYDSTEINBERG) for fr in frames]
    q[0].save(os.path.join(OUT, "hub_breach.gif"), save_all=True, append_images=q[1:], duration=80, loop=0, optimize=True)


# ------------------------------------------------------------------ inner_ring.png
def ring_sheet():
    W = 2400
    im, d = new_sheet(W, 1500, "INNER RING SEGMENTS",
                      "Three 10-tick segments between the hub and the slices (GDD 2.1 / 6.4). The slice sets the action; the segment under the pointer sets a modifier. "
                      "Glyphs in the locked flat language; ANCHOR drawn for the first time.")
    head(d, 40, 120, "SEGMENT GLYPHS", (255, 214, 64), "content/rings/segments; 64 / 24 / 16 px + greyscale; nearest twin in the whole final set at 16 px")
    ids = C.all_ids() + [s[0] for s in SEGS] + ["CORE_" + c[1] for c in CLASS] + ["HUB_" + e[1] for e in ENEMY]
    for i, (gid, nm, desc) in enumerate(SEGS):
        x = 40 + i * 336
        y = 166
        glyph_strip(im, d, x, y + 40, gid, (150, 150, 170))
        d.text((x, y), nm.upper(), font=f_ui(20, b"Bold SemiCondensed"), fill=(255, 214, 64) if gid == "SEG_anchor" else (230, 230, 240))
        d.text((x, y + 22), desc[:44], font=f_mono(10, False), fill=(170, 170, 182))
        sc, tw = C.nearest(C.cov(SL.glyph_mask(gid)), ids, exclude={gid})
        d.text((x + 150, y + 50), "twin %.2f" % sc, font=f_ui(15, b"Bold SemiCondensed"), fill=(150, 225, 150) if sc < 0.62 else (255, 214, 120))
        d.text((x + 150, y + 70), tw.replace("PI_", "").replace("ST_", "")[:18], font=f_mono(10, False), fill=(165, 165, 180))
    head(d, 40, 290, "ON THE WHEEL", (255, 214, 64), "Breaker ring (x2 / Pierce / -), the segment under the pointer is lit; r = 220 and r = 60, colour + greyscale")
    breaker = dict(acc=PINK, emblem="CORE_breaker_core", name="BREAKER CORE", sub="+1 SPIN // PERFECT x2")
    w220 = H.wheel(PLAYER_SLICES, RINGS["breaker"], breaker, r_px=220)
    im.alpha_composite(w220, (30, 336))
    g220 = grey(w220)
    im.alpha_composite(g220, (30 + w220.width, 336))
    cx = 60 + 2 * w220.width
    ring_close = H.hub_closeup(breaker, ring_segs=RINGS["breaker"], size=360)
    im.alpha_composite(ring_close, (cx, 336))
    d.text((cx + 10, 336 + 362), "hub + ring close-up (x1.6)", font=f_mono(12, False), fill=(170, 170, 182))
    sx = cx + 380
    w60 = H.wheel(PLAYER_SLICES, RINGS["breaker"], breaker, r_px=60)
    im.alpha_composite(w60, (sx, 360))
    im.alpha_composite(grey(w60), (sx + w60.width + 10, 360))
    d.text((sx, 360 + w60.height), "r = 60 colour / grey: the ring", font=f_mono(12, False), fill=(170, 170, 182))
    d.text((sx, 376 + w60.height), "reads as 3 lit / unlit bands;", font=f_mono(12, False), fill=(170, 170, 182))
    d.text((sx, 392 + w60.height), "glyphs are decorative there", font=f_mono(12, False), fill=(170, 170, 182))
    y3 = 336 + w220.height + 10
    head(d, 40, y3, "EVERY RANK 1 RING + RANK 3 SWAP POOL", (255, 214, 64), "content/rings: Breaker, Ghost, Rigger, Botnet (alternates use their base class ring); Rank 3 swaps from x2, Pierce, Corrupt, Anchor, Accelerator, Echo")
    ringcls = [("BREAKER / WRECKER", "breaker", PINK, "CORE_breaker_core", "BREAKER CORE"),
               ("GHOST / PHANTOM", "ghost", (159, 232, 255), "CORE_ghost_core", "GHOST CORE"),
               ("RIGGER / OVERCLOCKER", "rigger", (255, 210, 77), "CORE_rig_core", "RIG CORE"),
               ("BOTNET / HIVEMIND", "botnet", (123, 224, 123), "CORE_swarm_core", "SWARM CORE")]
    for i, (lab, rk, acc, em, nm) in enumerate(ringcls):
        x = 40 + i * 420
        h = H.hub_closeup(dict(acc=acc, emblem=em, name=nm, sub=""), ring_segs=RINGS[rk], size=300)
        im.alpha_composite(h, (x, y3 + 44))
        d.text((x + 10, y3 + 346), lab, font=f_ui(17, b"Bold SemiCondensed"), fill=acc)
        d.text((x + 10, y3 + 368), " / ".join(s.replace("SEG_", "").replace("blank", "-") for s in RINGS[rk]), font=f_mono(12, False), fill=(170, 170, 182))
    xr = 40 + 4 * 420
    h = H.hub_closeup(dict(acc=PINK, emblem="CORE_breaker_core", name="BREAKER CORE", sub="RANK 3"), ring_segs=["SEG_anchor", "SEG_corrupt", "SEG_accelerator"], size=300)
    im.alpha_composite(h, (xr, y3 + 44))
    d.text((xr + 10, y3 + 346), "RANK 3 SWAP EXAMPLE", font=f_ui(17, b"Bold SemiCondensed"), fill=(255, 214, 64))
    d.text((xr + 10, y3 + 368), "anchor / corrupt / accelerator", font=f_mono(12, False), fill=(170, 170, 182))
    out = bloom(im.convert("RGB"), 1, 0.25, 0.66)
    out = out.crop((0, 0, W, y3 + 400))
    out.save(os.path.join(OUT, "inner_ring.png"))
    print("saved inner_ring.png", out.size, flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("hubs", "all"):
        hub_sheet()
    if what in ("ring", "all"):
        ring_sheet()
