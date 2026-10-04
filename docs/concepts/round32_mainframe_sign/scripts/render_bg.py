"""Render the F1b night facade backdrops with a given sign texture + spill (Blender, then post).
Usage: python render_bg.py <name> <sign_rgba.png> <spill_hex|-> <spill_k>  -> ../scratch/bg_<name>.png
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.abspath(os.path.join(HERE, '..', 'scratch'))
BL = r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'


def render(name, sign_png, spill, k):
    env = dict(os.environ, MF_VAR='b', MF_PCT='100', MF_SAMPLES='48', MF_SIGN_PNG=os.path.abspath(sign_png),
               MF_SPILL_K=str(k))
    if spill != '-':
        env['MF_SPILL'] = spill
    else:
        env.pop('MF_SPILL', None)
    pre = os.path.join(SCR, 'bg_' + name)
    with open(pre + '_log.txt', 'w') as log:
        subprocess.run([BL, '-b', '--factory-startup', '--python', os.path.join(HERE, 'scene.py'), '--', 'f1',
                        'night', pre], env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    subprocess.run([sys.executable, os.path.join(HERE, 'post.py'), pre, 'night', pre + '.png'], check=True)
    for ext in ('_beauty.npy', '_id.npy', '_nrm.npy', '_beauty.exr', '_id.exr', '_nrm.exr'):
        try:
            os.remove(pre + ext)
        except OSError:
            pass
    return pre + '.png'


if __name__ == '__main__':
    render(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]))
