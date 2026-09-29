"""01 - a fight (NEON INK).
blender -b --factory-startup --python still_01_combat.py -- <out.png>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ni_lib import *
from ni_parts import *
from ni_city_scene import *


def forecast_tag(pl, x, y, w, title, sub, accent, hand, spill=None):
    fill_poly(pl, "panel", rect(x, y, w, 58), "#050D1C", 0.92)
    if spill:  # the wheel below lights the tag's lower edge (feedback 10)
        for i in range(6):
            fill_poly(pl, "panel", rect(x, y + 58 - (i + 1) * 5, w, 5), spill, 0.05 * (6 - i))
    ink(pl, "panel", rect(x, y, w, 58), "cyan", 1.3, 0.8, hand, 0.4, closed=True)
    fill_poly(pl, "panel", rect(x, y, 6, 58), accent, 1.0)
    pl.text(title, x + 18, y + 26, 18, "#F2F6FF", FONT_MONO)
    pl.text(sub, x + 18, y + 48, 15, "#AFC0D6", FONT_MONO)


def operative_polaroid(pl, x, y, hand, rot=-0.06):
    cx, cy = x + 90, y + 110
    T = lambda pts: rot_pts(pts, cx, cy, rot)
    fill_poly(pl, "shadow", T([(px + 8, py + 10) for px, py in rect(x, y, 180, 214)]), "#000000", 0.5)
    fill_poly(pl, "paper", T(rect(x, y, 180, 214)), "paper", 1)
    fill_poly(pl, "paper", T(rect(x + 12, y + 12, 156, 150)), "#1A1420", 1)
    # inked portrait: Breaker, heavy jacket, crowbar-antenna (original)
    hx, hy = x + 90, y + 80
    ink(pl, "art", T(ellipse(hx, hy, 30, 38, 30)), "pink", 3, 1, hand, .8, closed=True)
    ink(pl, "art", T([(hx - 26, hy - 10), (hx - 38, hy - 30), (hx - 20, hy - 42), (hx + 10, hy - 48), (hx + 34, hy - 30), (hx + 30, hy - 8)]), "pink", 3.4, 1, hand, 1.0, smooth=True)
    ink(pl, "art", T([(hx - 22, hy + 2), (hx + 24, hy + 2)]), "cyan", 5, 1, hand, .4)  # visor bar
    ink(pl, "art", T([(hx - 60, y + 162), (hx - 50, hy + 44), (hx - 20, hy + 36), (hx, hy + 50), (hx + 20, hy + 36), (hx + 52, hy + 44), (hx + 64, y + 162)]), "pink", 3.2, 1, hand, 1.0, smooth=True)
    ink(pl, "art", T([(hx + 30, hy - 40), (hx + 52, hy - 74)]), "acid", 2.4, 1, hand, .3)
    ink(pl, "art", T([(hx + 46, hy - 74), (hx + 58, hy - 70)]), "acid", 2.4, 1, hand, .3)
    ink(pl, "art", T(rect(x, y, 180, 214)), "ink", 1.6, 1, hand, .5, closed=True)
    # tape
    fill_poly(pl, "tape", T([(x + 60, y - 12), (x + 124, y - 8), (x + 122, y + 14), (x + 58, y + 10)]), "#E9E4D6", 0.8)
    tx, ty = T([(x + 18, y + 196)])[0]
    pl.text("BREAKER // 60/60", tx, ty, 17, "ink", FONT_PLEX, rot=-rot)


def enemy_holo(pl, cx, cy, hand):
    """Enemy bust as a projected hologram (violet corp hue, concentric civic rings)."""
    for i in range(3):
        ink(pl, "holo", ellipse(cx, cy + 120, 70 + 26 * i, 16 + 6 * i, 40), "halcyon", 1.2, 0.6 - 0.15 * i, hand, .3, closed=True)
    fill_poly(pl, "holo", [(cx - 70, cy + 120), (cx + 70, cy + 120), (cx + 110, cy - 110), (cx - 110, cy - 110)], "halcyon", 0.06)
    ink(pl, "holo", ellipse(cx, cy - 30, 38, 48, 30), "halcyon", 2.6, 1, hand, .8, closed=True)
    ink(pl, "holo", [(cx - 86, cy + 100), (cx - 70, cy + 40), (cx - 30, cy + 22), (cx, cy + 34), (cx + 30, cy + 22), (cx + 70, cy + 40), (cx + 86, cy + 100)],
        "halcyon", 2.6, 1, hand, .8, smooth=True)
    ink(pl, "holo", [(cx - 40, cy - 40), (cx + 40, cy - 40)], "#FFFFFF", 3.5, 0.9, hand, .3)  # eye slit
    ink(pl, "holo", [(cx - 30, cy - 80), (cx, cy - 96), (cx + 30, cy - 80)], "halcyon", 1.6, .8, hand, .3)
    for yy in range(int(cy - 110), int(cy + 120), 5):
        ink(pl, "holo", [(cx - 100, yy), (cx + 100, yy)], "halcyon", 0.6, 0.12, None, 0)


def main():
    sc = reset_scene(16)
    hand = Hand(2024)
    # ---- city backdrop: desaturated, blurred, dimmed (feedback 3)
    city, cplanes, pal = make_city(23, "desat", bands=[(420, 9.0), (99999, 6.0)], detail=0.55, u=30, ox=900, oy=420,
                                   hq=None, cables=True, prefix="bgcity", fade_far=False)
    for p in cplanes[1:]:
        p.opacity = 0.75
    scrim = Plane("scrim", ("s",), blur=0)
    fill_poly(scrim, "s", rect(-10, -10, W + 20, H + 20), "#02030A", 0.45)
    for i in range(8):  # vignette: the edges fall off, the wheels hold the centre
        fill_poly(scrim, "s", rect(-10, H - 60 - i * 26, W + 20, 30 + i * 26), "#02030A", 0.08)
    # ---- wheel planes
    back = Plane("wheel_back", ("shadow",), blur=16)
    spill = Plane("spill", ("spill",), blur=40, blend={"spill": "ADD"})
    wheels = Plane("wheels", ("body", "line", "slice", "glyph", "hub", "needle", "sheen"), blur=0)
    ui = Plane("ui", ("panel", "ink"), blur=0)
    fx = Plane("fx", ("fx",), blur=0)

    class Dual:  # spinner() writes shadow + spill to 'back'; route spill to the additive plane
        def __init__(s, a, b): s.a, s.b = a, b
        def add(s, layer, *args, **kw):
            (s.b if layer == "spill" else s.a).add(layer, *args, **kw)
    dual = Dual(back, spill)

    op_slices = [("atk", 5), ("def", 4), ("atk", 4), ("crit", 2), ("evd", 4), ("def", 5), ("atk", 3), ("miss", 3)]
    en_slices = [("afl", 5), ("atk", 6), ("def", 5), ("crit", 2), ("atk", 5), ("def", 4), ("miss", 3)]
    OP = (560, 500); EN = (1350, 480); R = 205
    op = spinner(dual, wheels, OP[0], OP[1], R, op_slices, "op", hand, needle=-0.35, hp=(60, 60), accent="pink", spin=0.2)
    en = spinner(dual, wheels, EN[0], EN[1], R, en_slices, "enemy", Hand(7), needle=2.5, hp=(26, 40), accent="halcyon", spin=-0.4)
    wheels.text("BREAKER", OP[0], OP[1] - 34, 20, "#F2F6FF", FONT_MONO, align="CENTER")
    wheels.text("CORE 3", OP[0], OP[1] - 12, 14, "#AFC0D6", FONT_MONO, align="CENTER")
    wheels.text("COLLECTIONS", EN[0], EN[1] - 34, 18, "#F2F6FF", FONT_MONO, align="CENTER")
    wheels.text("AGENT", EN[0], EN[1] - 14, 18, "#F2F6FF", FONT_MONO, align="CENTER")
    wheels.text("60/60", OP[0], OP[1] + 236, 30, "gain", FONT_ANTON, align="CENTER")
    wheels.text("26/40", EN[0], EN[1] + 236, 30, "amber", FONT_ANTON, align="CENTER")
    # pink cables: the operative's wheel is jacked into the deck (bottom-left)
    for i, (sx, sy, sag) in enumerate(((-40, 760, 60), (-40, 820, 90), (-40, 700, 40))):
        a = wproj(OP[0], OP[1], R * 1.0, math.pi * (0.78 + 0.05 * i), 16, 0.8)
        pts = [(sx + (a[0] - sx) * t, sy + (a[1] - sy) * t + sag * math.sin(t * math.pi)) for t in [j / 24 for j in range(25)]]
        neon_line(wheels, "body", pts, "pink", 3.0 - i * 0.6, hand, jit=0.6, core=i == 0)
        fill_poly(wheels, "line", ellipse(a[0], a[1], 9, 7, 12), "#1A1A22", 1)
        ink(wheels, "line", ellipse(a[0], a[1], 9, 7, 12), "pink", 2, 1, hand, .2, closed=True)
    # enemy hologram
    enemy_holo(fx, 1735, 250, Hand(9))
    # forecast tags (glass), lit from below by their wheels
    forecast_tag(ui, 330, 196, 360, "ATTACK // PERFECT AIM", "+14 DMG  -> COLLECTIONS AGENT", "pink", hand, spill="pink")
    forecast_tag(ui, 1150, 176, 380, "AFFLICT // GOOD AIM", "PUTS CORRUPTED ON YOU", "halcyon", hand, spill="halcyon")
    # top bar (glass), minimal
    fill_poly(ui, "panel", rect(0, 0, W, 50), "#040A16", 0.9)
    ink(ui, "panel", [(0, 50), (W, 50)], "cyan", 1.2, 0.7, hand, .3)
    for i, (lab, val, c) in enumerate((("HEAT", "34", "amber"), ("HP", "60/60", "gain"), ("CYCLES", "120", "#F2F6FF"),
                                      ("RAM", "3/5", "cyan"), ("TURN", "2", "#F2F6FF"))):
        x = 30 + i * 190
        ui.text(lab, x, 33, 15, "#7A889C", FONT_MONO)
        ui.text(val, x + 70, 34, 22, c, FONT_ANTON)
    ui.text("NET // ARENA 04 - COLLECTIONS", W - 30, 33, 15, "#AFC0D6", FONT_MONO, align="RIGHT")
    # ---- the hit: projectile, binary shards, damage number
    hit = wproj(EN[0], EN[1], R * 0.98, math.pi * 0.93, 30, 0.8)
    tip = op["tip"]
    ink(fx, "fx", [tip, ((tip[0] + hit[0]) / 2, min(tip[1], hit[1]) - 120), hit], "acid", 4, 1, hand, 0.4, smooth=True,
        w_profile=lambda t: 0.2 + 0.8 * t)
    binary_shards(fx, "fx", hit[0], hit[1], Hand(5), n=46, spread=(1.9, 4.5), speed=(40, 250), color="harm")
    fx.text("-14", hit[0] - 250, hit[1] + 170, 72, "harm", FONT_ANTON, align="CENTER")
    # ---- EXECUTE button (glass) with the washed digital word
    bx, by, bw, bh = 1480, 850, 390, 160
    fill_poly(ui, "panel", rect(bx, by, bw, bh), "#050D1C", 0.92)
    ink(ui, "panel", rect(bx, by, bw, bh), "cyan", 1.4, 0.5, hand, 0.4, closed=True)
    ui.text("EXECUTE", bx + bw / 2, by + 104, 64, "#2C5566", FONT_MONO, align="CENTER", spacing=1.1)
    for yy in range(by + 6, by + bh, 4):
        ink(ui, "ink", [(bx + 4, yy), (bx + bw - 4, yy)], "#050D1C", 1.4, 0.55, None, 0, taper=0)
    ui.text("[SPACE]", bx + bw - 14, by + bh - 12, 14, "#7A889C", FONT_MONO, align="RIGHT")
    # ---- stickers (no glow: they never light their neighbours)
    stick = Plane("stickers", ("shadow", "paper", "art", "tape", "fx"), glow=False)
    operative_polaroid(stick, 60, 150, hand)
    cards = [("JOLT", 1, "note_yellow", "spin", "Spin a wheel 3 ticks."), ("FINE TUNE", 1, "note_pink", "bolt", "+-1 nudge, one ring."),
             ("BRUTE SPIN", 2, "note_yellow", "fist", "Spin a wheel 6 ticks."), ("OVERCLOCK", 2, "pink", "bolt", "Double the next hit."),
             ("FIREWALL", 1, "cyan", "shield", "+6 block this turn.")]
    xs = [70, 262, 454, 686, 880]
    rots = [-0.06, 0.03, -0.02, 0.09, 0.05]
    for i, (t, c, colr, art, sub) in enumerate(cards):
        lift = 1.0 if i == 3 else 0.0
        sticker_card(stick, xs[i], 820 if not lift else 790, 172, 236, rots[i], t, c, colr, Hand(40 + i), art=art, lift=lift, sub=sub)
    slap_marks(stick, "fx", 686 - 30, 790 - 60, 172 * 1.22 + 20, 236 * 1.22, Hand(3), "white")
    stick.text("RAM 3/5", 70, 800, 16, "#AFC0D6", FONT_MONO)
    # ---- marker: SEND IT scrawled over EXECUTE, with drips
    mk = Plane("marker", ("ink",), glow=False)
    st, _ = marker_word_strokes("SEND IT", bx + 16, by + 112, 72, slant=0.2, hand=Hand(77))
    mh = Hand(78)
    for li, s in st:
        ink(mk, "ink", s, "pink", 16, 1, mh, 0.5, smooth=True, w_profile=marker_profile)
    for (dx, L) in ((34, 70), (150, 38), (262, 96), (330, 30)):
        drip(mk, "ink", bx + dx, by + 112, L, 8, "pink", hand=mh)
    # underline flick
    ink(mk, "ink", [(bx + 30, by + 140), (bx + 200, by + 146), (bx + 350, by + 136)], "pink", 7, 1, mh, 0.6, smooth=True, taper=0.1)
    planes = cplanes + [scrim, back, spill, ui, wheels, fx, stick, mk]
    render(sc, planes, out_path("01_combat.png"), bloom=(0.22, 0.75, 0.8))


main()
