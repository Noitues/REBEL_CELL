"""Bake the menus' concept art (ART-10 4C; ART_BIBLE v2 4.13) from the concept scripts, unchanged.

Designer ruling (2026-10-05): never redraw art the art pass already made. The title, Options and menu
pieces are drawn by the round 33 ui_chrome scripts on tag `art-concepts-r43`
(`docs/concepts/round33_ui_chrome/scripts/`: title.py, menu33.py, ui31.py, sticker_lib31.py,
settings.py, abandon.py). This runs their drawing functions as they are and splits the result into
per-item PNGs under `assets/ui/menus/`:

- `stickers/`: abandon.py's answer stickers (`dialog_cancel`, `dialog_burn_it` and `dialog_delete`, each
  at rest and with its focus halo; `--only dialog` bakes just these); BREACH (rest, focus halo, the 12 focused gloss-sweep frames), SIMULATE (calm, the two
  burst frames, each with its focus halo), OVERTHROW with the fist (rest, focus), and the yellow screen
  titles (OPTIONS, PAUSED, CODEX, STATS, CAMPAIGN SLOTS, NEW CAMPAIGN) with `ui31.sticker`'s round 33
  parameters. Placed with `sticker_lib31.place` (its own drop shadow) at 2x the 1920x1080 board space.
- `sign/`: the REBEL_CELL neon sign: `board()` + `neon()` for every distinct lit state of
  `lit_state()` over its 48-frame loop (`sign_<n>.png`), each sign state's glow alone on black for an
  additive layer (`glow_<n>.png`), and `meta.json` (frame -> state, the board rect).
- `pencil/`: the plan (the numbers 1. 2. 3. at the board's 112 px row pitch and the plan bracket) and
  the motto (NEVER SLEEP + crown), with `ui31.Pencil` at the board's coordinates.
- `kit/`: the pill switch (`ui31.toggle`, on / off, idle / hover / disabled), the slider handle
  (`ui31.slider`), the tab plates (`ui31.tabs`, active / idle), the choice tiles
  (`settings.tiles`, selected / idle) and the title's terminal chip plates (`ui31.term_panel` as
  `title.static_ui` calls it, hot / idle) with no words on them (the game writes its own, translated),
  and the ON AIR block (`title.ticker`).
- `glitch/`: the Heat glitch preview frames, cropped from the round 18 storyboard exactly as
  settings.py crops them.

Only paths change: the scripts' font paths point at the shipped faces (`assets/fonts`), and the
function defaults that captured the old path are re-pointed. No drawing code is edited.

Usage (never from stdin on this machine):
    git archive -o %TEMP%\\a4c\\c.tar art-concepts-r43 docs/concepts/round33_ui_chrome docs/concepts/round18_combat_fx/heat_glitch_storyboard.png
    (extract it to <dir>) then
    python tools/art/bake_menus_r33.py --src <dir>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "assets" / "ui" / "menus"
# Board space (the concept canvas) and the export scale for stickers (sticker_lib31 works at SS = 2).
BOARD_W, BOARD_H = 1920, 1080
STICKER_SCALE = 2.0
# abandon.py's answer stickers: (size, fill, seed). CANCEL and BURN IT as abandon.py draws them;
# DELETE (the title's delete-slot verb) with BURN IT's parameters (the pink committing verb).
DIALOG_WORDS = {"CANCEL": (50, "FILL_YELLOW", 41), "BURN IT": (58, "FILL_PINK", 40), "DELETE": (58, "FILL_PINK", 40)}
TITLE_WORDS = {"OPTIONS": (66, 19), "PAUSED": (54, 60), "CODEX": (54, 61), "STATS": (54, 62),
               "CAMPAIGN SLOTS": (54, 63), "NEW CAMPAIGN": (54, 64)}


def point_fonts(SL, U, M) -> None:
    """Re-point the scripts' font paths (and the defaults that captured them) at assets/fonts."""
    faces = {"Anton-Regular.ttf": FONTS / "Anton-Regular.ttf", "PermanentMarker-Regular.ttf": FONTS / "PermanentMarker-Regular.ttf",
             "IBMPlexSansCondensed-Medium.ttf": FONTS / "IBMPlexSansCondensed-Medium.ttf",
             "IBMPlexSansCondensed-Regular.ttf": FONTS / "IBMPlexSansCondensed-Regular.ttf",
             "ShareTechMono-Regular.ttf": FONTS / "ShareTechMono-Regular.ttf"}

    def fix(p):
        if isinstance(p, str):
            for name, path in faces.items():
                if p.replace("\\", "/").endswith(name):
                    return str(path)
        return p

    for mod in (SL, U):
        for k in ("ANTON", "MARKER", "PLEX", "PLEX_M", "MONO"):
            if hasattr(mod, k):
                setattr(mod, k, fix(getattr(mod, k)))
    for fn in (SL.lettering, SL.Pen.text):
        if fn.__defaults__:
            fn.__defaults__ = tuple(fix(d) for d in fn.__defaults__)
    if hasattr(SL, "text_img"):
        pass
    U._fc.clear()


