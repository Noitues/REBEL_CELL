"""bd2_solve.py [key ...] : solve the stage-2 room grade (review 2.8, rb2-1) per room on the extracted current p1 board.
Shared recipe (SHARED) + the step6-1 per-room chroma / contrast / pink pull + one solved number per room: ceil (the luma shoulder's
ceiling), bisected so the rb_checks room region's p95 L* on p1 is P95_TARGET.  The room mean follows the shoulder (the bright half of the
room carries the mean of luminance); it is then checked on the room regions of all five beats (p1, p2, p2b, p3, nowords masks) and, if
any beat reads below MEAN_MIN_BEATS, tone_lo steps up 0.02 (max TONE_LO_MAX) and ceil is re-solved.
Meridian's room is the shop (the kit's only room without a Solace sign) under the Meridian corp light.
Writes work/bd2_params.json {key: params} and work/bd2_solve_report.json."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
import numpy as np
import bd2_lib as L
import bd_grade as BG
import rb_tokens as TK

P95_TARGET = 38.0        # below the occupied-NOW glass floor L* 40 by 2 (rb_checks gate: p95 + 1 <= reference); other beats read up to +0.7
MEAN_MIN_BEATS = 28.6    # ROOM_MEAN_L floor 28 + 0.6
MEAN_MAX_BEATS = 33.4    # ROOM_MEAN_L ceiling 34 - 0.6
TONE_LO_MAX = 0.25
SPILL_L = 0.38           # luma (sRGB-encoded) of the spill colour taken from the room's own key light
BEATS = ('p1', 'p2', 'p2b', 'p3', 'nowords')
SHARED = dict(
    cx=1500.0, cy=600.0, rx=330.0, ry=270.0, f0=0.85, f1=1.55,
    hull_poly=[[1195, 488], [1465, 338], [1792, 523], [1792, 672], [1512, 808], [1195, 632]], pf0=10.0, pf1=3.0,
    hull_blur=0.4, mid_blur=1.6, city_blur=4.0, blur_reach=40.0,
    neon_chroma=0.8, city_chroma=0.3, pivot=0.16,
    hull_value=0.8, city_value=0.6,
    tone_lo=0.17, tone_hi=0.38, tone_s=0.09, tone_blur=14.0, tone_gmax=3.5, tone_out=0.45, tone_d0=1.5, tone_d1=2.6,
    knee=0.24, ceil=0.35,
    haze=0.05, haze_out=0.5, haze_rgb=[20, 18, 34], sp0=1.0, sp1=2.6,
    vignette=0.1, v0=0.9, v1=2.6, board_falloff=0.08, bx0=700.0, bx1=1250.0)
MERIDIAN_LIGHT = dict(hue_lo=88.0, hue_hi=162.0, hue_f=14.0, hue_to=20.0, hue_amt=0.88, chroma=1.05, neon_chroma=0.9)
JOBS = [(r, 'neutral', r) for r in L.ROOMS] + [('bio', 'solace', 'bio_solace_check'), ('shop', 'meridian', 'shop_meridian')]
REGS = {s: L.room_region(s) for s in BEATS}


def make_eval(room, corp, P):
    pre = BG.grade_pre(L.bare(room), P)
    F, T = L.fg(corp)

    def ev(P2, beats=('p1',)):
        bd = np.clip(L.G2().scrim(BG.grade_post(pre, P2), 'P'), 0, 255)
        Y = TK.lum(np.clip(F + T * bd, 0, 255).astype(np.float64))
        Ls = TK.lstar(Y)
        return {s: (float(TK.lstar(Y[REGS[s]].mean())), float(np.percentile(Ls[REGS[s]], 95))) for s in beats}
    return ev


def solve(room, corp):
    P = dict(SHARED)
    old = BG.ROOMS_STEP61[room]
    P.update(chroma=old['chroma'], contrast=old['contrast'], pink_chroma=old['pink_chroma'])
    if corp == 'meridian':
        P.update(MERIDIAN_LIGHT)
    P['spill_rgb'] = L.spill_rgb(room, lum_target=SPILL_L, P=P)
    ev = make_eval(room, corp, P)
    while True:
        lo, hi = P['knee'] + 0.01, 0.50
        for _ in range(12):
            P['ceil'] = round(0.5 * (lo + hi), 4)
            if ev(P)['p1'][1] < P95_TARGET:
                lo = P['ceil']
            else:
                hi = P['ceil']
        P['ceil'] = round(lo, 4)
        allb = ev(P, BEATS)
        mins = min(v[0] for v in allb.values())
        print(room, corp, 'tone_lo', P['tone_lo'], 'ceil', P['ceil'], {k: (round(a, 2), round(b, 2)) for k, (a, b) in allb.items()}, flush=True)
        if mins >= MEAN_MIN_BEATS or P['tone_lo'] >= TONE_LO_MAX:
            break
        P['tone_lo'] = round(P['tone_lo'] + 0.02, 3)
    return P, allb


if __name__ == '__main__':
    only = sys.argv[1:]
    out_f = L.HERE + 'work/bd2_params.json'
    rep_f = L.HERE + 'work/bd2_solve_report.json'
    try:
        OUT = json.load(open(out_f))
    except Exception:
        OUT = {}
    try:
        REP = json.load(open(rep_f))
    except Exception:
        REP = {}
    for room, corp, key in JOBS:
        if only and key not in only:
            continue
        if key == 'bio_solace_check':          # Solace uses the bio grade; this job only measures it on the Solace board
            P = OUT['bio']
            allb = make_eval(room, corp, P)(P, BEATS)
        else:
            P, allb = solve(room, corp)
            OUT[key] = P
        REP[key] = dict(room=room, corp=corp, ceil=P['ceil'], tone_lo=P['tone_lo'], beats={k: dict(mean=round(a, 2), p95=round(b, 2)) for k, (a, b) in allb.items()})
        json.dump(OUT, open(out_f, 'w'), indent=1)
        json.dump(REP, open(rep_f, 'w'), indent=1)
    for k, v in REP.items():
        print('%-18s ceil %.4f tone_lo %.3f  %s' % (k, v['ceil'], v['tone_lo'], ' '.join('%s %.1f/%.1f' % (b, x['mean'], x['p95']) for b, x in v['beats'].items())))
