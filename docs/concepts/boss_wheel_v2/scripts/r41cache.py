"""Boss Wheel v2: cache the round 41 pieces used read-only (player wheel at combat size, HUD plate).

python r41cache.py
Writes to D:/rc_scratch/boss_wheel_v2/r41/: player_typ.png (+ centre json), hud_jpg.png, clean_meridian.png.
Round 41 code is imported, never edited.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
R41 = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\round41_wheel_stack\scripts"
OUT = r"D:\rc_scratch\boss_wheel_v2\r41"
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, R41)
_cwd = os.getcwd()
os.chdir(R41)
import combat41 as C41  # noqa: E402
import combat42 as C42  # noqa: E402
import specs14 as S  # noqa: E402
import sat2 as S2  # noqa: E402
os.chdir(_cwd)


def main():
    os.chdir(R41)
    clean, jpg = C41.base_plate()
    clean.save(os.path.join(OUT, "clean_meridian.png"))
    jpg.save(os.path.join(OUT, "hud_jpg.png"))
    P = S.player()
    img, cc, al = C42.wheel(P, S2.BOTNET_DRONE, False, True, C41.PLAYER["r"], 0.0, None, 1.0)
    img.save(os.path.join(OUT, "player_typ.png"))
    json.dump(dict(cx=cc[0], cy=cc[1]), open(os.path.join(OUT, "player_typ.json"), "w"))
    # the current boss (The Manifest) for the v1 reference
    B, bm = S.boss("meridian", 1)
    img, cc, al = C42.wheel(B, C41.COURIER, False, False, C41.BOSS["r"], 0.0, None, 1.0)
    img.save(os.path.join(OUT, "boss_manifest.png"))
    json.dump(dict(cx=cc[0], cy=cc[1]), open(os.path.join(OUT, "boss_manifest.json"), "w"))
    print("ok")


if __name__ == "__main__":
    main()
