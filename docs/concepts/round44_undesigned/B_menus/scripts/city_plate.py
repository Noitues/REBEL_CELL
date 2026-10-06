"""Renders the title's lit night city (round 33 title backdrop, locked) once into scratch/city_f00.png.
Reuses round33_ui_chrome/scripts cm.py + roads.py unchanged (imported in place, no bytecode written)."""
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.dirname(HERE)
CONC = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(CONC, 'round33_ui_chrome', 'scripts'))
import cm  # noqa: E402
import roads  # noqa: E402


def main():
    out = os.path.join(B, 'scratch', 'city_f00.png')
    if os.path.exists(out):
        return out
    roads.Network.sky = True
    roads.Network.mixed = True
    s = cm.Scene('night')
    img = s.frame(0, 48, opts=dict(labels=False, hires=True))
    img.save(out)
    print('wrote', out, img.size)
    return out


if __name__ == '__main__':
    main()
