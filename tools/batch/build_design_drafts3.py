"""Build the plan-2 design-draft batches, ROUND 3 (docs/handoff/plan2/BATCH_ROUND3.md), as Message Batches payloads.

    python tools/batch/build_design_drafts3.py --out <dir> --stage A            # triage, questions, test_plans, raids, names, balance_sweeps
    python tools/batch/build_design_drafts3.py --out <dir> --stage B            # v2, briefs (after triage is ingested + merged)
    python tools/batch/build_design_drafts3.py --out <dir> --only triage,names  # some batches
    python tools/batch/build_design_drafts3.py --out <dir> --retry-file <ids.txt>  # rebuild the listed custom_ids alone (retry.jsonl, max_tokens 64000)

Batches (custom_id prefix -> drafts/<dir>): triage (Haiku), questions (Haiku), names (Haiku), tplan (test_plans, Sonnet),
raid3 (raids, Sonnet), bsweep (balance_sweeps, Sonnet), v2 (v2, Sonnet), brief (briefs, Sonnet).
The Sonnet batches use the SAME cached shared block as rounds 1 and 2 (build_design_drafts.common_system); round-3 notes
come after the cache point. The Haiku batches carry no shared block (the cache is per model).
Drafts only: nothing here builds content. Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_design_drafts as b1  # noqa: E402
import build_design_drafts2 as b2  # noqa: E402
from build_design_drafts import ROOT, read, req  # noqa: E402
from build_design_drafts2 import DRAFTS, COMMON_TOKENS, strip_header  # noqa: E402

HAIKU = "claude-haiku-4-5"
HAIKU_IN, HAIKU_OUT = 0.5, 2.5  # $/MTok, batch price
EXPECT_OUT = {"triage": 700, "questions": 900, "names": 900, "tplan": 9000, "raid3": 22000, "bsweep": 9000,
              "v2": 11000, "brief": 2500}

ROUND3_HEAD = """ROUND 3 NOTES: rounds 1 and 2 exist under docs/handoff/plan2/drafts (drafts, critic reviews, passes). The rules R1-R13 and the 2026-10-16 designer rulings stay binding. Same output discipline as before: ONE markdown document, no preamble, concrete numbers, "Q:" lines at the end (max 5). Dependencies on new systems: N# from CONTENT_DESIGN_V2 section 5, else "NEW: <name>". Designer scope: text 1.0 and mouse/keyboard only; US English in every player-facing string.
"""

ROUND3_BATCHES = ["triage", "questions", "names", "test_plans", "raids", "balance_sweeps", "v2", "briefs"]
SUBDIR = {"tplan": "test_plans", "raid3": "raids", "bsweep": "balance_sweeps", "brief": "briefs"}


def mk(cid: str, user: str, max_tokens: int, role: str = "") -> dict:
    return req(cid, ROUND3_HEAD + role, user, max_tokens)


def haiku_req(cid: str, system: str, user: str, max_tokens: int) -> dict:
    return {"custom_id": cid, "params": {"model": HAIKU, "max_tokens": max_tokens,
                                          "system": system, "messages": [{"role": "user", "content": user}]}}


def kind_of(cid: str) -> str:
    return cid.split("__")[0]


def draft_files(include_critic: bool = False) -> list[tuple[str, Path]]:
    out = []
    for d in sorted(p for p in DRAFTS.iterdir() if p.is_dir()):
        if d.name == "critic" and not include_critic:
            continue
        if d.name in ("triage", "questions", "names", "test_plans", "balance_sweeps", "v2", "briefs"):
            continue
        for f in sorted(d.glob("*.md")):
            out.append((d.name, f))
    return out


# ---------------------------------------------------------------- 1. triage (Haiku)

TRIAGE_SYS = """You compress review findings. Input: numbered issue paragraphs, each already labeled BLOCKER by a critic of a game design draft. Output ONLY one line per input paragraph, in input order, pipe separated:
BLOCKER | <one-line statement of the problem, max 25 words, plain text> | <theme>
theme is exactly one of: phase-budget-arithmetic, tier-or-hp-bands, statuses-and-parking, new-system-dependency, rule-violation-R1-R13, amount-modes-and-scaling, sustain-and-defense, wheel-geometry, parasite-or-satellite, preview-or-determinism, text-or-naming, other.
Do not add, merge, skip or invent lines: the number of output lines equals the number of input paragraphs. No preamble, no markdown, no commentary."""

BLOCKER_START = re.compile(r"^\s*\d+\.\s+\**BLOCKER")
ISSUE_START = re.compile(r"^\s*\d+\.\s|^#")


NL = chr(10)


def blocker_paragraphs(text: str) -> list[str]:
    """The critic's issues whose label is BLOCKER (a numbered line starting '**BLOCKER'), each with its continuation lines."""
    paras, cur = [], None
    for line in text.splitlines():
        if BLOCKER_START.match(line):
            if cur is not None:
                paras.append(NL.join(cur))
            cur = [line]
        elif cur is not None and ISSUE_START.match(line):
            paras.append(NL.join(cur))
            cur = None
        elif cur is not None:
            cur.append(line)
    if cur is not None:
        paras.append(NL.join(cur))
    return paras


