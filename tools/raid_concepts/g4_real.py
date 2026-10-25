"""G4 (docs/handoff/raid_integration/G4_PHASE1.md): the real game's numbers for the H4 oracle, read from the content
files (never edited) at import. Python 3 stdlib only.

- campaign_config.tres ([resource] block), falling back to the CampaignConfigData defaults in campaign_config_data.gd
  for any key the .tres leaves out (the bloom_* keys, node_base_cost, asset_drop_chance ...).
- content/nodes/home_standard.tres: the HOME integrity (the home server node; no internal nodes).
- content/raids/*.tres + content/threats/*.tres: each Solace raid's threats and their damage, for the HOME hit damage per
  Heat band (see home_hit_damage_by_band).
- content/corporations/solace.tres: the Site graph, checked against g1_geo's copy (check_graph).

REAL is the dict the oracle reads. Every value has the content path it came from in SOURCES."""
from __future__ import annotations

import math
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def _p(*parts) -> str:
    return os.path.join(ROOT, *parts)


def _parse_value(v: str):
    v = v.strip()
    m = re.match(r"Packed(?:Int32|Int64|Float32|Float64)Array\((.*)\)$", v)
    if m:
        body = m.group(1).strip().strip("[]").strip()
        if not body:
            return []
        return [float(x) if "." in x else int(x) for x in (s.strip() for s in body.split(","))]
    m = re.match(r"Vector2i?\((.*)\)$", v)
    if m:
        return [float(x) if "." in x else int(x) for x in (s.strip() for s in m.group(1).split(","))]
    if v in ("true", "false"):
        return v == "true"
    if re.match(r"^-?\d+$", v):
        return int(v)
    if re.match(r"^-?\d+\.\d*(e-?\d+)?$", v):
        return float(v)
    if v.startswith('"') and v.endswith('"'):
        return v[1:-1]
    if v.startswith('&"') and v.endswith('"'):
        return v[2:-1]
    return v


def _tres_blocks(path: str) -> list:
    """[(header, {key: raw value})] for every [section] in a .tres file."""
    out = []
    cur = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("["):
                cur = (line, {})
                out.append(cur)
                continue
            if cur is None or line.startswith(";") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cur[1][k.strip()] = v.strip()
    return out


def _gd_defaults(path: str) -> dict:
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"@export(?:_range\([^)]*\))? var (\w+)\s*:\s*[\w\[\]]+\s*=\s*(.+?)\s*(#.*)?$", line.strip())
            if m:
                try:
                    out[m.group(1)] = _parse_value(m.group(2))
                except ValueError:
                    pass
    return out


def _config() -> dict:
    cfg = _gd_defaults(_p("scripts", "data", "campaign_config_data.gd"))
    res = [b for h, b in _tres_blocks(_p("content", "config", "campaign_config.tres")) if h == "[resource]"][0]
    for k, v in res.items():
        try:
            cfg[k] = _parse_value(v)
        except ValueError:
            cfg[k] = v
    return cfg


def _threat_damage() -> dict:
    out = {}
    d = _p("content", "threats")
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".tres"):
            for h, b in _tres_blocks(os.path.join(d, fn)):
                if "damage" in b:
                    out[fn[:-5]] = int(b["damage"])
    return out


def _raid_threats(name: str) -> list:
    """The threat file names of every wave of content/raids/<name>.tres, in wave order."""
    path = _p("content", "raids", name + ".tres")
    ext = {}
    with open(path, encoding="utf-8") as f:
        text = f.read()
    for m in re.finditer(r'path="res://content/threats/(\w+)\.tres" id="(\w+)"', text):
        ext[m.group(2)] = m.group(1)
    out = []
    for m in re.finditer(r"threats = Array\[[^\]]*\]\(\[(.*?)\]\)", text):
        out.extend(ext[i] for i in re.findall(r'ExtResource\("(\w+)"\)', m.group(1)))
    return out


def _major_strength_pct(cfg_path: str) -> float:
    for h, b in _tres_blocks(cfg_path):
        if 'id="rm_major_raid_strength"' in h:
            return float(b["value"])
    return 0.0


def home_hit_damage_by_band(cfg: dict) -> list:
    """HOME damage of one unanswered HOME hit, per Heat band (COOL, NOTICED, FLAGGED, HUNTED, PURGE): the summed damage
    of the Solace raid that band fires (claim raid below 25; heat_25, heat_50, heat_75; purge at 100) as if every threat
    reached HOME, with the 75-band +25 % raid strength (rm_major_raid_strength) from HUNTED on. G4 assumption: in the
    Infected Tide a beam that reaches HOME is the whole raid getting through."""
    dmg = _threat_damage()
    pct = _major_strength_pct(_p("content", "config", "campaign_config.tres"))
    out = []
    for i, raid in enumerate(("raid_claim", "raid_heat_25", "raid_heat_50", "raid_heat_75", "raid_purge")):
        scale = 1.0 + (pct / 100.0 if i >= 3 else 0.0)
        out.append(int(math.floor(sum(dmg[t] for t in _raid_threats(raid)) * scale + 0.5)))
    return out


