"""contact_sheet.jpg: the six stills + a frame from each GIF.

python contact.py
"""
import os
from PIL import Image, ImageDraw
import fwlib as F
L = F.L

ITEMS = ["firmware_set.png", "firmware_socket.png", "firmware_medium.png", "daemon_set.png", "daemon_row.png", "shop_v3.png"]
GIFS = [("firmware_trigger.gif", 0.45), ("daemon_trigger.gif", 0.55)]


def main():
    tw, th = 624, 351
    W, H = 1920, 40 + 2 * (th + 34) + 300
    img = Image.new("RGB", (W, H), (12, 10, 18))
    d = ImageDraw.Draw(img)
    d.text((24, 8), "ROUND 33  -  FIRMWARE (microchips) + DAEMONS", font=L.f_num(28), fill=(240, 240, 248))
    for i, n in enumerate(ITEMS):
        im = Image.open(os.path.join(F.OUT, n)).convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = 18 + (i % 3) * (tw + 10), 48 + (i // 3) * (th + 34)
        img.paste(im, (x, y))
        d.text((x, y + th + 6), n, font=L.f_mono(16), fill=(200, 200, 215))
    y0 = 48 + 2 * (th + 34)
    x = 18
    for n, at in GIFS:
        g = Image.open(os.path.join(F.OUT, n))
        g.seek(int(g.n_frames * at))
        fr = g.convert("RGB")
        k = 270 / fr.height
        fr = fr.resize((int(fr.width * k), 270), Image.LANCZOS)
        img.paste(fr, (x, y0))
        d.text((x, y0 + 274), n, font=L.f_mono(16), fill=(200, 200, 215))
        x += fr.width + 16
    d.text((x + 10, y0 + 20), "Firmware = a socketed die (pins in the bezel, rarity LED),", font=L.f_mono(18), fill=(200, 220, 235))
    d.text((x + 10, y0 + 46), "outer CCW corner of its slice; gold trace on trigger.", font=L.f_mono(18), fill=(200, 220, 235))
    d.text((x + 10, y0 + 86), "Daemon = a sigil on a CRT tile in the rack beside the", font=L.f_mono(18), fill=(200, 220, 235))
    d.text((x + 10, y0 + 112), "player wheel; phosphor = trigger family, bezel = rarity.", font=L.f_mono(18), fill=(200, 220, 235))
    path = os.path.join(F.OUT, "contact_sheet.jpg")
    img.save(path, quality=88)
    print("wrote", path)


if __name__ == "__main__":
    main()