def build_triage() -> list[dict]:
    out = []
    for f in sorted((DRAFTS / "critic").glob("*.md")):
        paras = blocker_paragraphs(strip_header(read(f)))
        if not paras:
            continue  # no BLOCKER-labeled issue: nothing to triage (corporation reviews carry none)
        body = (NL + NL).join(f"[{i + 1}] {p}" for i, p in enumerate(paras))
        head = f"Critic file: critic/{f.stem}.md ({len(paras)} paragraphs)"
        out.append(haiku_req(f"triage__{f.stem}", TRIAGE_SYS, head + NL + NL + body, 2500))
    return out


# ---------------------------------------------------------------- 3. questions (Haiku)

Q_SYS = """You extract open design questions. Input: one design draft for a roguelite deckbuilder. List every open question or item left for the designer to decide: lines starting with "Q:" or "Q1:" etc., sections titled Open questions or Questions, and phrases such as "designer to decide", "needs a ruling", "TBD by designer", "open question". Do not invent questions and do not list resolved choices.
Output ONLY lines, pipe separated, one per question:
Q | <the question, one line, max 40 words, keep the draft's wording> | <topic-slug: 2-4 lowercase words joined by hyphens naming the underlying decision, reused for the same decision across drafts> | <area: one of rules, balance, new-system, ui-and-art, economy, narrative, process>
If the draft has none, output exactly: NONE. No preamble, no commentary."""


def build_questions() -> list[dict]:
    out = []
    for batch, f in draft_files():
        body = strip_header(read(f))
        out.append(haiku_req(f"questions__{batch}__{f.stem}", Q_SYS, f"Draft file: {batch}/{f.stem}.md\n\n{body}", 3500))
    return out


# ---------------------------------------------------------------- 7. names (Haiku)

NAME_CORPS = {
    "meridian": "Meridian Freight Systems (logistics, freight, supply chains)",
    "orbital": "Orbital Commons (satellites, launch, space infrastructure)",
    "solace": "Solace Biosystems (biotech, clinics, genome, 'a doctor treating a disease and the disease is you')",
    "tethys": "Tethys Deep (new corporation, deep-sea / ocean infrastructure; art calls the HQ the Black Smoker)",
    "aurelian": "Aurelian Concord (new corporation, finance / golden concord, ceremony and ledgers)",
}
NAMES_SYS = """You propose display names for a corporation's Central Server (the boss Site of a cyberpunk netrun game). Names are ALL CAPS with a leading THE where natural, 2-4 words, evocative, readable on a sign. Output ONLY markdown in exactly this form, no preamble:
## <CORP>
1. **NAME**: one-line rationale (the corporation's fiction and the boss mechanic hook).
2. **NAME**: ...
3. **NAME**: ...
Exactly 3 options. Avoid every name in the CONFLICT list (already used by the art or other corporations), avoid trademarks of real companies, and avoid names that repeat words used in the other corporations' existing Central Server names. US spelling."""


