"""Round 9 MANHUNT variants M9a SEALED / M9b SPOOF / M9c BOTH (frames on concept_m9_base; rules in ghost2.py).
render_all loads concept_m9a / m9b / m9c, which pick VARIANT and call frames(VARIANT)."""
from __future__ import annotations

from r2_kit import *  # noqa: F403
from concept_h7_bastion import signed_coin
import concept_m9_base as B
import ghost2 as G2

NAMES = {"sealed": "M9a MANHUNT SEALED r9", "spoof": "M9b MANHUNT SPOOF r9", "both": "M9c MANHUNT SEALED+SPOOF r9"}


def plan_for(v):
    if v == "sealed":
        return B.best_sealed(), None
    if v == "spoof":
        e, a, sp, hit, miss = B.best_spoof()
        return a, sp
    _, a = B.best_both()
    return a, B.react_plan(a)[B.REVEAL][0]


def outcome_row(d, x, y, label_col, vals, title):
    B_panel = (x, y, x + 520, y + 64 + 50 * len(vals))
    panel(d, B_panel)
    text(d, (x + 14, y + 10), title, 15, DIM)
    for i, (glyph, v) in enumerate(vals):
        yy = y + 50 + i * 50
        glyph(d, (x + 40, yy + 10))
        signed_coin(d, (x + 120, yy - 4), int(round(v)), 26)


def cand_glyph(i):
    def g(d, c):
        x, y = c
        d.line([(x - 22, y), (x + 22, y)], fill=THREAT_LIGHT, width=4)
        disc(d, (x + 34, y), i + 1, THREAT)
    return g


def press_glyph(hit):
    def g(d, c):
        x, y = c
        d.rounded_rectangle((x - 24, y - 12, x + 24, y + 12), radius=4, outline=STAMP_CLEAN if hit else DIM, width=3)
        if hit:
            check(d, (x + 40, y), 10, STAMP_CLEAN)
        else:
            pencil_x(d, (x + 40, y), 10, DMG)
    return g


def frames(v):
    name = NAMES[v]
    alloc, sp = plan_for(v)

    def f1():
        notes = {"sealed": "One beam is SEALED: three faint candidates.", "spoof": "One SPOOF press in reserve.",
                 "both": "Sealed beam + one spoof press in reserve."}
        return B.frame_contact(name, notes[v])

    def f2():
        img, d = new_frame(name, "plan")
        B.contact_hud(d)
        if v == "spoof":
            B.network(d, alloc, b2=B.CANDS[0], spoof=sp)
        else:
            B.network(d, alloc, cands=True, hunter=False)
        B.tray(d, 860, 100, alloc)
        if v != "sealed":
            panel(d, (860, 250, 1190, 330))
            d.rounded_rectangle((880, 270, 980, 310), radius=6, fill=(40, 44, 70), outline=STAMP_CLEAN, width=3)
            text(d, (930, 279), "SPACE", 18, STAMP_CLEAN, anchor="ma")
            text(d, (1000, 280), "x1", 20, INK, "mono")
        notes = {"sealed": "plan against three possible beam-2 lines (faint, numbered on the first)",
                 "spoof": "plan with the spoof: the teal ring is where you intend to land it",
                 "both": "plan against three candidates; the spoof stays in reserve for after the reveal"}
        header(d, name, 2, "Plan (scarce: 1 ghost costs +5 Heat, 1 decoy costs 3, go dark costs income): " + notes[v])
        return img

    def f3():
        img, d = new_frame(name, "forecast")
        B.contact_hud(d)
        if v == "sealed":
            B.network(d, alloc, cands=True, hunter=False)
            vals = [(cand_glyph(i), G2.outcome(B.ASSETS, B.B1, c, B.OWN3, alloc)) for i, c in enumerate(B.CANDS)]
            outcome_row(d, 720, 100, None, vals, "IF BEAM 2 IS")
            e = B.ev_sealed(alloc)
            note = f"each candidate's exact result ({', '.join(f'{x:+.0f}' for _, x in vals)}); the reveal decides which"
        elif v == "spoof":
            B.network(d, alloc, b2=B.CANDS[0], spoof=sp)
            hit = G2.outcome(B.ASSETS, B.B1, B.CANDS[0], B.OWN3, alloc, sp)
            miss = G2.outcome(B.ASSETS, B.B1, B.CANDS[0], B.OWN3, alloc)
            outcome_row(d, 720, 100, None, [(press_glyph(True), hit), (press_glyph(False), miss)], "SPOOF")
            note = f"exact: landed {hit:+.0f}, missed {miss:+.0f}; the press decides"
        else:
            B.network(d, alloc, cands=True, hunter=False)
            rp = B.react_plan(alloc)
            vals = []
            for i, (s, h, m) in enumerate(rp):
                vals.append((cand_glyph(i), h))
            outcome_row(d, 720, 100, None, vals, "IF BEAM 2 IS (+ your best spoof)")
            note = "per candidate, the result with your best reaction (" + ", ".join(f"{h:+.0f} / {m:+.0f} missed" for _, h, m in rp) + ")"
        header(d, name, 3, "Forecast: " + note)
        return img

    def f4():
        img, d = new_frame(name, "playout")
        B.contact_hud(d)
        b2 = B.CANDS[B.REVEAL]
        faded = [i for i in range(len(B.CANDS)) if i != B.REVEAL]
        if v == "sealed":
            B.network(d, alloc, b2=b2, cands=True, faded=faded)
            note = "beam 2 unseals (candidate 1 lights, the others fade); the hunter follows"
        elif v == "spoof":
            B.network(d, alloc, b2=b2, spoof=sp)
            note = "the beam reaches the spoof node: press SPACE in the teal window"
        else:
            B.network(d, alloc, b2=b2, cands=True, faded=faded, spoof=sp)
            note = "beam 2 unsealed; now spend the spoof where it matters on THIS line (teal)"
        step_track(d, 760, 470, 400, 3, 2, "BEAM")
        speed_controls(d, 760, 510)
        if v != "sealed":
            d.rounded_rectangle((760, 570, 1160, 620), radius=10, fill=(40, 44, 70), outline=CELL, width=3)
            d.rectangle((760 + 170, 574, 760 + 230, 616), fill=(90, 220, 200))
        header(d, name, 4, "Playout: " + note)
        return img

    def f5():
        b2 = B.CANDS[B.REVEAL]
        return B.aftermath(name, alloc, b2, spoof=sp if v != "sealed" else None,
                           note="(spoof landed)" if v != "sealed" else "(zero input)")

    return [f1, f2, f3, f4, f5], B.MOMENTS
