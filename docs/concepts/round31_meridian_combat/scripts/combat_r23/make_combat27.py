"""Round 26 (closer framing, round 26 HQs): boss fights over each corp's HQ (the same model and street layout as on the city map) -> ../../combat_<corp>.png (1920 x 1080).

Base = the locked D4 combat screen (round 22/23: D4 player wheel, HUD, sticker cards, raid-style SEND IT sticker).
Changed per corp: the backdrop (../../scratch/backdrops/<corp>_boss_night.png from backdrop24.py, calmed behind the
wheels as in round 11), the boss wheel (round 18 D4 corp code, tier III, from wheels_r18/render_bosses24.py), the
status line, forecast tag and nameplate colours. Heat stays a backdrop-only effect (not shown: calm, Heat 0).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
R24 = os.path.normpath(os.path.join(HERE, "..", ".."))
WH = os.path.join(R24, "scratch", "wheels")
BD = os.path.join(R24, "scratch", "backdrops")

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import plates as P
import make_combat as MC
import fx_r22 as FX22
from slicelib import bloom, R_OUT

W, H = 1920, 1080
PLAYER, BOSS = MC.PLAYER, MC.BOSS
ACC = {"meridian": (255, 140, 26), "solace": (150, 255, 70), "halcyon": (176, 120, 255), "orbital": (205, 240, 255), "rebel_cell": (232, 20, 30)}
CORPNAME = {"meridian": "MERIDIAN FREIGHT", "solace": "SOLACE BIOSYSTEMS", "halcyon": "HALCYON CIVIC", "orbital": "ORBITAL COMMONS", "rebel_cell": "REBEL_CELL"}
SITE = {"meridian": "THE CONTAINER FORTRESS", "solace": "THE DOUBLE HELIX", "halcyon": "THE CIVIC CORE", "orbital": "THE SILO CRESCENT",
        "rebel_cell": "THE CELL (TAKEN)"}
BACK = {"meridian": "meridian_hq_night", "solace": "solace_hq_night", "halcyon": "halcyon_hq_night", "orbital": "orbital_hq_open_night",
        "rebel_cell": "rebel_cell_hq_dispatch_night"}


def load_wheel(key, r):
    im = Image.open(os.path.join(WH, key + ".png")).convert("RGBA")
    m = json.load(open(os.path.join(WH, key + ".json")))
    k = r / (R_OUT * m["ss"])
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    return im, (m["c"][0] * k, m["c"][1] * k), m


def calm_base(corp, pools):
    src = Image.open(os.path.join(BD, BACK[corp] + ".png")).convert("RGB")
    a = np.asarray(src, np.float32) / 255
    soft = np.asarray(src.filter(ImageFilter.GaussianBlur(3.5)), np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    pool = np.zeros((H, W), np.float32)
    for (cx, cy), R in pools:
        pool = np.maximum(pool, np.exp(-(np.hypot(xx - cx, yy - cy) / (R * 1.02)) ** 4))
    a = a * (1 - pool[..., None]) + soft * pool[..., None]
    dim = np.full((H, W), 0.86, np.float32)
    dim *= 1 - 0.55 * pool
    dim *= 1 - 0.55 * np.clip((yy - 800) / 260, 0, 1)
    dim *= 1 - 0.40 * np.clip((96 - yy) / 96, 0, 1)
    return a * dim[..., None]


def compose(corp):
    slots = json.load(open(os.path.join(WH, "boss_slots.json")))[corp]
    pw, pc, pm = load_wheel("player", PLAYER["r"])
    bw, bc, bm = load_wheel("%s_boss" % corp, BOSS["r"])
    pools = [(PLAYER["c"], PLAYER["r"] * 1.12), (BOSS["c"], BOSS["r"] * 1.12)]
    base = calm_base(corp, pools)
    ppos = (int(PLAYER["c"][0] - pc[0]), int(PLAYER["c"][1] - pc[1]))
    bpos = (int(BOSS["c"][0] - bc[0]), int(BOSS["c"][1] - bc[1]))
    emit = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    emit.alpha_composite(pw, ppos)
    emit.alpha_composite(bw, bpos)
    img = MC.to_rgba(MC.light_spill(base, emit, k=1.4, add=0.14))
    sh = Image.new("L", (W, H), 0)
    ds = ImageDraw.Draw(sh)
    for (c, R) in ((PLAYER["c"], PLAYER["r"] * 1.14), (BOSS["c"], BOSS["r"] * 1.14)):
        ds.ellipse([c[0] - R, c[1] - R + 14, c[0] + R, c[1] + R + 14], fill=150)
    shl = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    shl.putalpha(sh.filter(ImageFilter.GaussianBlur(22)))
    img.alpha_composite(shl)
    img.alpha_composite(pw, ppos)
    img.alpha_composite(bw, bpos)
    img = bloom(img.convert("RGB"), 1, 0.32, 0.66).convert("RGBA")
    # HUD (plates.hud with this corp's names / colours)
    acc = ACC[corp]
    name = slots["name"].upper()
    hp_e, hp_max = json.load(open(os.path.join(WH, "%s_boss.json" % corp)))["hp"]
    MC.status_bar(img, "TURN 3   |   FREE NUDGE 1", "NETRUN // %s // %s // BOSS: %s" % (CORPNAME[corp], SITE[corp], name))
    pb = MC.hp_number(img, PLAYER["c"], PLAYER["r"] * pm["meta"]["hp_r"] / 436, 41, 60)
    MC.next_plate(img, int(pb[2]) + 16, int(pb[1]) + 12, 27, -14, MC.HPG)
    eb = MC.hp_number(img, BOSS["c"], BOSS["r"] * bm["meta"]["hp_r"] / 436, hp_e, hp_max)
    MC.next_plate(img, int(eb[2]) + 16, int(eb[1]) + 12, hp_e - 8, -8, acc)
    MC.nudge_buttons(img, PLAYER["c"], PLAYER["r"])
    MC.forecast_tag(img, 30, 84, "YOU", "ZERO-DAY", 12, 2, [("HIT 12 - SHIELD 4 = 8", MC.PINK), ("RING x2 ON PERFECT", (200, 200, 215))],
                    MC.PINK, width=400)
    s0 = slots["slots"][slots["pointers"][0] // 5]
    MC.forecast_tag(img, 1560, 84, name, s0["program"], s0["value"], 3, [("HIT %d > YOU" % s0["value"], MC.RED), ("+4 SHIELD", acc)],
                    acc, width=352)
    P.ram_meter(img, 30, 958, 5, 12, 0, "")
    MC.piles(img, 450, 958)
    bx = MC.small_button(img, 1370, 1010, "RESPIN", "4 RAM  [R]", (92, 225, 255))
    MC.small_button(img, bx, 1006, "UNDO", "[Z]", (190, 190, 205))
    # hand of vinyl sticker cards (idle: nothing hovered)
    n = len(P.CARDS)
    for i in range(n):
        c = P.card_body(i, 144, 192)
        x, y, r = P.hand_slot(i, n)
        c = c.rotate(r, resample=Image.BICUBIC, expand=True)
        img.alpha_composite(c, (int(x - c.width / 2), int(y)))
    FX22.stickers_r22(img)  # CELL-9 name plate + the raid-style SEND IT over EXECUTE
    out = img.convert("RGB")
    out.save(os.path.join(R24, "combat_%s.jpg" % corp), quality=92)
    print("combat", corp, flush=True)


if __name__ == "__main__":
    for corp in (sys.argv[1:] or ["meridian", "solace", "halcyon", "orbital"]):
        compose(corp)
