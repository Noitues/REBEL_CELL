"""E10-equivalent configs for the tower core + the render pipeline with hooks (wheel_core design harness)."""
import sys, os, math, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import build10 as B
from build10 import *
import wc_tower as T
import slicelib as SL
import roster_wheel as RW_
import cv_over as O
import cv_board as CB9
CACHE = 'D:/rc_scratch/combat_redesign/locked/wheel/cache/'
os.makedirs(CACHE, exist_ok=True)
ROOM = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v2/room_bio_bare.png'


def frame_cur(over, d, ss, cx, cy):
    for rr in (RS['s1'] / T.KE + 2, RS['hp0'] / T.KE - 1):
        d.ellipse([cx - rr * ss, cy - rr * ss, cx + rr * ss, cy + rr * ss], outline=tuple(int(v * 0.8) for v in CYAN) + (255,), width=ss)


def hub_cur(over, d, ss, cx, cy, nowords):
    RW_.CX, RW_.CY = cx / ss, cy / ss
    RW_.draw_hub(over, d, None, ss, RS['hub'] / T.KE, CYAN, RW_.CLASS_STYLE['breaker']['emblem'], '' if nowords else 'Breaker', '')


def icons_cur(canvas, ss, cx, cy, s, t):
    prog, _ = T.SLC[t]
    SL.R_IN, SL.R_OUT = T.R_IN_M, T.R_OUT_M
    blk = SL.shadowed(SL.icon_block(prog, None, 60, ss, 1.0, 1.0, 'SHIELD' if t == 'SHIELD' else None), ss)
    rc = (T.R_IN_M + 0.55 * (T.R_OUT_M - T.R_IN_M)) * ss
    mid = 60 * s
    bx = cx + rc * math.sin(math.radians(mid)); by = cy - rc * math.cos(math.radians(mid))
    SL.paste_rgba(canvas, blk, bx - blk.width / 2, by - blk.height / 2)


def cur_cfg():
    return dict(tile=dict(), frame=frame_cur, hub=hub_cur, icons=icons_cur, icon_dims=(52, 52))


def get_state(beat, show=None):
    key = {'p1': 'f1', 'nowords': 'f1', 'p2': 'f2', 'p2b': 'f1', 'p3': 'f2'}[beat]
    f = json.loads(json.dumps(J[key]))
    if show:
        show(f)
    return f


def board_cached(beat, f):
    keep = beat == 'p2'
    nm = 'bd_%s_%s_%s.npy' % ('f2' if beat in ('p2', 'p3') else 'f1', int(keep), int(beat == 'nowords'))
    p = CACHE + nm
    if os.path.exists(p):
        return Image.fromarray(np.load(p), 'RGBA')
    NOW['words'] = beat != 'nowords'
    CB9.HUB['name'] = 'Breaker' if beat != 'nowords' else ''
    b = render_board(board_frame(J['f2' if beat in ('p2', 'p3') else 'f1'], keep_all=keep), CONS)
    np.save(p, np.asarray(b))
    return b


def backdrop_room():
    return Image.open(ROOM).convert('RGBA')


HOOK = {}


def hk(name, default):
    return HOOK.get(name) or default


def B_p3_lines(L, f):
    for e_ in f['log']:
        if e_[0] == 'fire' and e_[3] is not None:
            s_, dep_ = e_[1], e_[5]
            L.line([ppx(C, RS['s1'] + 3, 60 * s_ + 3), pt(CB.ring_geom(dep_)[0] + 20, 60 * s_, 6)], CYAN + (170,), 2.4, dash=(5, 6))


