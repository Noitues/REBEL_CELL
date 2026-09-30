"""r2b_painterly_matte - turns the Blender city passes into matte-painting stills 01-03.
Usage: python make_city.py <workdir> <stills_dir> [modes...]
Needs <workdir>/city_{day,night,alarm,depth}.png and city_day.json / city_alarm.json."""
import sys, os, json, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import paintlib as P

WORK, OUTDIR = sys.argv[1], sys.argv[2]
MODES = sys.argv[3:] or ["day", "night", "alarm"]
HORIZON = 0.32

MODE_CFG = {
    "day":   {"haze": (184, 198, 216), "haze_amt": 0.62, "band": (236, 222, 198), "band_amt": 0.45,
              "bloom": (235, (6, 24), (0.25, 0.18)), "path": P.GOLD_HI, "susp": 2, "file": "01_city_day.png",
              "time": "DAY 3  •  14:20"},
    "night": {"haze": (30, 28, 62), "haze_amt": 0.50, "band": (120, 70, 120), "band_amt": 0.30,
              "bloom": (170, (5, 20, 60), (0.8, 0.6, 0.45)), "path": P.CYAN, "susp": 5, "file": "02_city_night.png",
              "time": "NIGHT 3  •  23:40"},
    "alarm": {"haze": (60, 14, 26), "haze_amt": 0.50, "band": (170, 40, 40), "band_amt": 0.35,
              "bloom": (160, (5, 20, 60), (0.9, 0.7, 0.55)), "path": P.CYAN, "susp": 9, "file": "03_city_suspicion.png",
              "time": "NIGHT 3  •  01:15"},
}

def load_json(name):
    with open(os.path.join(WORK, name)) as f:
        return json.load(f)

def searchlights(img, info, depth):
    """Painted searchlight cones from the helicopters down to their ground pools."""
    beam = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(beam)
    pools = Image.new("L", img.size, 0)
    pd = ImageDraw.Draw(pools)
    for h in info["helis"]:
        sx, sy = h["src"][0], h["src"][1]
        ring = [(p[0], p[1]) for p in h["dst_ring"]]
        angs = [(math.atan2(py - sy, px - sx), (px, py)) for (px, py) in ring]
        angs.sort()
        a_min, a_max = angs[0][1], angs[-1][1]
        for k in range(8):   # soft layered cone, brighter at the core
            t = k / 8
            mx = (a_min[0] + a_max[0]) / 2; my = (a_min[1] + a_max[1]) / 2
            l = (P.lerp(a_min[0], mx, t), P.lerp(a_min[1], my, t))
            r = (P.lerp(a_max[0], mx, t), P.lerp(a_max[1], my, t))
            d.polygon([(sx, sy), l, r], fill=40 + k * 24)
        pd.polygon(ring, fill=235)
    beam = beam.filter(ImageFilter.GaussianBlur(5))
    pools = pools.filter(ImageFilter.GaussianBlur(9))
    col = P.solid((226, 236, 255), img.size)
    img = Image.composite(col, img, beam.point(lambda v: int(min(255, v) * 0.8)))
    img = ImageChops.add(img, Image.composite(P.solid((210, 220, 240), img.size), P.solid((0, 0, 0), img.size), pools))
    return img

def alarm_lights(img, info):
    """Red/blue strobes on the helicopters and drones: soft glow plus a hard core."""
    g = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    pts = [(h["src"][0], h["src"][1], 1.0) for h in info["helis"]] + [(p[0], p[1], 0.6) for p in info["drones"]]
    for i, (x, y, s) in enumerate(pts):
        col = (255, 40, 30) if i % 2 == 0 else (60, 120, 255)
        r = 26 * s
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (150,))
    g = g.filter(ImageFilter.GaussianBlur(10))
    d = ImageDraw.Draw(g)
    for i, (x, y, s) in enumerate(pts):
        r = 4 * s + 1
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 240, 230, 255))
    return Image.alpha_composite(img.convert("RGBA"), g).convert("RGB")

