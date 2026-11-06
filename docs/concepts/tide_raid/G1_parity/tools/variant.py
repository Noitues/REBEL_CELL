"""Writes a variant of the grade config: python variant.py <base.tres> <out.tres> key=value ...  (numbers only; overrides appended / replaced). No python from stdin."""
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, "D:/rc_art/godot_look_tide/tools/look_parity")
import tune

base, out = sys.argv[1], sys.argv[2]
ov = tune.read_overrides(base)
for a in sys.argv[3:]:
    k, v = a.split("=")
    ov[k] = float(v)
tune.write_tres(base, ov, out)