def save_crop(img, path: Path, box=None) -> list:
    from PIL import Image  # noqa: F401
    if box is None:
        box = img.getbbox()
    out = img.crop(box)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    return [int(v) for v in box]


def sticker_png(SL, sd, path: Path) -> None:
    """One sticker, placed by sticker_lib31.place (its own shadow) on a clear canvas at STICKER_SCALE."""
    from PIL import Image
    w, h = sd["img"].size
    cw, ch = int(w * STICKER_SCALE / SL.SS) + 240, int(h * STICKER_SCALE / SL.SS) + 240
    canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    canvas = SL.place(canvas, sd, cw / 2, ch / 2, angle=0.0, scale=STICKER_SCALE)
    save_crop(canvas, path)


def bake_stickers(SL, U, M, T) -> None:
    d = OUT / "stickers"
    breach = T.stk("BREACH", U.FILL_PINK, 60, 50, focus=False)
    breach_f = T.stk("BREACH", U.FILL_PINK, 60, 50, focus=True)
    sticker_png(SL, breach["base"], d / "breach.png")
    sticker_png(SL, breach_f["base"], d / "breach_focus.png")
    for k, sw in enumerate(breach_f["sweeps"]):
        sticker_png(SL, sw, d / ("breach_sweep_%02d.png" % k))
    sim = T.stk("SIMULATE", "glitch", 60, 51)
    sticker_png(SL, sim["base"], d / "simulate.png")
    sticker_png(SL, U.focus_sticker(sim["base"]), d / "simulate_focus.png")
    for ph, sd in sim["glitch"].items():
        sticker_png(SL, sd, d / ("simulate_burst_%d.png" % ph))
        sticker_png(SL, U.focus_sticker(sd), d / ("simulate_burst_%d_focus.png" % ph))
    ovr = T.stk("OVERTHROW", "fist", 60, 52)
    sticker_png(SL, ovr["base"], d / "overthrow.png")
    sticker_png(SL, U.focus_sticker(ovr["base"]), d / "overthrow_focus.png")
    for word, (size, seed) in TITLE_WORDS.items():
        sticker_png(SL, U.sticker(word, size, U.FILL_YELLOW, seed=seed), d / ("title_%s.png" % word.lower().replace(" ", "_")))


def bake_dialog_stickers(SL, U) -> None:
    """abandon.py: the yellow CANCEL (safe, default focus) and the pink verb, at rest and with
    U.focus_sticker's lime die-cut halo."""
    d = OUT / "stickers"
    for word, (size, fill, seed) in DIALOG_WORDS.items():
        sd = U.sticker(word, size, getattr(U, fill), seed=seed)
        key = "dialog_" + word.lower().replace(" ", "_")
        sticker_png(SL, sd, d / (key + ".png"))
        sticker_png(SL, U.focus_sticker(sd), d / (key + "_focus.png"))