def draw_overlay(data, depth, mode):
    cfg = MODE_CFG[mode]
    ui = P.UI()
    dp = depth.load()
    glow = Image.new("RGBA", (P.W, P.H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    pc = cfg["path"]

    def occluded(p):
        x, y = int(p[0]), int(p[1])
        if not (0 <= x < P.W and 0 <= y < P.H):
            return True
        v = math.sqrt(max(0.0, p[2]) / data["DMAX"])
        return dp[x, y] / 255.0 < v - 0.012

    # ---- paths: dark under-stroke, then brass/neon dashes; hidden stretches go dotted
    for path in data["paths"]:
        pts = path["pts"]
        ui.d.line(ui.P([(p[0], p[1]) for p in pts]), fill=(10, 8, 6, 120), width=ui.S(8), joint="curve")
        acc = 0.0
        for p0, p1 in zip(pts[:-1], pts[1:]):
            seg = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            acc += seg
            hidden = occluded(p0)
            phase = (acc % 22.0)
            if hidden:
                if phase < 5:
                    ui.d.line(ui.P([(p0[0], p0[1]), (p1[0], p1[1])]), fill=pc + (150,), width=ui.S(3))
            elif phase < 14:
                ui.d.line(ui.P([(p0[0], p0[1]), (p1[0], p1[1])]), fill=pc + (255,), width=ui.S(4))
                gd.line([(p0[0], p0[1]), (p1[0], p1[1])], fill=pc + (200,), width=10)

    # ---- node ground rings
    kind_col = {"target": P.CRIMSON, "site": (72, 200, 186), "safehouse": P.GOLD}
    for i, n in enumerate(data["nodes"]):
        here = i == data["here"]
        ring = [(p[0], p[1]) for p in n["ring"]]
        c = n["c"]
        sc = 1.6 if here else 1.0
        ring = [(c[0] + (x - c[0]) * sc, c[1] + (y - c[1]) * sc) for (x, y) in ring]
        col = kind_col[n["kind"]]
        ui.d.polygon(ui.P(ring), fill=col + (90,))
        ui.d.line(ui.P(ring + [ring[0]]), fill=(20, 14, 8, 220), width=ui.S(7))
        ui.d.line(ui.P(ring + [ring[0]]), fill=P.GOLD + (255,), width=ui.S(3))
        inner = [(c[0] + (x - c[0]) * 0.55, c[1] + (y - c[1]) * 0.55) for (x, y) in ring]
        ui.d.line(ui.P(inner + [inner[0]]), fill=col + (255,), width=ui.S(2))
        gd.polygon(ring, fill=col + (120,))
        if here:
            for k, s in enumerate((1.35, 1.7)):
                outer = [(c[0] + (x - c[0]) * s, c[1] + (y - c[1]) * s) for (x, y) in ring]
                ui.d.line(ui.P(outer + [outer[0]]), fill=P.GOLD_HI + (200 - k * 80,), width=ui.S(2))
                gd.line(outer + [outer[0]], fill=P.GOLD_HI + (160,), width=8)

    # ---- markers: stem, diamond, label plate
    f_lab = ui.font("georgiab.ttf", 15)
    f_here = ui.font("georgiab.ttf", 19)
    f_small = ui.font("georgiai.ttf", 13)
    for i, n in enumerate(data["nodes"]):
        here = i == data["here"]
        c = n["c"]
        col = kind_col[n["kind"]]
        tx, ty = c[0], c[1] - (58 if here else 40)
        ui.d.line(ui.P([(c[0], c[1]), (tx, ty + 12)]), fill=(20, 14, 8, 230), width=ui.S(5))
        ui.d.line(ui.P([(c[0], c[1]), (tx, ty + 12)]), fill=P.GOLD + (255,), width=ui.S(2))
        r = 17 if here else 12
        ui.diamond(tx, ty, r + 3, (20, 16, 12, 255), P.GOLD, 2.5)
        ui.diamond(tx, ty, r - 2, col + (255,), P.GOLD_HI, 1.2)
        ui.d.ellipse(ui.P([(tx - 3, ty - r * 0.55), (tx + 2, ty - r * 0.2)]), fill=(255, 255, 255, 170))
        gd.ellipse([tx - r * 2, ty - r * 2, tx + r * 2, ty + r * 2], fill=col + (90,))
        label = n["label"]
        fw = ui.d.textlength(label, font=f_here if here else f_lab) / ui.ss
        if here:
            pw = max(fw, 128) + 34
            box = (tx - pw / 2, ty - r - 64, tx + pw / 2, ty - r - 10)
            ui.plate(box, fill=(26, 20, 12, 235), border=P.GOLD_HI, bw=2.5, notch=9)
            ui.text((tx, box[1] + 17), "YOU ARE HERE", ui.font("georgiai.ttf", 14), P.GOLD_HI + (255,), anchor="mm", sh_off=1)
            ui.text((tx, box[1] + 38), label, f_here, (255, 246, 222, 255), anchor="mm", sh_off=1)
            ui.d.polygon(ui.P([(tx - 8, box[3]), (tx + 8, box[3]), (tx, box[3] + 7)]), fill=P.GOLD_HI + (255,))
        else:
            pw = fw + 22
            box = (tx - pw / 2, ty - r - 32, tx + pw / 2, ty - r - 8)
            ui.plate(box, fill=(16, 18, 22, 215), border=P.GOLD, bw=1.5, notch=6, inner=False)
            ui.text((tx, (box[1] + box[3]) / 2), label, f_lab, (244, 234, 210, 255), anchor="mm", sh_off=1)
    glow = glow.filter(ImageFilter.GaussianBlur(9 if mode == "day" else 12))
    return glow, ui

def hud(ui, mode):
    cfg = MODE_CFG[mode]
    # district title + suspicion gauge (top-left)
    ui.plate((24, 22, 470, 128), fill=(16, 18, 22, 222), notch=12)
    ui.text((46, 36), "THE VERDIGRIS WARD", ui.font("georgiab.ttf", 24), (246, 232, 200, 255))
    ui.text((46, 68), "SUSPICION", ui.font("georgiai.ttf", 15), P.GOLD_HI + (255,))
    lvl = cfg["susp"]
    for k in range(10):
        x0 = 146 + k * 30
        if k < lvl:
            t = k / 9
            col = P.lerp_c((72, 200, 186), (236, 176, 64), min(1, t * 1.8)) if t < 0.55 else P.lerp_c((236, 176, 64), P.CRIMSON, (t - 0.55) / 0.45)
        else:
            col = (62, 66, 76)
        ui.d.polygon(ui.P([(x0, 70), (x0 + 24, 70), (x0 + 20, 90), (x0 - 4, 90)]), fill=col + (255,))
        ui.d.line(ui.P([(x0, 70), (x0 + 24, 70)]), fill=(255, 255, 255, 60 if k < lvl else 20), width=ui.S(1))
    state = {2: "Quiet streets", 5: "Patrols doubled", 9: "LOCKDOWN — sweeps in progress"}[lvl]
    ui.text((46, 100), state, ui.font("georgiai.ttf", 15),
            (P.CRIMSON if lvl >= 8 else (220, 212, 190)) + (255,))
    # time + funds (top-right)
    ui.plate((1540, 22, 1896, 96), fill=(16, 18, 22, 222), notch=12)
    ui.text((1564, 38), cfg["time"], ui.font("georgiab.ttf", 20), (246, 232, 200, 255))
    ui.text((1564, 66), "¢ 1,240   •   CELL: 4 OPERATIVES", ui.font("georgia.ttf", 15), P.GOLD_HI + (255,))
    # legend (bottom-right)
    ui.plate((1618, 950, 1896, 1056), fill=(16, 18, 22, 210), notch=10)
    f = ui.font("georgia.ttf", 15)
    for k, (name, col) in enumerate([("Corporate target", P.CRIMSON), ("Site", (72, 200, 186)), ("Hideout", P.GOLD)]):
        y = 972 + k * 28
        ui.diamond(1644, y + 8, 9, col + (255,), P.GOLD_HI, 1.2)
        ui.text((1664, y), name, f, (236, 226, 204, 255), sh_off=1)

def build(mode):
    cfg = MODE_CFG[mode]
    render = Image.open(os.path.join(WORK, "city_%s.png" % mode)).convert("RGBA")
    depth = P.load_depth(os.path.join(WORK, "city_depth.png"))
    data = load_json("city_day.json")
    img = P.painted_sky(mode, seed=21, horizon=HORIZON)
    img.paste(render, (0, 0), render)
    img = P.atmosphere(img, depth, cfg["haze"], start=0.40, end=0.97, max_amt=cfg["haze_amt"], power=1.25, alpha=render.split()[3])
    img = P.haze_band(img, int(P.H * HORIZON) - 60, int(P.H * HORIZON) + 150, cfg["band"], cfg["band_amt"])
    if mode == "alarm":
        img = searchlights(img, load_json("city_alarm.json"), depth)
    img = P.repaint(img, depth, keep_near=0.45, seed=31, step_near=4, step_far=8, default_angle=-0.2)
    thr, radii, gains = cfg["bloom"]
    img = P.bloom(img, thr, radii, gains)
    if mode == "alarm":
        img = alarm_lights(img, load_json("city_alarm.json"))
    if mode == "day":
        img = P.split_tone(img, amt_hi=0.30, amt_lo=0.32)
        img = P.contrast(img, 1.08)
    elif mode == "night":
        img = P.split_tone(img, warm=(255, 190, 140), cool=(60, 80, 170), amt_hi=0.15, amt_lo=0.35)
    else:
        img = P.contrast(P.color_balance(img, 1.04, 0.86, 0.92), 1.12, 90)
        img = P.split_tone(img, warm=(255, 150, 120), cool=(90, 40, 110), amt_hi=0.2, amt_lo=0.4)
    img = P.canvas_grain(img, seed=5, amount=0.08, blotch=0.05)
    img = P.vignette(img, 0.42 if mode != "day" else 0.30, (0, 0, 0) if mode != "alarm" else (70, 0, 8))
    img.save(os.path.join(WORK, "plate_%s.png" % mode))
    glow, ui = draw_overlay(data, depth, mode)
    hud(ui, mode)
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, Image.merge("RGBA", glow.split()[:3] + (glow.split()[3].point(lambda v: int(v * 0.6)),)))
    img = Image.alpha_composite(img, ui.finish())
    img.convert("RGB").save(os.path.join(OUTDIR, cfg["file"]))
    # the pushed-back plate for the combat screen
    print("saved", cfg["file"])

if __name__ == "__main__":
    os.makedirs(OUTDIR, exist_ok=True)
    for m in MODES:
        build(m)