def _solace_graph() -> dict:
    sites = {}
    for h, b in _tres_blocks(_p("content", "corporations", "solace.tres")):
        if 'id="site_' not in h or "id" not in b:
            continue
        sid = _parse_value(b["id"])
        links = re.findall(r'&"(\w+)"', b.get("links", ""))
        locked = re.findall(r'&"(\w+)"', b.get("locked_links", ""))
        sites[sid] = {"tier": int(b.get("tier", "1")), "links": links, "locked": locked,
                      "objective": int(b.get("objective", "0")), "heat_change": int(b.get("heat_change", "0")),
                      "exploit_type": int(b.get("exploit_type", "0"))}
    return sites


def _home_integrity() -> int:
    for h, b in _tres_blocks(_p("content", "nodes", "home_standard.tres")):
        if "integrity" in b:
            return int(b["integrity"])
    raise ValueError("home_standard.tres has no integrity")


CFG = _config()
SOLACE = _solace_graph()

REAL = {
    "home_integrity": _home_integrity(),
    "home_repair_cost_per_point": float(CFG["home_repair_cost_per_point"]),
    "starting_schematics": int(CFG["starting_schematics"]),
    "node_base_cost": int(CFG["node_base_cost"]),
    "node_repair_ratio": float(CFG["node_repair_ratio"]),
    "rack_schematics_by_tier": list(CFG["rack_schematics_by_tier"]),
    "rack_heat_by_tier": list(CFG["rack_heat_by_tier"]),
    "raid_schematics_by_tier": list(CFG["raid_schematics_by_tier"]),
    "clean_defense_heat": int(CFG["clean_defense_heat"]),
    "exploit_heat": int(CFG["exploit_heat"]),
    "death_heat_base": int(CFG["death_heat_base"]),
    "elite_heat": int(CFG["elite_heat"]),
    "asset_drop_chance": float(CFG["asset_drop_chance"]),
    "min_exploits_for_breach": int(CFG["min_exploits_for_breach"]),
    "heat_purchase_amount": int(CFG["heat_purchase_amount"]),
    "heat_purchase_cost": int(CFG["heat_purchase_cost"]),
    "heat_purchase_increment": int(CFG["heat_purchase_increment"]),
    "heat_max": int(CFG["heat_max"]),
    "major_heat": (25, 50, 75),
    "purge_heat": 100,
    "home_hit_damage_by_band": home_hit_damage_by_band(CFG),
    "bloom_start_gap_milli_by_tier": list(CFG["bloom_start_gap_milli_by_tier"]),
    "bloom_pace_node_milli_by_tier": list(CFG["bloom_pace_node_milli_by_tier"]),
    "bloom_pace_turn_milli": int(CFG["bloom_pace_turn_milli"]),
    "bloom_dose_push_milli": int(CFG["bloom_dose_push_milli"]),
    "bloom_max_gap_milli": int(CFG["bloom_max_gap_milli"]),
    "bloom_virus_pace_pct": int(CFG["bloom_virus_pace_pct"]),
    "bloom_pace_heat_pct_by_band": list(CFG["bloom_pace_heat_pct_by_band"]),
    "bloom_breach_setback_milli": int(CFG["bloom_breach_setback_milli"]),
    "bloom_intel_turn_pct": int(CFG["bloom_intel_turn_pct"]),
    "bloom_close_gap_milli": int(CFG["bloom_close_gap_milli"]),
    "bloom_dose_price": int(CFG["bloom_dose_price"]),
    "map_layers": int(CFG["map_layers"]),
    "target_turns_per_phase": float(CFG["target_turns_per_phase"]),
}
SOURCES = {
    "home_integrity": "content/nodes/home_standard.tres (home_server integrity)",
    "home_hit_damage_by_band": "content/raids/raid_{claim,heat_25,heat_50,heat_75,purge}.tres + content/threats/*.tres"
                               " damage, x1.25 from 75 (campaign_config.tres rm_major_raid_strength)",
    "*": "content/config/campaign_config.tres [resource], else scripts/data/campaign_config_data.gd defaults",
}


def check_graph(geo_module) -> list:
    """Differences between solace.tres and g1_geo's copy (SOL_LINKS, SOL_LOCKED, SOL_TIER, objectives, exploits)."""
    G = geo_module
    diffs = []
    core = "the_genome_core"
    for sid, s in SOLACE.items():
        if sid in ("home", core):
            continue
        if G.SOL_TIER.get(sid) != s["tier"]:
            diffs.append("tier %s %s != %s" % (sid, G.SOL_TIER.get(sid), s["tier"]))
        links = sorted("core" if l == core else l for l in s["links"])
        if sorted(G.SOL_LINKS.get(sid, [])) != links:
            diffs.append("links %s %s != %s" % (sid, sorted(G.SOL_LINKS.get(sid, [])), links))
        for l in s["locked"]:
            if (sid, l) not in G.SOL_LOCKED:
                diffs.append("locked %s-%s missing" % (sid, l))
        if s["heat_change"] and G.SOL_OBJECTIVE_HEAT.get(sid) != s["heat_change"]:
            diffs.append("objective heat %s" % sid)
        if s["exploit_type"] and sid not in G.SOL_EXPLOITS:
            diffs.append("exploit %s" % sid)
    if sorted(G.SOL_LINKS["home"]) != sorted(SOLACE["home"]["links"]):
        diffs.append("home links")
    return diffs


if __name__ == "__main__":
    import json
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import g1_geo
    print(json.dumps(REAL, indent=1))
    print("graph diffs:", check_graph(g1_geo) or "none")
