"""Render the helix sprite + preview, crop the sprite to its bounds and write anchor.json.

  python build_helix.py [samples]      (default 32; R2E_TMP picks the temp folder)

Outputs in ..:
  helix_rgba.png   transparent sprite, city pixel scale (px_per_unit = S of city.py default_cam)
  anchor.json      base centre in sprite px, and where to paste the sprite in city_day.png px
  helix_preview.png  3/4 perspective close-up on a neutral backdrop
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
SAMPLES = sys.argv[1] if len(sys.argv) > 1 else "32"
TMP = tempfile.mkdtemp(prefix="r2hx_", dir=os.environ.get("R2E_TMP"))


def blender(*a):
    with open(os.path.join(TMP, a[0] + ".log"), "w") as f:
        subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "helix_scene.py"), "--", *a],
                       stdout=f, stderr=subprocess.STDOUT, timeout=900, check=True)


raw, meta_p = os.path.join(TMP, "raw.png"), os.path.join(TMP, "meta.json")
blender("sprite", raw, meta_p, SAMPLES)
blender("preview", os.path.join(ROOT, "helix_preview.png"), SAMPLES)
meta = json.load(open(meta_p))
im = Image.open(raw).convert("RGBA")
x0, y0, x1, y1 = im.getbbox()
pad = 4
x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
x1, y1 = min(im.width, x1 + pad), min(im.height, y1 + pad)
im.crop((x0, y0, x1, y1)).save(os.path.join(ROOT, "helix_rgba.png"), optimize=True)
off_x, off_y = meta["canvas_offset_in_city_px"]          # canvas (0,0) sits at this city pixel
bcx, bcy = meta["base_center_canvas_px"]
anchor = {
    "sprite": "helix_rgba.png",
    "sprite_size": [x1 - x0, y1 - y0],
    "base_center_sprite_px": [round(bcx - x0, 2), round(bcy - y0, 2)],
    "base_center_city_px": [round(meta["base_center_city_px"][0], 2), round(meta["base_center_city_px"][1], 2)],
    "paste_topleft_city_px": [off_x + x0, off_y + y0],
    "note": "Image.alpha_composite / paste the sprite with its top-left at paste_topleft_city_px (it may be "
            "negative: the tower rises above the frame). The base centre is the helix axis at ground level "
            "(city units x=43.4, y=1.9, z=0) projected with city.py default_cam; the podium (r=6.4, h=1.2) "
            "replaces the Pillow plaza.",
    "px_per_unit": meta["px_per_unit"],
    "projection": meta["projection"],
    "axis_city_units": meta["axis_city_units"],
}
json.dump(anchor, open(os.path.join(ROOT, "anchor.json"), "w"), indent=2)
print(json.dumps(anchor, indent=2))
shutil.rmtree(TMP, ignore_errors=True)
