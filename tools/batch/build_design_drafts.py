"""Build the plan-2 design-draft batches (docs/handoff/plan2/drafts) as Message Batches payloads.

    python tools/batch/build_design_drafts.py --out batches/plan2 --art <dir with fetched art docs>
    python tools/batch/build_design_drafts.py --out batches/plan2 --art <dir> --only enemies,events

Writes <out>/<batch>.jsonl for: enemies, bosses, hq, nodes, raids, events; plus <out>/manifest.json and
prints a token/cost estimate. The art docs (art-pass commit 7f021c21) come from --art (fetched with
`git show` by a helper). Drafts only: nothing here builds content.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MODEL = "claude-sonnet-5-5"
MAX_TOKENS = 40000
PRICE_IN, PRICE_OUT = 2.0, 10.0  # $/MTok, Sonnet 5.5; batch = 50 %

SYSTEM_HEAD = """You are a senior game designer drafting content for REBEL_CELL, a cyberpunk roguelite deckbuilder in Godot (combat on spinning 30-tick wheels; a City Grid campaign layer with Heat and raid defense).
You write DESIGN DRAFTS for the designer's review. Nothing you write is built or auto-applied; the designer and orchestrator choose from your drafts.

Ground rules:
- The rules R1-R13 in CONTENT_DESIGN_V2 and the designer rulings in DECISIONS are binding. Where they conflict with older text (GDD, CONTENT_CONCEPTS), the rulings win.
- Direct design, never procedural: design this one item as its own thing. Every phase asks a new question; none is attrition.
- Names are placeholders: spend no effort on names. Use short descriptive working names.
- Every number is a placeholder pending the balance sim, but give concrete numbers (sizes, amounts, thresholds, HP per tier) so the designer can judge feel. Show your arithmetic against the R2 phase budget where HP is involved.
- Use only systems that exist (GDD) or that are listed as N1-N20 in CONTENT_DESIGN_V2 section 5 or approved in the DECISIONS rulings. Mark every dependency on a new system with its N# (or "NEW: <name>" if none fits) and say whether a data-only fallback exists.
- The core is deterministic: no randomness outside named RNG streams; previews must equal results.
- Be concrete and decisive. Where you must choose, choose and say why in one line. List genuinely open design questions as lines starting with "Q:" at the end (max 5).
- Output ONE markdown document and nothing else. No preamble, no closing remarks. Do not write code; content tables and field lists are fine.
"""

# ---------------------------------------------------------------- shared context


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def decisions_block() -> str:
    t = read(ROOT / "docs/DECISIONS.md")
    a = t.index("### 2026-10-16 — Designer rulings on the replan")
    b = t.index("### 2026-10-15 — Open red")
    return t[a:b]


def gdd_block() -> str:
    t = read(ROOT / "docs/GDD.md")
    a = t.index("# REBEL_CELL")
    b = t.index("## 9. UX & Visual Direction")
    return t[a:b]


def enums_block() -> str:
    t = read(ROOT / "scripts/data/rc.gd")
    return "\n".join(l for l in t.splitlines() if l.startswith(("enum ", "const ", "\t", "}", "##")) or l.strip().startswith("enum"))


def common_system() -> list[dict]:
    parts = [
        ("CONTENT_DESIGN_V2 (rules R1-R13, specs, systems N1-N20)", read(ROOT / "docs/handoff/plan2/CONTENT_DESIGN_V2.md")),
        ("DECISIONS: designer rulings (2026-10-16)", decisions_block()),
        ("GDD sections 1-8 (rules; source of truth for behaviour)", gdd_block()),
        ("Code enums (scripts/data/rc.gd)", enums_block()),
    ]
    body = "\n\n".join(f"<<< {n} >>>\n{t}\n<<< end {n} >>>" for n, t in parts)
    return [
        {"type": "text", "text": SYSTEM_HEAD},
        {"type": "text", "text": body, "cache_control": {"type": "ephemeral"}},
    ]


def req(cid: str, extra_system: str, user: str, max_tokens: int = MAX_TOKENS) -> dict:
    system = common_system()
    if extra_system:
        system = system + [{"type": "text", "text": extra_system}]
    return {
        "custom_id": cid,
        "params": {
            "model": MODEL,
            "max_tokens": max_tokens,
            "system": system,
            "thinking": {"type": "adaptive"},
            "output_config": {"effort": "medium"},
            "messages": [{"role": "user", "content": user}],
        },
    }


# ---------------------------------------------------------------- enemies

EXT_RE = re.compile(r'\[ext_resource type="Resource" path="res://([^"]+)"')


def tres_ref_closure(path: Path, depth: int = 2, seen: set | None = None) -> list[tuple[str, str]]:
    seen = seen if seen is not None else set()
    out: list[tuple[str, str]] = []
    for m in EXT_RE.finditer(read(path)):
        rel = m.group(1)
        if rel in seen or rel.startswith("content/enemies/"):
            continue
        seen.add(rel)
        p = ROOT / rel
        if p.exists():
            out.append((rel, read(p)))
            if depth > 1:
                out.extend(tres_ref_closure(p, depth - 1, seen))
    return out


def prop(text: str, key: str, default: str = "") -> str:
    m = re.search(rf"^{key} = (.+)$", text, re.M)
    return m.group(1).strip().strip('"') if m else default


def enemy_index() -> dict[str, dict]:
    files = sorted((ROOT / "content/enemies").glob("*.tres"))
    texts = {f.stem: read(f) for f in files}
    referenced: set[str] = set()
    for t in texts.values():
        for m in re.finditer(r'path="res://content/enemies/(\w+)\.tres"', t):
            referenced.add(m.group(1))
    idx = {}
    for sid, t in texts.items():
        cls = "boss" if prop(t, "is_boss") == "true" else "mini_boss" if prop(t, "is_mini_boss") == "true" else "elite" if prop(t, "is_elite") == "true" else "normal"
        idx[sid] = {
            "id": sid,
            "name": prop(t, "display_name"),
            "corp": prop(t, "corporation_id").replace("&", "").strip('"'),
            "cls": cls,
            "hp": prop(t, "hp"),
            # spawned satellites, plus drones that only cards / Firmware deploy (player drones)
            "satellite": sid in referenced or sid in ("botnet_drone", "seed_drone"),
            "text": t,
            "path": f"content/enemies/{sid}.tres",
        }
    return idx


def baseline_rows() -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    tier = 0
    in_sweep = False
    header = ""
    for line in read(ROOT / "docs/balance/BASELINE_e2e13918.md").splitlines():
        if line.startswith("## Fight sweep"):
            in_sweep = True
        elif line.startswith("## ") and in_sweep:
            in_sweep = False
        if not in_sweep:
            continue
        m = re.match(r"### Tier (\d)", line)
        if m:
            tier = int(m.group(1))
        if line.startswith("| enemy | category"):
            header = line
        m = re.match(r"\| (\w+) \| (enemy|elite|mini_boss|boss) ", line)
        if m and tier:
            rows.setdefault(m.group(1), []).append(f"T{tier}: {line}")
    rows["_header"] = [header]
    return rows


def mentions(e: dict, limit: int = 14) -> list[str]:
    pat = re.compile(rf"\b({re.escape(e['id'])}|{re.escape(e['id'].replace('_', ' '))}|{re.escape(e['name'])})\b", re.I)
    out: list[str] = []
    roots = [ROOT / "docs/playtest", ROOT / "docs/handoff", ROOT / "docs/balance"]
    for r in roots:
        for f in sorted(r.rglob("*.md")):
            if f.name in ("CONTENT_DESIGN_V2.md", "BASELINE_e2e13918.md"):
                continue
            try:
                for ln, line in enumerate(read(f).splitlines(), 1):
                    if pat.search(line) and len(out) < limit:
                        out.append(f"{f.relative_to(ROOT).as_posix()}:{ln}: {line.strip()[:320]}")
            except OSError:
                pass
    return out


CLASS_BRIEF = {
    "normal": "NORMAL enemy: exactly 1 phase, 3-4 turns, no enrage (R1, R4). Target fight 3-4 turns.",
    "elite": "ELITE: 2 phases (one threshold), 3-4 turns per phase, target 6-8 turns, enrage default start 8. Decide whether to keep its heat_effects.",
    "mini_boss": "MINI-BOSS: 2-3 phases, 3-4 turns per phase, target 6-12 turns, enrage default start 10. It guards the final Server Rack of a netrun at T1-T3. CONTENT_DESIGN_V2 section 3 has a concept for it: refine it into a full design (you may change it if you can do better, and say so).",
    "boss": "HQ BOSS (Central Server): 4-5 phases, 3-4 turns per phase, target 12-20 turns, T4 only, HP from hp_bands, many strong buffs each with a counter Exploit (a route draws a subset), enrage default start 10.",
}

ENEMY_TEMPLATE = """Produce the draft with exactly these sections (keep it tight; normals ~700-1100 words, elites ~1200-1800, mini-bosses/bosses ~2000-3500):
# <id>: direct design
1. **Identity & the one question** (class, corporation, which layers it appears in L1-2 teaching vs L5-6 pressure; the question each phase asks; which answer shortens the fight)
2. **Phase plan** (a table per phase: threshold/HP share, needles and pointer behavior with tick positions, wheel layout as slices with tick size summing to 30 and each slice's effect with amount mode FLAT/PERCENT, hub rule if any, statuses/parasites used, listeners). Include the transition (what changes, what is parked or cleansed).
3. **Sustain** (at most one source, cap 30 % of reference damage per turn; show it) and **intake per turn** at the reference player (must be above 0)
4. **HP by tier** T1-T4 inside the class band of R2, with the phase-budget arithmetic (or hp_bands for the boss)
5. **Enrage** (default or authored and why)
6. **Buffs and counter Exploits** (bosses only; a table; strong buffs; say which ones are the signature)
7. **Counterplay** (what a good player does per phase; what a weak player gets wrong)
8. **Systems needed** (N# list, and the data-only fallback if any)
9. **Delta vs today** (what changes against the current .tres; what is kept; heat_effects decision)
10. **Predicted sim check** (expected turns, win % at T1-T4 and one line on why, compared with the baseline row)
11. **Q:** open questions (max 5)
"""


def build_enemies(idx: dict[str, dict]) -> list[dict]:
    base = baseline_rows()
    out = []
    for sid, e in idx.items():
        if e["satellite"]:
            continue
        refs = tres_ref_closure(ROOT / e["path"])
        refs_txt = "\n\n".join(f"--- {rel} ---\n{t}" for rel, t in refs)
        sibs = ", ".join(f"{o['name']} ({o['cls']})" for o in idx.values() if o["corp"] == e["corp"] and o["id"] != sid and not o["satellite"])
        corp = read(ROOT / f"content/corporations/{e['corp']}.tres") if (ROOT / f"content/corporations/{e['corp']}.tres").exists() else "(no corporation file)"
        brows = base.get(sid)
        btxt = ("Columns: " + base["_header"][0] + "\n" + "\n".join(brows)) if brows else "No baseline row (the baseline sweep covered Solace enemies only). Estimate from the wheel yourself and say so."
        ment = mentions(e)
        user = f"""Design this enemy directly under rules R1-R13.

Class brief: {CLASS_BRIEF[e['cls']]}
Enemy: {e['name']} (id {sid}), corporation {e['corp']}, current hp {e['hp']}.
Other non-satellite enemies of the same corporation (keep designs distinct from them): {sibs}

=== Current data: {e['path']} ===
{e['text']}

=== Referenced slices/resources (read-only context) ===
{refs_txt or '(none)'}

=== Corporation file ===
{corp}

=== Balance baseline rows (docs/balance/BASELINE_e2e13918.md) ===
{btxt}

=== Playtest / handoff / balance mentions (grep) ===
{chr(10).join(ment) if ment else '(none found)'}

{ENEMY_TEMPLATE}"""
        if sid == "renewal_engine":
            user += "\nNote: CONTENT_DESIGN_V2 section 2 already specifies the Genome Core. Treat that spec as the draft to stress-test: confirm or improve it, point out arithmetic errors, weak phases, missing counterplay, and give the final spec in the template above."
        out.append(req(f"enemy__{sid}", "", user, 48000 if e["cls"] in ("boss", "mini_boss") else MAX_TOKENS))
    return out


# ---------------------------------------------------------------- new corps (mini-boss + boss + roster)

NEWCORP_TEMPLATE = """Produce one document with these sections:
# <Corp>: corporation content draft
1. **Corporation identity summary** (what they sell, the house rule/signature mechanic and how it plays on the wheel, tone, Exploit trio flavour, raid flavour, story-path hooks; condense the art identity into game terms; flag where the art identity needs a game-side change)
2. **Mini-boss** (2-3 phases): full direct design in the ENEMY format below
3. **Boss / Central Server** (4-5 phases, buffs + Exploits): full direct design in the ENEMY format below; include a phase table, the buffs-and-counter-Exploits table (8 buffs, signature ones marked), the enrage rule, hp_bands
4. **Enemy roster sketch**: 6 normals and 2 elites, one table each: working name, class, layer role (teach/pressure), the one question, 1-line wheel sketch (slices/sizes/needle), HP per tier band, N# needed. Make them distinct from each other and from the other corporations' enemies (list below), and have the roster teach the corporation's house rule before the mini-boss uses it hard.
5. **Systems needed** summary (N# list) and the order you would build them
6. **Q:** open questions (max 6)

ENEMY format for the mini-boss and boss: identity & the one question; phase plan table (threshold, needles and tick positions, wheel layout as slices with tick sizes summing to 30 and effects with FLAT/PERCENT amount modes, hub rule); sustain (<=30 % of reference damage per turn) and intake; HP by tier from the R2 budget with arithmetic; enrage; counterplay per phase; systems; delta/notes.
Length: about 6000-9000 words in total.
"""


def build_bosses(idx: dict[str, dict], art: Path) -> list[dict]:
    corps = {
        "aurelian": ("Aurelian Concord", ["roman_identity", "roman_boss", "roman_notes"]),
        "tethys": ("Tethys Deep", ["atlantis_identity", "atlantis_boss", "atlantis_notes"]),
    }
    others = "\n".join(f"- {e['corp']}: {e['name']} ({e['cls']})" for e in idx.values() if not e["satellite"])
    out = []
    for key, (name, docs) in corps.items():
        parts = "\n\n".join(f"--- art-pass doc {d}.md ---\n{read(art / (d + '.md'))[:22000]}" for d in docs)
        user = f"""Draft the full corporation content for the NEW corporation {name} (added completely and playable per designer ruling D1).

The art-pass identity documents (concept art; not yet game content) follow. Treat them as the creative source and the GDD/rules as the constraint.

{parts}

=== Existing enemies of the other corporations (stay distinct) ===
{others}

=== Existing mini-boss concepts for the five old corporations: see CONTENT_DESIGN_V2 section 3 (match their depth) ===

{NEWCORP_TEMPLATE}"""
        out.append(req(f"corp__{key}", "", user, 64000))
    return out


# ---------------------------------------------------------------- HQ netruns

HQ_SPEC = {
    "solace": ("Solace", ["hq_solace"], "Twin helix towers; the ladder (UP / ACROSS); UNREAD rooms frosted; crown with THE GENOME CORE; glazed skybridges only on route floors."),
    "meridian": ("Meridian", ["hq_meridian_v3_design", "hq_meridian_v3_notes"], "Container fortress: shuttle containers wall<->train every other turn, the slewing keep crane, movers carrying rooms, the freight line off the north side; MANIFEST CONTROL."),
    "halcyon": ("Halcyon", ["hq_halcyon"], "Stepped pyramid with THE PANOPTICON eye turret: the gaze spot (90 degree sector), blade scan line, lighthouse beam, lockdown red."),
    "orbital": ("Orbital", ["hq_orbital"], "Launch podium, silo doors open/shut, rocket height, hacked bands lit lime, the override link, dish stations, truss antenna tower with two elite vaults, LAUNCH CONTROL gantry."),
    "rebel_cell": ("REBEL_CELL", ["hq_rebel_cell"], "No tower: a Tokyo-alley district in three stacked lanes (roofs, alley, service tunnel), THE UNDERCROFT; the window sequence SEQ (0..3) and PULSE; the MAINFRAME red sign moves to the target (DISPATCH). Ties to the Sync Strike pass."),
    "aurelian": ("Aurelian Concord", ["roman_identity", "roman_boss", "roman_notes"], "THE CIRCUS AURELIUS: a colosseum of four turning seating rings with gates (the TURNING GATES); VERDICT house rule; the Grand Stand hub (emperor's box)."),
    "tethys": ("Tethys Deep", ["hq_tethys", "atlantis_boss"], "Dams / water locks over a drowned quarter; underwater look with deep distance fade; (see the HQ design doc)."),
}

HQ_TEMPLATE = """Produce one document with these sections:
# <Corp>: HQ netrun draft
1. **Concept & the named mechanic** (what the art shows, restated as a game mechanic; why this HQ cannot be mistaken for another)
2. **Structure** (this HQ netrun is UNIQUE and may exceed 7 layers: give the layer count, nodes per layer, and an ASCII/tabular layer map with edges or branching rules; the mapping onto the landmark's slots; HQ netruns end at the corporation's boss fight, designed in the enemy/corp drafts - reference it by working name only)
3. **Unique mechanics** (2-4 rules that exist only here, driven by game state the art can visualise; for each: rule, per-turn/per-layer trigger, what the player sees, what counters it, determinism notes - RNG stream if any; use the art's named mechanic as the spine)
4. **Node kit** (node types used: fight/elite/event/shop/rest/cache/etc, with this HQ's twist on each; which nodes are mini-fights vs puzzles; how Exploit/key buildings (D5) pay off in the run, e.g. what each owned Exploit does inside this HQ)
5. **Pacing & difficulty curve** (expected minutes, number of fights, HP/Heat pressure, a rest/heal budget; tier T4 assumptions)
6. **Rewards** (what completing it grants beyond the boss)
7. **Failure & retry** (what death/breach costs; Heat effects)
8. **Systems needed** (N# list; NEW systems; data-only parts), and a build order
9. **Art hooks** (which mechanic visuals the art must expose per frame)
10. **Q:** open questions (max 6)
About 2500-4000 words.
"""


def build_hq(art: Path) -> list[dict]:
    pipeline = read(art / "pipeline.md").splitlines()
    sect = "\n".join(pipeline[950:981]) + "\n" + "\n".join(pipeline[1032:1046])
    out = []
    for key, (name, docs, hint) in HQ_SPEC.items():
        parts = "\n\n".join(f"--- art-pass doc {d}.md ---\n{read(art / (d + '.md'))[:30000]}" for d in docs)
        user = f"""Design the UNIQUE HQ netrun for {name} (designer rulings G12 and D10: every HQ netrun is unique with unique mechanics; may run longer than 7 layers; ends at the corporation boss).

The art's named mechanic: {hint}

=== PIPELINE_SPEC sections 8.4-8.8 excerpt (how the art maps the game graph onto the landmark, per-corp mechanics) ===
{sect}

=== Per-corp art documents ===
{parts}

{HQ_TEMPLATE}"""
        out.append(req(f"hq__{key}", "", user, 40000))
    return out


# ---------------------------------------------------------------- nodes

NODE_SPECS = {
    "rest": ("REST (netrun node, D4)", "A REST node on the netrun map: designer ruling: heal OR swap Firmware locations (two modes the player chooses between). Decide placement (layers, counts, generator rule), heal amount mode, what 'swap firmware locations' means exactly (which Firmware slots/rings, any cost or limit), the warm-light/sticker presentation hooks, interaction with Heat and the death rules, and what the run graph generator must guarantee."),
    "workshop": ("WORKSHOP (netrun node)", "A Workshop node: slice upgrade / card upgrade (Level I, II, III, IV... per G5/G15; slice upgrades and card upgrades are separate passes, so design the node so it hosts either now with clear, simple offers). Include the player-facing choice, costs (Cycles/Schematics), limits, what one visit offers, unlock gating, and how it differs from the Shop."),
    "cache": ("CACHE (netrun node) and its event mini-puzzle", "A Cache node (a stash to crack). Also VET the proposed mini-puzzle from CONTENT_CONCEPTS EV4 'Dial the vault' (a 6-slice reward wheel, N nudges, extra nudges cost HP/Heat; event wheel N17): is it good? Is it readable? Is it too similar to combat? Give a revised spec, the reward table, the nudge budget, the failure cost, the deterministic RNG handling (events stream at a checkpoint), and how it teaches nudging."),
    "black_market": ("BLACK MARKET (unknown event)", "The Black Market appears on the map as an UNKNOWN event node (the player does not know it is a market until entered). Design what it is, what it sells (a rotating inventory with odd rules: Heat-priced goods, paid-in-HP, cursed items, trade-in), the reveal, pricing, risk, a small event wheel option if apt, and how it stays distinct from the Shop and from regular events. Give 3 example inventories."),
    "safehouse": ("SAFEHOUSE (City GRID node, NOT a netrun node)", "The Safehouse is an existing City Grid network node (content/nodes/safehouse.tres: stations an operative). Design its role in the campaign layer: what stationing does (G8: every class gets a unique station bonus; alternates feel similar - give the station-bonus framework and examples for the existing operative classes found in the GDD), upgrades, raid interaction, Heat interaction, installation cost curve, and slots. This is a City Grid node, not a netrun node."),
    "heat_sink": ("HEAT SINK (City GRID node, NOT a netrun node)", "A Heat Sink is a City Grid node (a Site/network node) that reduces Heat. Check GDD 4.x/3.x for the existing Heat-reduction objective and design this as a distinct placeable/claimable node: how much Heat it sinks and when (per interlude, per raid, on demand), cost, build/repair, vulnerability to raids (it is a raid target?), limits (diminishing returns / one per territory), interaction with the Heat bands (NOTICED/FLAGGED/HUNTED), and the decision it creates (defend it vs spend on offense)."),
}

NODE_TEMPLATE = """Produce one document with these sections:
# <Node>: design draft
1. **Purpose & the decision it creates** (one paragraph; what the player weighs)
2. **Rules** (precise: inputs, outputs, costs, limits; FLAT/PERCENT amount modes; all numbers as placeholders in config terms, naming the config key you would add)
3. **Placement & generation** (where it appears, counts per run/campaign, weights by layer/tier/corporation, guarantees and exclusions; deterministic RNG stream)
4. **UX flow** (screens/prompts in order, what is previewed before commitment, how Undo/cancel works, text keys needed)
5. **Interactions** (Heat, raids, Daemons/Firmware, other nodes, Exploits, tiers)
6. **Data & systems** (new data fields/resources, N# systems, estimated size S/M/L)
7. **Examples** (3 concrete instances/offers with numbers)
8. **Risks & balance notes** (exploits, degenerate strategies, what to test in the sim)
9. **Q:** open questions (max 5)
About 1500-2500 words.
"""


def build_nodes() -> list[dict]:
    replan = read(ROOT / "docs/handoff/gates/REPLAN_2026-10-16.md")
    nodes = "\n\n".join(f"--- {p.relative_to(ROOT).as_posix()} ---\n{read(p)}" for p in sorted((ROOT / "content/nodes").glob("*.tres")))
    out = []
    for key, (title, brief) in NODE_SPECS.items():
        user = f"""Design: {title}.

Brief: {brief}

=== Existing network node data (content/nodes/*.tres) ===
{nodes}

=== Replan document (D4 and node variety) ===
{replan[:16000]}

{NODE_TEMPLATE}"""
        out.append(req(f"node__{key}", "", user, 32000))
    return out


# ---------------------------------------------------------------- raids

RAID_TEMPLATE = """Produce one document with these sections:
# Raid design pass: R1-R4
1. **Raid model recap** (as it works today in your own words, with the GDD 7 numbers: steps, spread, routing, what the preview shows; and where the new rules plug in)
2. **R1 EXPOSED spotlight** (rules: how a node becomes EXPOSED, the extra damage as FLAT or PERCENT, moving the spotlight along a link for Heat or Schematics, preview/determinism, the decision, UI)
3. **R2 Encrypted routes** (at which Heat bands; dashed paths; decryption cost with Ghost/Intel/1 Schematic; what the preview shows when encrypted; the decision)
4. **R3 Vehicle types** (LANDER / FLYING / HEAVY or better; effect on ICE Lock, Tar Pit, Turrets; which existing threats become which; per-corporation vehicle mixes for all 7 corporations incl. Aurelian LEVIES and Tethys; new threat entries as field lists matching content/threats/*.tres)
5. **R4 Heat-scaled second wave + ultimatum** (trigger Heat bands, wave composition rule, the ultimatum: pay Schematics or Heat to cancel, or take it for a reward; this is THE Schematics sink: price curve, how it keeps Schematics scarce, reward for refusing; failure states)
6. **How the four combine** (worked example of one raid at HUNTED Heat, step by step, and a worked example at NOTICED)
7. **Raid-win reward screen** (events in the raid view are approved: what a raid-win reward screen offers)
8. **Corporation flavour table** (7 corporations: raid name, threat roster, signature twist)
9. **Systems & data** (N# or NEW; new fields on RaidData/ThreatData/RaidWaveData; config keys; estimated size)
10. **Balance & sim notes** (what to measure)
11. **Q:** open questions (max 6)
About 3500-5000 words.
"""


def build_raids() -> list[dict]:
    raids = "\n\n".join(f"--- {n} ---\n{read(ROOT / 'content/raids' / n)}" for n in ("raid_hal_heat_50.tres", "raid_heat_75.tres", "raid_story.tres", "raid_purge.tres"))
    threats = "\n\n".join(f"--- {p.name} ---\n{read(p).split('[resource]')[-1]}" for p in sorted((ROOT / "content/threats").glob("*.tres")))
    assets = ""
    for sub in ("defense_assets", "assets"):
        d = ROOT / "content" / sub
        if d.exists():
            assets = "\n\n".join(f"--- {p.name} ---\n{read(p)}" for p in sorted(d.glob("*.tres")))
    cc = read(ROOT / "docs/handoff/plan2/CONTENT_CONCEPTS.md")
    a = cc.index("### Raid modifiers (G9)")
    b = cc.index("## 5. Fight length levers")
    user = f"""Draft the single raid design pass R1-R4 (designer ruling: all four, as stated, in one raid design pass; R4's ultimatum is the Schematics sink).

=== CONTENT_CONCEPTS section 4.2 (raid modifiers) ===
{cc[a:b]}

=== Existing raids (samples; 40 raid files exist: per corporation heat_25/50/75, claim, node_built, purge, retaliation, story) ===
{raids}

=== Existing threats (content/threats/*.tres) ===
{threats}

=== Defense assets present in content (if any) ===
{assets or '(not found: use GDD 7 and 6)'}

{RAID_TEMPLATE}"""
    return [req("raid__main", "", user, 48000)]


# ---------------------------------------------------------------- events

EVENT_MECH = {
    "FUTURE": "alters FUTURE FIGHTS on this run (run-level next_combat_overrides, N16: e.g. enemy starts Frozen, -1 resistance, a satellite removed, phase reveal, +X% enemy damage, a free nudge, enemy HP percent change; for the next combat or the next N combats)",
    "PATHS": "alters the PATHS available on the map (N16 map_edits: open/close/add a link or node, reveal a node's type, turn a node into another type, cut a layer's option)",
    "AMBUSH": "an IMPROMPTU FIGHT (N16 starts_combat with combat_overrides: a named existing enemy, a tier tweak, a stake and a reward)",
    "WHEEL": "uses an EVENT WHEEL (N17): a small wheel of outcome slices (6 slices or so), a nudge budget, extra nudges cost HP/Heat/Cycles; spell out every slice outcome and size",
    "RAIDWIN": "appears on the RAID-WIN REWARD SCREEN after a successful raid defense (approved context): a decision about spoils",
    "HQVIEW": "appears in the HQ/City view between netruns (approved context): a decision about the cell, an operative or the city",
}
EVENT_PLAN = [
    ("FUTURE", "solace"), ("FUTURE", "meridian"), ("FUTURE", "halcyon"), ("FUTURE", "orbital"), ("FUTURE", "rebel_cell"), ("FUTURE", "aurelian"), ("FUTURE", "tethys"),
    ("PATHS", "solace"), ("PATHS", "meridian"), ("PATHS", "halcyon"), ("PATHS", "orbital"), ("PATHS", "aurelian"), ("PATHS", "tethys"),
    ("AMBUSH", "solace"), ("AMBUSH", "meridian"), ("AMBUSH", "halcyon"), ("AMBUSH", "orbital"), ("AMBUSH", "rebel_cell"), ("AMBUSH", "tethys"),
    ("WHEEL", "solace"), ("WHEEL", "meridian"), ("WHEEL", "halcyon"), ("WHEEL", "orbital"), ("WHEEL", "rebel_cell"), ("WHEEL", "aurelian"), ("WHEEL", "any"),
    ("RAIDWIN", "any"), ("RAIDWIN", "rebel_cell"),
    ("HQVIEW", "any"),
]
EVENT_PLAN.append(("PATHS", "any"))  # 30th
assert len(EVENT_PLAN) == 30

EVENT_TEMPLATE = """Produce ONE event draft as a markdown document:
# ev_<snake_id>: <working title>
**Mechanic:** <FUTURE|PATHS|AMBUSH|WHEEL|RAIDWIN|HQVIEW>, corporation <id or any>, min_tier <1-4>, weight, dispatch_clue/foreshadows if apt
**One-line decision:** what the player weighs
## TerminalEventData fields
id, title, speaker (Voice enum), text (3-5 sentences, noir cyberpunk, US spelling), corporation_id, min_tier, dispatch_clue, foreshadows, weight
## Choices (2-4; each as EventChoiceData fields)
For every choice: label, result_text, cycle_cost, hp_cost, effects (EffectData list with type/target/amount/status/duration_turns, using existing EffectType values when possible), reward (card/firmware/daemon/defense asset/class by working description), AND the new-system fields as "(new)" lines: starts_combat (enemy id + overrides + stake), combat_overrides / next_combat_overrides (precise list, duration), map_edits (precise), event_wheel (below).
## Event wheel (only if used)
Slice table: size_ticks (sum 30), outcome per slice (effects), nudge budget, extra-nudge cost, deterministic RNG note.
## Design notes
Why the choice is interesting (no obviously dominant option), risk/reward numbers vs typical run economy (placeholders from GDD 11), interactions, and any text keys needed.
## Q:
At most 2 open questions.
Keep it to 450-900 words. Use only enemy ids from the list given. Be original; do not duplicate the existing event titles listed.
"""


def build_events(idx: dict[str, dict]) -> list[dict]:
    titles = []
    for p in sorted((ROOT / "content/events").glob("*.tres")):
        titles.append(f"{p.stem}: {prop(read(p), 'title')}")
    samples = "\n\n".join(f"--- {n} ---\n{read(ROOT / 'content/events' / n)}" for n in ("ev_abandoned_cache.tres", "ev_billing_loop.tres"))
    schema = "\n\n".join(f"--- {n} ---\n{read(ROOT / 'scripts/data' / n)}" for n in ("terminal_event_data.gd", "event_choice_data.gd", "effect_data.gd"))
    enemies = ", ".join(f"{e['id']} ({e['corp']}, {e['cls']})" for e in idx.values() if not e["satellite"])
    extra = f"""=== Event schema (scripts/data) ===
{schema}

=== Sample existing events ===
{samples}

=== Existing event ids and titles (do not duplicate) ===
{chr(10).join(titles)}

=== Enemy ids usable in impromptu fights ===
{enemies}
"""
    out = []
    for i, (mech, corp) in enumerate(EVENT_PLAN, 1):
        user = f"""Write new event draft number {i:02d} of 30.

Mechanic family: {mech}: {EVENT_MECH[mech]}.
Corporation: {corp}{' (the event is corporation-neutral)' if corp == 'any' else ' (use its tone: see the GDD world section and, for aurelian/tethys, the art-pass identities: aurelian = Bread. Circus. Terms apply, VERDICT, patron/clients, Lanista; tethys = deep-sea hull/pressure/water locks)'}.
Variation seed {i:02d}: choose a setting, speaker and stake that would not collide with the other 29 drafts in the same family (hint: lean on the seed number for the hook: {['a debt', 'a favor', 'a broadcast', 'a malfunction', 'a witness', 'a contract', 'a shortcut', 'a rumor', 'a prisoner', 'a delivery'][i % 10]}).

{extra}
{EVENT_TEMPLATE}"""
        out.append(req(f"event__{i:02d}_{mech.lower()}_{corp}", "", user, 24000))
    return out


# ---------------------------------------------------------------- main


def est_tokens(s: str) -> int:
    return int(len(s) / 3.6)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--art", required=True)
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    art = Path(args.art)
    idx = enemy_index()
    builders = {
        "enemies": lambda: build_enemies(idx),
        "bosses": lambda: build_bosses(idx, art),
        "hq": lambda: build_hq(art),
        "nodes": build_nodes,
        "raids": build_raids,
        "events": lambda: build_events(idx),
    }
    only = [x for x in args.only.split(",") if x]
    manifest = {}
    total_in = total_out = 0
    common_tokens = est_tokens(common_system()[1]["text"])
    for name, fn in builders.items():
        if only and name not in only:
            continue
        reqs = fn()
        path = out / f"{name}.jsonl"
        with path.open("w", encoding="utf-8", newline="\n") as fh:
            for r in reqs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        b_in = sum(est_tokens(r["params"]["messages"][0]["content"]) + common_tokens for r in reqs)
        b_out = sum(min(r["params"]["max_tokens"], 14000) for r in reqs)  # expected, not cap
        total_in += b_in
        total_out += b_out
        manifest[name] = [r["custom_id"] for r in reqs]
        cap_out = sum(r["params"]["max_tokens"] for r in reqs)
        print(f"{name}: {len(reqs)} requests, ~{b_in:,} in (common prefix ~{common_tokens:,}), expected out ~{b_out:,}, cap out {cap_out:,}")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    cost = (total_in * PRICE_IN + total_out * PRICE_OUT) / 1e6 * 0.5
    worst = total_in * PRICE_IN / 1e6 * 0.5
    print(f"estimate (batch -50 %, no cache credit): expected ${cost:.2f}; cap-output worst case computed per batch above")
    return 0


if __name__ == "__main__":
    sys.exit(main())
