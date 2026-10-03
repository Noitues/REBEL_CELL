"""settings_menu.png: Options > Accessibility, opened from the pause menu over combat.

Media: OPTIONS = screen-title sticker; the panel, tabs, switches, sliders, tiles = terminal (the Cell's
system); HEAT GLITCH row carries the round 18 storyboard's live preview (ON at HUNTED / OFF = static
edge tint only). Rows and words follow scripts/ui/kit/settings_panel.gd (TOGGLE_WORDS, HEADINGS).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageChops, ImageDraw, ImageFilter  # noqa: E402

import sticker_lib31 as SL  # noqa: E402
import ui31 as U  # noqa: E402

W, H = 1920, 1080
BG = os.path.join(U.CONC, 'round30_meridian_castle', 'combat_meridian.jpg')
STORY = os.path.join(U.CONC, 'round18_combat_fx', 'heat_glitch_storyboard.png')
OUT = os.path.join(U.ROOT, 'settings_menu.png')


def tiles(img, xy, items, sel, focus=None, w=132, h=58):
    x, y = xy
    for k, (a, b) in enumerate(items):
        box = (x, y, x + w, y + h)
        m = U.rect_mask(img.size, box, chamfer=8)
        if k == sel:
            img = U.over(img, U.CYAN, m, 0.92)
            tc, mc = U.NAVY, (20, 50, 70)
        else:
            img = U.over(img, U.NAVY, m, 0.9)
            e = ImageChops.subtract(m, SL.erode(m, 2))
            img = U.over(img, U.CYAN, e, 0.5)
            tc, mc = U.WHITE, (130, 160, 190)
        U.text(img, (x + w / 2, y + 22), a, U.F(U.MONO, 20), tc, 'mm', 1.2)
        if b:
            U.text(img, (x + w / 2, y + 44), b, U.F(U.MONO, 13), mc, 'mm', 0.4)
        if focus == k:
            img = U.focus_brackets(img, box, gap=5, ln=10)
        x += w + 10
    return img


def main():
    bg = U.fit_cover(Image.open(BG).convert('RGB'), W, H)
    img = U.grade(bg, 0.36, 6, 0.6)
    img = U.vignette(img, 0.5)
    P = (300, 150, 1620, 1004)
    img = U.term_panel(img, P, 'PAUSED  //  OPTIONS', seed=31, alpha=240, glow=0.5)
    st = U.sticker('OPTIONS', 66, U.FILL_YELLOW, seed=19)
    img = U.place(img, st, 1440, 150, angle=3)
    img, _ = U.tabs(img, (330, 204), ['ACCESSIBILITY', 'DISPLAY', 'AUDIO', 'CONTROLS', 'LANGUAGE'], 0)
    U.text(img, (1590, 224), '[LB] [RB] switch tab', U.F(U.MONO, 15), (120, 150, 180), 'rm', 0.8)
    # ------------------------------------------------ left: switches
    U.text(img, (334, 280), 'EFFECTS & MOTION', U.F(U.MONO, 16), U.CYAN, 'la', 2.0)
    rows = [('REDUCE EFFECTS', 'No scanlines, flicker, chromatic or distortion.', False, None),
            ('REDUCE MOTION', 'No camera moves or parallax; pages cross-fade.', False, None),
            ('FLASH LIMITER', 'At most 3 flashes a second. On by default.', True, None),
            ('HEAT GLITCH', 'Screen-wide Heat distortion, pulsing on Heat events.', True, 'focus'),
            ('HIGH CONTRAST', 'Opaque panels, 7:1 text and thick edges.', False, None),
            ('SUBTITLES', 'Every spoken line, with the speaker\'s name.', True, None),
            ('SUBTITLES TYPE IN', 'Off: each line shows at once.', True, None),
            ('ASSIST MODE', 'New campaigns: free nudge, more HP. No ICE records.', False, None)]
    y = 316
    for k, (lab, desc, on, st_) in enumerate(rows):
        box = (330, y - 8, 970, y + 58)
        if st_ == 'focus':
            m = U.rect_mask(img.size, box, chamfer=8)
            img = U.over(img, U.CYAN, m, 0.10)
            img = U.focus_brackets(img, box, gap=4, ln=12)
            U.text(img, (340, y + 12), '>', U.F(U.MONO, 24), U.LIME, 'lm')
        U.text(img, (364, y + 12), lab, U.F(U.MONO, 24), U.WHITE, 'lm', 1.6)
        U.text(img, (364, y + 40), desc, U.F(U.PLEX, 19), (176, 190, 208), 'lm')
        img = U.toggle(img, (888, y - 2), on, 'idle')
        if lab == 'HEAT GLITCH':
            # dependency chip: the Flash limiter is on, so only the slowest layer plays
            img = U.term_panel(img, (650, y + 60, 970, y + 86), None, accent=U.AMBER, hexbg=False, chamfer=6, header=False, glow=0.3)
            U.text(img, (810, y + 73), 'LIMITED: flash limiter on, slow layer only', U.F(U.MONO, 13), U.AMBER, 'mm', 0.3)
            y += 28
        d = U.BD(img)
        d.line([(334, y + 64), (966, y + 64)], fill=U.CYAN + (40,), width=1)
        y += 74
    # ------------------------------------------------ right: scale, tiles, preview
    X = 1010
    U.text(img, (X, 280), 'TEXT SCALE', U.F(U.MONO, 16), U.CYAN, 'la', 2.0)
    img = U.slider(img, (X + 4, 318, X + 470, 338), 0.5, ticks=(0, 0.5, 1), readout='1.3x', labels=('1.0', '1.3', '1.6'))
    pb = (X, 372, 1590, 446)
    img = U.term_panel(img, pb, None, hexbg=False, chamfer=8, header=False, glow=0.2, alpha=200)
    U.text(img, (X + 16, 409), 'The Cell never sleeps. Every word grows with this.', U.F(U.PLEX, 27), U.WHITE, 'lm')
    U.text(img, (X, 476), 'COLOUR-BLIND CORRECTION', U.F(U.MONO, 16), U.CYAN, 'la', 2.0)
    img = tiles(img, (X, 502), [('OFF', 'no correction'), ('DEUTAN', 'green-weak'), ('PROTAN', 'red-weak'), ('TRITAN', 'blue-weak')], 0)
    U.text(img, (X, 576), 'Patterns and glyphs stay the main cue.', U.F(U.PLEX, 17), (150, 166, 186), 'la')
    U.text(img, (X, 612), 'RESOLVE SPEED AFTER SEND IT', U.F(U.MONO, 16), U.CYAN, 'la', 2.0)
    img = tiles(img, (X, 638), [('1x', 'full replay'), ('2x', 'twice as fast'), ('INSTANT', 'results at once')], 1, w=150)
    U.text(img, (X, 724), 'HEAT GLITCH PREVIEW  (HUNTED, 82)', U.F(U.MONO, 16), U.CYAN, 'la', 2.0)
    sb = Image.open(STORY).convert('RGB')
    on = sb.crop((20, 860, 1018, 1385)).resize((280, 147), Image.LANCZOS).convert('RGBA')
    off = sb.crop((3074, 860, 4072, 1385)).resize((280, 147), Image.LANCZOS).convert('RGBA')
    for k, (th, lab, col) in enumerate(((on, 'ON  //  slip + split, 320 ms', U.CYAN), (off, 'OFF  //  static edge tint', (150, 160, 178)))):
        x0 = X + k * 300
        m = U.rect_mask(img.size, (x0 - 3, 750, x0 + 283, 900))
        img = U.over(img, col, m)
        img.alpha_composite(th, (x0, 752))
        U.text(img, (x0, 918), lab, U.F(U.MONO, 14), col, 'la', 0.6)
    d = U.BD(img)
    d.line([(1576, 744), (1576, 744)], fill=(0, 0, 0, 0))
    # ------------------------------------------------ footer
    d.line([(330, 958), (1590, 958)], fill=U.CYAN + (60,), width=1)
    img = U.term_button(img, (334, 966, 594, 996), 'RESET TO DEFAULTS', None, 'idle')
    x = 1080
    for g, s in (('A', 'toggle'), ('B', 'close'), ('Y', 'reset')):
        d = U.BD(img)
        d.ellipse([x, 968, x + 26, 994], fill=(240, 238, 232, 255), outline=(10, 10, 14, 255), width=2)
        U.text(img, (x + 13, 982), g, U.F(U.BAHN, 16, 'Bold'), (14, 14, 20), 'mm')
        U.text(img, (x + 34, 981), s, U.F(U.MONO, 17), U.WHITE, 'lm', 0.8)
        x += 120
    U.text(img, (1590, 981), 'saved to profile', U.F(U.MONO, 17), (150, 176, 200), 'rm', 0.8)
    img.convert('RGB').save(OUT)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
