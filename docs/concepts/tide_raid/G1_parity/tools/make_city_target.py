"""Builds the city-only graded target: the offline plate pipeline (P3 scripts, read only) run on the Godot raid capture with NO beams, UI or pressure layers.
That is what the live city has to match per band, without the HUD, beams, rings and tiles the plates add on top. Written as a file on purpose (no python from stdin).
usage: python make_city_target.py <out.png> [beat]   (beat: add that plate beat's Blender light-spill layer, the beams' light on the city, but none of the beams, UI or pressure layers)   (needs the P3 work dir D:/rc_scratch/tide_concepts/p3_work)"""
import sys

sys.dont_write_bytecode = True
SCRIPTS = "D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/scripts"
sys.path.insert(0, SCRIPTS)
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

import p1lib as L  # noqa: E402
import p1_comp as C  # noqa: E402
import p2_grade as G  # noqa: E402
import p2_signs as S  # noqa: E402
import p3_look as P3  # noqa: E402
import p1_final as F  # noqa: E402


def main() -> None:
    out = sys.argv[1]
    geo = dict(np.load(L.WORK + "geo.npz"))
    Pw = np.load(L.WORK + C.REC)["P"]
    sg = S.signs(geo, Pw)
    import os
    if os.environ.get('BASE_IMG'):
        P = C.lin(np.asarray(Image.open(os.environ['BASE_IMG']).convert('RGB'), np.float32) / 255)
    else:
        P = C.load_plate()
    hp = P3.hero_pack(geo, Pw)
    r = G.grade_city(P, geo)
    img = r["img"] * (1 - sg["body"][..., None] * .7) + sg["emis"]
    img = img * (1 - hp["mul"][..., None]) + (hp["emis"] + hp["rim"])
    img = img * (1 - 0.8 * hp["ink"][..., None])
    shaft = P3.shafts(img, 0.0, None, hp["src"], k=0.7)
    img = C.haze(img, strength=0.18) + shaft
    refl = P3.wet2(r["emis"] * 0.8 + sg["emis"] * 0.7 + hp["emis"] * 0.6, r["wet"], k=1.0)
    img = img + refl
    if len(sys.argv) > 2:
        lay = C.layers(sys.argv[2], passes=('spill',))
        img = img + lay['spill'][..., :3]
    em2 = np.maximum(r["emis"] + sg["emis"] + hp["emis"] - 0.35, 0)
    img = img + C.bloom(em2) * 0.5
    glow = C.blur(em2.mean(-1), 16)
    rain = C.rain_layer()[..., None] * np.array([.55, .7, 1.0], np.float32)
    img = img + rain * (0.5 + 7.0 * glow[..., None]) * (1 - 0.5 * C.depth_norm()[..., None])
    img = C.tiltshift(img)
    res = F.finish(C.tone(img))
    Image.fromarray((res * 255 + .5).astype(np.uint8)).save(out)
    print("target written", out)


if __name__ == "__main__":
    main()
