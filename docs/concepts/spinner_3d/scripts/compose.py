"""Spinner depth study: assemble the final PNGs, GIFs and the contact sheet (Pillow).

Run from the spinner_3d folder after the t0*.py Blender scripts:  python scripts/compose.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REN = os.path.join(ROOT, "work", "renders")
FONTS = os.path.normpath(os.path.join(ROOT, "..", "..", "..", "assets", "fonts"))
MONO = os.path.join(FONTS, "ShareTechMono-Regular.ttf")
ANTON = os.path.join(FONTS, "Anton-Regular.ttf")
BG = (4, 5, 12)
TXT = (242, 246, 255)
MID = (175, 192, 214)
PINK = (255, 61, 168)


def f(size, path=MONO):
    return ImageFont.truetype(path, size)


def R(name):
    return Image.open(os.path.join(REN, name)).convert("RGB")


def caption(im, title, sub=""):
    """Label strip, bottom-left."""
    im = im.copy()
    d = ImageDraw.Draw(im, "RGBA")
    ft, fs = f(30, ANTON), f(20)
    w = max(d.textlength(title, font=ft), d.textlength(sub, font=fs)) + 36
    h = 84 if sub else 56
    d.rectangle([0, im.height - h, w, im.height], fill=(2, 3, 10, 200))
    d.rectangle([0, im.height - h, 6, im.height], fill=PINK + (255,))
    d.text((20, im.height - h + 8), title, font=ft, fill=TXT)
    if sub:
        d.text((20, im.height - 32), sub, font=fs, fill=MID)
    return im


def header(canvas, title, sub):
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, 8, 90], fill=PINK)
    d.text((28, 12), title, font=f(40, ANTON), fill=TXT)
    d.text((30, 64), sub, font=f(22), fill=MID)


def tile_label(canvas, x, y, text):
    d = ImageDraw.Draw(canvas, "RGBA")
    ft = f(22)
    w = d.textlength(text, font=ft) + 20
    d.rectangle([x, y, x + w, y + 34], fill=(2, 3, 10, 210))
    d.text((x + 10, y + 5), text, font=ft, fill=TXT)


def three_up(names, labels, title, sub):
    c = Image.new("RGB", (1920, 1080), BG)
    header(c, title, sub)
    for i, (n, lab) in enumerate(zip(names, labels)):
        im = R(n).resize((620, 620), Image.LANCZOS)
        x = 20 + i * 630
        c.paste(im, (x, 180))
        tile_label(c, x + 10, 190, lab)
    d = ImageDraw.Draw(c)
    d.text((30, 830), "Offsets are the same pointer positions in each tile; layers slide by pointer x depth.",
           font=f(22), fill=MID)
    return c


def six_up(folder, frames, labels, title, sub):
    c = Image.new("RGB", (1920, 1080), BG)
    header(c, title, sub)
    for i, (fr, lab) in enumerate(zip(frames, labels)):
        src = Image.open(os.path.join(REN, folder, f"f{fr:03d}.png")).convert("RGB")
        im = src.resize((460, 460), Image.LANCZOS)
        # 2x inset of the needle so the tick and its shadow read at this size
        ins = src.crop((245, 70, 355, 180)).resize((150, 150), Image.LANCZOS)
        ImageDraw.Draw(ins).rectangle([0, 0, 149, 149], outline=PINK, width=2)
        im.paste(ins, (460 - 158, 8))
        x = 20 + (i % 3) * 470 + 230
        y = 110 + (i // 3) * 480
        c.paste(im, (x, y))
        tile_label(c, x + 8, y + 8, f"f{fr:02d}  {lab}")
    return c


def gif(folder, out, size=440, ms=50, hold_last=0, first=None):
    names = sorted(n for n in os.listdir(os.path.join(REN, folder)) if n.endswith(".png"))
    frames = [Image.open(os.path.join(REN, folder, n)).convert("RGB").resize((size, size), Image.LANCZOS)
              for n in names]
    # one shared palette from a montage of sample frames
    sample = Image.new("RGB", (size * 4, size))
    for k, idx in enumerate(range(0, len(frames), max(1, len(frames) // 4))):
        if k < 4:
            sample.paste(frames[idx], (k * size, 0))
    pal = sample.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    q = [fr.quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG) for fr in frames]
    dur = [ms] * len(q)
    if hold_last:
        dur[-1] = hold_last
    path = os.path.join(ROOT, out)
    q[0].save(path, save_all=True, append_images=q[1:], duration=dur, loop=0, optimize=True, disposal=1)
    print(out, round(os.path.getsize(path) / 1e6, 2), "MB")


def sprite_sheet():
    c = Image.new("RGB", (1920, 1080), BG)
    main = R("04_prerendered_3d.png").resize((1080, 1080), Image.LANCZOS)
    c.paste(main, (0, 0))
    main_cap = caption(c.crop((0, 0, 1080, 1080)), "04 PRE-RENDERED 3D",
                       "true 3D wheel, baked; right: the sprite layers a bake exports")
    c.paste(main_cap, (0, 0))
    d = ImageDraw.Draw(c)
    d.text((1110, 20), "BAKED SPRITE LAYERS", font=f(34, ANTON), fill=TXT)
    d.text((1110, 66), "transparent PNGs, same camera, lighting baked in", font=f(20), fill=MID)
    labels = {"bezel": "bezel.png  (static)", "wheel": "wheel.png  (rotates in 2D)",
              "hub": "hub.png  (static)", "needle": "needle.png  (pivot, 3 tick frames)"}
    for i, g in enumerate(("bezel", "wheel", "hub", "needle")):
        x = 1110 + (i % 2) * 400
        y = 110 + (i // 2) * 470
        chk = Image.new("RGB", (380, 380), (30, 32, 40))
        dc = ImageDraw.Draw(chk)
        for yy in range(0, 380, 20):
            for xx in range(0, 380, 20):
                if (xx // 20 + yy // 20) % 2:
                    dc.rectangle([xx, yy, xx + 19, yy + 19], fill=(44, 46, 56))
        sp = Image.open(os.path.join(REN, f"04_sprite_{g}.png")).convert("RGBA")
        if g in ("needle", "hub"):
            box = sp.getbbox()
            if box:
                cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
                half = max(box[2] - box[0], box[3] - box[1]) / 2 + 20
                sp = sp.crop((int(cx - half), int(cy - half), int(cx + half), int(cy + half)))
        sp = sp.resize((380, 380), Image.LANCZOS)
        base = chk.convert("RGBA")
        base.alpha_composite(sp)
        c.paste(base.convert("RGB"), (x, y))
        d.text((x, y + 388), labels[g], font=f(20), fill=MID)
    return c


def contact_sheet(items):
    W, cw, ch = 1920, 620, 420
    c = Image.new("RGB", (W, 110 + 3 * (ch + 60)), BG)
    header(c, "SPINNER DEPTH STUDY", "five techniques alone, then combined; same wheel, same dimmed city")
    for i, (name, label) in enumerate(items):
        im = Image.open(os.path.join(ROOT, name)).convert("RGB")
        im.thumbnail((cw, ch), Image.LANCZOS)
        x = 20 + (i % 3) * (cw + 20) + (cw - im.width) // 2
        y = 120 + (i // 3) * (ch + 60) + (ch - im.height) // 2
        c.paste(im, (x, y))
        ImageDraw.Draw(c).text((20 + (i % 3) * (cw + 20), 120 + (i // 3) * (ch + 60) + ch + 8), label,
                               font=f(24), fill=TXT)
    c.save(os.path.join(ROOT, "contact_sheet.jpg"), quality=88)


if __name__ == "__main__":
    caption(R("01_physical_stack.png"), "01 PHYSICAL STACK",
            "bezel on top, slices sunk below, glass dome; real shadows + one specular").save(
        os.path.join(ROOT, "01_physical_stack.png"))
    three_up(["02_parallax_a.png", "02_parallax_b.png", "02_parallax_c.png"],
             ["pointer up-left", "centred", "pointer down-right"],
             "02 PARALLAX", "flat unlit layers on separate planes: slices deep, ring 0, hub +0.8, needle +1.4").save(
        os.path.join(ROOT, "02_parallax.png"))
    gif("seq02", "02_parallax.gif")
    caption(R("03_normal_lit.png"), "03 NORMAL-LIT 2D",
            "flat sprite + normal maps; pink sign and cyan tube rake the bevels").save(
        os.path.join(ROOT, "03_normal_lit.png"))
    sprite_sheet().save(os.path.join(ROOT, "04_prerendered_3d.png"))
    labs = ["full speed: rim blurs, hub reads", "slowing: glyphs return", "peg pushes the flap (inset)",
            "stop: overshoot", "wobble back", "rest: crisp"]
    fr = [3, 16, 26, 27, 30, 44]
    six_up("seq05", fr, labs, "05 MOTION DEPTH",
           "flat layers; depth from rotational blur, a ticking needle with its own shadow, a wobble on stop").save(
        os.path.join(ROOT, "05_motion_depth.png"))
    gif("seq05", "05_motion_depth.gif", hold_last=900)
    three_up(["06_combo_a.png", "06_combo_b.png", "06_combo_c.png"],
             ["pointer up-left", "centred", "pointer down-right"],
             "06 STACK + PARALLAX + NORMAL-LIT", "1 + 2 + 3: stacked planes with shadows and dome, lit by the glows, sliding with the pointer").save(
        os.path.join(ROOT, "06_combo_stack_parallax_lit.png"))
    gif("seq06", "06_combo_stack_parallax_lit.gif")
    six_up("seq07", fr, labs, "07 PRE-RENDER + MOTION",
           "4 + 5: the 3D wheel spun down; the metal needle ticks on the dividers and shadows the inlay").save(
        os.path.join(ROOT, "07_combo_prerender_motion.png"))
    gif("seq07", "07_combo_prerender_motion.gif", hold_last=900)
    caption(R("08_combo_everything.png"), "08 EVERYTHING, READABLE",
            "3D wheel + dome + glow lighting + small orbit + ticking needle; glyphs stay crisp").save(
        os.path.join(ROOT, "08_combo_everything.png"))
    gif("seq08", "08_combo_everything.gif", hold_last=900)
    caption(R("09_enemy_pair.png"), "09 OPERATIVE vs ENEMY (combo 8)",
            "left: stickered bezel, pink rim; right: machined Meridian-orange bezel, container stripes, notched hostile edge").save(
        os.path.join(ROOT, "09_enemy_pair.png"))
    contact_sheet([
        ("01_physical_stack.png", "01 physical stack"), ("02_parallax.png", "02 parallax (+gif)"),
        ("03_normal_lit.png", "03 normal-lit"), ("04_prerendered_3d.png", "04 pre-rendered 3D"),
        ("05_motion_depth.png", "05 motion depth (+gif)"), ("06_combo_stack_parallax_lit.png", "06 = 1+2+3 (+gif)"),
        ("07_combo_prerender_motion.png", "07 = 4+5 (+gif)"), ("08_combo_everything.png", "08 everything (+gif)"),
        ("09_enemy_pair.png", "09 operative vs enemy"),
    ])
    print("composed")