def render(beat='p1', sel=None, core='e10', cfg=None, show=None, state=None):
    """RGBA 1920x1080 plate, no HUD.  sel: hook name -> callable."""
    HOOK.clear(); HOOK.update(sel or {})
    reg_reset()
    NOW['words'] = beat != 'nowords'
    f = state if state is not None else get_state(beat, show)
    bg = backdrop_room()
    board = board_cached(beat, f)
    dim_ids = [u['id'] for u in f['units'] if u['id'] != J['hover']['id']] if beat == 'p2b' else None
    gb = grade_units(board, f, keep_all=(beat == 'p2'), dim_ids=dim_ids)
    if core == 'wc':
        tw = T.render_core(f['wheel'], cfg or cur_cfg(), ss=3, nowords=(beat == 'nowords'))
        m = Image.new('L', (W, H), 0)
        ImageDraw.Draw(m).ellipse([C[0] - 160, C[1] - 160, C[0] + 160, C[1] + 160], fill=255)
        m = ImageChops.multiply(m.filter(ImageFilter.GaussianBlur(0.6)), tw.split()[3])
        gb.paste(tw, (0, 0), m)
    sh = np.asarray(gb.split()[3], np.float32)
    sh = np.asarray(Image.fromarray(sh.astype(np.uint8)).filter(ImageFilter.GaussianBlur(14)), np.float32) / 255
    sh = np.roll(np.roll(sh, 10, 0), 6, 1)
    a = np.asarray(bg, np.float32); a[..., :3] *= (1 - 0.38 * sh[..., None]); bg = Image.fromarray(a.astype(np.uint8), 'RGBA')
    bg.alpha_composite(gb)
    L = L2()
    hk('hp_ring', O.hp_ring)(L, f['hp'], f['pv']['hp_after'], f['maxhp'])
    if cfg and cfg.get('post_frame'):
        cfg['post_frame'](L)
    bezel9(L, f['schedule'])
    O.sector_digits(L)
    occ = {(u['dep'], q) for u in f['units'] for q in sectors(u)}
    for d in range(3):
        for q in range(6):
            if (d, q) not in occ:
                O.cell_border(L, d, q, alpha=70)
    wave_arcs10(L, arcs_data(f))
    ward_arc(L, f)
    hk('slice_stage', tower_slice_bars)(L, f)
    if beat in ('p1', 'nowords', 'p2b'):
        hk('threat_trim', threat_trim)(L, f)
    dim = None
    if beat == 'p2b':
        hv = J['hover']
        Ld = L2(); draw_units(Ld, f, skip={hv['id']}); dim = Ld.done()
        dim.putalpha(dim.split()[3].point(lambda v: int(v * 0.36)))
        Lh = L2(); draw_units(Lh, f, only={hv['id']})
        cell_outline(Lh, [u for u in f['units'] if u['id'] == hv['id']][0], col=YEL, w=5)
        L.im.alpha_composite(Lh.im)
    else:
        draw_units(L, f)
    adjuster_body(L, f['adj'])
    if beat in ('p1', 'nowords'):
        hk('guns', gun_tracers10)(L, f)
    elif beat == 'p3':
        hk('p3guns', B_p3_lines)(L, f)
    elif beat == 'p2':
        hk('p2guns', lambda L, f: None)(L, f)
    landing_arcs(L, f, only=({J['hover']['id']} if beat == 'p2b' else None))
    ring_tags(L, f)
    hk('nudge', nudge_ghost)(L)
    if beat in ('p2', 'p3'):
        twist_badge(L, f); refund_marks(L, f)
    if beat == 'p2':
        for tr in J['trigs']:
            trigger_paths(L, f, dict(tr, entries=[e for e in tr['entries'] if e[0] != 'refund']))
    if beat == 'p2b':
        hover_path(L, f)
    for fn in HOOK.get('extras', []):
        fn(L, f)
    if dim is not None:
        bg.alpha_composite(dim)
    bg.alpha_composite(L.done())
    return bg


def crop(im, box, k=2):
    c = im.crop(box).convert('RGB')
    return c.resize((c.width * k, c.height * k), Image.LANCZOS)


if __name__ == '__main__':
    import time
    t = time.time()
    a = render('p1', core='e10'); print(time.time() - t)
    b = render('p1', core='wc'); print(time.time() - t)
    o = 'D:/rc_scratch/e10_design/wheel_core/'
    crop(a, (356, 360, 716, 720), 2).save(o + 't_e10_c.png')
    crop(b, (356, 360, 716, 720), 2).save(o + 't_wc_c.png')
