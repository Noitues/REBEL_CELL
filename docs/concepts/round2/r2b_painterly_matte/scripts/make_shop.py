"""r2b_painterly_matte - still 05: the black-market shop.
Usage: python make_shop.py <workdir> <stills_dir>   (needs shop_beauty/shop_depth, part_*.png, plate_*.png)"""
import sys, os, math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import paintlib as P
import cards as C
from make_combat import paint_object

WORK, OUTDIR = sys.argv[1], sys.argv[2]

def background():
    render = Image.open(os.path.join(WORK, "shop_beauty.png")).convert("RGBA")
    depth = P.load_depth(os.path.join(WORK, "shop_depth.png"))
    img = Image.new("RGB", render.size, (14, 18, 34))
    img.paste(render, (0, 0), render)
    img = P.atmosphere(img, depth, (70, 44, 34), start=0.5, end=0.8, max_amt=0.2, power=1.0, alpha=render.split()[3])
    img = P.repaint(img, depth, keep_near=0.38, keep_start=0.44, keep_end=0.66, seed=51, step_near=4, step_far=8,
                    default_angle=-0.35)
    img = P.contrast(P.color_balance(img, 1.0, 0.9, 0.86), 1.22, 110)
    img = P.bloom(img, 225, (6, 24, 70), (0.45, 0.32, 0.25))
    img = P.split_tone(img, warm=(255, 196, 140), cool=(60, 90, 170), amt_hi=0.25, amt_lo=0.35)
    img = P.canvas_grain(img, seed=9, amount=0.08, blotch=0.05)
    img = P.vignette(img, 0.6)
    return img

def price_tag(ui, cx, cy, price, afford=True):
    ui.plate((cx - 62, cy - 20, cx + 62, cy + 20), fill=(30, 22, 12, 235), border=P.GOLD, notch=8, inner=False)
    col = (255, 236, 190) if afford else (236, 90, 70)
    ui.text((cx, cy + 1), "¢ %d" % price, ui.font("georgiab.ttf", 20), col + (255,), anchor="mm", sh_off=1)
    ui.d.ellipse(ui.P([(cx - 70, cy - 4), (cx - 62, cy + 4)]), fill=(20, 14, 8, 255))

