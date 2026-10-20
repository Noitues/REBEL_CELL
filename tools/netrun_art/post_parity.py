"""L3 post parity: one linear HDR frame through the plate post chain (post_aaa "real", stages 6 on) and through Godot's
city_post aaa chain (post_parity_lab), compared stage by stage.

  python -m netrun_art.post_parity prep --npy <combined.npy> --out DIR           writes DIR/frame.f32 (+ frame.json)
  (run post_parity_lab windowed, --in=DIR/frame.f32 --out=DIR/godot)
  python -m netrun_art.post_parity compare --npy <combined.npy> --out DIR        writes DIR/report.json + DIR/sheet.jpg

The plate side runs post_aaa's own helpers (gblur, tonemap, to_srgb, lum; --post-aaa = the storyboard scripts folder on the
art-pass branch) with the terms that need passes Godot has no counterpart for switched off: emit and volume bloom, background
dim, volume composite, rain. "gmath" is the plate chain with Godot's two math choices (luminance-normalised shadow tint, CA on
the HDR input taps), so a diff splits into math choices vs the bloom approximation.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

DEF_POST_AAA = "D:/rc_art/art-pass/docs/concepts/route_map_graph/storyboard/scripts"


def _post_aaa(d):
    sys.dont_write_bytecode = True
    if d not in sys.path:
        sys.path.insert(0, d)
    import post_aaa
    return post_aaa


def plate_chain(A, comb, look, bloom=True, ca=False, gmath=False):
    """post_aaa.finish from stage 6 (exposure) to the CA, with img = comb (no emit / vol / bg passes), grain off."""
    P = dict(A.LOOKS[look])
    H, W = comb.shape[:2]
    sc = W / 2560.0
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    cx, cy = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
    kca = P["ca"] * sc * np.clip(rr - 0.3, 0, 1) ** 1.5

    def samp(ch, s):
        xs = np.clip(np.round(xx + cx * s).astype(np.int32), 0, W - 1)
        ys = np.clip(np.round(yy + cy * s).astype(np.int32), 0, H - 1)
        return ch[ys, xs]

    img = comb * P["exposure"]
    if ca and gmath:
        img = np.stack([samp(img[..., 0], kca), img[..., 1], samp(img[..., 2], -kca)], axis=-1)
    if bloom:
        hot = np.maximum(img - P["bloom_thr"], 0)
        b1 = A.gblur(hot, 6 * sc, 2)
        b2 = A.gblur(hot, 24 * sc, 4)
        b3 = A.gblur(hot, 135 * sc, 8)
        img = img + b1 * P["bloom"][0] + b2 * P["bloom"][1] + b3 * P["bloom"][2]
    out = A.tonemap(img)
    l1 = A.lum(out)[..., None]
    st = np.array(P["shadow_tint"], np.float32)
    if gmath:
        st = st / float(st[0] * 0.2126 + st[1] * 0.7152 + st[2] * 0.0722)
    ht = np.array(P["hi_tint"], np.float32)
    w_sh = np.clip(1 - l1 * 2.2, 0, 1)
    tk = P["tint_k"]
    out = out * (1 - tk * w_sh) + out * st * tk * w_sh
    out = out * (1 - 0.25 * np.clip(l1 * 2 - 0.6, 0, 1)) + out * ht * 0.25 * np.clip(l1 * 2 - 0.6, 0, 1)
    l1 = A.lum(out)[..., None]
    out = np.clip(l1 + (out - l1) * P["sat"], 0, None)
    out = out + np.array(P["lift"], np.float32) * (1 - out)
    out = out * (1 - P["vignette"] * np.clip(rr - 0.35, 0, 1) ** 1.6)[..., None]
    out = A.to_srgb(out)
    out = np.clip(0.18 * np.power(np.maximum(out, 0) / 0.18, P["contrast"]), 0, 1)
    kn = A.KNEE
    out = np.where(out > kn, kn + (0.93 - kn) * np.tanh((out - kn) / (0.93 - kn)), out)
    if ca and not gmath:
        out = np.stack([samp(out[..., 0], kca), out[..., 1], samp(out[..., 2], -kca)], axis=-1)
    return np.clip(out, 0, 1)


def q8(a):
    return (np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)


def load8(p):
    return np.asarray(Image.open(p).convert("RGB"), np.uint8)


def stats(a8, b8, masks):
    d = np.abs(a8.astype(np.int16) - b8.astype(np.int16)).max(axis=-1)
    o = {"mean_255": round(float(d.mean()), 3), "p99_255": int(np.percentile(d, 99)), "max_255": int(d.max()),
         "over_2": round(float((d > 2).mean()), 4)}
    for k, m in masks.items():
        if m.any():
            o[k] = {"px": int(m.sum()), "mean_255": round(float(d[m].mean()), 2), "p99_255": int(np.percentile(d[m], 99))}
    return o


def bloom_energy(full8, nob8):
    """Mean sRGB lift the bloom adds (0..255) and the share of pixels it lifts by more than 2/255."""
    d = full8.astype(np.int16).max(axis=-1) - nob8.astype(np.int16).max(axis=-1)
    return {"mean_lift_255": round(float(d.mean()), 3), "lifted_px": round(float((d > 2).mean()), 4)}


def cmd_prep(a):
    comb = np.load(a.npy).astype(np.float32)
    os.makedirs(a.out, exist_ok=True)
    np.ascontiguousarray(comb[..., :3]).astype("<f4").tofile(os.path.join(a.out, "frame.f32"))
    H, W = comb.shape[:2]
    json.dump({"npy": a.npy, "w": W, "h": H, "max": float(comb.max()), "p99": float(np.percentile(comb, 99))},
              open(os.path.join(a.out, "frame.json"), "w"), indent=1)
    print("POSTPAR prep %dx%d -> %s" % (W, H, a.out))


def cmd_compare(a):
    A = _post_aaa(a.post_aaa)
    comb = np.load(a.npy).astype(np.float32)[..., :3]
    g = os.path.join(a.out, "godot")
    R = {}
    runs = {"nobloom": dict(bloom=False), "full": dict(), "ca": dict(ca=True),
            "nobloom_gm": dict(bloom=False, gmath=True), "full_gm": dict(gmath=True), "ca_gm": dict(ca=True, gmath=True)}
    py = {k: q8(plate_chain(A, comb, a.look, **kw)) for k, kw in runs.items()}
    for k in ("full", "nobloom"):
        Image.fromarray(py[k]).save(os.path.join(a.out, "plate_%s.png" % k))
    l = py["full"].astype(np.float32).max(axis=-1) / 255
    halo = (py["full"].astype(np.int16).max(axis=-1) - py["nobloom"].astype(np.int16).max(axis=-1)) > 2
    masks = {"dark": l < 0.1, "mid": (l >= 0.1) & (l < 0.6), "bright": l >= 0.6, "bloom_halo": halo}
    calib_p = os.path.join(g, "calib.png")
    if os.path.exists(calib_p):
        R["calib_vs_srgb_input"] = stats(load8(calib_p), q8(A.to_srgb(comb)), {})
    for m in ("nobloom", "full", "ca"):
        p = os.path.join(g, m + ".png")
        if not os.path.exists(p):
            continue
        gd = load8(p)
        R[m] = {"vs_plate": stats(gd, py[m], masks), "vs_plate_gmath": stats(gd, py[m + "_gm"], masks),
                "plate_vs_plate_gmath": stats(py[m], py[m + "_gm"], masks)}
    gf, gn = os.path.join(g, "full.png"), os.path.join(g, "nobloom.png")
    if os.path.exists(gf) and os.path.exists(gn):
        R["bloom_energy"] = {"plate": bloom_energy(py["full"], py["nobloom"]), "godot": bloom_energy(load8(gf), load8(gn))}
    gg = os.path.join(g, "grain.png")
    if os.path.exists(gg) and os.path.exists(gf):
        dg = load8(gg).astype(np.float32) - load8(gf).astype(np.float32)
        R["grain_sd_255"] = {"godot": round(float(dg[..., 1].std()), 2),
                             "plate_nominal": round(A.LOOKS[a.look]["grain"] * 255, 2)}
    json.dump(R, open(os.path.join(a.out, "report.json"), "w"), indent=1)
    print(json.dumps(R, indent=1))
    if os.path.exists(gf):
        gd = load8(gf)
        d = np.abs(gd.astype(np.int16) - py["full"].astype(np.int16)).max(axis=-1)
        heat = np.clip(d * 8, 0, 255).astype(np.uint8)
        heat = np.stack([heat, heat // 3, heat // 6], axis=-1)
        top = np.concatenate([py["full"], gd], axis=1)
        bot = np.concatenate([heat, heat * 0], axis=1)
        if os.path.exists(gn):
            hb = (np.clip(np.abs(load8(gn).astype(np.int16) - py["nobloom"].astype(np.int16)).max(axis=-1) * 8, 0, 255)).astype(np.uint8)
            bot = np.concatenate([heat, np.stack([hb, hb // 3, hb // 6], axis=-1)], axis=1)
        Image.fromarray(np.concatenate([top, bot], axis=0)).save(os.path.join(a.out, "sheet.jpg"), quality=90)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prep", "compare"])
    ap.add_argument("--npy", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--look", default="real")
    ap.add_argument("--post-aaa", default=DEF_POST_AAA)
    a = ap.parse_args()
    {"prep": cmd_prep, "compare": cmd_compare}[a.cmd](a)


if __name__ == "__main__":
    main()
