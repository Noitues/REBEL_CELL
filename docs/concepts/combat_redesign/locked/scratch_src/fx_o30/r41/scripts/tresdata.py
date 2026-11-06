"""Read the real roster data from content/*.tres (Godot text resources), read-only.

Gives plain dicts: classes (wheel slots, hub core, inner ring, hp) and enemies
(wheel, pointers, orbit, resistance, spawns, boss phases).
"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
CONTENT = os.path.join(ROOT, "content")

SLICE_TYPES = ["ATTACK", "CRIT", "DEFEND", "EVADE", "SHIELD", "DEPLOY", "HEAL", "AFFLICT", "MISS"]
PROGRAM_OF = {"ATTACK": "EXPLOIT", "CRIT": "ZERO-DAY", "DEFEND": "FIREWALL", "EVADE": "PROXY",
              "SHIELD": "SANDBOX", "DEPLOY": "TROJAN", "HEAL": "PATCH", "AFFLICT": "VIRUS", "MISS": "NULL"}
POINTER_BEHAVIOR = ["FIXED", "MULTIPLY", "MIGRATE", "ORBIT"]


class Ref:
    def __init__(self, kind, rid):
        self.kind, self.id = kind, rid

    def __repr__(self):
        return "%s(%s)" % (self.kind, self.id)


def _parse_value(s, i=0):
    """Tiny recursive parser for the subset of Variant syntax used in content/."""
    def ws(i):
        while i < len(s) and s[i] in " \t\r\n,":
            i += 1
        return i

    i = ws(i)
    c = s[i]
    if c == '"':
        j = i + 1
        out = []
        while s[j] != '"':
            if s[j] == "\\":
                j += 1
            out.append(s[j])
            j += 1
        return "".join(out), j + 1
    if c == "&" and s[i + 1] == '"':
        v, j = _parse_value(s, i + 1)
        return v, j
    if c == "[":
        arr = []
        i += 1
        while True:
            i = ws(i)
            if s[i] == "]":
                return arr, i + 1
            v, i = _parse_value(s, i)
            arr.append(v)
    if c == "{":
        j = s.index("}", i)
        return {}, j + 1
    m = re.match(r"[-+]?\d+\.?\d*(e[-+]?\d+)?", s[i:])
    if m:
        t = m.group(0)
        return (float(t) if ("." in t or "e" in t) else int(t)), i + len(t)
    m = re.match(r"[A-Za-z_][A-Za-z0-9_]*", s[i:])
    name = m.group(0)
    j = i + len(name)
    if name in ("true", "false"):
        return name == "true", j
    if name == "null":
        return None, j
    if s[j] == "[":  # typed array Array[Type]([...])
        depth = 0
        while True:
            if s[j] == "[":
                depth += 1
            elif s[j] == "]":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
    if j < len(s) and s[j] == "(":
        j += 1
        args = []
        while True:
            j = ws(j)
            if s[j] == ")":
                j += 1
                break
            v, j = _parse_value(s, j)
            args.append(v)
        if name in ("ExtResource", "SubResource"):
            return Ref(name, args[0]), j
        if name.startswith("Packed"):
            return list(args), j
        if name == "Array":
            return args[0] if args else [], j
        return (name, args), j
    return name, j


def load_tres(path):
    txt = open(path, encoding="utf-8").read()
    ext, sub, res = {}, {}, {}
    cur = None
    lines = txt.splitlines()
    k = 0
    while k < len(lines):
        ln = lines[k].strip()
        k += 1
        if not ln or ln.startswith(";"):
            continue
        if ln.startswith("[ext_resource"):
            rid = re.search(r'id="([^"]+)"', ln).group(1)
            p = re.search(r'path="([^"]+)"', ln).group(1)
            ext[rid] = p
            cur = None
            continue
        if ln.startswith("[sub_resource"):
            rid = re.search(r'id="([^"]+)"', ln).group(1)
            cur = sub.setdefault(rid, {})
            continue
        if ln.startswith("[resource]"):
            cur = res
            continue
        if ln.startswith("[gd_resource"):
            continue
        if cur is not None and "=" in ln:
            key, val = ln.split("=", 1)
            val = val.strip()
            # multi-line values (rare): join until brackets balance
            while val.count("(") > val.count(")") or val.count("[") > val.count("]"):
                val += lines[k].strip()
                k += 1
            try:
                cur[key.strip()] = _parse_value(val)[0]
            except Exception:
                cur[key.strip()] = val
    return dict(ext=ext, sub=sub, res=res, path=path)


_cache = {}


def res_path(p):
    return os.path.join(ROOT, p.replace("res://", ""))


def load(p):
    p = res_path(p) if p.startswith("res://") else p
    if p not in _cache:
        _cache[p] = load_tres(p)
    return _cache[p]


def deref(doc, v):
    """Resolve a Ref to (doc, props)."""
    if isinstance(v, Ref):
        if v.kind == "SubResource":
            return doc, doc["sub"][v.id]
        p = doc["ext"][v.id]
        d2 = load(p)
        return d2, d2["res"]
    return doc, v


def slice_info(doc, slot_ref):
    d, slot = deref(doc, slot_ref)
    d2, sl = deref(d, slot["slice"])
    st = SLICE_TYPES[sl.get("slice_type", 0)]
    sid = sl.get("id")
    out = dict(id=sid, name=sl.get("display_name"), type=st, value=sl.get("base_output", 0),
               program=PROGRAM_OF[st], special=None, badge=None)
    # extra effects -> special glyph / badge
    extra = sl.get("extra_effects", [])
    for te in extra:
        d3, t = deref(d2, te)
        for fx in t.get("effects", []):
            d4, f = deref(d3, fx)
            ftype = f.get("type", 0)
            if ftype == 10:
                out["badge"] = "+%dR" % f.get("amount", 1)
            elif ftype == 13:
                out["badge_ram"] = f.get("amount", 1)
    if sid in ("tariff", "citation", "solar_flare", "dose"):
        out["special"] = sid
    if sid and sid.endswith("_drain"):
        out["badge"] = "-RAM"
    if sid == "tariff":
        out["value"] = out.get("badge_ram", 3)
        out["badge"] = None
    return out


def wheel_info(doc, wref):
    d, w = deref(doc, wref)
    slots = [slice_info(d, s) for s in w.get("slots", [])]
    hub = None
    if "hub" in w and w["hub"] is not None:
        dh, h = deref(d, w["hub"])
        hub = dict(id=h.get("id"), name=h.get("display_name"), desc=h.get("description"))
    ring = None
    if w.get("inner_ring") is not None:
        ring = ring_info(d, w["inner_ring"])
    return dict(slots=slots, count=w.get("slice_count", 6), pointers=w.get("pointer_ticks", [0]),
                resistance=w.get("passive_resistance", 0), orbit=w.get("pointer_orbit_per_turn", 0),
                hub=hub, ring=ring)


def ring_info(doc, rref):
    d, r = deref(doc, rref)
    segs = []
    for s in r.get("segments", []):
        d2, sg = deref(d, s)
        segs.append(sg.get("id") or os.path.basename(d2["path"]).replace(".tres", ""))
    if not segs or any(x is None for x in segs):
        segs = []
        for s in r.get("segments", []):
            p = d["ext"][s.id] if isinstance(s, Ref) and s.kind == "ExtResource" else ""
            segs.append(os.path.basename(p).replace(".tres", ""))
    return segs


def load_class(cid):
    doc = load(os.path.join(CONTENT, "classes", cid + ".tres"))
    r = doc["res"]
    w = wheel_info(doc, r["starting_wheel"])
    ring = None
    for rr in r.get("rank_rewards", []):
        d2, rk = deref(doc, rr)
        if rk.get("inner_ring") is not None:
            ring = ring_info(d2, rk["inner_ring"])
    return dict(id=cid, name=r.get("display_name"), desc=r.get("description"), hp=r.get("base_hp"),
                wheel=w, ring=ring)


def load_enemy(eid):
    doc = load(os.path.join(CONTENT, "enemies", eid + ".tres"))
    r = doc["res"]
    w = wheel_info(doc, r["wheel"])
    spawns = []
    for s in r.get("spawns", []):
        d2, sp = deref(doc, s)
        d3, sat = deref(d2, sp["satellite"])
        spawns.append(dict(id=sat.get("id"), name=sat.get("display_name"), hp=sat.get("hp"),
                           max_active=sp.get("max_active", 1), every_n=sp.get("every_n", 1),
                           trigger=sp.get("trigger", 0), dock=sp.get("dock_slot", -1)))
    phases = []
    for ph in r.get("phases", []):
        d2, p = deref(doc, ph)
        pw = wheel_info(d2, p["wheel_override"]) if p.get("wheel_override") is not None else None
        psp = []
        for s in p.get("spawns", []):
            d3, sp = deref(d2, s)
            d4, sat = deref(d3, sp["satellite"])
            psp.append(dict(id=sat.get("id"), name=sat.get("display_name"), hp=sat.get("hp"),
                            max_active=sp.get("max_active", 1)))
        hub = None
        if p.get("hub_override") is not None:
            dh, h = deref(d2, p["hub_override"])
            hub = dict(id=h.get("id"), name=h.get("display_name"), desc=h.get("description"))
        phases.append(dict(threshold=p.get("hp_threshold_pct", 0.5),
                           behavior=POINTER_BEHAVIOR[p.get("pointer_behavior", 0)],
                           pointers=p.get("pointer_ticks", []), orbit=p.get("orbit_ticks_per_turn", 0),
                           wheel=pw, hub=hub, spawns=psp, line=p.get("phase_line", "")))
    role = "Boss" if r.get("is_boss") else ("Elite" if r.get("is_elite") else "Regular")
    return dict(id=eid, name=r.get("display_name"), desc=r.get("description"), corp=r.get("corporation_id"),
                hp=r.get("hp"), role=role, wheel=w, spawns=spawns, phases=phases)


def all_enemies():
    out = []
    for f in sorted(os.listdir(os.path.join(CONTENT, "enemies"))):
        if f.endswith(".tres"):
            out.append(load_enemy(f[:-5]))
    return out


if __name__ == "__main__":
    for c in ["breaker", "wrecker", "ghost", "phantom", "rigger", "overclocker", "botnet", "hivemind"]:
        k = load_class(c)
        print(c, k["hp"], [(s["program"], s["value"]) for s in k["wheel"]["slots"]], k["wheel"]["hub"]["name"], k["ring"])
    for e in all_enemies():
        w = e["wheel"]
        print("%-22s %-10s %-7s hp%-4s ptr%s orb%s res%s hub=%s spawns=%s phases=%d" % (
            e["id"], e["corp"], e["role"], e["hp"], w["pointers"], w["orbit"], w["resistance"],
            w["hub"]["name"] if w["hub"] else "-", [(s["name"], s["hp"], s["max_active"]) for s in e["spawns"]], len(e["phases"])))
        print("     ", [(s["id"], s["value"], s["badge"]) for s in w["slots"]])