def central_names_context() -> str:
    gdd = read(ROOT / "docs/GDD.md")
    a = gdd.index("### 8.2 The Cell & DISPATCH")
    b = gdd.index("### 8.6 Delivery")
    sec8 = gdd[a:b]
    c = gdd.index("### 11.7 Central Server: Exploits")
    d = gdd.index("### 11.8 Pacing Targets")
    names = {}
    for f in sorted((ROOT / "docs/handoff/netrun_art").glob("*.md")):
        for m in re.finditer(r"\bTHE [A-Z][A-Z]+(?: [A-Z]+){0,2}\b", read(f)):
            names[m.group(0)] = names.get(m.group(0), 0) + 1
    conf = "\n".join(f"- {k} ({v}x)" for k, v in sorted(names.items(), key=lambda kv: (-kv[1], kv[0]))[:60])
    return (f"=== GDD 8.2-8.5 (world) ===\n{sec8}\n\n=== GDD 11.7 ===\n{gdd[c:d]}\n\n"
            f"=== CONFLICT list: all-caps THE-names already used in docs/handoff/netrun_art/ (plus Halcyon's chosen THE PANOPTICON, "
            f"THE GENOME CORE, THE MASTER MANIFEST, LAUNCH CONTROL, DISPATCH, THE BLACK SMOKER) ===\n{conf}\n\n"
            f"=== ART_DECISIONS ===\n{read(ROOT / 'docs/handoff/netrun_art/ART_DECISIONS.md')}")


def build_names() -> list[dict]:
    ctx = central_names_context()
    return [haiku_req(f"names__{cid}", NAMES_SYS, f"Corporation: {desc}\n\n{ctx}", 2500) for cid, desc in NAME_CORPS.items()]


# ---------------------------------------------------------------- 5. test_plans (Sonnet)

TPLAN_ROLE = """YOU ARE A TEST DESIGNER writing a GUT test plan for one new system. Output exactly one markdown document:
# test plan: <N#> <system name>
1. **What is a rule here** (the rule-bearing code per CLAUDE.md rule 6; what is view glue and gets only a flow test, not unit tests).
2. **Test files** table: target path under tests/unit/ or tests/integration/ (snake_case, test_<topic>.gd), the manifest tier (fast for rules, full for sweeps; deferred is for text scale > 1.0 / high contrast / gamepad and is out of scope), approx seconds, what it covers.
3. **Cases**: for each file a numbered list of GUT test names (test_<what>_<expected>) with one line each on setup and assertion. Cover, where they apply: preview equals result; seeded replay equal (same seed + same inputs = same state hash); determinism and RngService stream use (no global randi); deterministic tie-breaks (content id, then node id); rewind never crosses a checkpoint; undo-clean staging; save round trip and migration where a save version changes; content validation rejects bad data (named reasons); amount-mode / tier-scaling arithmetic with exact numbers; edge values (0, 1, max); the data-only fallback path if the draft names one.
4. **Fixtures and helpers** needed (seeds, tests/fixtures files, helper scripts), reusing tests/helpers/bounded_wait.gd conventions.
5. **Existing tests likely to break** and how to adapt them (name them if you can see them in the shown list; otherwise say what to grep).
6. **Order**: which test is written first and what it proves before any code is done.
Concrete numbers, no filler. 500-1100 words. At most 3 "Q:" lines at the end."""

N_HINTS = {"N6": "ON_NUDGE / ON_CARD_PLAYED / ON_PERFECT listeners; preview must equal result and undo cleanly",
           "N8": "save version 2 -> 3 migration is the key risk",
           "N12": "WheelMath on cumulative boundaries; every geometry caller",
           "N18": "reward rows replace hard-coded offers in _finish_combat"}


def n_row(n: str) -> str:
    t = read(ROOT / "docs/handoff/plan2/CONTENT_DESIGN_V2.md")
    for line in t.splitlines():
        if line.startswith(f"| {n} |"):
            return line
    raise KeyError(n)


def test_context() -> str:
    spec = read(ROOT / "docs/TECH_SPEC.md")
    a = spec.index("## 9. Testing")
    b = spec.index("## 10. Performance")
    manifest = json.loads(read(ROOT / "tests/test_manifest.json"))["scripts"]
    names = sorted(k.replace("res://tests/", "") for k in manifest)
    return (f"=== TECH_SPEC section 9 (testing) ===\n{spec[a:b]}\n\n=== existing test scripts (manifest, {len(names)}) ===\n" + "\n".join(names))


