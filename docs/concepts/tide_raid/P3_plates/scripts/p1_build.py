"""compose a beat's 3D layers over the graded Godot plate (linear light). compose(beat, **opts) -> float32 linear (H,W,3)
python p1_build.py <beat> -> WORK/<beat>/comp3d.png (no UI)"""
import sys, json, numpy as np
from PIL import Image
import p1lib as L
import p1_comp as C


def compose(beat, ghost_k=0.8, spill_k=1.0, bloom_k=1.0, grade=None, haze_k=0.18, streak_k=0.22, flash_k=0.0, plate_k=1.0, moon_k=1.0, bloom_layer=None):
    P = C.load_plate()
    lay = C.layers(beat)
    ui = json.load(open(C.WORK + beat + '/ui.json'))
    rp = list(ui.get('route_px', {}).values())
    rd = C.route_distance(rp) if rp else None
    occ = lay['world_occ']; gh = lay['world_ghost']
    ho = lay.get('heads_occ'); hg = lay.get('heads_ghost')
    gA = np.clip(gh[..., 3:4] - occ[..., 3:4], 0, 1)
    hA = np.clip(hg[..., 3:4] - ho[..., 3:4], 0, 1) if hg is not None else None
    corr = np.clip(C.blur(gA[..., 0], 7) * 1.6, 0, 1)
    img = C.grade_plate(P, rd, corridor=corr, **(grade or {})) * plate_k
    img = C.haze(img, strength=haze_k)
    img = img + lay['spill'][..., :3] * spill_k
    ghost_rgb = gh[..., :3] * gA * ghost_k
    if hg is not None:
        ghost_rgb = ghost_rgb + hg[..., :3] * hA * ghost_k
    img = img + ghost_rgb
    img = img * (1 - occ[..., 3:4]) + occ[..., :3]
    if ho is not None:
        img = img * (1 - ho[..., 3:4]) + ho[..., :3]
    emis = occ[..., :3] + (ho[..., :3] if ho is not None else 0) + ghost_rgb * 0.6
    em2 = np.maximum(emis - 0.35, 0)
    img = img + C.bloom(em2) * bloom_k
    if streak_k:
        img = img + C.vstreak(em2, k=streak_k)
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
