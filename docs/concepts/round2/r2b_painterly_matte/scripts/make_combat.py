"""r2b_painterly_matte - still 04: combat. Two brass spinners over the pushed-back night city.
Usage: python make_combat.py <workdir> <stills_dir>   (needs plate_*.png from make_city.py and the spinner renders)"""
import sys, os, json, math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
import paintlib as P
import cards as C

WORK, OUTDIR = sys.argv[1], sys.argv[2]

def pushed_back_city():
    plate = Image.open(os.path.join(WORK, "plate_night.png")).convert("RGB")
    w, h = plate.size
    z = 1.18   # zoom toward the hero dome, then blur and sink it
    crop = plate.crop((int(w * 0.30), int(h * 0.10), int(w * 0.30 + w / z), int(h * 0.10 + h / z))).resize((w, h), Image.LANCZOS)
    img = crop.filter(ImageFilter.GaussianBlur(4))
    img = ImageEnhance.Color(img).enhance(0.75)
    img = ImageEnhance.Brightness(img).enhance(0.55)
    # a painted dark floor band for the hand and a soft central pool of light behind the wheels
    band = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(band)
    for y in range(h):
        t = P.clamp01((y - 640) / 380)
        d.line([(0, y), (w, y)], fill=int(235 * t ** 1.2))
    img = Image.composite(P.solid((10, 10, 16)), img, band.filter(ImageFilter.GaussianBlur(10)))
    pool = Image.new("L", (w, h), 0)
    ImageDraw.Draw(pool).ellipse([200, 80, 1720, 820], fill=90)
    img = Image.composite(P.solid((120, 90, 70)), img, pool.filter(ImageFilter.GaussianBlur(160)))
    return P.vignette(img, 0.55)

def paint_object(rgba, seed):
    """Light brushwork on a rendered object while keeping its silhouette (alpha) crisp."""
    rgb = Image.new("RGB", rgba.size, (0, 0, 0)); rgb.paste(rgba, (0, 0), rgba)
    depth = Image.new("L", rgba.size, 60)
    painted = P.brush_pass(rgb, depth, seed=seed, step_near=3, step_far=4, fine=False, length=2.0)
    mixed = Image.blend(painted, rgb.filter(ImageFilter.UnsharpMask(1.5, 60, 2)), 0.55)
    mixed = P.canvas_grain(mixed, seed=seed, amount=0.07, blotch=0.03)
    out = mixed.convert("RGBA"); out.putalpha(rgba.split()[3])
    return out

