"""Round 18 / 4: fx_sheet.png, one overview of the three combat FX (frames read back from the GIFs).

python make_sheet.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from PIL import Image, ImageDraw
import plates as P
from slicelib import f_num, f_ui

OUT = P.OUT
TW, TH = 320, 288
CARD = (520, 140, 920, 500)      # GIF-px crop boxes (10:9) around the action
BOSS = (560, 0, 960, 360)
PARC = (0, 220, 400, 540)
PTOP = (0, 0, 400, 360)
SCREEN = (380, 0, 860, 432)
GAP = 12
ROWS = [
    ("1  CARD PLAY  -  peel, aim, slap, bit-stream dissolve, spin", "card_play.gif",
     [(5, "idle", CARD), (18, "hover: corner peels", CARD), (33, "drag + grease aim", (440, 140, 840, 500)), (43, "slap: squash, shadow snap", CARD),
      (50, "dissolve A: scan front", CARD), (56, "0/1 spiral into hub", CARD), (64, "spin 9 ticks, blur", CARD), (80, "landed, hand closes", CARD)]),
    ("2  DAMAGE SHARDS  -  0/1 from the hit point, by severity", "damage_shards.gif",
     [(7, "hit on slice (M)", BOSS), (10, "number pops", BOSS), (18, "-> HP, arc redrawn", (560, 180, 960, 540)), (36, "hit on your HP arc", PARC),
      (59, "crit: hit-stop, RGB", BOSS), (64, "crit: streaks shatter", BOSS), (93, "blocked: wall", PTOP), (98, "2 through, equation", PTOP)]),
    ("3  HEAT GLITCH  -  one post shader, 4 bands, Options switch", "heat_glitch.gif",
     [(5, "COOL: flicker", SCREEN), (10, "NOTICED: tears", SCREEN), (18, "FLAGGED: roll", SCREEN), (22, "FLAGGED: blocks", SCREEN),
      (32, "HUNTED: slip+split", SCREEN), (36, "HUNTED between", SCREEN), (52, "Options switch", SCREEN), (61, "OFF: edge tint", SCREEN)]),
]
TABLE = [
    ("", "TIER", "LENGTH", "EASING", "GODOT 4.7 BUILD", "REDUCED (reduce effects / motion)"),
    ("card play", "T2", "hover 300 / peel 240 / drag ~600 / slap 240 / dissolve 600 / spin 900 ms",
     "out-back hover+spin, in-cubic drop, in stream", "peel+gloss CanvasItem shader on the card; GPUParticles2D 0/1 atlas for the stream; Tween chain",
     "no peel/curl: card slides 150 ms, 1-frame outline, fades; no glyphs; spin 2x, no blur"),
    ("damage shards", "T2 (crit T3)", "tracer 200, burst 450-720, number fly 200 ms",
     "damped (k 5.5) + gravity; number out-back 2.0 / in-cubic", "GPUParticles2D one-shot per hit, 0/1 atlas, additive; Line2D cracks; slice flash via CanvasItem shader",
     "no particles/flash/shake: HP set at once + static -n chip (colour + number carry it)"),
    ("heat glitch", "T0 ambient", "bursts 80-320 ms every 3.2-1.6 s",
     "sine envelope, states hold 80 ms (steppy)", "ColorRect + screen-texture shader on a CanvasLayer under the HUD; uniforms intensity, band, time; Options flag",
     "reduce effects: tears only, no roll/slip/split, max 1 burst / 3 s; HEAT GLITCH off: static edge tint"),
]


def main():
    W = 8 * TW + 9 * GAP
    head = 96
    row_h = 46 + TH + 30
    tab_h = 44 * len(TABLE) + 30
    S = Image.new("RGB", (W, head + len(ROWS) * row_h + tab_h + 40), (14, 13, 20))
    d = ImageDraw.Draw(S)
    d.text((GAP, 10), "REBEL_CELL  COMBAT FX  (round 18)", font=f_num(54), fill=(255, 255, 255))
    d.text((GAP, 70), "card play / damage shards / heat glitch on the locked D4 combat screen. GIFs + storyboards + NOTES.md in this folder.",
           font=P.mono(19), fill=(170, 170, 188))
    y = head
    for title, gif, picks in ROWS:
        d.rectangle([GAP, y + 8, GAP + 6, y + 38], fill=(255, 61, 168))
        d.text((GAP + 16, y + 4), title, font=f_num(34), fill=(255, 255, 255))
        im = Image.open(os.path.join(OUT, gif))
        for k, (i, lab, box) in enumerate(picks):
            im.seek(min(i, im.n_frames - 1))
            th = im.convert("RGB").crop(box).resize((TW, TH), Image.LANCZOS)
            x = GAP + k * (TW + GAP)
            S.paste(th, (x, y + 46))
            d.text((x + 2, y + 46 + TH + 4), "%d  %s" % (k + 1, lab), font=f_ui(18, b"SemiBold"), fill=(205, 205, 218))
        y += row_h
    cols = [GAP, 200, 340, 900, 1330, 2010]
    fs = f_ui(17, b"SemiBold")
    for r, row in enumerate(TABLE):
        yy = y + 10 + r * 44
        if r == 0:
            d.rectangle([GAP, yy - 4, W - GAP, yy + 26], fill=(30, 28, 40))
        for c, txt in enumerate(row):
            col = (255, 214, 64) if r == 0 or c == 0 else (215, 215, 228)
            f = f_ui(18, b"Bold Condensed") if r == 0 or c == 0 else fs
            maxw = (cols[c + 1] if c + 1 < len(cols) else W - GAP) - cols[c] - 12
            words, lines, cur = txt.split(), [], ""
            for w in words:
                if f.getlength((cur + " " + w).strip()) > maxw:
                    lines.append(cur)
                    cur = w
                else:
                    cur = (cur + " " + w).strip()
            lines.append(cur)
            for k, ln in enumerate(lines[:2]):
                d.text((cols[c], yy + k * 19), ln, font=f, fill=col)
    S.save(os.path.join(OUT, "fx_sheet.png"), optimize=True)
    print("fx_sheet", S.size)


if __name__ == "__main__":
    main()
