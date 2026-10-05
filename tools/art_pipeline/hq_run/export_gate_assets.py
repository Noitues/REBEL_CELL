"""ART-8 8w: the Central Server gate's art-pass assets (bible 4.9), exported by the art pass's own generator.

  python tools/art_pipeline/hq_run/export_gate_assets.py [--src <dir>]

Runs art-concepts-r43:docs/concepts/round38_landing_exploits/scripts/exploits.py UNCHANGED (its drawing code) and
saves what the gate screen needs, at the generator's 2x (sticker_lib19.SS):
  assets/hq_run/keycards/<corp>_<intel|breach|virus>.png   the Exploit keycard stickers (exploits.card)
  assets/hq_run/breach_off.png, breach_on.png               the BREACH vinyl, grey (not ready) and pink (ready)
  assets/hq_run/manifest.json                               rebel_cell.art_export/1 (source, settings, files)
The wrapper only points the generator's font paths at this repo's copies (assets/fonts: the same OFL faces) and its
output at a temp folder; nothing is redrawn. `--src` reuses an already extracted copy of the tag's concepts folder.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

TAG = "art-concepts-r43"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "assets", "hq_run")
# The tag's content/ too: the generator's modules read it at import (tresdata, the round 23 wheel sheets).
PATHS = ["docs/concepts/round38_landing_exploits/scripts", "docs/concepts/round17_slice_system/glyphs", "content"]
KIND_FILES = ["intel", "breach", "virus"]  # exploits.KINDS order


def git(*args):
    return subprocess.run(["git", "-C", ROOT] + list(args), check=True, capture_output=True, text=True).stdout.strip()


def extract(dst):
    tar = os.path.join(dst, "src.tar")
    git("archive", "-o", tar, TAG, *PATHS)
    subprocess.run(["tar", "-xf", tar, "-C", dst], check=True)
    return os.path.join(dst, "docs", "concepts")


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


TRIM_PAD = 4  # px kept round a sticker's own alpha (its die-cut border and shadow) when the padding is cut away


def trim(img):
    """The sticker cut out of the generator's padded canvas (its alpha box + TRIM_PAD): a crop, nothing redrawn."""
    box = img.getchannel("A").getbbox()
    if box is None:
        return img
    return img.crop((max(0, box[0] - TRIM_PAD), max(0, box[1] - TRIM_PAD), min(img.width, box[2] + TRIM_PAD),
                     min(img.height, box[3] + TRIM_PAD)))


def main():
    argv = sys.argv[1:]
    tmp = tempfile.mkdtemp(prefix="a8w_gate_")
    concepts = argv[argv.index("--src") + 1] if "--src" in argv else extract(tmp)
    scripts = os.path.join(concepts, "round38_landing_exploits", "scripts")
    sys.path.insert(0, scripts)
    os.chdir(scripts)
    import sticker_lib19 as SL
    fonts = os.path.join(ROOT, "assets", "fonts")
    SL.ANTON = os.path.join(fonts, "Anton-Regular.ttf")
    SL.MARKER = os.path.join(fonts, "PermanentMarker-Regular.ttf")
    SL.PLEX = os.path.join(fonts, "IBMPlexSansCondensed-Medium.ttf")
    SL.MONO = os.path.join(fonts, "ShareTechMono-Regular.ttf")
    import exploits as EX
    from PIL import Image

    os.makedirs(os.path.join(OUT, "keycards"), exist_ok=True)
    files = []
    for corp in sorted(EX.CORPS):
        for k, kind in enumerate(KIND_FILES):
            sd = EX.card(k, corp)
            rel = "keycards/%s_%s.png" % (corp, kind)
            trim(sd["img"]).save(os.path.join(OUT, rel), optimize=True)
            files.append(rel)
    blank = Image.new("RGBA", (EX.W, EX.H), (0, 0, 0, 0))
    for state in ("off", "on"):
        EX.breach_button(blank.copy(), state)
        rel = "breach_%s.png" % state
        trim(EX._BT[state]["img"]).save(os.path.join(OUT, rel), optimize=True)
        files.append(rel)
    src_files = [os.path.join(scripts, f) for f in ("exploits.py", "sticker_lib19.py")]
    manifest = {
        "schema": "rebel_cell.art_export/1",
        "asset": "central_server_gate",
        "about": "ART-8 8w (bible 4.9). Built by tools/art_pipeline/hq_run/export_gate_assets.py; do not edit by hand.",
        "source": {
            "script": "tools/art_pipeline/hq_run/export_gate_assets.py",
            "generator": "%s:docs/concepts/round38_landing_exploits/scripts/exploits.py @ %s" % (TAG, git("rev-list", "-n", "1", TAG)),
            "functions": ["exploits.card(kind, corp)", "exploits.breach_button(state)"],
            "commit": git("rev-parse", "HEAD"),
            "generator_sha256": {os.path.basename(p): sha(p) for p in src_files},
            "scripts_sha256": sha(os.path.abspath(__file__)),
        },
        "settings": {"scale": "2x (sticker_lib19.SS)", "fonts": "assets/fonts (the generator's OFL faces)",
                     "kinds": KIND_FILES, "corps": sorted(EX.CORPS)},
        "files": [{"path": f, "bytes": os.path.getsize(os.path.join(OUT, f)), "sha256": sha(os.path.join(OUT, f))} for f in files],
    }
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)
    os.chdir(ROOT)
    shutil.rmtree(tmp, ignore_errors=True)
    print("DONE", len(files), "files")


if __name__ == "__main__":
    main()
