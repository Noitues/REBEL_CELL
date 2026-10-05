"""Round 42 v4 -> breach_icon_options_v4.png: three bold BREACH Exploit icons, each at close and at grid zoom
(on a full marker), picked: A, the sledgehammer."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import markers42 as M
import r31lib as RL
import city_view as CV


def big(mask_fn, px):
    return M.tint(M.g_mask(mask_fn, px), (255, 236, 170))


def main():
    W, H = 1920, 760
    img = Image.new("RGBA", (W, H), (12, 11, 18, 255))
    bg = ImageEnhance.Brightness(CV.base_map()).enhance(0.35).filter(ImageFilter.GaussianBlur(3))
    img.alpha_composite(bg.crop((0, 0, W, H)))
    img = RL.place_sticker(img, RL.sticker_word(["BREACH ICON"], 46, fills=["yellow"], seed=44), 190, 50, angle=-2)
    d = ImageDraw.Draw(img)
    d.text((400, 50), "one heavy silhouette, readable at grid zoom; the key stays 'Exploit Site'", font=RL.f_ui(24, b"SemiBold"),
           fill=(235, 235, 240, 255), anchor="lm")
    opts = [("A  SLEDGEHAMMER (PICK)", M.hammer_mask, "brute force through the customs override; one blunt shape"),
            ("B  BATTERING RAM", M.ram_mask, "reads as 'break the gate'; long and thin at small size"),
            ("C  BROKEN CHAIN", M.chain_mask, "reads as 'freed'; two links blur together from afar")]
    for i, (title, fn, why) in enumerate(opts):
        x = 60 + i * 620
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([x - 20, 120, x + 580, 700], radius=14, outline=(255, 214, 64, 255) if i == 0 else (90, 96, 120, 255), width=3)
        d.text((x, 150), title, font=RL.f_ui(28, b"Bold"), fill=(255, 214, 64, 255) if i == 0 else (220, 225, 235, 255))
        d.text((x, 190), why, font=RL.f_mono(15), fill=(180, 190, 200, 255))
        g = big(fn, 260)
        d.ellipse([x + 20, 240, x + 300, 520], fill=(18, 14, 4, 255), outline=(255, 206, 72, 255), width=6)
        img.alpha_composite(g, (x + 30, 250))
        # at grid zoom on a full Exploit marker (badge swapped)
        old = M.hammer_mask
        M.hammer_mask = fn
        img = M.marker(img, x + 420, 330, "exploit", 2, "corporate", "next", "BREACH", scale=1.6)
        img = M.marker(img, x + 420, 520, "exploit", 2, "corporate", "next", "BREACH", scale=1.0)
        M.hammer_mask = old
        d = ImageDraw.Draw(img)
        d.text((x + 420, 410), "close", font=RL.f_mono(14), fill=(170, 180, 190, 255), anchor="mm")
        d.text((x + 420, 570), "grid", font=RL.f_mono(14), fill=(170, 180, 190, 255), anchor="mm")
        d.text((x + 160, 620), "silhouette", font=RL.f_mono(14), fill=(170, 180, 190, 255), anchor="mm")
    RL.save(img, "breach_icon_options_v4.png")


if __name__ == "__main__":
    main()