def main():
    img = background().convert("RGBA")
    ui = P.UI()
    # hanging sign
    for x in (760, 1160):
        ui.d.line(ui.P([(x, 0), (x, 44)]), fill=(20, 16, 10, 255), width=ui.S(5))
        ui.d.line(ui.P([(x, 0), (x, 44)]), fill=P.GOLD_SH + (255,), width=ui.S(2))
    sign_glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sign_glow).rectangle([640, 50, 1280, 160], fill=(80, 230, 220, 120))
    img = Image.alpha_composite(img, sign_glow.filter(ImageFilter.GaussianBlur(30)))
    ui.plate((640, 44, 1280, 164), fill=(22, 18, 14, 240), border=P.GOLD_HI, bw=3, notch=16)
    ui.text((960, 94), "THE UNDERSIDE", ui.font("georgiab.ttf", 54), P.GOLD_HI + (255,), anchor="mm",
            shadow=(0, 60, 60, 200), stroke=1, stroke_fill=(90, 60, 20, 255))
    ui.d.line(ui.P([(740, 128), (1180, 128)]), fill=(110, 240, 230, 255), width=ui.S(2))
    ui.text((960, 146), "black market  •  cash only  •  no names", ui.font("georgiai.ttf", 17), (200, 238, 232, 255), anchor="mm", sh_off=1)
    # funds
    ui.plate((1600, 30, 1890, 100), fill=(16, 18, 22, 225), notch=10)
    ui.text((1624, 42), "YOUR CREDITS", ui.font("georgiai.ttf", 14), P.GOLD_HI + (255,))
    ui.text((1624, 62), "¢ 290", ui.font("georgiab.ttf", 26), (248, 234, 204, 255))
    # section labels
    f_sec = ui.font("georgiab.ttf", 20)
    ui.plate((240, 470, 540, 510), fill=(16, 18, 22, 215), notch=8, inner=False)
    ui.text((390, 490), "PROGRAMS  (cards)", f_sec, (246, 232, 200, 255), anchor="mm", sh_off=1)
    ui.plate((1150, 470, 1510, 510), fill=(16, 18, 22, 215), notch=8, inner=False)
    ui.text((1330, 490), "WHEEL PARTS", f_sec, (246, 232, 200, 255), anchor="mm", sh_off=1)
    # cards for sale
    plates = {m: Image.open(os.path.join(WORK, "plate_%s.png" % m)).convert("RGB") for m in ("day", "night", "alarm")}
    stock = [(C.CARD_SET[4], plates["night"].crop((1040, 360, 1500, 760)), 90),
             (("Data Siphon", 1, "CREDIT", "Spin 4 ticks. Each CREDIT slice passed gives 10."), plates["day"].crop((600, 420, 1000, 760)), 120),
             (("Breach Charge", 3, "ATTACK", "Deal 14. Suspicion +1."), plates["alarm"].crop((1000, 150, 1500, 600)), 150)]
    for i, ((title, cost, kind, text), art, price) in enumerate(stock):
        cx = 330 + i * 240
        card, M = C.make_card(title, cost, kind, text, art, glow=(255, 190, 90) if i == 1 else None)
        img.alpha_composite(card, (int(cx - card.size[0] / 2), int(700 - card.size[1] / 2)))
        price_tag(ui, cx, 890, price)
    # spinner parts on little velvet plinths
    parts = [("part_wedge", "Violet Wedge", "+5 HACK ticks", 180, True),
             ("part_hub", "Verdigris Hub", "Re-spin once per fight", 240, True),
             ("part_pointer", "Hooked Pointer", "Stop one tick late", 320, False)]
    for i, (fn, name, desc, price, afford) in enumerate(parts):
        cx = 1110 + i * 230
        back = P.UI(); back.plate((cx - 100, 540, cx + 100, 850), fill=(40, 12, 16, 225), border=P.GOLD, notch=12)
        img = Image.alpha_composite(img, back.finish())
        halo = Image.new("L", img.size, 0)
        ImageDraw.Draw(halo).ellipse([cx - 80, 570, cx + 80, 730], fill=150)
        img = Image.composite(P.solid((200, 140, 80)).convert("RGBA"), img, halo.filter(ImageFilter.GaussianBlur(30)))
        p = paint_object(Image.open(os.path.join(WORK, fn + ".png")).convert("RGBA"), 60 + i).resize((180, 180), Image.LANCZOS)
        img.alpha_composite(p, (cx - 90, 560))
        ui.text((cx, 770), name, ui.font("georgiab.ttf", 18), (248, 234, 204, 255), anchor="mm", sh_off=1)
        ui.text((cx, 796), desc, ui.font("georgiai.ttf", 14), P.GOLD_HI + (255,), anchor="mm", sh_off=1)
        if not afford:
            ui.text((cx, 824), "not enough credits", ui.font("georgiai.ttf", 13), (236, 110, 90, 255), anchor="mm", sh_off=1)
        price_tag(ui, cx, 890, price, afford)
    # dealer's line
    ui.plate((1300, 300, 1640, 380), fill=(16, 18, 22, 215), notch=10)
    ui.text((1470, 326), "“Corp gear, fell off a drone.”", ui.font("georgiai.ttf", 16), (236, 226, 204, 255), anchor="mm", sh_off=1)
    ui.text((1470, 354), "— Mother Kestrel, fence", ui.font("georgia.ttf", 13), P.GOLD_HI + (255,), anchor="mm", sh_off=1)
    ui.d.polygon(ui.P([(1330, 380), (1360, 380), (1318, 404)]), fill=(16, 18, 22, 215))
    # leave + reroll
    ui.plate((1620, 980, 1890, 1050), fill=(40, 20, 14, 235), border=P.GOLD_HI, bw=2.5, notch=12)
    ui.text((1735, 1015), "LEAVE", ui.font("georgiab.ttf", 30), (255, 240, 214, 255), anchor="mm")
    ui.d.polygon(ui.P([(1818, 1000), (1858, 1015), (1818, 1030)]), fill=P.GOLD_HI + (255,))
    ui.plate((1340, 988, 1590, 1042), fill=(16, 18, 22, 225), notch=10)
    ui.text((1465, 1015), "Restock  ¢ 40", ui.font("georgiab.ttf", 20), (236, 226, 204, 255), anchor="mm")
    img = Image.alpha_composite(img, ui.finish())
    img.convert("RGB").save(os.path.join(OUTDIR, "05_shop.png"))
    print("saved 05_shop.png")

if __name__ == "__main__":
    main()
