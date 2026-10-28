"""Publish the P2 shared base to D:/rc_scratch/tide_concepts/p2_base/ : graded city (default / decay / lost), masks, heads sheet.
python p2_base.py"""
import os, json, shutil
import numpy as np
from PIL import Image
import p1lib as L, p1_comp as C, p2_grade as G, p2_signs as S, p1_heads

OUT = 'D:/rc_scratch/tide_concepts/p2_base/'
os.makedirs(OUT + 'layers', exist_ok=True)
os.makedirs(OUT + 'heads', exist_ok=True)
W, H = 1920, 1080


def save8(a, f):
    Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8)).save(f)


def city(scn, geo, P, sg, w):
    lightk = np.ones((H, W), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cold = 0.0
    if scn == 'decay':
        for sid in ('t1_a', 't1_b'):
            b = w.sites[sid]['B']
            lightk *= 1 - 0.8 * np.exp(-(np.hypot(xx - b[0], (yy - b[1]) * 1.5) / 110) ** 2)
    if scn == 'lost':
        lightk *= 0.5
        cold = 1.0
    r = G.grade_city(P, geo, lightk=lightk)
    img = r['img'] * (1 - sg['body'][..., None] * .7 * lightk[..., None]) + sg['emis'] * lightk[..., None]
    refl = G.wet_reflect(r['emis'] + sg['emis'] * .5 * lightk[..., None], r['wet'])
    img = img + refl * .9
    if cold:
        lum = img.mean(-1, keepdims=True)
        img = (lum + (img - lum) * 0.7) * np.array([0.9, 0.85, 1.05], np.float32)
    return C.haze(img, strength=.18), r, refl


def main():
    geo = dict(np.load(L.WORK + 'geo.npz'))
    z = np.load(L.WORK + 'recon15.npz'); Pw = z['P']
    sg = S.signs(geo, Pw)
    w = L.load_world()
    Pl = C.load_plate()
    for scn in ('default', 'decay', 'lost'):
        img, r, refl = city(scn, geo, Pl, sg, w)
        save8(C.tone(img), OUT + 'city_%s.png' % scn)
        if scn == 'default':
            np.save(OUT + 'layers/city_default_linear_f16.npy', img.astype(np.float16))
            save8(C.tone(r['emis'] * 1.0), OUT + 'layers/city_emissive.png')
            save8(C.tone(refl), OUT + 'layers/wet_reflection.png')
            save8(r['wet'].astype(np.float32), OUT + 'layers/street_mask.png')
            save8(r['park'].astype(np.float32), OUT + 'layers/park_mask.png')
            save8(r['wm'], OUT + 'layers/warmth_field.png')
    hag = geo['hag']
    h16 = (np.clip(hag, 0, 100) / 100 * 65535).astype(np.uint16)
    Image.fromarray(h16).save(OUT + 'layers/height_above_ground_16.png')
    occ = ((hag > 1.5) & (geo['idm'] == 2)).astype(np.float32)
    save8(occ, OUT + 'layers/occluder_mask.png')
    d = C.depth_norm()
    Image.fromarray((d * 65535).astype(np.uint16)).save(OUT + 'layers/depth_norm_16.png')
    Image.fromarray(geo['idm'].astype(np.uint8) * 30).save(OUT + 'layers/class_id_x30.png')
    save8(sg['body'], OUT + 'layers/sign_plates_mask.png')
    np.savez_compressed(OUT + 'layers/world_pos_f16.npz', P=Pw.astype(np.float16), idm=geo['idm'])
    # heads: 16 headings x D,N,E at 44 px (E 0.852 inside the sprite scale of heads6 via size) + sheet
    sheet = Image.new('RGBA', (16 * 56 + 20, 3 * 56 + 20), (14, 16, 38, 255))
    for ri, t in enumerate('DNE'):
        for ci in range(16):
            ang = ci * 22.5
            sz = 44
            im = p1_heads.sprite(t, ang, sz)
            im.save(OUT + 'heads/%s_%03d.png' % (t, int(ang)))
            sheet.alpha_composite(im, (10 + ci * 56 + (56 - im.width) // 2, 10 + ri * 56 + (56 - im.height) // 2))
    sheet.convert('RGB').save(OUT + 'heads_sheet.png')
    H6 = 'D:/rc_art/art-pass/docs/concepts/tide_raid/H6_heads_final/heads/'
    for f in ('D.svg', 'N.svg', 'E.svg', 'X4.svg'):
        shutil.copy(H6 + f, OUT + 'heads/' + f)
    json.dump(dict(walls=sg['walls'], hero=sg['hero']), open(OUT + 'layers/signs.json', 'w'), default=float)
    print('base ok')


if __name__ == '__main__':
    main()