def build_tplan() -> list[dict]:
    ctx = test_context()
    # which drafts mention each N#: paths only, not content
    texts = [(b, f, read(f)) for b, f in draft_files()]
    out = []
    for i in range(1, 21):
        n = f"N{i}"
        users = [f"{b}/{f.stem}" for b, f, t in texts if re.search(rf"\b{n}\b", t)]
        user = (f"Write the test plan for {n}.\n\nSystem row from CONTENT_DESIGN_V2 section 5:\n{n_row(n)}\n\n"
                f"Hint: {N_HINTS.get(n, 'follow the rule-6 scope')}\n\n"
                f"Drafts that depend on {n} (paths under docs/handoff/plan2/drafts, {len(users)}): {', '.join(users[:40])}\n\n{ctx}")
        out.append(mk(f"tplan__{n.lower()}", user, 24000, TPLAN_ROLE))
    return out


# ---------------------------------------------------------------- 6. raids (Sonnet)

RAID_ROLE = """YOU ARE THE RAID DESIGNER for the single raid design pass (designer Q14). Designer rulings: R1 EXPOSED spotlight, R2 encrypted routes, R3 vehicle types, R4 a Heat-scaled second wave with an ULTIMATUM, which is the Schematics sink; all four in one pass. The round-1 raids draft and its critic review are shown: keep what the critic marked strong, fix every BLOCKER and MAJOR issue, and reconcile with the station-bonus drafts (docs/handoff/plan2/drafts/station) and the defense trio (BLOCK / SHIELD / SANDBOX). Use real GDD 7 numbers (setup phase, steps, spread, routing, preview) and the config facts supplied.
Output ONE markdown document:
# raids: unified design pass
1. **Raid model recap** (GDD 7 numbers and where each rule plugs in).
2. **R1 EXPOSED spotlight**, **R2 encrypted routes**, **R3 vehicle types** (a table of vehicle types with HP, speed, route behavior, what counters it, tier availability), **R4 second wave and ultimatum** (Heat scaling table, ultimatum offer, Schematics price formula tied to the economy numbers in the baseline: income about 1410, unspent about 191 per campaign, and how it sinks surplus without becoming mandatory).
3. **How the four interact** (one worked raid, step by step, with numbers; a table of failure modes and dominated plays).
4. **Preview and determinism** (what the setup preview shows; which RNG stream; preview equals result).
5. **Data and new systems** (fields needed, N# or NEW:, data-only fallback, size).
6. **Differences vs the round-1 draft** (bullet list, what each critic BLOCKER/MAJOR became).
7. **Q:** (max 5).
900-1800 words, concrete numbers."""


def build_raids() -> list[dict]:
    d1 = strip_header(read(DRAFTS / "raids" / "raids.md")) if (DRAFTS / "raids" / "raids.md").exists() else ""
    if not d1:
        f = sorted((DRAFTS / "raids").glob("*.md"))[0]
        d1 = strip_header(read(f))
    crit = "\n\n".join(f"--- {f.name} ---\n{strip_header(read(f))}" for f in sorted((DRAFTS / "critic").glob("critic*raids*.md")) + sorted((DRAFTS / "critic").glob("raids__*.md")))
    cfg = "\n".join(l for l in read(ROOT / "content/config/campaign_config.tres").splitlines()
                    if re.search(r"raid|heat|schem|station|crew|wave|defen", l, re.I) and not l.startswith("[ext_resource"))
    stations = "\n\n".join(f"--- station/{f.stem} (excerpt) ---\n{strip_header(read(f))[:1800]}" for f in sorted((DRAFTS / "station").glob("*.md")))
    base = read(ROOT / "docs/balance/BASELINE_e2e13918.md")
    raid_lines = "\n".join(l for l in base.splitlines() if re.search(r"raid|heat|schem", l, re.I))[:5000]
    tech = read(ROOT / "docs/TECH_SPEC.md")
    sec7 = tech[tech.index("## 7. Raid Resolver"):tech.index("## 8. Saving")]
    user = (f"Write the unified raid design pass.\n\n=== Round-1 raids draft ===\n{d1}\n\n=== Its critic review(s) ===\n{crit}\n\n"
            f"=== campaign_config.tres raid / heat / schematics / station lines ===\n{cfg}\n\n=== TECH_SPEC section 7 ===\n{sec7}\n\n"
            f"=== Baseline rows: raids, heat, schematics ===\n{raid_lines}\n\n=== Station bonus drafts (excerpts) ===\n{stations}")
    return [mk("raid3__unified", user, 40000, RAID_ROLE)]


