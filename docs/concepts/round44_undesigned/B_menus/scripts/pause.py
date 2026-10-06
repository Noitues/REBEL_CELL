"""pause.png + pause_abandon.png (build: PARITY/fixes/PAUSE_b.jpg).

Designer ruling (round 44, overrides REVIEW D13): keep the build's all-sticker pause menu; every option is a
sticker. Rendered in our language:
  * colour carries a role, never decoration: RESUME = yellow (the safe choice, default focus), ABANDON = pink
    (the destructive verb; its confirm carries BURN IT), every other option = neutral white vinyl;
  * size carries the hierarchy: RESUME is the big one, the rest are small plates;
  * focus = the peel-back curl only (ruling 3); one sticker mid-sweep (RESUME);
  * no grease-pencil captions (jokes in pencil are banned); each option's consequence is a mono line under it;
  * ONE terminal panel holds them, with the run line and the campaign code row.
The abandon confirm keeps the round 33 dialog as built: terminal body, yellow CANCEL (default focus: curl) and
pink BURN IT. The menu sits over the paused fight (the screen it pauses), dimmed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import b44 as K  # noqa: E402

U, SL = K.U, K.SL
P = (440, 190, 1480, 850)


def draw_pause(img, focus_resume=True):
    img = K.darken(img, P, 0.5, 40)
    img = U.term_panel(img, P, 'PAUSED  //  NETRUN  //  MERIDIAN FREIGHT  //  LAYER 4 OF 7', seed=48, alpha=240, glow=0.45)
    sub = U.F(U.MONO, 16)
    # left column: RESUME (big, yellow, default focus) + OPTIONS / CODEX (white)
    r = K.stk('RESUME', 92, U.FILL_YELLOW, seed=120, focus=focus_resume, sweep=focus_resume)
    img = K.place(img, r, 700, 330, angle=-2, focus=focus_resume)
    U.text(img, (700, 410), 'back to the fight   [Esc]', sub, (200, 210, 170), 'mm', 0.8)
    o = K.stk('OPTIONS', 44, K.FILL_WHITE, seed=121)
    img = K.place(img, o, 610, 500, angle=2)
    c = K.stk('CODEX', 44, K.FILL_WHITE, seed=122)
    img = K.place(img, c, 800, 500, angle=-3)
    U.text(img, (610, 556), '[O]', sub, (140, 160, 184), 'mm', 0.8)
    U.text(img, (800, 556), '[X]', sub, (140, 160, 184), 'mm', 0.8)
    # right column: ABANDON (pink) + the two QUITs (white)
    d = U.BD(img)
    d.line([(940, 250), (940, 600)], fill=U.CYAN + (50,), width=1)
    rows = [('ABANDON RUN', U.FILL_PINK, 'lose BREAKER 1 + the unbanked  //  Heat +11', (255, 150, 170)),
            ('QUIT TO MAIN MENU', K.FILL_WHITE, 'saved at the last node you cleared', (140, 160, 184)),
            ('QUIT TO DESKTOP', K.FILL_WHITE, 'saved at the last node; closes the game', (140, 160, 184))]
    for k, (w, f, s, sc) in enumerate(rows):
        y = 290 + k * 112
        sd = K.stk(w, 38, f, seed=130 + k)
        img = K.place(img, sd, 976 + K.bw(sd)[0] / 2, y, angle=(-2, 1.5, -1)[k])
        U.text(img, (984, y + 48), s, sub, sc, 'lm', 0.6)
    # campaign code row (terminal)
    d = U.BD(img)
    d.line([(470, 634), (1450, 634)], fill=U.CYAN + (70,), width=1)
    U.text(img, (476, 664), 'CAMPAIGN CODE   (share it: it starts this campaign)', U.F(U.MONO, 16), U.CYAN, 'lm', 1.4)
    d.rectangle([476, 690, 1250, 732], fill=(4, 10, 20, 255), outline=U.CYAN + (140,), width=1)
    U.text(img, (490, 711), 'RC1-meridian-4-20261006-standard-breaker', U.F(U.MONO, 20), (210, 226, 240), 'lm', 0.6)
    img = U.term_button(img, (1266, 690, 1450, 732), 'COPY', None, 'idle')
    U.text(img, (476, 790), 'run 9  //  Heat 58 FLAGGED  //  autosaved 00:42 ago', U.F(U.MONO, 16), (140, 160, 184), 'lm', 0.6)
    img = K.pad_hints(img, 1120, 790, [('A', 'select'), ('B', 'resume')])
    return img


def main():
    img = K.combat_backdrop()
    img = draw_pause(img)
    K.save(img, 'pause.png')
    # ------------------------------------------------ the abandon confirm (round 33 dialog, as built)
    base = K.combat_backdrop()
    base = draw_pause(base, focus_resume=False)
    base = U.grade(base, 0.45, 3, 0.7)
    D = (520, 250, 1400, 760)
    base = K.darken(base, D, 0.5, 30)
    img = U.term_panel(base, D, 'CONFIRM  //  ABANDON RUN', accent=U.HARM, tag='CANNOT UNDO', tag_col=U.HARM, seed=7, alpha=246)
    U.text(img, (560, 320), 'Abandon the run?', U.F(U.PLEX_M, 40), U.WHITE, 'la')
    U.text(img, (560, 380), 'BREAKER 1 is lost for good, with everything unbanked:', U.F(U.PLEX, 24), (205, 212, 226), 'la')
    rows = [('CYCLES', '140'), ('CARDS ADDED', '2'), ('FIRMWARE', '1'), ('DAEMONS', '1')]
    for k, (a, b) in enumerate(rows):
        x = 560 + (k % 2) * 400
        y = 430 + (k // 2) * 34
        U.text(img, (x, y), a, U.F(U.MONO, 20), (150, 176, 200), 'la', 1.2)
        U.text(img, (x + 330, y), b, U.F(U.MONO, 22), U.WHITE, 'ra', 1.0)
    U.text(img, (560, 512), 'HEAT  +11   (operative death, tier 1)', U.F(U.MONO, 22), U.HARM, 'la', 1.0)
    U.text(img, (560, 546), 'Schematics already banked at a Server Rack stay banked.', U.F(U.PLEX, 21), U.GREEN, 'la')
    d = U.BD(img)
    d.line([(540, 588), (1380, 588)], fill=U.HARM + (90,), width=1)
    cancel = K.stk('CANCEL', 50, U.FILL_YELLOW, seed=41, focus=True, curl_px=24)
    burn = K.stk('BURN IT', 58, U.FILL_PINK, seed=40)
    img = K.place(img, cancel, 760, 655, angle=2, focus=True)
    img = K.place(img, burn, 1170, 653, angle=-3)
    U.text(img, (760, 722), 'keep running  [B]', U.F(U.MONO, 16), (170, 190, 210), 'mm', 1.0)
    U.text(img, (1170, 722), 'abandon, lose BREAKER 1  [hold A]', U.F(U.MONO, 16), (255, 150, 170), 'mm', 0.8)
    K.save(img, 'pause_abandon.png')


if __name__ == '__main__':
    main()
