# Copied verbatim from C:/Users/noitu/Documents/Godot/rebel_cell/.claude/worktrees/art-pass/docs/concepts/HANDOFF_PACKAGE/na02/seeds_ref.py (2026-10-18). Frozen NA-02 reference; do not edit.
"""Reference art-seed hash for the NA-02 contract (C3). Pure Python, no deps.

python seeds_ref.py  -> writes na02_vectors.json next to this file.
"""
import json
import os

FNV_OFF = 0xCBF29CE484222325
FNV_PRIME = 0x100000001B3
M64 = (1 << 64) - 1


def fnv1a64(data: bytes) -> int:
    h = FNV_OFF
    for b in data:
        h = ((h ^ b) * FNV_PRIME) & M64
    return h


def art_seed(layout_seed: int, stream: str, *keys) -> int:
    for k in keys:
        if isinstance(k, float) or isinstance(k, bool) or not isinstance(k, (int, str)):
            raise TypeError("keys are int or str only")
    arr = [str(layout_seed), "art/" + stream, *keys]
    return fnv1a64(json.dumps(arr, separators=(",", ":"), ensure_ascii=True).encode("utf-8"))


def splitmix64(state: int):
    """Yields (next_state, value)."""
    while True:
        state = (state + 0x9E3779B97F4A7C15) & M64
        z = state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
        yield z ^ (z >> 31)


def uniform(x: int) -> float:
    return (x >> 11) * (2.0 ** -53)


CASES = [
    (0, "building", ["0:0"]),
    (1, "building", ["12:7"]),
    (1, "building", ["hq:meridian"]),
    (424242, "room_wall", ["n3"]),
    (424242, "lanes_tile", [4, 9]),
    (18446744073709551615, "scene", []),
    (9007199254740993, "hero_sign", [2]),
    (77, "variance", ["7:3"]),
    (77, "key_landmark.tethys", ["21:14", 0]),
    (123456789, "fauna.tethys", [-3, "pod"]),
    (5, "beams", ["\u00e9t\u00e9"]),
]

if __name__ == "__main__":
    out = []
    for ls, st, ks in CASES:
        s = art_seed(ls, st, *ks)
        g = splitmix64(s)
        draws = [next(g) for _ in range(3)]
        out.append({"layout_seed": str(ls), "stream": st, "keys": ks, "seed": str(s),
                    "splitmix64_first3": [str(d) for d in draws], "uniform_first": round(uniform(draws[0]), 12)})
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "na02_vectors.json")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(p, len(out))