# ---------------------------------------------------------------- 8. balance_sweeps (Sonnet)

BSWEEP_ROLE = """YOU ARE THE BALANCE SWEEP PLANNER. You write sweep specs for the logic-only balance sim (tools/balance/balance.py). Use EXACT command syntax from the tool docs shown (modes campaign|fight|boss|netrun; options --policy --skill --ice --seeds A:B -j N --name --set <id>.<prop>=<json> | *= | += --variant file.json --enemy --tiers --categories --source). Only reference properties that exist: take config property names from the campaign_config.tres shown and content ids from the lists shown; if a lever you need does not exist as data, say "NO LEVER: <what>" instead of inventing a property. Designer rule: no content change until the designer rules on 2-3 options; the sweeps measure, they do not edit files. Machine: at most 2 sim processes at once (-j 2), 6 cores, a campaign takes about 20-60 s per seed.
Output ONE markdown document:
# balance sweeps: <topic>
1. **Question and hypotheses** (from the baseline numbers; each hypothesis states the expected direction and size).
2. **Sweep table**: id | mode | exact command line | variants (file contents as JSON where used) | seeds | expected wall time | the metric to read | decision rule (what result confirms or rejects the hypothesis).
3. **Variant files** (JSON bodies, `{"set": [...]}`), ready to save under docs/balance/variants/.
4. **Order and stop rules** (cheap first, what to run only if the earlier result says so).
5. **Compare plan** (which pairs go to `balance.py compare`, output names CMP_<name>.md).
6. **Options write-up skeleton** for BALANCE_OPTIONS.md (the headings the Batch summarizer fills from the sweep JSON).
7. **Q:** (max 4).
Concrete and terse. 700-1500 words."""

BSWEEP_TOPICS = {
    "step0_calibration": "Step 0, calibration (feeds N2 tier base-value tables): measure fight turns and damage per tier for the reference_dpt_by_tier = [9, 11, 14, 18] question (CONTENT_DESIGN_V2 open question 1) and the HP bands; builtin vs heuristic policy vs skill 0.2-0.6 testers; fight mode over enemy / elite / mini_boss at tiers 1-4; what to record so N2 can set hp_by_tier and enemy_damage_by_tier; determinism check (the same sweep twice gives identical JSON).",
    "boss_length": "Boss length: baseline boss 38 turns and 25 % win at ICE 0 (fresh), 8 % in campaigns; the designer calls it tediously long (V4). Sweep boss HP, phase count, enrage turn, pointer count and Exploit effects as available levers; targets: 12-20 turns, win rate to be proposed against open question 12.",
    "campaign_pace": "Campaign pacing: baseline 605 minutes mean (median 793) vs GDD 11.8 target 395; runs 38.6, fights 203, deaths 10.5. Find which levers cut minutes (fight length, deaths, heal availability, run cap, enemy HP scale, layers) without moving the win rate off 50 %.",
    "economy_heat_attrition": "D2 HP attrition with no heal (heals available 1.94 / used 0.37 per run), D3 fight length 9-16 turns and enemy self-heal, D5 flatline Heat driving raids (raids from flatline 0.75 per campaign, Heat peak 84), D6 Schematics economy (income 1410, unspent 191, recruit price). One sweep set per issue, 2-3 options each.",
}