def bake_sign(T, U) -> dict:
    from PIL import Image
    d = OUT / "sign"
    letters = T.word_masks()
    board = T.board(Image.new("RGBA", (BOARD_W, BOARD_H), (0, 0, 0, 0)))
    x0, y0, x1, y1 = T.BOARD
    box = (x0 - 24, 0, x1 + 24, y1 + 28)  # the cables hang from the top edge
    gbox = (x0 - 90, max(0, y0 - 90), x1 + 90, y1 + 90)
    states: list = []
    frames: list = []
    for f in range(T.N):
        lit = tuple(round(v, 3) for v in T.lit_state(f, len(letters)))
        if lit not in states:
            n = len(states)
            states.append(lit)
            sign = T.neon(board.copy(), letters, list(lit))
            save_crop(sign, d / ("sign_%d.png" % n), box)
            glow = T.neon(Image.new("RGBA", (BOARD_W, BOARD_H), (0, 0, 0, 255)), letters, list(lit))
            save_crop(glow, d / ("glow_%d.png" % n), gbox)
        frames.append(states.index(lit))
    meta = {"frames": frames, "frame_ms": 80, "sign_box": list(box), "glow_box": list(gbox), "board": list(T.BOARD),
            "board_space": [BOARD_W, BOARD_H], "states": [list(s) for s in states]}
    (d / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return meta


def bake_pencil(U, T) -> dict:
    from PIL import Image
    d = OUT / "pencil"
    pen = U.Pencil((BOARD_W, BOARD_H), U.PEN_Y, seed=12)
    for k in range(3):
        cy = 392 + k * 112
        pen.text("%d." % (k + 1), 110, cy + 4, 44, angle=-4)
    pen.stroke(pen.wobble([(96, 340), (90, 500), (96, 690)], 1.2), width=5)
    plan = pen.ink(Image.new("RGBA", (BOARD_W, BOARD_H), (0, 0, 0, 0)), 0.9)
    plan_box = save_crop(plan, d / "plan.png", (60, 300, 170, 730))
    pen = U.Pencil((BOARD_W, BOARD_H), U.PEN_Y, seed=12)
    T.slogan(pen)
    motto = pen.ink(Image.new("RGBA", (BOARD_W, BOARD_H), (0, 0, 0, 0)), 0.9)
    motto_box = save_crop(motto, d / "motto.png")
    meta = {"plan_box": plan_box, "row_y": [392, 504, 616], "row_pitch": 112, "motto_box": motto_box}
    (d / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return meta


def bake_kit(U, S, T) -> None:
    from PIL import Image
    d = OUT / "kit"
    clear = lambda: Image.new("RGBA", (400, 200), (0, 0, 0, 0))  # noqa: E731
    for on in (True, False):
        for st in ("idle", "hover", "disabled"):
            save_crop(U.toggle(clear(), (40, 40), on, st), d / ("toggle_%s_%s.png" % ("on" if on else "off", st)))
    # the slider handle alone (ui31.slider draws the track, fill and handle; the handle is its box)
    sl = U.slider(Image.new("RGBA", (600, 120), (0, 0, 0, 0)), (40, 40, 540, 60), 0.5)
    save_crop(sl, d / "slider_handle.png", (282, 28, 300, 66))
    # tab plates: active and idle, wordless (the game writes the section name)
    img, boxes = U.tabs(Image.new("RGBA", (400, 120), (0, 0, 0, 0)), (20, 20), ["MMMMMMMM", "MMMMMMMM"], 0)
    blank, boxes = U.tabs(Image.new("RGBA", (400, 120), (0, 0, 0, 0)), (20, 20), ["        ", "        "], 0)
    save_crop(blank, d / "tab_active.png", tuple(boxes[0]))
    save_crop(blank, d / "tab_idle.png", tuple(boxes[1]))
    # choice tiles: selected and idle, wordless
    t = S.tiles(Image.new("RGBA", (400, 120), (0, 0, 0, 0)), (20, 20), [("", ""), ("", "")], 0)
    save_crop(t, d / "tile_selected.png", (20, 20, 152, 78))
    save_crop(t, d / "tile_idle.png", (162, 20, 294, 78))
    # the title's terminal chip plates (title.static_ui's term_panel call), wordless; padding keeps
    # their drop shadow and edge glow
    for name, glow, accent in (("chip_hot", 0.4, U.CYAN), ("chip_idle", 0.2, (110, 150, 180))):
        c = U.term_panel(Image.new("RGBA", (600, 160), (0, 0, 0, 0)), (40, 40, 510, 104), None, hexbg=False, chamfer=10,
                         header=False, glow=glow, alpha=220, accent=accent)
        save_crop(c, d / (name + ".png"), (28, 28, 524, 118))
    # the ON AIR block of the title's ticker
    tk = T.ticker(Image.new("RGBA", (BOARD_W, BOARD_H), (0, 0, 0, 0)), 0)
    save_crop(tk, d / "on_air.png", (0, 1026, 212, 1064))


def bake_glitch(S, src: Path) -> None:
    from PIL import Image
    d = OUT / "glitch"
    story = src / "docs" / "concepts" / "round18_combat_fx" / "heat_glitch_storyboard.png"
    sb = Image.open(story).convert("RGB")
    d.mkdir(parents=True, exist_ok=True)
    # settings.py: the ON frame and the OFF frame of the storyboard, at its 280 x 147 preview size
    sb.crop((20, 860, 1018, 1385)).resize((280, 147), Image.LANCZOS).save(d / "glitch_on.png")
    sb.crop((3074, 860, 4072, 1385)).resize((280, 147), Image.LANCZOS).save(d / "glitch_off.png")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="extracted art-concepts-r43 tree (its root)")
    ap.add_argument("--only", default="", help="bake one part only: dialog (abandon.py's stickers)")
    args = ap.parse_args()
    src = Path(args.src)
    scripts = src / "docs" / "concepts" / "round33_ui_chrome" / "scripts"
    sys.path.insert(0, str(scripts))
    import sticker_lib31 as SL  # noqa: E402
    import ui31 as U  # noqa: E402
    import menu33 as M  # noqa: E402
    point_fonts(SL, U, M)
    import title as T  # noqa: E402
    import settings as S  # noqa: E402
    OUT.mkdir(parents=True, exist_ok=True)
    bake_dialog_stickers(SL, U)
    print("dialog stickers", flush=True)
    if args.only == "dialog":
        return 0
    bake_stickers(SL, U, M, T)
    print("stickers", flush=True)
    meta = bake_sign(T, U)
    print("sign states", len(meta["states"]), flush=True)
    bake_pencil(U, T)
    print("pencil", flush=True)
    bake_kit(U, S, T)
    print("kit", flush=True)
    bake_glitch(S, src)
    print("glitch", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
