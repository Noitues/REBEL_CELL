"""P2 compositor: graded city (warm / cool, signage, wet street) + pressure (creep, dread) + Blender layers (ghost / occluded / spill) + atmosphere.
compose(beat, **opts) -> float32 linear (H,W,3)."""
import sys, json, numpy as np
from PIL import Image
import p1lib as L
import p1_comp as C
import p2_grade as G
import p2_signs as S
import p2_press as PR

CREEP = {'plan': 30.0, 'forecast': 34.0, 'reveal': 38.0, 'impact': 42.0, 'home_hit': 46.0, 'aftermath': 52.0}
DREAD = {'plan': 0.62, 'forecast': 0.66, 'reveal': 0.55, 'impact': 0.40, 'home_hit': 0.45}
_cache = {}


def static():
    if 'geo' not in _cache:
        _cache['geo'] = dict(np.load(L.WORK + ('geo.npz' if C.S == 1 else 'geo30.npz')))
        _cache['sg'] = S.signs(_cache['geo'], np.load(L.WORK + C.REC)['P'])
        _cache['P'] = C.load_plate()
    return _cache['geo'], _cache['sg'], _cache['P']


def yellow_mask(e):
    mn = np.minimum(e[..., 0], e[..., 1]); mx = np.maximum(e[..., 0], e[..., 1])
    ok = (mn > 0.7 * mx) & (e[..., 2] < 0.55 * mn) & (mx > 0.05)
    return C.blur(ok.astype(np.float32), 1.5)


def hcap(x, cap):
    """hue-preserving highlight cap: scale each pixel so its max channel never exceeds cap (smooth knee at 0.6 cap)."""
    m = x.max(-1, keepdims=True)
    t = cap * 0.6
    new = np.where(m > t, t + (cap - t) * (1 - np.exp(-(m - t) / max(cap - t, 1e-6))), m)
    return x * (new / np.maximum(m, 1e-6))


def compose(beat, ghost_k=0.8, spill_k=1.0, bloom_k=1.0, haze_k=0.18, streak_k=0.22, flash_k=0.0, plate_k=1.0, creep=None, dread_k=None,
            refl_k=0.9, e_bloom=0.6, home_bloom=1.0, burn=None, cap_occ=None, cap_spill=None):
    geo, sg, P = static()
    lay = C.layers(beat)
    ui = json.load(open(C.WB + beat + '/ui.json'))
    rp = ui.get('route_px', {})
    rd = C.route_distance(list(rp.values())) if rp else None
    occ = lay['world_occ']; gh = lay['world_ghost']
    if cap_occ:
        occ = occ.copy(); gh = gh.copy()
        occ[..., :3] = hcap(occ[..., :3], cap_occ)
        gh[..., :3] = hcap(gh[..., :3], cap_occ)
    if cap_spill:
        lay['spill'] = lay['spill'].copy()
        lay['spill'][..., :3] = hcap(lay['spill'][..., :3], cap_spill)
    ho = lay.get('heads_occ'); hg = lay.get('heads_ghost')
    gA = np.clip(gh[..., 3:4] - occ[..., 3:4], 0, 1)
    corr = np.clip(C.blur(gA[..., 0], 7) * 1.6, 0, 1)
    r = G.grade_city(P, geo, route_dist=rd, corridor=corr)
    img = r['img'] * (1 - sg['body'][..., None] * .7) + sg['emis']
    cr = CREEP.get(beat) if creep is None else creep
    hair = None
    if cr:
        img, hair = PR.creep(img, geo, cr)
    if burn:
        img = PR.burn_marks(img, burn)
    img = C.haze(img, strength=haze_k)
    dk = DREAD.get(beat, 0.0) if dread_k is None else dread_k
    if dk and ui.get('heads'):
        hr = []
        for h in ui['heads']:
            if h.get('rid') in rp and h.get('k', 1.0) >= 0.9:
                hr.append((h['rid'], h['s']))
        # head s is arclength in the route's screen polyline units (R.cs), same as route_px (R.sp[cs>=0])
        if hr:
            dm = PR.dread(hr, rp, k=dk)
            img = img * (1 - dm[..., None])
    img = img + lay['spill'][..., :3] * spill_k
    gA3 = gA
    ghost_rgb = gh[..., :3] * gA3 * ghost_k
    hA = None
    if hg is not None:
        hA = np.clip(hg[..., 3:4] - ho[..., 3:4], 0, 1)
        ghost_rgb = ghost_rgb + hg[..., :3] * hA * ghost_k
    img = img + ghost_rgb
    rib_e = occ[..., :3] + ghost_rgb * 0.6
    refl = G.wet_reflect(r['emis'] * 0.0 + rib_e * 0.55 + sg['emis'] * 0.0, r['wet'], k=refl_k)
    img = img + refl
    img = img * (1 - occ[..., 3:4]) + occ[..., :3]
    if ho is not None:
        img = img * (1 - ho[..., 3:4]) + ho[..., :3]
    emis = occ[..., :3] + (ho[..., :3] if ho is not None else 0) + ghost_rgb * 0.6
    em2 = np.maximum(emis - 0.35, 0)
    ym = yellow_mask(em2)[..., None]
    hm = np.zeros((C.H, C.W), np.float32)
    ui_home = ui.get('home_px')
    hp = np.array([ui_home]) if ui_home else None
    bl = C.bloom(em2 * (1 - ym)) + e_bloom * C.bloom(em2 * ym)
    if hp is not None:
        yy, xx = (np.mgrid[0:C.H, 0:C.W].astype(np.float32) / C.S)
        hm = np.exp(-(np.hypot(xx - hp[0, 0], (yy - hp[0, 1]) * 1.4) / 150) ** 2)
        bl = bl * (1 + (home_bloom - 1) * hm[..., None])
    img = img + bl * bloom_k
    if hair is not None:
        img = img + C.bloom(hair) * 0.9
    if streak_k:
        img = img + C.vstreak(em2 * (1 - 0.4 * ym), k=streak_k)
    if flash_k:
        img = img + C.hstreak(np.maximum(emis - 3.0, 0), k=flash_k)
    glow = C.blur(em2.mean(-1), 16)
    rain = C.rain_layer()[..., None] * np.array([.55, .7, 1.0], np.float32)
    img = img + rain * (0.5 + 7.0 * glow[..., None]) * (1 - 0.5 * C.depth_norm()[..., None])
    img = C.tiltshift(img)
    return img


if __name__ == '__main__':
    beat = sys.argv[1]
    img = compose(beat)
    out = C.tone(img)
    Image.fromarray((out * 255 + .5).astype(np.uint8)).save(C.WORK + beat + '/comp3d.png')
    print('ok')