def build_bsweep() -> list[dict]:
    parts = [
        ("BALANCE_SIM.md", read(ROOT / "docs/handoff/plan2/BALANCE_SIM.md")),
        ("docs/balance/README.md", read(ROOT / "docs/balance/README.md")),
        ("BASELINE_e2e13918.md", read(ROOT / "docs/balance/BASELINE_e2e13918.md")),
        ("tools/balance/balance_defaults.json", read(ROOT / "tools/balance/balance_defaults.json")),
        ("tools/balance/balance.py (usage header + argparse)", read(ROOT / "tools/balance/balance.py")[:1800]
         + "\n...\n" + "\n".join(l for l in read(ROOT / "tools/balance/balance.py").splitlines() if "add_argument" in l)),
        ("tools/balance/balance_sim.gd", read(ROOT / "tools/balance/balance_sim.gd")),
        ("tools/balance/balance_content.gd (override syntax header)", read(ROOT / "tools/balance/balance_content.gd")[:1800]),
        ("content/config/campaign_config.tres (properties)", "\n".join(l for l in read(ROOT / "content/config/campaign_config.tres").splitlines() if "=" in l and not l.startswith("[")).strip()),
        ("CONTENT_DESIGN_V2 open questions + R2 tier bands", read(ROOT / "docs/handoff/plan2/CONTENT_DESIGN_V2.md")[read(ROOT / "docs/handoff/plan2/CONTENT_DESIGN_V2.md").index("## 7. Open questions"):]),
    ]
    ids = sorted(p.stem for p in (ROOT / "content/enemies").rglob("*.tres"))
    ctx = "\n\n".join(f"=== {n} ===\n{t}" for n, t in parts)
    out = []
    for key, topic in BSWEEP_TOPICS.items():
        user = f"Topic: {topic}\n\nEnemy / boss content ids available: {', '.join(ids[:200])}\n\n{ctx}"
        out.append(mk(f"bsweep__{key}", user, 24000, BSWEEP_ROLE))
    return out


# ---------------------------------------------------------------- 2. v2 (Sonnet, stage B)

V2_ROLE = """YOU ARE THE REVISER. You rewrite ONE round-1 design draft into its v2, applying its critic review and the triage rows. Apply every BLOCKER and MAJOR concrete fix, re-check the arithmetic yourself (re-add tick sizes and the HP/phase budget), keep what the critic marked strong, and do not add scope. If a fix conflicts with a designer ruling, the ruling wins and you say so. Output ONE markdown document, no preamble, that STARTS with the heading "## Changes vs v1" (a bullet list: each critic issue number -> what changed, or "kept, because ..."), followed by the complete revised draft in the SAME section structure as the template it follows (the full document, not a diff). End with at most 5 "Q:" lines."""


def triage_rows(kind_item: str) -> str:
    f = DRAFTS / "triage" / f"{kind_item}.md"
    return strip_header(read(f)) if f.exists() else "(no triage rows)"


def build_v2(idx: dict) -> list[dict]:
    out = []
    for batch in ("enemies", "bosses", "hq", "nodes", "raids", "events"):
        for f in sorted((DRAFTS / batch).glob("*.md")):
            crit = DRAFTS / "critic" / f"{batch}__{f.stem}.md"
            if not crit.exists():
                continue
            ctx = ""
            if batch == "enemies":
                e = idx.get(f.stem)
                if e:
                    ctx = f"Enemy {e['name']} ({f.stem}), class {e['cls']}, corporation {e['corp']}. Class brief: {b1.CLASS_BRIEF[e['cls']]}\n"
            if batch == "events":
                mech = f.stem.split("_")[1].upper()
                ctx = f"Event mechanic family: {mech}: {b1.EVENT_MECH.get(mech, '')}\n"
            user = (f"Revise the draft {batch}/{f.stem} into v2.\n{ctx}\n=== Template the draft follows ===\n{b2.CRIT_TEMPLATES[batch]}\n\n"
                    f"=== The v1 draft ===\n{strip_header(read(f))}\n\n=== Its critic review ===\n{strip_header(read(crit))}\n\n"
                    f"=== Triage rows for it ===\n{triage_rows(batch + '__' + f.stem)}")
            out.append(mk(f"v2__{batch}__{f.stem}", user, 40000, V2_ROLE))
    return out


# ---------------------------------------------------------------- 4. briefs (Sonnet, stage B)

