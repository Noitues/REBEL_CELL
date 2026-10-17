"""Build the plan-2 design-draft batches, ROUND 2 (docs/handoff/plan2/drafts), as Message Batches payloads.

    python tools/batch/build_design_drafts2.py --out <dir>                       # all batches
    python tools/batch/build_design_drafts2.py --out <dir> --only critic,station # some batches
    python tools/batch/build_design_drafts2.py --out <dir> --retry-file <ids.txt>
                                                                    # rebuild the listed custom_ids alone (retry.jsonl, max_tokens 64000)

Batches (custom_id prefix -> drafts/<dir>): critic (critic), station (station), slice_upgrades (slup),
card_upgrades (cardup), inner_ring (inner), rim_gates (rim), catalog (catalog), sync_strike (sync),
firmware (fw), gdd (gdd). Uses the SAME cached shared block as round 1 (build_design_drafts.common_system),
so the prefix cache is shared. Drafts only: nothing here builds content.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_design_drafts as b1  # noqa: E402
from build_design_drafts import ROOT, read, prop, req, enemy_index, tres_ref_closure  # noqa: E402

DRAFTS = ROOT / "docs/handoff/plan2/drafts"
CORPS = ["solace", "meridian", "halcyon", "orbital", "rebel_cell", "aurelian", "tethys"]
COMMON_TOKENS = 32007  # measured in round 1 (cache-read tokens of the shared block); the old estimate was wrong
EXPECT_OUT = {"critic": 6000, "corp": 10000, "station": 12000, "slup": 14000, "cardup": 6000, "inner": 22000,
              "rim": 18000, "catalog": 28000, "sync": 22000, "fw": 8000, "fwnew": 28000, "gdd": 16000}

ROUND2_HEAD = """ROUND 2 NOTES: the round-1 drafts (enemies, bosses, hq, nodes, raids, events under docs/handoff/plan2/drafts) exist; you may be shown some of them. Round 2 covers reviews and the cross-cutting design passes. The rules R1-R13 and the 2026-10-16 designer rulings stay binding. Same output discipline as before: ONE markdown document, no preamble, concrete numbers, "Q:" lines at the end (max 5). Dependencies on new systems: N# from CONTENT_DESIGN_V2 section 5, else "NEW: <name>".
"""


def extras() -> str:
    """Older designer context for the cross-cutting passes (concept notes and the G re-evaluation)."""
    return ("=== G_REEVAL.md (G1-G16 re-evaluation) ===\n" + read(ROOT / "docs/handoff/plan2/G_REEVAL.md")
            + "\n\n=== CONTENT_CONCEPTS.md (older concepts; the rulings win where they differ) ===\n"
            + read(ROOT / "docs/handoff/plan2/CONTENT_CONCEPTS.md"))


def strip_header(t: str) -> str:
    return re.sub(r"^<!--.*?-->\s*", "", t, count=1, flags=re.S)


def script_dump(*names: str) -> str:
    return "\n\n".join(f"--- scripts/data/{n} ---\n{read(ROOT / 'scripts/data' / n)}" for n in names)


def kind_of(cid: str) -> str:
    if cid.startswith("critic__corp__"):
        return "corp"
    if cid == "fw__new_chips":
        return "fwnew"
    return cid.split("__")[0]


def mk(cid: str, user: str, max_tokens: int, role: str = "") -> dict:
    return req(cid, ROUND2_HEAD + role, user, max_tokens)


# ---------------------------------------------------------------- 1. critic

CRIT_TEMPLATES = {
    "enemies": b1.ENEMY_TEMPLATE, "bosses": b1.NEWCORP_TEMPLATE, "hq": b1.HQ_TEMPLATE,
    "nodes": b1.NODE_TEMPLATE, "raids": b1.RAID_TEMPLATE, "events": b1.EVENT_TEMPLATE,
}
CRITIC_ROLE = """YOU ARE THE CRITIC. You review one existing design draft for the designer; you do not redesign it from scratch.
Check, in this order: (1) hard rule violations of R1-R13 and the rulings (phase counts and 3-4 turns per phase, tier bands, threshold parking, enrage, amount modes FLAT/PERCENT, sustain cap 30 %, intake above zero, slice sizes summing to 30, pointers on any tick, statuses survive phases, Parasite ring rules, corruption as double RAM cost, Site names removed, US spelling); (2) arithmetic: re-add the tick sizes and HP/phase budget yourself and say where it fails; (3) systems: every new system tagged with a real N# or NEW:, a data-only fallback stated, nothing that already exists in the game invented again, no invented content ids; (4) design quality: is each phase a new question, is there a dominated choice, is it readable, does it match the template sections; (5) what is good and must be kept.
Output exactly:
# critic: <batch>/<id>
**Verdict:** OK or FIX (FIX if any hard violation or arithmetic error remains; OK may still list nits)
## Issues
numbered, most severe first: severity (BLOCKER / MAJOR / NIT), the rule or section, a short quote or locator, why it fails.
## Concrete fixes
for each BLOCKER/MAJOR issue the replacement text, number or table row, ready to paste. No vague advice.
## Keep
2-4 lines on what is strong.
## Q:
at most 3 open questions.
Be terse: 250-600 words total unless many BLOCKERs."""

CORP_ROLE = """YOU ARE THE CORPORATION CONSISTENCY CRITIC. You read ALL drafts of one corporation together (its enemies, mini-boss and boss as classed, HQ netrun, events) and judge the set, not each draft.
Output exactly:
# critic: corporation <id>
**Verdict:** OK or FIX
## Roster variety
a table: draft | class | the one question it asks | the wheel/mechanic hook it relies on. Call out pairs that are too similar and say which to rework and how.
## Phase and hook overlap
which phase shapes, needle/pointer behaviors, statuses, parasites or satellites repeat; whether a sub-set uses one system too much or leaves a needed teaching step out.
## Systems used
the N#/NEW list across the set, and which are shared (build once) vs single-use; flag a corporation that depends on too many new systems.
## Difficulty curve
L1-2 teaching versus L5-6 pressure, elite vs mini-boss vs boss, expected turns, whether the HQ run and boss escalate in a way the roster prepared the player for.
## Identity
does the set read as this corporation (tone, GDD world section, art identity)?
## Concrete fixes
numbered, each naming the draft and the exact change.
## Q:
at most 4 open questions.
Be terse and specific: 500-1000 words."""


def build_critic(idx: dict[str, dict]) -> list[dict]:
    out = []
    for batch in ("enemies", "bosses", "hq", "nodes", "raids", "events"):
        for f in sorted((DRAFTS / batch).glob("*.md")):
            body = strip_header(read(f))
            ctx = ""
            if batch == "enemies":
                e = idx.get(f.stem)
                if e:
                    ctx = f"Enemy {e['name']} ({f.stem}), class {e['cls']}, corporation {e['corp']}. Class brief: {b1.CLASS_BRIEF[e['cls']]}\n"
            if batch == "events":
                mech = f.stem.split("_")[1].upper()
                ctx = f"Event mechanic family: {mech}: {b1.EVENT_MECH.get(mech, '')}\n"
            user = (f"Review the draft {batch}/{f.stem}.\n{ctx}\n=== The template the draft was asked to follow ===\n{CRIT_TEMPLATES[batch]}\n\n"
                    f"=== The draft ===\n{body}")
            out.append(mk(f"critic__{batch}__{f.stem}", user, 20000, CRITIC_ROLE))
    for corp in CORPS:
        parts = []
        for e in idx.values():
            if e["corp"] == corp and not e["satellite"] and (DRAFTS / "enemies" / f"{e['id']}.md").exists():
                parts.append((f"enemies/{e['id']} ({e['cls']})", strip_header(read(DRAFTS / "enemies" / f"{e['id']}.md"))))
        for sub in ("bosses", "hq"):
            if (DRAFTS / sub / f"{corp}.md").exists():
                parts.append((f"{sub}/{corp}", strip_header(read(DRAFTS / sub / f"{corp}.md"))))
        for f in sorted((DRAFTS / "events").glob(f"*_{corp}.md")):
            parts.append((f"events/{f.stem}", strip_header(read(f))))
        docs = "\n\n".join(f"##### DRAFT {n} #####\n{t}" for n, t in parts)
        user = f"Review the corporation set for {corp} ({len(parts)} drafts).\n\n{docs}"
        out.append(mk(f"critic__corp__{corp}", user, 32000, CORP_ROLE))
    return out


# ---------------------------------------------------------------- 2. station

ALT = {"hivemind": "botnet", "overclocker": "rigger", "phantom": "ghost", "wrecker": "breaker"}


def class_summary() -> str:
    rows = []
    for p in sorted((ROOT / "content/classes").glob("*.tres")):
        t = read(p)
        comments = " ".join(l[1:].strip() for l in t.splitlines() if l.startswith(";"))
        rows.append(f"- {p.stem}: hp {prop(t, 'base_hp')}, {prop(t, 'description')} | notes: {comments[:700]}")
    return "\n".join(rows)


STATION_TEMPLATE = """Design the STATION BONUS for this class (G8: every class has a unique station bonus; an alternate class feels similar to its base class). The station bonus applies when the operative is stationed on a node of the city (GDD sections 3 and 7; raid defense) and is scaled by Rank (station_bonus_multiplier 1.0 / 1.25 / 1.5 / 2.0 today).
Produce:
# station: <class>
1. **Current** (one line, and whether it is unique and meaningful for the class).
2. **Proposed station bonus** (what it does, in raid terms and in non-raid terms if it has one; trigger; exact numbers per Rank 0-3; how it reads on the node in the grid view).
3. **Family / alternates** (if this class is a base: sketch what each of its alternates would do so they feel similar but distinct; if it is an alternate: say how it relates to its base in one sentence and what is different). Keep the whole family consistent; propose the other members' bonuses in a short table.
4. **Fit with the defense trio** (BLOCK / SHIELD / SANDBOX) and with the other 7 classes: no two classes may have the same bonus; avoid dominant stacking when all stationed.
5. **Data** (TriggeredEffectData/EffectData fields needed; whether a data-only change; new N# or NEW: system and size).
6. **Q:** (max 3)
Keep it to 500-900 words."""


def build_station() -> list[dict]:
    out = []
    summ = class_summary()
    cfg = "\n".join(l for l in read(ROOT / "content/config/campaign_config.tres").splitlines() if "station" in l.lower())
    for p in sorted((ROOT / "content/classes").glob("*.tres")):
        cid = p.stem
        fam = f"{cid} is an ALTERNATE of {ALT[cid]}." if cid in ALT else "base class" + (", alternates: " + ", ".join(k for k, v in ALT.items() if v == cid) if cid in ALT.values() else "")
        user = f"""Class: {cid} ({fam})

=== All classes (summary) ===
{summ}

=== station-related config ===
{cfg}

=== This class file ===
{read(p)}

{STATION_TEMPLATE}"""
        out.append(mk(f"station__{cid}", user, 24000))
    return out


# ---------------------------------------------------------------- 3. slice_upgrades

SLICE_ENUM = ["SHIM", "OVERFLOW", "DEFRAG", "DETOUR", "SANDBOX", "TROJAN", "HOTFIX", "INFECT", "NULL"]
SLICE_TYPES = ["SHIM", "OVERFLOW", "DEFRAG", "DETOUR", "SANDBOX", "TROJAN", "HOTFIX", "NULL"]
SLICE_TEMPLATE = """Design the LEVEL I-IV UPGRADE PROGRESSION for this player slice type (G5: slice upgrades are their own pass; tiers are called Level I, II, III, IV...).
Context you must respect: slice sizes vary, even sizes included (R11); each sub-tick of a slice has a quality (a 4-tick slice reads WEAK, GOOD, GOOD, WEAK; a 5-tick slice WEAK, GOOD, PERFECT, GOOD, WEAK; a chip may upgrade tick values); the three defense tiers BLOCK (temporary), SHIELD (lingering), SANDBOX (negates a whole attack) are kept; amount modes FLAT/PERCENT exist; the wheel is 30 ticks and the player has few slices, so size is the scarcest resource.
Produce:
# slice_upgrades: <type>
1. **Role of the type** (what it is for; today's variants from the content list and which are redundant).
2. **Level table** Level I (base) .. Level IV: size in ticks, tick-quality pattern, output (FLAT or PERCENT), extra effect, what the player gives up or pays. Show that each level is a real choice rather than a strict upgrade where possible, and that Level IV is exciting. Say how a Level maps onto existing SliceData fields (size, base_output, extra_effects) and the new fields needed.
3. **Tick-quality interplay (R11)**: how upgrades change the quality pattern, interplay with the "Calibrated" firmware idea (a chip that upgrades a slice's tick values) and with PERFECT-only effects; avoid making size 1-2 slices pointless or mandatory.
4. **Rack flash** (G15): the Server Rack reward "flash": upgrade a slice by one Level OR swap it for another slice of the pool. Spell out what is offered (how many choices, rarity, whether the type can be swapped to a different type), cost, and how this type shows up in flash offers; the reward-table row kind (N18).
5. **Economy**: where else upgrades come from (shop/workshop/Cycles cost placeholder) and how they interact with Firmware sockets.
6. **Systems & data** (N# or NEW:, size), **Q:** (max 4).
Keep it to 700-1200 words."""


def build_slice_upgrades() -> list[dict]:
    out = []
    by_type: dict[int, list[Path]] = {}
    for p in sorted((ROOT / "content/slices").glob("*.tres")):
        by_type.setdefault(int(prop(read(p), "slice_type", "0") or 0), []).append(p)
    fw = "\n".join(f"- {p.stem}: {prop(read(p), 'description')} (allowed types {prop(read(p), 'allowed_slice_types') or 'any'})" for p in sorted((ROOT / "content/firmware").glob("*.tres")))
    for t in SLICE_TYPES:
        n = SLICE_ENUM.index(t)
        slices = "\n\n".join(f"--- {p.relative_to(ROOT).as_posix()} ---\n{read(p)}" for p in by_type.get(n, []))
        user = f"""Slice type: {t} (SliceType enum value {n}).

=== Existing slices of this type ===
{slices or '(none in content/slices; describe from the GDD)'}

=== Slice schema ===
{script_dump('slice_data.gd', 'wheel_slot_data.gd')}

=== Firmware list (so upgrades and chips do not overlap) ===
{fw}

{extras()}

{SLICE_TEMPLATE}"""
        out.append(mk(f"slup__{t.lower()}", user, 32000))
    return out


# ---------------------------------------------------------------- 4. card_upgrades

CARD_TEMPLATE = """Design the UPGRADED version of this card (G5: card upgrades are their own pass; Level naming is for slices, here call it the + version unless you need more than one level, and say so).
Produce:
# card_upgrades: <id>
1. **Role** (what the card is for in its class deck; one line).
2. **Upgraded card**: name (placeholder, e.g. "<Name>+"), RAM cost, Cycle cost multiplier, text, exact effect list (EffectData: type, target, amount or percent with amount mode, ring_scope, status, durations), exhaust flag, wheel_target. Keep the role: an upgrade sharpens the card, it must not turn it into a different card; prefer one of: a bigger number, a cost reduction, an added rider, a wider target. Do not make the + version strictly dominate at every cost point if a sidegrade is better; justify.
3. **Interplay** with the new rules in one or two lines (variable slice sizes, tick quality, corruption as double RAM, statuses as anti-firmware, parasites on the Parasite ring) only where it matters.
4. **Data**: fields changed against the current .tres; any new effect or system (N# or NEW:).
5. **Q:** (max 2)
Keep it to 200-400 words. Be precise."""


def build_card_upgrades() -> list[dict]:
    out = []
    schema = script_dump("card_data.gd", "effect_data.gd")
    owners: dict[str, list[str]] = {}
    for c in (ROOT / "content/classes").glob("*.tres"):
        for m in re.finditer(r'content/cards/(\w+)\.tres', read(c)):
            owners.setdefault(m.group(1), []).append(c.stem)
    index = "\n".join(f"- {p.stem}: {prop(read(p), 'display_name')} (RAM {prop(read(p), 'ram_cost')}, class {prop(read(p), 'class_id') or 'any'}): {prop(read(p), 'description')}" for p in sorted((ROOT / "content/cards").glob("*.tres")))
    for p in sorted((ROOT / "content/cards").glob("*.tres")):
        own = ", ".join(sorted(set(owners.get(p.stem, [])))) or "reward pool only"
        user = f"""Card: {p.stem}. Class link: {prop(read(p), 'class_id') or 'neutral'}. Referenced by class files: {own}.

=== Card file ===
{read(p)}

=== Schema ===
{schema}

=== All cards (index) ===
{index}

{CARD_TEMPLATE}"""
        out.append(mk(f"cardup__{p.stem}", user, 16000))
    return out


# ---------------------------------------------------------------- 5. inner ring (3 concepts), 6. rim gates

RING_LENSES = {
    "a": ("EVOLUTION", "Keep a ring concentric on the wheel and a few-segment idea, but make it read from afar and make its effect and manipulation obvious. The smallest change that fixes G1."),
    "b": ("SEPARATE_PLATE", "Take the inner ring OFF the wheel face: a separate readable plate/track (for example a row, a dial or a slot-machine strip next to the wheel) that is fed by the wheel's results. The wheel stays a clean 30-tick disc."),
    "c": ("POINTER_COUPLED", "Fuse the inner ring with the pointer/needle system: pointers may sit on any tick, there can be several, enemies have needles; make the inner layer a modifier track that rides pointers, tick quality or slice boundaries instead of being its own spinning disc."),
}
RING_TEMPLATE = """Produce ONE redesign concept for the INNER RING (G1: the inner ring does not read from afar, and it is unclear what it does or how to manipulate it; slice REARRANGING is not a priority, maybe never). Concept lens: {lens}.
Hard constraints: readable at a glance from afar; consistent with VARIABLE slice sizes (R11; even sizes included; tick quality per sub-tick) and with the FUTURE PARASITE RING (anti-slices that act against the player; parasites are placed by enemies; statuses are anti-firmware); deterministic, previews equal results; class identity (Breaker x2/Pierce, Ghost freeze, etc.) must survive; the Rank 1/3 inner-ring unlocks and the Rank 3 segment swap in content/classes must map onto it.
Produce:
# inner_ring concept {key}: <working title>
1. **One-sentence pitch** and a **plain-language description of what it does to the outcome of a spin**.
2. **Anatomy**: the elements (count, size, states), how each shows its effect on the wheel face or HUD (describe the picture precisely enough for an artist: shapes, colors by role, motion), the legibility test from three metres.
3. **Manipulation**: every way the player can change it (cards, nudges, Firmware, class abilities, free action?), costs in RAM and ticks, how the preview shows the result, what undo does.
4. **Rules**: precise resolution order with the outer slice, PERFECT/GOOD/WEAK interplay, pierce/x2/anchor/corrupt/echo/accelerator segment equivalents (map every existing segment in content/rings/segments to the new design: keep/change/retire), interaction with satellites and the Parasite ring.
5. **Class mapping**: how each of the 8 classes' inner ring/segment options (Rank 1 and 3) translate; what the Rank 3 swap becomes.
6. **Worked example**: one full turn with numbers.
7. **Data & systems**: new/changed resources and fields (InnerRingData, RingSegmentData, wheel_data), N# or NEW:, size S/M/L, migration cost of existing content, data-only fallback if any.
8. **Risks and what it costs against the other two concepts you can imagine**, and **Q:** (max 5).
Keep it to 1200-2000 words."""


def build_inner_ring() -> list[dict]:
    rings = "\n\n".join(f"--- {p.relative_to(ROOT).as_posix()} ---\n{read(p)}" for p in sorted((ROOT / "content/rings").glob("*.tres")))
    segs = "\n\n".join(f"--- {p.relative_to(ROOT).as_posix()} ---\n{read(p)}" for p in sorted((ROOT / "content/rings/segments").glob("*.tres")))
    hubs = "\n".join(f"- {p.stem}: {prop(read(p), 'description')}" for p in sorted((ROOT / "content/hub_cores").glob("*.tres")))
    out = []
    for key, (name, lens) in RING_LENSES.items():
        user = f"""Concept {key.upper()} of 3: {name}. {lens}

=== Inner ring schema ===
{script_dump('inner_ring_data.gd', 'ring_segment_data.gd', 'wheel_data.gd', 'hub_core_data.gd')}

=== Rings ===
{rings}

=== Segments ===
{segs}

=== Hub cores (descriptions) ===
{hubs}

=== Classes (summary) ===
{class_summary()}

{extras()}

{RING_TEMPLATE.format(lens=name + ': ' + lens, key=key.upper())}"""
        out.append(mk(f"inner__{key}", user, 48000))
    return out


RIM_TEMPLATE = """Design RIM GATES (G7: keep them, and move them earlier in the roadmap; N15 in CONTENT_DESIGN_V2: gate ticks plus effects; traversal detection in nudges and spins, never the respin; the preview lights crossed gates). The Orbital mini-boss (P1 Countdown: 2 rim gates; a nudge or spin that carries a gate past its needle advances a countdown) is the first consumer; the Orbital corporation's satellites and the rest of the corporations may use them too.
Produce:
# rim_gates: mechanic design
1. **What a rim gate is** (a marker on a tick of the wheel's rim, owned by whom: enemy, player, event?; what the gate does when a slice, needle or pointer crosses/lands on it; difference between crossing and stopping).
2. **Rules**: exact definition of "traversal" for nudges (1-tick moves), card spins (N ticks), the main spin, the respin (explicitly excluded) and pointer motion; order of resolution; what happens with multiple gates in one move; interaction with threshold parking, variable slice sizes, tick quality, satellites, statuses and the Parasite ring; determinism and preview lighting.
3. **Gate types** (a small catalog, 5-8, with effects, FLAT/PERCENT amounts, who benefits) including player-side gates (Firmware, Daemon, class, event) so it is not only an enemy tool.
4. **Player-facing readability and counterplay**: art/HUD description, how the player learns it, how to disarm/move/exploit gates, anti-frustration rules.
5. **Worked example** with numbers against the Orbital mini-boss concept.
6. **Data & systems**: fields, N15 scope, rollout order (what to build first), S/M/L, data-only fallback, test list (preview == result).
7. **Q:** (max 5).
Keep it to 1000-1800 words."""


def build_rim_gates() -> list[dict]:
    orb = read(DRAFTS / "enemies" / "mission_director.md") if (DRAFTS / "enemies" / "mission_director.md").exists() else ""
    user = f"""=== Schema ===
{script_dump('satellite_spawn_data.gd', 'wheel_data.gd')}

=== Round-1 draft that uses rim gates: Orbital mini-boss (enemies/mission_director) ===
{strip_header(orb)}

{extras()}

{RIM_TEMPLATE}"""
    return [mk("rim__gates", user, 32000)]


# ---------------------------------------------------------------- 7. catalogs


def status_usage() -> str:
    lines = []
    for sub in ("enemies", "cards", "firmware", "slices", "daemons"):
        n = sum(1 for p in (ROOT / "content" / sub).glob("*.tres") if re.search(r"^status = [1-9]", read(p), re.M))
        lines.append(f"- content/{sub}: {n} files apply a status")
    return "\n".join(lines)


CATALOG_STATUS = """Design the STATUS CATALOG. Rulings: statuses are ANTI-FIRMWARE (percent output reduction, tick-strength reduction such as Perfect -> Good, and similar; firmware improves a slice, a status degrades it); xN stacks are yes (G2); statuses SURVIVE a phase change (a boss may cleanse on phase change); heal/shield/corruption effects come in FLAT and PERCENT amount modes (variants of existing effects, not new statuses); CORRUPTED becomes a debuff: cards and nudges cost DOUBLE RAM on a corrupted slice (damage moves to the Parasite ring); today's enum is NONE, CORRUPTED, OVERCLOCKED, ENCRYPTED, PARASITE and PARASITE (a drone that halves the slice) moves to the Parasite ring design. New status types are allowed once the rules are settled.
Produce:
# catalog: statuses
1. **Rules of a status** (applies to: a slice, a wheel, the player, an enemy; stacking xN: how stacks add, cap, decay; duration/turn rules; display; cleanse rules; which sources apply and remove them; interaction with phase change, threshold parking, enrage; ordering with FLAT/PERCENT modifiers; how tick-quality reduction interacts with variable slice sizes R11).
2. **Catalog table** (aim for 12-18): id, applies to, effect per stack with numbers (placeholders), cap, duration, who applies it (player / enemy / event), cleanse, the firmware idea it is the anti-of, one-line icon/read at a glance. Mark which exist today (CORRUPTED, OVERCLOCKED, ENCRYPTED, PARASITE) and what changes. Include both slice-targeted statuses (anti-firmware) and a few entity-targeted ones if you judge them necessary (justify; the ruling is anti-firmware).
3. **Pairings**: for each status, the player's counterplay (cards/chips/daemons/Exploits) and the enemies/bosses in the round-1 roster that would use it (name drafts only if you recognise them).
4. **Interaction matrix** of the 6 most dangerous combinations and how they are bounded.
5. **Data & systems**: schema for statuses as data (the enum becomes a resource?), N# or NEW:, migration of existing content, S/M/L, data-only fallback.
6. **Q:** (max 5).
Keep it to 1500-2500 words."""

CATALOG_PARASITE = """Design the PARASITE CATALOG (G3: build the Parasite ring; it is not in the code, today PARASITE is only a status that halves a slice). Rulings: parasites are ANTI-SLICES: anything a slice can do, a parasite can do against you (damage the player, reduce damage to the boss, apply or remove statuses); the ring is a second ring on the player's wheel owned by the enemy side; parasites are placed by enemies (and events) and removed/cleansed by the player; corruption damage moves to the Parasite ring; variable slice sizes apply (R11); statuses are anti-firmware (separate catalog).
Produce:
# catalog: parasites
1. **The ring**: geometry (how many ticks, how segments are sized and placed, relation to the player's outer slices and the inner ring redesign), who reads it, when does it resolve (with the player's spin? the enemy's turn?), whether it spins/has a pointer, how it reads from afar, how many parasites at once, what happens when it is full, determinism and preview.
2. **Segment types** (aim for 10-14): id, size in ticks, effect with numbers (FLAT/PERCENT), trigger (every spin / on a tick-quality / on card played / on nudge), what it mirrors from the slice catalog (Shim -> damage to player, Defrag -> ..., Sandbox -> ..., Hotfix, Trojan -> ..., Null), how it is removed (card, Perfect on it, firmware, daemon, time), what the player gives up to ignore it. Include at least 3 that apply or remove a status, 2 that reduce damage to the boss, 2 that damage the player, and 1 that is a pure threat to the wheel/inner ring.
3. **Placement and removal rules**: sources (enemy attacks, phases, satellites, events, raid), caps, stacking, whether a phase change keeps them (statuses survive; decide for parasites and say why).
4. **Counterplay and teaching**: cards/chips that interact (propose 4-6 new card or firmware hooks, naming them only descriptively), how L1-2 introduces the ring, how bosses use it.
5. **Existing PARASITE migration**: what Botnet's parasite drones and cards (parasite_pulse, leech_worm) become.
6. **Data & systems**: resources (ParasiteSegmentData, wheel/ring state in scripts/state), N# or NEW:, S/M/L, build order, data-only fallback, test list.
7. **Q:** (max 5).
Keep it to 1500-2500 words."""


def build_catalog() -> list[dict]:
    enemy_status = "\n".join(
        f"- {p.stem}: {m}" for p in sorted((ROOT / "content/enemies").glob("*.tres"))
        for m in [", ".join(sorted(set(re.findall(r"^status = (\d)", read(p), re.M))))] if m)
    cards = "\n".join(f"- {p.stem}: {prop(read(p), 'description')}" for p in sorted((ROOT / "content/cards").glob("*.tres")) if re.search(r"parasite|corrupt|status|encrypt|overclock|cleanse", read(p), re.I))
    base = f"""=== Current usage ===
{status_usage()}
Enemies that apply a status (value = Status enum ordinal: 1 CORRUPTED, 2 OVERCLOCKED, 3 ENCRYPTED, 4 PARASITE):
{enemy_status}

=== Schema ===
{script_dump('effect_data.gd', 'triggered_effect_data.gd', 'ring_segment_data.gd', 'satellite_spawn_data.gd')}

=== Cards that touch parasite/status ===
{cards}
"""
    return [
        mk("catalog__status", f"{base}\n\n{extras()}\n\n{CATALOG_STATUS}", 48000),
        mk("catalog__parasite", f"{base}\n\n{extras()}\n\n{CATALOG_PARASITE}", 48000),
    ]


# ---------------------------------------------------------------- 8. sync strike

SYNC_TEMPLATE = """Design pass for the DISPATCH SYNC STRIKE (designer: yes as current thinking, with its own design pass; a small fight for each operative, then the final fight). The designer's open questions: (Q-A) Do the three mini fights dictate effects in the final fight? (Q-B) Is the final fight a ROTATING FOCUS: all three operatives against the HQ, swapping between the three player wheels and managing all of them before End Turn?
Produce:
# sync_strike: design options
1. **Constraints** (what the existing systems and the route/HQ redesign allow; one living operative vs three; what happens with fewer than 3 operatives; the HQ run is longer than 7 layers and every HQ is unique; relate to the round-1 drafts if shown).
2. **Three options** (2-3, clearly different). For each: fight structure (number of fights, turns, HP and phase budget in R2 terms), how Q-A is answered (what each mini fight gives or removes in the final, concrete examples for three operative archetypes), how Q-B is answered (the turn UI: what 'focus' means, how the player swaps between three wheels, what is resolved when, RAM and nudge budgets per operative, End Turn rules, preview rules, undo/checkpoint rules, determinism), what it teaches, readability, expected total turns and failure/retry rules, narrative beat.
3. **Comparison table** and a **recommendation** with reasons.
4. **Systems & data**: N# or NEW:, a multi-combat boss run (NB-1, size L), minimum data-only version, build order, dependency on the route/HQ redesign (G12), test list.
5. **Q:** (max 5).
Keep it to 1500-2500 words."""


def build_sync() -> list[dict]:
    dr = ""
    for rel in ("enemies/the_handler.md", "enemies/dispatch_core.md", "hq/rebel_cell.md"):
        p = DRAFTS / rel
        if p.exists():
            dr += f"\n\n=== Round-1 draft {rel} ===\n{strip_header(read(p))}"
    cur = "\n\n".join(f"--- content/enemies/{n}.tres ---\n{read(ROOT / 'content/enemies' / (n + '.tres'))}" for n in ("dispatch_core", "the_handler") if (ROOT / "content/enemies" / (n + ".tres")).exists())
    user = f"""=== Current Dispatch/Handler data ===
{cur}

=== Round-1 drafts ==={dr}

=== Classes (summary) ===
{class_summary()}

{extras()}

{SYNC_TEMPLATE}"""
    return [mk("sync__strike", user, 48000)]


# ---------------------------------------------------------------- 9. firmware

FW_TEMPLATE = """Judge this Firmware chip under the new rules and decide: KEEP, CHANGE or RETIRE.
New rules that matter for firmware: slice sizes vary (even sizes included) with a quality per sub-tick (a 4-tick slice reads WEAK, GOOD, GOOD, WEAK); pointers may sit on any tick; STATUSES are anti-firmware (percent output reduction, tick-strength reduction; xN stacks); PARASITES are anti-slices on a Parasite ring; CORRUPTED is a double-RAM-cost debuff; amount modes FLAT/PERCENT exist; satellites are fixed to a slice; a Firmware socket belongs to one slice; the defense trio is BLOCK / SHIELD / SANDBOX; enemy listeners react to player actions (e.g. counter on any player Perfect).
Produce:
# firmware: <id>
**Verdict:** KEEP / CHANGE / RETIRE
1. **What it does today** (one line) and **what role it plays** in a build (which slice types, which classes).
2. **Under the new rules**: what breaks, what gets better, what becomes degenerate (infinite loops, dominant picks, dead chips with 2-tick or 6-tick slices), and which statuses or parasites interact.
3. **Proposed spec** (if CHANGE or KEEP with tweaks): description text (US spelling), rarity, Cycle cost, allowed_slice_types, multipliers, triggered effects with numbers (FLAT/PERCENT), and how it reads on the slice. If RETIRE: what replaces its niche (name a different existing chip or a new one in one line).
4. **Data**: fields changed, N# or NEW:, S/M/L.
5. **Q:** (max 2)
Keep it to 250-450 words."""

FWNEW_TEMPLATE = """Propose NEW Firmware chips for the new rules. Mandatory ideas: (1) "Calibrated": a chip that upgrades a slice's TICK QUALITY values (a 4-tick slice WEAK, GOOD, GOOD, WEAK becomes GOOD, PERFECT, PERFECT, GOOD): design 3 tiers or variants of this family with numbers and size limits, and its interplay with Level I-IV slice upgrades; (2) SATELLITE MOVERS (G2: satellites are fixed to a slice; an operative class and maybe Firmware/Daemons may SHIFT satellites and respin/nudge them; a satellite can replace a satellite; satellites' wheels cannot be nudged): chips that shift, swap, or respin a satellite, or that clear one; (3) others that use the new systems: counters to statuses (anti-anti-firmware), parasite eaters, listener-aware chips (react to enemy listeners), pointer-on-any-tick tricks, rim gates (N15), corruption-aware chips, amount-mode (PERCENT) chips, defense trio chips (BLOCK/SHIELD/SANDBOX), threshold-parking aware chips (excess damage lost: chips that exploit the parked hit).
Produce:
# firmware: new chips
1. **Design goals and gaps in the current 18 chips** (a short list: slice types and roles that no chip serves).
2. **Chip table** (aim for 14-20 chips): id (working), allowed slice types, rarity, Cycle cost, exact effect with numbers, which new rule/system it needs (N# or NEW:), what build it enables, what it must NOT break.
3. **Calibrated family** in detail (tick-pattern tables for sizes 1-8 before/after).
4. **Satellite movers** in detail (rules for shift/swap/respin; limits; determinism).
5. **Risks**: the three most abusable chips and the proposed bound.
6. **Data & systems**, **Q:** (max 5).
Keep it to 1500-2500 words."""


def build_firmware() -> list[dict]:
    out = []
    idx = "\n".join(f"- {p.stem}: {prop(read(p), 'description')} (rarity {prop(read(p), 'rarity', '0')}, cost {prop(read(p), 'cycle_cost')}, allowed {prop(read(p), 'allowed_slice_types') or 'any'})" for p in sorted((ROOT / "content/firmware").glob("*.tres")))
    schema = script_dump("firmware_data.gd")
    allchips = "\n".join(read(p) for p in sorted((ROOT / "content/firmware").glob("*.tres")))
    for p in sorted((ROOT / "content/firmware").glob("*.tres")):
        user = f"""Chip: {p.stem}

=== Chip file ===
{read(p)}

=== Schema ===
{schema}

=== All chips (index) ===
{idx}

{FW_TEMPLATE}"""
        out.append(mk(f"fw__{p.stem}", user, 20000))
    user = f"""=== Schema ===
{schema}

=== The current 18 chips (full) ===
{allchips}

{extras()}

{FWNEW_TEMPLATE}"""
    out.append(mk("fw__new_chips", user, 48000))
    return out


# ---------------------------------------------------------------- 10. gdd

GDD_SECTIONS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "11", "13"]
GDD_TEMPLATE = """Write the proposed AMENDMENT for this one GDD top-level section so that it reflects ALL the 2026-10-16 designer rulings that touch it. The rulings to apply (when relevant to this section): phases replace fight length (normal 1, elite 2, mini-boss 2-3, HQ boss 4-5; 3-4 turns each); boss HP by tier band; threshold parking (excess lost); tier sets base values only; enrage (not a turn-count phase trigger); amount modes FLAT/PERCENT; statuses survive phases; statuses are anti-firmware; parasites are anti-slices on a Parasite ring; corruption = double RAM on a slice; pointers on any tick; variable slice sizes with per-tick quality; new firmware ideas (tick-quality upgrade); satellites fixed to a slice, movable only by specific classes/chips, a satellite can replace a satellite, xN stacks; enemy listeners; block-nudge / block-respin; defense trio BLOCK / SHIELD / SANDBOX; Level I-IV slice upgrades, card upgrades, data-driven rewards, Rack flash; G8 unique station bonus per class; G14 shop wheel 100/80/100 and a nudge bought or from a Daemon; rim gates; Sync Strike; 7 corporations (Aurelian Concord, Tethys Deep added); new node types (Rest, Workshop, Cache; Safehouse and Heat Sink are grid-view nodes; no Intel/Relay/Ambush node); events that alter future fights/paths, impromptu fights, event wheel, events in HQ/raid-win views; access keys = Exploits, each Exploit has its own building (D5); the zoom between the grid view and the netrun (D6); the map shows a Heat chip and a "RAID AT n" tick (D9); HQ runs may be longer than 7 layers and each is unique (D10); raid modifiers R1-R4; Site NAMES removed (a Site is its type); G11 DOWN/TAKEN rules; new procedural city (D3); text 1.0 mouse/keyboard scope.
Output:
# gdd: section <N> amendment
1. **Summary** (3-6 lines: what changes in this section and what does not).
2. **Amendments**, numbered, in document order. Each is diff-style prose: "In <subsection/heading>, replace '<quoted old sentence or locator>' with:" then the exact new text (GDD voice: rule statements, numbered where the section is numbered; US spelling; numbers as placeholders marked '(placeholder)'). Include inserted new subsections with their full text. Mark deletions explicitly ("delete ...").
3. **Contradictions with other sections** you noticed (section + locator) so the other amendment passes can align.
4. **Not covered / needs a ruling** (only genuine gaps).
5. **Q:** (max 4)
If a ruling does not touch this section, do not invent changes: say so. Be exact and complete for the parts that change; length follows the amount of change (500-4000 words)."""


def gdd_sections() -> dict[str, str]:
    t = read(ROOT / "docs/GDD.md")
    heads = [(m.start(), m.group(1)) for m in re.finditer(r"^## (\d+)\. ", t, re.M)]
    heads.append((len(t), "end"))
    return {n: t[a:b] for (a, n), (b, _) in zip(heads, heads[1:])}


def build_gdd() -> list[dict]:
    secs = gdd_sections()
    titles = "\n".join(l for l in read(ROOT / "docs/GDD.md").splitlines() if l.startswith("## "))
    out = []
    for n in GDD_SECTIONS:
        user = f"""GDD outline:
{titles}

=== GDD section {n} (the text to amend; sections 1-8 are also in the shared context) ===
{secs[n]}

{extras()}

{GDD_TEMPLATE}"""
        out.append(mk(f"gdd__s{int(n):02d}", user, 40000))
    return out


# ---------------------------------------------------------------- main


def est_tokens(s: str) -> int:
    return int(len(s) / 3.6)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--retry-file", default="", help="custom_ids (one per line) to rebuild alone with max_tokens 64000")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    idx = enemy_index()
    builders = {
        "critic": lambda: build_critic(idx),
        "station": build_station,
        "slice_upgrades": build_slice_upgrades,
        "card_upgrades": build_card_upgrades,
        "inner_ring": build_inner_ring,
        "rim_gates": build_rim_gates,
        "catalog": build_catalog,
        "sync_strike": build_sync,
        "firmware": build_firmware,
        "gdd": build_gdd,
    }
    if args.retry_file:
        want = {l.strip() for l in Path(args.retry_file).read_text(encoding="utf-8").splitlines() if l.strip()}
        reqs = [r for fn in builders.values() for r in fn() if r["custom_id"] in want]
        for r in reqs:
            r["params"]["max_tokens"] = 64000
        with (out / "retry.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
            for r in reqs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"retry: {len(reqs)} requests of {len(want)} wanted")
        return 0
    only = [x for x in args.only.split(",") if x]
    manifest = {}
    tot_cost = tot_worst = 0.0
    for name, fn in builders.items():
        if only and name not in only:
            continue
        reqs = fn()
        with (out / f"{name}.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
            for r in reqs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        # uncached input = user message + the round-2 system block (the last system entry)
        unc = sum(est_tokens(r["params"]["messages"][0]["content"]) + est_tokens(r["params"]["system"][-1]["text"]) for r in reqs)
        b_out = sum(EXPECT_OUT.get(kind_of(r["custom_id"]), 8000) for r in reqs)
        cap = sum(r["params"]["max_tokens"] for r in reqs)
        shared = COMMON_TOKENS * len(reqs) * 0.10 + COMMON_TOKENS * 1.25  # cache reads + one write per batch
        cost = (unc * 1.0 + shared + b_out * 5.0) / 1e6
        worst = (unc * 1.0 + shared + cap * 5.0) / 1e6
        tot_cost += cost
        tot_worst += worst
        manifest[name] = [r["custom_id"] for r in reqs]
        print(f"{name}: {len(reqs)} requests, ~{unc:,} uncached in (+{COMMON_TOKENS:,} shared each), expected out ~{b_out:,}, expected ${cost:.2f}, cap-worst ${worst:.2f}")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"TOTAL expected ${tot_cost:.2f}, cap-worst ${tot_worst:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
