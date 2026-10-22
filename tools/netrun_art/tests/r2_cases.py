"""Street r2 test inputs derived from a plan: the facade-kit cases (one face per kit building of the camera row, plus variants and the roof
clutter of each), shared by the fixture generator, the Python tests and the live golden test (the GDScript twin reads the same cases
from `fixtures/r2/inputs/s1_kits.json`)."""
from typing import Any, Dict, List

from netrun_art.r2.streams import art_seed

KIT_SEED = 1


def _face(plan: Dict[str, Any], ff: Dict[str, Any]):
    axis, out = plan["axis"], ff["out"]
    if axis == 1:
        return [ff["face"], ff["u0"]], [ff["face"], ff["u1"]], out, 0.0
    return [ff["u0"], ff["face"]], [ff["u1"], ff["face"]], 0.0, out


def kit_cases(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Cases for `kit_face` / `roof_clutter`: every kit building of the camera row (rhythm record and window module of the plan), then four
    variants of the first building of each kit (no rhythm, lite, lit_low 3 for the atrium, a face that starts above the ground), then the
    roof clutter of every kit building."""
    cases: List[Dict[str, Any]] = []
    first: Dict[str, Dict[str, Any]] = {}
    for ff in plan["front_faces"]:
        uid = ff["uid"]
        kit = plan["kits"].get(uid)
        if kit in (None, "concrete_band") or uid not in plan["rhythm"]:
            continue
        a, c, nx, ny = _face(plan, ff)
        col = [v * 0.5 for v in plan["trims"][uid]["col"]]
        base = dict(op="face", kit=kit, a=a, c=c, z0=0.0, z1=ff["top"], nx=nx, ny=ny, col=col, module=plan["modules"].get(uid, 0),
                    seed=art_seed(KIT_SEED, "kitface", uid), uid=uid)
        cases.append(dict(base, rh=plan["rhythm"][uid]))
        first.setdefault(kit, dict(base, rh=plan["rhythm"][uid]))
    for kit in sorted(first):
        b = first[kit]
        cases.append(dict(b, rh=None, seed=art_seed(KIT_SEED, "kitface", b["uid"], "norh")))
        cases.append(dict(b, lite=True, seed=art_seed(KIT_SEED, "kitface", b["uid"], "lite")))
        cases.append(dict(b, z0=3.8, z1=b["z1"] + 3.8, lit_low=3, seed=art_seed(KIT_SEED, "kitface", b["uid"], "high")))
    for ff in plan["front_faces"]:
        uid = ff["uid"]
        kit = plan["kits"].get(uid)
        if kit in (None, "concrete_band"):
            continue
        d = 5.0                      # the roof is the face footprint, 5 BU deep behind the street face
        lo, hi = sorted((ff["face"], ff["face"] - d * ff["out"]))
        if plan["axis"] == 1:
            x0, x1, y0, y1 = lo, hi, ff["u0"], ff["u1"]
        else:
            x0, x1, y0, y1 = ff["u0"], ff["u1"], lo, hi
        cases.append(dict(op="roof", kit=kit, top=[[x0, y0], [x1, y0], [x1, y1], [x0, y1]], zt=ff["top"], seed=art_seed(KIT_SEED, "roof", uid), uid=uid))
    return cases


def pack(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Cases for a fixture file: the u64 `seed` as a decimal string (JSON numbers stop being exact at 2**53)."""
    return [dict(c, seed=str(c["seed"])) for c in cases]


def unpack(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Inverse of `pack`."""
    return [dict(c, seed=int(c["seed"])) for c in cases]


def signs_min(plan: Dict[str, Any]) -> Dict[str, Any]:
    """The part of a plan the sign textures read: each sign's id, colour, rectangle and texture request."""
    keys = ("id", "col", "u0", "u1", "z0", "z1", "tex")
    return dict(signs=[{k: s[k] for k in keys} for s in plan["signs"]])


def pack_signs(plan: Dict[str, Any]) -> Dict[str, Any]:
    """`signs_min` with the texture seeds as decimal strings."""
    p = signs_min(plan)
    for s in p["signs"]:
        s["tex"] = dict(s["tex"], seed=str(s["tex"]["seed"]))
    return p


def unpack_signs(p: Dict[str, Any]) -> Dict[str, Any]:
    """Inverse of `pack_signs`."""
    out = dict(signs=[dict(s, tex=dict(s["tex"], seed=int(s["tex"]["seed"]))) for s in p["signs"]])
    return out


# ---------------------------------------------------------------- stream vectors (the Mersenne Twister contract of the GDScript twin)
STREAM_OPS = ["random", "random", "randrange:7", "randrange:1", "randrange:2", "randrange:3", "randrange:100000", "randint:2:9", "randint:-3:3",
              "uniform:1:2.5", "uniform:0:25", "choice:5", "choice:10", "choices:3:1,1,2", "choices:4:5,1,1,1", "sample:5:2", "sample:6:3",
              "random", "randrange:12", "randrange:70000"] + ["random"] * 2 + ["randrange:624"] * 40
# seed: decimal string of the u64; seed_type "int" (the plate's art seeds) or "str" (a seed that is a text)
STREAM_CASES = [
    dict(seed="1", seed_type="int", stream="frontage", keys=["1_2"]),
    dict(seed="2", seed_type="int", stream="kit", keys=["3_44"]),
    dict(seed="1", seed_type="int", stream="lamp", keys=[12.3, -1]),
    dict(seed="1", seed_type="int", stream="lamp", keys=[-30.04996, 1]),
    dict(seed="1", seed_type="int", stream="tex", keys=["9:5", "shopsign"]),
    dict(seed="18446744073709551615", seed_type="int", stream="rhythm", keys=["a:b"]),
    dict(seed="9223372036854775808", seed_type="int", stream="module", keys=["c:3"]),
    dict(seed="4294967296", seed_type="int", stream="spikes", keys=["x"]),
    dict(seed="12345678901234567890", seed_type="str", stream="props", keys=["q", 7]),
    dict(seed="0", seed_type="int", stream="s", keys=[]),
]
# raw seeds for random.Random itself (no stream key): small, 32-bit edge, 64-bit
RAW_SEEDS = ["0", "1", "4294967295", "4294967296", "12297829382473034410", "18446744073709551615"]


def run_ops(r, ops: List[str]) -> List[Any]:
    """Draw from a generator by op strings; floats come back as hex strings (exact), samples as lists."""
    from netrun_art.r2.canon import hexf
    out: List[Any] = []
    for op in ops:
        n, *a = op.split(":")
        if n == "random":
            out.append(hexf(r.random()))
        elif n == "randrange":
            out.append(r.randrange(int(a[0])))
        elif n == "randint":
            out.append(r.randint(int(a[0]), int(a[1])))
        elif n == "uniform":
            out.append(hexf(r.uniform(float(a[0]), float(a[1]))))
        elif n == "choice":
            out.append(r.choice(list(range(int(a[0])))))
        elif n == "choices":
            out.append(r.choices(list(range(int(a[0]))), weights=[float(x) for x in a[1].split(",")])[0])
        elif n == "sample":
            out.append(r.sample(list(range(int(a[0]))), int(a[1])))
        else:
            raise ValueError(op)
    return out


def stream_vectors() -> Dict[str, Any]:
    """The expected record of every stream case: the key text, the u64 art seed (decimal string) and the draws."""
    import random
    from netrun_art.r2 import streams
    rows = []
    for cs in STREAM_CASES:
        seed: Any = int(cs["seed"]) if cs["seed_type"] == "int" else cs["seed"]
        r = streams.rng(seed, cs["stream"], *cs["keys"])
        rows.append(dict(key_text=streams.key_text(seed, cs["stream"], *cs["keys"]), art_seed=str(streams.art_seed(seed, cs["stream"], *cs["keys"])),
                         draws=run_ops(r, STREAM_OPS)))
    raw = [dict(seed=s, draws=run_ops(random.Random(int(s)), STREAM_OPS)) for s in RAW_SEEDS]
    return dict(streams=rows, raw=raw)