BRIEF_SLICES = {
    "NA-02": ("Data contract: city.json, net.json, run_graph.json, key_locations.json, art_seeds; derive_<run>.json v1; JSON Schemas; FNV-1a 64 art seeds that never read or advance a gameplay RNG stream; unique building ids.", "fix-rules (OPUS-BECAUSE: a derived seed must not perturb the saved RNG streams) + fix-mechanical exporter"),
    "NA-03": ("tools/netrun_art/ pure modules (layout, zoning, derive.street, hq.slots, rig, lod, occlusion, section, states, dress, seeds, io), no Blender.", "Batch (module ports) + fix-mechanical"),
    "NA-04": ("netrun_art.checks: data checks (12.3, 12.4, 12.6) and image checks (12.1, 12.2, 12.5, 12.7) on PNGs or Godot captures.", "Batch + fix-mechanical"),
    "N1": ("Amount modes FLAT / PERCENT; flat enemy amounts x the tier damage factor.", "fix-rules"),
    "N2": ("Tier base-value tables: hp_by_tier, boss hp_bands, enemy_damage_by_tier, reference_dpt_by_tier, a band validator.", "fix-rules (OPUS-BECAUSE: shared netrun_session slice, enemy_scale)"),
    "N3": ("Phases on every class, threshold parking, status keep, cleanse on enter, the PARKED preview.", "fix-rules (OPUS-BECAUSE: preview = result)"),
    "N4": ("Enrage: EnrageData + class defaults, HUD countdown chip.", "fix-rules"),
    "N19": ("Sim metrics: turns per phase, parked damage, enrage step reached, intake per phase, listener fires.", "fix-mechanical"),
    "N11": ("Pointers on any tick (GDD 2.1 amendment), uneven layouts, HUD readability for close needles.", "fix-rules"),
    "N13": ("Fixed satellites + replacement: refuse moves unless can_move_satellites, Undock scoped, on_occupied = REPLACE.", "fix-rules"),
    "N14": ("Defense trio: BLOCK / SHIELD / SANDBOX names; SANDBOX negates a whole resolution; pierce does not bypass it.", "fix-rules"),
}

BRIEF_ROLE = """YOU WRITE ONE AGENT BRIEF in the repo's brief style (the W3 brief is shown as the style model). HARD LIMIT: the brief text must be under 2700 characters including markdown (about 380 words; drop prose, use terse bullets, never exceed this); a long list goes to a named file under docs/handoff/ that the brief tells the agent to read (say which file and what it must hold; do not write that file's content here). Output exactly:
# <slice id>: <title>
- **Goal** (2-4 lines), **Base / tag** (placeholders `<BASE_SHA>`, `<TEMP_TAG>`), **Agent type and lane** (fix-rules / fix-mechanical / fix-visual / Batch; Opus only with an OPUS-BECAUSE line), **Depends on** (slice ids).
- **Files** (owned paths, from the system row's code area; real paths only, say "new" for new files).
- **Acceptance** (numbered, testable, each with a number or an observable).
- **Tests** (file names and tier, referencing the test plan docs/handoff/plan2/drafts/test_plans/<n#>.md when one exists; CLAUDE.md rule 6).
- **Not in scope** and **Conflicts** (shared files from REPLAN C.2).
- **Report**: the RESULT envelope from docs/process/agent_rules/common.md.
Do not invent file paths beyond the code areas shown. Keep scope to the slice. US English."""


