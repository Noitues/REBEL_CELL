"""options.png: Options, the round 31 terminal as built (build: MENUS.jpg options rows), opened from the title.

Same board as round31/33 settings.py (its layout and its `tiles` helper are reused; the rows follow the build's
settings_panel words). Changes, and only these:
  * backdrop = the title's blurred lit city, dimmed (opened from the title: '> TITLE // OPTIONS');
  * designer ruling Q12: RESET TO DEFAULTS resets every tab, so the terminal button reads RESET ALL TABS, with a
    mono line saying so (never a sticker);
  * the one sweep on the screen title sticker is off (nothing to press there); no sticker verb on this page.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image  # noqa: E402

import b44 as K  # noqa: E402
import settings as S33  # noqa: E402  (round33_ui_chrome/scripts/settings.py)

U, SL = K.U, K.SL
STORY = os.path.join(K.CONC, 'round18_combat_fx', 'heat_glitch_storyboard.png')


def main():
    img = K.city_backdrop()
    P = (300, 150, 1620, 1004)
    img = K.darken(img, P, 0.5, 50)
    img = U.term_panel(img, P, 'TITLE  //  OPTIONS', seed=31, alpha=240, glow=0.5)
    st = K.stk('OPTIONS', 66, U.FILL_YELLOW, seed=19)
    img = K.place(img, st, 1440, 150, angle=3)
    img, _ = U.tabs(img, (330, 204), ['ACCESSIBILITY', 'DISPLAY', 'AUDIO', 'CONTROLS', 'LANGUAGE'], 0)
    U.text(img, (1590, 224), '[LB] [RB] switch tab', U.F(U.MONO, 15), (120, 150, 180), 'rm', 0.8)
    U.text(img, (334, 280), 'EFFECTS & MOTION', U.F(U.MONO, 16), U.CYAN, 'la', 2.0)
    rows = [('REDUCE EFFECTS', 'No scanlines, flicker, chromatic or distortion.', False, 'focus'),
            ('REDUCE MOTION', 'No camera moves or parallax; pages cross-fade.', False, None),
            ('FLASH LIMITER', 'At most 3 flashes a second. On by default.', True, None),
            ('HEAT GLITCH', 'Screen-wide Heat distortion, pulsing on Heat events.', True, None),
            ('HIGH CONTRAST', 'Opaque panels, 7:1 text and thick edges.', False, None),
            ('SUBTITLES', 'Every spoken line, with the speaker\'s name.', True, None),
            ('SUBTITLES TYPE IN', 'Off: each line shows at once.', True, None),
            ('ASSIST MODE', 'New campaigns: free nudge, more HP. No ICE records.', False, None)]
    y = 316
    for lab, desc, on, st_ in rows:
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
            img = U.term_panel(img, (650, y + 60, 970, y + 86), None, accent=U.AMBER, hexbg=False, chamfer=6, header=False, glow=0.3)
            U.text(img, (810, y + 73), 'LIMITED: flash limiter on, slow layer only', U.F(U.MONO, 13), U.AMBER, 'mm', 0.3)
            y += 28
        d = U.BD(img)
        d.line([(334, y + 64), (966, y + 64)], fill=U.CYAN + (40,), width=1)
        y += 74
    X = 1010
    U.text(img, (X, 280), 'TEXT SCALE', U.F(U.MONO, 16), U.CYAN, 'la', 2.0)
    img = U.slider(img, (X + 4, 318, X + 470, 338), 0.0, ticks=(0, 0.5, 1), readout='1.0x', labels=('1.0', '1.3', '1.6'))
    pb = (X, 372, 1590, 446)
    img = U.term_panel(img, pb, None, hexbg=False, chamfer=8, header=False, glow=0.2, alpha=200)
    U.text(img, (X + 16, 409), 'The Cell never sleeps. Every word grows with this.', U.F(U.PLEX, 27), U.WHITE, 'lm')
    U.text(img, (X, 476), 'COLOUR-BLIND CORRECTION', U.F(U.MONO, 16), U.CYAN, 'la', 2.0)
    img = S33.tiles(img, (X, 502), [('OFF', 'no correction'), ('DEUTAN', 'green-weak'), ('PROTAN', 'red-weak'), ('TRITAN', 'blue-weak')], 0)
    U.text(img, (X, 576), 'Patterns and glyphs stay the main cue.', U.F(U.PLEX, 17), (150, 166, 186), 'la')
    U.text(img, (X, 612), 'RESOLVE SPEED AFTER SEND IT', U.F(U.MONO, 16), U.CYAN, 'la', 2.0)
    img = S33.tiles(img, (X, 638), [('1x', 'full replay'), ('2x', 'twice as fast'), ('INSTANT', 'results at once')], 0, w=150)
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
    # ------------------------------------------------ footer: RESET ALL TABS (designer ruling), terminal button
    d = U.BD(img)
    d.line([(330, 950), (1590, 950)], fill=U.CYAN + (60,), width=1)
    img = U.term_button(img, (334, 960, 574, 996), 'RESET ALL TABS', None, 'idle')
    U.text(img, (590, 978), 'every tab back to its defaults', U.F(U.MONO, 15), (130, 156, 180), 'lm', 0.6)
    img = U.term_button(img, (880, 960, 1010, 996), 'CLOSE', None, 'idle')
    x = 1080
    for g, s in (('A', 'toggle'), ('B', 'close'), ('Y', 'reset all')):
        d = U.BD(img)
        d.ellipse([x, 965, x + 26, 991], fill=(240, 238, 232, 255), outline=(10, 10, 14, 255), width=2)
        U.text(img, (x + 13, 979), g, U.F(U.BAHN, 16, 'Bold'), (14, 14, 20), 'mm')
        x = U.text(img, (x + 34, 978), s, U.F(U.MONO, 17), U.WHITE, 'lm', 0.8) + 24
    U.text(img, (1590, 250), 'saved to profile', U.F(U.MONO, 15), (120, 150, 180), 'rm', 0.8)
    K.save(img, 'options.png')


if __name__ == '__main__':
    main()