def place_spinner(img, ui, name, cx, cy, size, meta, rot_pointer_hint, glow_col):
    sp = Image.open(os.path.join(WORK, "spinner_%s.png" % name)).convert("RGBA")
    sp = paint_object(sp, 17 if name == "player" else 23).resize((size, size), Image.LANCZOS)
    # glow halo behind the wheel
    halo = Image.new("L", img.size, 0)
    ImageDraw.Draw(halo).ellipse([cx - size * 0.42, cy - size * 0.42, cx + size * 0.42, cy + size * 0.42], fill=190)
    halo = halo.filter(ImageFilter.GaussianBlur(40))
    img = Image.composite(P.solid(glow_col), img, halo)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 170), (cx - size // 2 + 14, cy - size // 2 + 22), sp.split()[3].point(lambda v: int(v * 0.7)))
    img = Image.alpha_composite(img.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(14)))
    img.paste(sp, (cx - size // 2, cy - size // 2), sp)
    # slice glyphs and tick counts (crisp UI on the enamel)
    px_per_unit = size / meta["ortho"]
    ocx = cx - meta["center"][0] * px_per_unit
    ocy = cy + meta["center"][1] * px_per_unit
    fnum = ui.font("georgiab.ttf", 15)
    for s in meta[name]:
        a = (s["start"] + s["len"] / 2) / meta["ticks"] * math.tau
        r = 0.62 * px_per_unit
        gx, gy = ocx + math.sin(a) * r, ocy - math.cos(a) * r
        if s["kind"] != "BLANK":
            C.glyph(ui.d, s["kind"], gx, gy - 6, 17 if s["len"] > 3 else 13, ui.ss)
        r2 = 0.83 * px_per_unit
        nx, ny = ocx + math.sin(a) * r2, ocy - math.cos(a) * r2
        ui.text((nx, ny), str(s["len"]), fnum, (255, 246, 226, 235), anchor="mm", sh_off=1)
    return img

def main():
    meta = json.load(open(os.path.join(WORK, "spinners.json")))
    img = pushed_back_city().convert("RGBA")
    ui = P.UI()
    SIZE = 600
    img = place_spinner(img, ui, "player", 560, 400, SIZE, meta, 0, (60, 150, 150))
    img = place_spinner(img, ui, "enemy", 1360, 400, SIZE, meta, 0, (150, 40, 36))
    # name plates + health bars
    f_name = ui.font("georgiab.ttf", 24); f_sub = ui.font("georgiai.ttf", 15); f_hp = ui.font("georgiab.ttf", 16)
    for (cx, name, sub, hp, mx, col) in [(560, "YOUR CELL", "Wheel of the Verdigris", 42, 60, (58, 186, 150)),
                                         (1360, "ARGENT ENFORCER", "Corporate security unit", 55, 80, (200, 50, 40))]:
        ui.plate((cx - 190, 34, cx + 190, 92), fill=(16, 18, 22, 225), notch=10)
        ui.text((cx, 55), name, f_name, (248, 234, 204, 255), anchor="mm")
        ui.text((cx, 79), sub, f_sub, P.GOLD_HI + (255,), anchor="mm", sh_off=1)
        ui.bar((cx - 220, 708, cx + 220, 736), hp / mx, col, label="%d / %d" % (hp, mx), f=f_hp)
    # enemy intent chip
    ui.plate((1600, 150, 1850, 214), fill=(40, 14, 12, 225), border=P.GOLD, notch=8)
    C.glyph(ui.d, "ATTACK", 1630, 182, 21, ui.ss)
    ui.text((1656, 166), "INTENT: STRIKE 12", ui.font("georgiab.ttf", 15), (255, 226, 210, 255))
    ui.text((1656, 188), "lands on ATTACK", ui.font("georgiai.ttf", 13), (230, 190, 170, 255))
    # the VS medallion between the wheels
    cx, cy = 960, 400
    ui.d.ellipse(ui.P([(cx - 46, cy - 46), (cx + 46, cy + 46)]), fill=(20, 14, 8, 240))
    ui.d.ellipse(ui.P([(cx - 40, cy - 40), (cx + 40, cy + 40)]), fill=P.GOLD + (255,))
    ui.d.ellipse(ui.P([(cx - 33, cy - 33), (cx + 33, cy + 33)]), fill=(30, 22, 18, 255))
    ui.text((cx, cy + 1), "VS", ui.font("georgiab.ttf", 28), P.GOLD_HI + (255,), anchor="mm")
    ui.text((960, 470), "ROUND 2", ui.font("georgiab.ttf", 18), (248, 234, 204, 255), anchor="mm")
    # deck / discard / bandwidth
    ui.plate((30, 900, 190, 1050), fill=(16, 18, 22, 225), notch=10)
    ui.text((110, 930), "DECK", ui.font("georgiai.ttf", 15), P.GOLD_HI + (255,), anchor="mm")
    ui.text((110, 975), "14", ui.font("georgiab.ttf", 42), (248, 234, 204, 255), anchor="mm")
    ui.text((110, 1022), "discard 3", ui.font("georgiai.ttf", 14), (200, 190, 170, 255), anchor="mm")
    ui.plate((30, 790, 190, 880), fill=(16, 18, 22, 225), notch=10)
    ui.text((110, 812), "BANDWIDTH", ui.font("georgiai.ttf", 14), P.GOLD_HI + (255,), anchor="mm")
    for k in range(4):
        x = 58 + k * 34; y = 850
        on = k < 3
        ui.d.ellipse(ui.P([(x - 12, y - 12), (x + 12, y + 12)]), fill=(20, 14, 8, 255))
        ui.d.ellipse(ui.P([(x - 9, y - 9), (x + 9, y + 9)]), fill=((80, 232, 222) if on else (50, 56, 62)) + (255,))
        if on:
            ui.d.ellipse(ui.P([(x - 6, y - 7), (x, y - 2)]), fill=(230, 255, 250, 200))
    # the hand: five cards fanned along the bottom, the hovered one raised and glowing
    plates = {m: Image.open(os.path.join(WORK, "plate_%s.png" % m)).convert("RGB") for m in ("day", "night", "alarm")}
    arts = [plates["alarm"].crop((380, 200, 900, 640)), plates["day"].crop((1080, 330, 1480, 700)),
            plates["night"].crop((1180, 560, 1560, 880)), plates["day"].crop((0, 760, 520, 1080)),
            plates["night"].crop((1040, 360, 1500, 760))]
    n = len(C.CARD_SET)
    for i, (title, cost, kind, text) in enumerate(C.CARD_SET):
        t = i - (n - 1) / 2
        hovered = i == 2
        card, M = C.make_card(title, cost, kind, text, arts[i], glow=(90, 236, 226) if hovered else None)
        ang = -t * 5.0 if not hovered else 0
        card = card.rotate(ang, resample=Image.BICUBIC, expand=True)
        cx = 960 + t * 190
        cy = 930 + abs(t) ** 1.6 * 12 - (70 if hovered else 0)
        img.alpha_composite(card, (int(cx - card.size[0] / 2), int(cy - card.size[1] / 2)))
    # GO button: brass-ringed enamel disc
    gx, gy, r = 1730, 900, 92
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([gx - r - 20, gy - r - 20, gx + r + 20, gy + r + 20], fill=(255, 150, 60, 170))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(26)))
    ui.d.ellipse(ui.P([(gx - r - 6, gy - r - 6), (gx + r + 6, gy + r + 6)]), fill=(20, 14, 8, 255))
    ui.d.ellipse(ui.P([(gx - r, gy - r), (gx + r, gy + r)]), fill=P.GOLD + (255,))
    for k in range(24):
        a = k / 24 * math.tau
        ui.rivet(gx + math.cos(a) * (r - 7), gy + math.sin(a) * (r - 7), 3.2)
    ui.d.ellipse(ui.P([(gx - r + 16, gy - r + 16), (gx + r - 16, gy + r - 16)]), fill=(150, 36, 22, 255))
    ui.d.ellipse(ui.P([(gx - r + 22, gy - r + 20), (gx + r - 22, gy + 4)]), fill=(214, 78, 44, 255))
    ui.d.ellipse(ui.P([(gx - 40, gy - 58), (gx + 10, gy - 36)]), fill=(255, 200, 150, 110))
    ui.text((gx, gy + 2), "GO", ui.font("georgiab.ttf", 64), (255, 246, 226, 255), anchor="mm", shadow=(40, 6, 0, 220), sh_off=3)
    ui.text((gx, gy + r + 26), "spin the wheels", ui.font("georgiai.ttf", 15), P.GOLD_HI + (255,), anchor="mm")
    img = Image.alpha_composite(img, ui.finish())
    img = img.convert("RGB")
    img.save(os.path.join(OUTDIR, "04_combat.png"))
    print("saved 04_combat.png")

if __name__ == "__main__":
    main()