def build_briefs() -> list[dict]:
    replan = read(ROOT / "docs/handoff/gates/REPLAN_2026-10-16.md")
    w3 = read(ROOT / "docs/handoff/plan1/W3.md")[:3000]
    common = read(ROOT / "docs/process/agent_rules/common.md")
    # REPLAN sections A, C.2
    a = replan.index("## A. The netrun art build")
    b = replan.index("## B. Game-design items")
    c = replan.index("### C.2 Conflicts")
    d = replan.index("### C.3 Parallel")
    out = []
    for sid, (goal, lane) in BRIEF_SLICES.items():
        row = ""
        if re.fullmatch(r"N[0-9]+", sid):
            row = n_row(sid)
            tplan = DRAFTS / "test_plans" / f"{sid.lower()}.md"
            tp = strip_header(read(tplan))[:3500] if tplan.exists() else "(no test plan file)"
            row = f"System row:\n{row}\n\nTest plan (excerpt, to reference):\n{tp}"
        else:
            row = "REPLAN section A (the slice rows are in it)."
        user = (f"Write the brief for slice {sid}.\nGoal summary: {goal}\nSuggested lane: {lane}\n\n{row}\n\n"
                f"=== REPLAN section A ===\n{replan[a:b]}\n\n=== REPLAN C.2 conflicts ===\n{replan[c:d]}\n\n"
                f"=== Style model: W3 brief (head) ===\n{w3}\n\n=== RESULT envelope and rules (common.md) ===\n{common}")
        out.append(mk(f"brief__{sid.lower().replace('-', '')}", user, 6000, BRIEF_ROLE))
    return out


# ---------------------------------------------------------------- main


def est_tokens(s: str) -> int:
    return int(len(s) / 3.6)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--stage", default="", choices=["", "A", "B"])
    ap.add_argument("--only", default="")
    ap.add_argument("--retry-file", default="")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    idx = b1.enemy_index()
    builders = {
        "triage": build_triage, "questions": build_questions, "test_plans": build_tplan, "raids": build_raids,
        "names": build_names, "balance_sweeps": build_bsweep,
        "v2": lambda: build_v2(idx), "briefs": build_briefs,
    }
    stage = {"A": ["triage", "questions", "test_plans", "raids", "names", "balance_sweeps"], "B": ["v2", "briefs"]}
    if args.retry_file:
        want = {l.strip() for l in Path(args.retry_file).read_text(encoding="utf-8").splitlines() if l.strip()}
        reqs = [r for fn in builders.values() for r in fn() if r["custom_id"] in want]
        for r in reqs:
            r["params"]["max_tokens"] = 64000 if r["params"]["model"] != HAIKU else 8000
        with (out / "retry.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
            for r in reqs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"retry: {len(reqs)} requests of {len(want)} wanted")
        return 0
    only = [x for x in args.only.split(",") if x]
    names = only or stage.get(args.stage, list(builders))
    manifest = {}
    tot = worst_tot = 0.0
    for name in names:
        reqs = builders[name]()
        with (out / f"{name}.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
            for r in reqs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        haiku = reqs and reqs[0]["params"]["model"] == HAIKU
        if haiku:
            unc = sum(est_tokens(r["params"]["messages"][0]["content"]) + est_tokens(r["params"]["system"]) for r in reqs)
            b_out = sum(EXPECT_OUT.get(kind_of(r["custom_id"]), 900) for r in reqs)
            cap = sum(r["params"]["max_tokens"] for r in reqs)
            cost = (unc * HAIKU_IN + b_out * HAIKU_OUT) / 1e6
            wcost = (unc * HAIKU_IN + cap * HAIKU_OUT) / 1e6
        else:
            unc = sum(est_tokens(r["params"]["messages"][0]["content"]) + est_tokens(r["params"]["system"][-1]["text"]) for r in reqs)
            b_out = sum(EXPECT_OUT.get(kind_of(r["custom_id"]), 8000) for r in reqs)
            cap = sum(r["params"]["max_tokens"] for r in reqs)
            shared = COMMON_TOKENS * len(reqs) * 0.10 + COMMON_TOKENS * 1.25
            cost = (unc * 1.0 + shared + b_out * 5.0) / 1e6
            wcost = (unc * 1.0 + shared + cap * 5.0) / 1e6
        tot += cost
        worst_tot += wcost
        manifest[name] = [r["custom_id"] for r in reqs]
        print(f"{name}: {len(reqs)} requests ({'haiku' if haiku else 'sonnet'}), ~{unc:,} uncached in, expected out ~{b_out:,}, expected ${cost:.2f}, cap-worst ${wcost:.2f}")
    mp = out / "manifest.json"
    old = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else {}
    old.update(manifest)
    mp.write_text(json.dumps(old, indent=1), encoding="utf-8")
    print(f"TOTAL expected ${tot:.2f}, cap-worst ${worst_tot:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
