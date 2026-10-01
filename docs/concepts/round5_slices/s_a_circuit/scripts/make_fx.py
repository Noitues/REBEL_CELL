"""shader_fx.gif (all 9 programs + the Meridian corp board, looping) and shader_fx_strip.png."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from circ_lib import OUT, F_NUM, F_SILK, ORDER, PROGRAMS, make_board, make_corp_board, render_tile, hexc  # noqa: E402

SS = 2
RO = 250
RI = RO * 130 / 360
N = 36
FX = {"EXPLOIT": "breach spark + tear", "ZERO-DAY": "rare cascade", "FIREWALL": "scan bar + shimmer",
      "SANDBOX": "containment pulse", "PROXY": "detour signal", "PATCH": "solder + mend glow",
      "VIRUS": "infection front", "TROJAN": "unpack + blink", "NULL": "dead grain", "MERIDIAN": "clocked conveyor"}


def boards():
    bs = [(n, make_board(n, 3, RO, RI, SS)) for n in ORDER]
    bs.append(("MERIDIAN", make_corp_board("EXPLOIT", 3, RO, RI, SS, value=6)))
    return bs


def colour(name):
    if name == "MERIDIAN":
        return (255, 140, 26)
    if name == "NULL":
        return (170, 170, 170)
    return tuple(int(c * 255) for c in hexc(PROGRAMS[name][1]))


def main():
    bs = boards()
    f_name = ImageFont.truetype(F_NUM, 22)
    f_small = ImageFont.truetype(F_SILK, 13)
    tiles = {}
    for name, b in bs:
        frames = []
        for i in range(N):
            im = render_tile(b, i / N)
            frames.append(im.resize((im.width // SS, im.height // SS), Image.LANCZOS))
        tiles[name] = frames
        print(name, "done", flush=True)
    tw, th = tiles["EXPLOIT"][0].size
    cw, ch = tw + 24, th + 52
    W, H = cw * 5 + 20, ch * 2 + 56
    bg = (10, 8, 14)
    gif_frames = []
    for i in range(N):
        img = Image.new("RGB", (W, H), bg)
        d = ImageDraw.Draw(img)
        d.text((16, 12), "s_a_circuit  shader behaviours (loop)", font=f_name, fill=(240, 236, 248))
        for k, (name, _) in enumerate(bs):
            x = 10 + (k % 5) * cw + 12
            y = 50 + (k // 5) * ch
            im = tiles[name][i]
            img.paste(im, (x, y), im)
            d.text((x + tw / 2, y + th + 12), name, font=f_name, anchor="mm", fill=colour(name))
            d.text((x + tw / 2, y + th + 33), FX[name], font=f_small, anchor="mm", fill=(160, 160, 175))
        gif_frames.append(img)
    # one shared palette built from a mosaic of several frames: no palette flicker
    mosaic = Image.new("RGB", (W, H * 4))
    for j, i in enumerate((0, N // 4, N // 2, 3 * N // 4)):
        mosaic.paste(gif_frames[i], (0, H * j))
    pal = mosaic.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG) for f in gif_frames]
    path = os.path.join(OUT, "shader_fx.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=70, loop=0, optimize=True, disposal=1)
    print("gif", os.path.getsize(path) / 1e6, "MB", flush=True)

    # strip: rows = programs, columns = 6 phases
    cols = [0, 6, 12, 18, 24, 30]
    lw = 190
    SW, SH = lw + len(cols) * (tw + 10) + 10, 60 + len(bs) * (th + 10)
    strip = Image.new("RGB", (SW, SH), bg)
    d = ImageDraw.Draw(strip)
    d.text((16, 14), "s_a_circuit  shader strip  (t = 0, 1/6 ... 5/6 of the loop)", font=f_name, fill=(240, 236, 248))
    for r, (name, _) in enumerate(bs):
        y = 56 + r * (th + 10)
        d.text((16, y + th / 2 - 12), name, font=f_name, fill=colour(name))
        d.text((16, y + th / 2 + 14), FX[name], font=f_small, fill=(160, 160, 175))
        for c, i in enumerate(cols):
            im = tiles[name][i]
            strip.paste(im, (lw + c * (tw + 10), y), im)
    strip.save(os.path.join(OUT, "shader_fx_strip.png"))
    print("strip ok", strip.size, flush=True)


if __name__ == "__main__":
    main()
