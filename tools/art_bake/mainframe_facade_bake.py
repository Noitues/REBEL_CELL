"""ART-9 4A: bakes the MAINFRAME shop's F1b Tenement facade (day / night / rain) for the game.

Uses the round 33 generator scripts on tag `art-concepts-r43`
(docs/concepts/round33_mainframe_sign/scripts: scene.py + flib.py for Blender 5.2 headless, post.py,
flicker_sign.py for the sign textures). Extract them first, e.g.

    git archive -o %TEMP%/a4a/gen.tar art-concepts-r43 docs/concepts/round33_mainframe_sign
    tar -xf %TEMP%/a4a/gen.tar -C %TEMP%/a4a/gen

then run (as a file, never `python -`):

    python tools/art_bake/mainframe_facade_bake.py --gen %TEMP%/a4a/gen/docs/concepts/round33_mainframe_sign/scripts
        --scratch %TEMP%/a4a/bake [--states day,night,rain] [--post-only]

Per state it renders the facade three times with the same seed (dark sign, blue sign + blue spill,
red sign + red spill) and writes, at 1280x720 under assets/backdrops/shop/:
    facade_<state>.webp            the facade with the sign dark (rain streaks left out: the game
                                   draws them moving)
    facade_<state>_spill_blue.webp the blue sign's light on the walls, street and puddles (added)
    facade_<state>_spill_red.webp  the same for the Cell's red sign
The game adds a spill layer times its level over the dark facade (MainframeFacade), which is the
round 33 composite `dark + a * (normal - dark)`.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'assets', 'backdrops', 'shop')
BLENDER = r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
GAME = (1280, 720)
SPILL = {'blue': '#3a7dff', 'red': '#ff2a2a'}
# How bright a spill layer is stored (the game multiplies it back): headroom for 8 bits.
SPILL_GAIN = 1.0


def sign_textures(gen: str, scratch: str) -> dict:
    sys.path.insert(0, gen)
    import flicker_sign as FS  # noqa: E402
    s = FS.FlickerSign('mainframe')
    paths = {}
    FS.SIGN_PAL = 'blue'
    paths['blue'] = os.path.join(scratch, 'tex_blue.png')
    FS.save_rgba(s.state_normal(), paths['blue'])
    FS.SIGN_PAL = 'red'
    paths['red'] = os.path.join(scratch, 'tex_red.png')
    FS.save_rgba(s.state_normal(), paths['red'])
    paths['dark'] = os.path.join(scratch, 'tex_dark.png')
    FS.save_rgba(s.render(frame=0.0, traces=0.0), paths['dark'])
    return paths


def render(gen: str, scratch: str, state: str, variant: str, sign_png: str) -> str:
    """One facade render; every variant of a state shares the file name (post.py seeds by it)."""
    d = os.path.join(scratch, variant)
    os.makedirs(d, exist_ok=True)
    pre = os.path.join(d, 'f1b_' + state)
    env = dict(os.environ, MF_VAR='b', MF_PCT='100', MF_SAMPLES='48', MF_SIGN_PNG=os.path.abspath(sign_png),
               MF_SPILL_K='1.0' if variant != 'dark' else '0.0')
    if variant in SPILL:
        env['MF_SPILL'] = SPILL[variant]
    else:
        env.pop('MF_SPILL', None)
    with open(pre + '_log.txt', 'w') as log:
        subprocess.run([BLENDER, '-b', '--factory-startup', '--python', os.path.join(gen, 'scene.py'), '--', 'f1',
                        state, pre], env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    return pre


def post(gen: str, pre: str, state: str) -> np.ndarray:
    sys.path.insert(0, gen)
    import post as P  # noqa: E402
    P.ST[state] = dict(P.ST[state], rain=0)   # rain streaks move in the game (MainframeFacade)
    out = pre + '.png'
    P.run(pre, state, out)
    return np.asarray(Image.open(out).convert('RGB'), np.float32) / 255.0


def save(a: np.ndarray, name: str, quality: int) -> None:
    im = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).resize(GAME, Image.LANCZOS)
    im.save(os.path.join(OUT, name), 'WEBP', quality=quality, method=6)
    print('wrote', name, os.path.getsize(os.path.join(OUT, name)) // 1024, 'KB', flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--gen', required=True)
    ap.add_argument('--scratch', required=True)
    ap.add_argument('--states', default='day,night,rain')
    ap.add_argument('--post-only', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    tex = sign_textures(a.gen, a.scratch)
    for state in a.states.split(','):
        imgs = {}
        for variant in ('dark', 'blue', 'red'):
            pre = os.path.join(a.scratch, variant, 'f1b_' + state)
            if not a.post_only:
                pre = render(a.gen, a.scratch, state, variant, tex[variant])
            imgs[variant] = post(a.gen, pre, state)
            print('rendered', state, variant, flush=True)
        save(imgs['dark'], 'facade_%s.webp' % state, 86)
        for v in ('blue', 'red'):
            save(np.clip(imgs[v] - imgs['dark'], 0, 1) * SPILL_GAIN, 'facade_%s_spill_%s.webp' % (state, v), 80)


if __name__ == '__main__':
    main()
