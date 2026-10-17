"""Netrun art batch round 1 (BATCH_ART1): build, submit and ingest Message Batches for the art-pass session.

    python tools/batch/build_art_drafts.py build  --out <scratch> [--only landmarks,audit,...] [--ids a,b --max-tokens 64000]
    python tools/batch/build_art_drafts.py build2 --out <scratch>        # vision cross-corp summary, from the ingested findings
    python tools/batch/build_art_drafts.py submit --out <scratch> <jsonl stems>   # e.g. main  |  summary  |  retry
    python tools/batch/build_art_drafts.py ingest --out <scratch> [--no-wait]     # poll, write docs/handoff/netrun_art/batch/**

Items (custom_id prefix -> output): lm (landmarks/<corp>_landmark.py + NOTES.md), audit (spec_audit/), vis (vision_review/<corp>.md,
SUMMARY.md), aur (aurelian_design/DESIGN.md), tsh (tethys_shots/SHOTS.md), gold (golden_plates/SPEC_SECTION.md),
cov (asset_coverage/MATRIX_*.md, Haiku). All outputs start with the DRAFT line. Plan and surface only: nothing here renders.

The art-pass clone is READ ONLY (this script only reads from it). Images: downscaled to <= 1568 px, JPEG q85, into <scratch>/img.
Credentials: ANTHROPIC_API_KEY or the Windows user variable of that name (tools/batch/ingest_drafts.api_key); never printed.
Cost per MTok (batch): Sonnet 5.5 in 1.00 / cache write 1.25 / cache read 0.10 / out 5.00; Haiku 4.5 in 0.50 / 0.625 / 0.05 / 2.50.
Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

SRC = Path("C:/Users/noitu/Documents/Godot/rebel_cell/.claude/worktrees/art-pass/docs/concepts")  # READ ONLY
RMG = SRC / "route_map_graph"
MAIN_ASSET_LIST = Path("D:/Godot/rebel_cell/docs/art_asset.md")  # main's list (untracked in some worktrees)
OUT_ROOT = ROOT / "docs/handoff/netrun_art/batch"
DRAFT = "DRAFT for the art-pass session; unverified (no render)."
SONNET, HAIKU = "claude-sonnet-5-5", "claude-haiku-4-5"
PRICE = {SONNET: (1.0, 1.25, 0.10, 5.0), HAIKU: (0.5, 0.625, 0.05, 2.5)}
MAX_EDGE = 1568

# corp -> hq folder, image finals (OVERVIEW, DECISION, HOVER) per HANDOFF_PACKAGE README section 8
FINALS = {
    "halcyon": ("hq_halcyon", ["H_overview_v2.png", "H_decision_E_v2.png", "H_hover_E_v2.png"]),
    "orbital": ("hq_orbital", ["H_overview_v2.png", "H_decision_v2.png", "H_hover_v2.png"]),
    "rebel_cell": ("hq_rebel_cell", ["H_overview_v3.png", "H_decision_v3.png", "H_hover_v3.png"]),
    "solace": ("hq_solace", ["H_overview_v4.png", "H_decision_v4.png", "H_hover_v4.png"]),
    "meridian": ("hq_meridian_v3", ["H_overview_v3.png", "H_decision_v3.png", "H_hover_v3.png"]),
    "tethys": ("hq_tethys", ["H_overview_v2.png", "tethys_closeup_v2.png"]),
}
LM_CORPS = ["halcyon", "solace", "orbital", "aurelian", "rebel_cell"]  # corps without a standalone landmark module


# ---------------------------------------------------------------- helpers

def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def lines(p: Path, a: int, b: int) -> str:
    ls = read(p).splitlines()
    return "\n".join(ls[a - 1:b])


def md_section(text: str, prefix: str) -> str:
    """From the heading starting with prefix to the next heading of the same or a higher level."""
    ls = text.splitlines()
    for i, l in enumerate(ls):
        if l.startswith(prefix):
            lvl = len(l) - len(l.lstrip("#"))
            j = i + 1
            while j < len(ls) and not (ls[j].startswith("#") and (len(ls[j]) - len(ls[j].lstrip("#"))) <= lvl):
                j += 1
            return "\n".join(ls[i:j])
    return ""


def grep(p: Path, pat: str, ctx: int = 0, cap: int = 60) -> str:
    ls = read(p).splitlines()
    rx = re.compile(pat)
    out, n = [], 0
    for i, l in enumerate(ls):
        if rx.search(l):
            out.append(f"{p.name}:{i + 1}: " + " | ".join(x.strip() for x in ls[max(0, i - ctx):i + ctx + 1])[:600])
            n += 1
            if n >= cap:
                break
    return "\n".join(out)


def doc(label: str, text: str) -> str:
    return f"=== {label} ===\n{text}\n\n"


def img_block(path: Path, cache_dir: Path) -> dict:
    from PIL import Image

    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / (path.parent.name + "__" + path.stem + ".jpg")
    if not out.exists():
        im = Image.open(path).convert("RGB")
        w, h = im.size
        s = min(1.0, MAX_EDGE / max(w, h))
        if s < 1.0:
            im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
        im.save(out, "JPEG", quality=85)
    data = base64.standard_b64encode(out.read_bytes()).decode("ascii")
    return {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": data}}


def images(label_paths: list[tuple[str, Path]], cache_dir: Path) -> list[dict]:
    out: list[dict] = []
    for label, p in label_paths:
        out.append({"type": "text", "text": f"IMAGE: {label} ({p.name})"})
        out.append(img_block(p, cache_dir))
    return out


def sysblock(text: str, cache: bool = False) -> dict:
    b = {"type": "text", "text": text}
    if cache:
        b["cache_control"] = {"type": "ephemeral"}
    return b


def request(cid: str, system: list[dict], user, max_tokens: int, model: str = SONNET) -> dict:
    params = {"model": model, "max_tokens": max_tokens, "system": system,
              "messages": [{"role": "user", "content": user}]}
    if model == SONNET:
        params["thinking"] = {"type": "adaptive"}
        params["output_config"] = {"effort": "medium"}
    return {"custom_id": cid, "params": params}


# ---------------------------------------------------------------- shared context

COMMON_RULES = f"""You are drafting for the art-pass session of REBEL_CELL (a cyberpunk roguelite deckbuilder; Godot 4.7). The designer approved the netrun art direction; the art-pass session keeps Blender (reference builds, golden plates, glb exports) and the build session owns tools/netrun_art and Godot. Your drafts are PLAN AND SURFACE only: nothing you write has been rendered or run, and you cannot see anything except the images you are given in a request.
Rules for every output:
- The FIRST line of your answer must be exactly: {DRAFT}  (the tooling adds nothing before it; for code it is a comment or the first docstring line).
- US spelling (center, color, defense). Plain ASCII punctuation where possible. No emojis.
- Be concrete: section references (spec section numbers such as "spec 8.6b"), file paths, numbers, names. No filler, no restating the brief.
- Label guesses as "ASSUMPTION:" and questions for the designer or the art director as "Q:" lines at the end (max 6). Never present unverified claims about rendering as fact.
- Binding sources, in order: the designer rulings in the supplied text, PIPELINE_SPEC (below), the supplied corp notes. Later entries override earlier ones. Names: THE PANOPTICON is Halcyon's Central Server (not "Civic Core"); the GDD 11.7 names are the working names (THE GENOME CORE, THE MASTER MANIFEST, THE PANOPTICON, LAUNCH CONTROL, DISPATCH, THE BLACK SMOKER; Aurelian's is a made-up gap name).
- Open numbers N1-N5 (spec 14.1) are for the build session to calibrate; never invent final values for them, propose defaults and mark them.
"""


def common_block() -> dict:
    spec = read(RMG / "PIPELINE_SPEC.md")
    return sysblock(COMMON_RULES + "\n" + doc("PIPELINE_SPEC.md (art-pass, route_map_graph)", spec), cache=True)


# ---------------------------------------------------------------- item 1: landmarks

LM_BRIEF = """TASK: write the standalone landmark module `{corp}_landmark.py` for corp {corp}, to the SAME API and conventions as the two templates you are given (meridian_landmark.py, tethys_landmark.py) and spec 8.5, 8.6, 8.6b, 8.6c.
Requirements:
1. Module docstring in the template style: title, ENTRY POINTS, what it builds, units/placing, seeds. First line is the DRAFT line as a docstring first line (`\"\"\"{draft}` then a new line with the title).
2. City hook (mandatory): `build(ctx) -> dict(label=(x, y, z), crown=(x, y, z) or None, hue=(r, g, b))`, using ONLY the ctx attributes that `landmarks.landmark_ctx(corp)` provides (SURF, SMOOTH, NEON, GLASS, STREAK, box, cyl, dome, bar, strip, ring_line, annulus, circle, prism, sc, mixc, spot_at, W, O, CP, station, zw, hq, hq_lot, footprint, seed, ...). Port the corp's built-in function from landmarks.py (supplied) faithfully: same geometry rules, same silhouette, same lights; replace exec-namespace globals with ctx attributes. Deterministic: random.Random(seed-derived) per named stream; no global random, no time. Everything inside the lot footprint.
3. HQ-netrun-scale entry (spec 8.5): if an hq_build source is supplied, add `build_hq(K, rooms=True, rail=False)` with the K namespace described in meridian_landmark.py and a dispatcher `build(K_or_ctx, ...)` like the template; port what you can see. If no usable source is supplied (e.g. Halcyon), still provide `build_hq` as a documented stub that raises NotImplementedError with a precise TODO list of what the HQ builder must expose (room slots from the corp graph, beams, hooks dict) so the art-pass session knows the gap.
4. Add `landmark_info()` returning a small dict (corp, central_server_name per the GDD 11.7 working names, footprint_bu, tier_heights) the pipeline checks 12.2 (landmark ratio) can read. Keep names as constants at module top.
5. Pure Python 3 stdlib only (math, random, types); no imports of Blender, numpy or the city namespace; the file must parse with `ast.parse`.
Output format, exactly two parts, nothing else:
=====PY=====
<the complete module source, no markdown fences>
=====NOTES=====
<markdown bullets: assumptions you made, what was dropped or simplified, ctx attributes you relied on that the templates do not use, anything the art-pass session must verify by rendering. Max 25 bullets.>
"""


def build_landmarks(cache: Path, ids: set[str] | None, max_tokens: int) -> list[dict]:
    meridian = read(RMG / "hq_meridian_v3/scripts/meridian_landmark.py")
    tethys = read(RMG / "hq_tethys/scripts/tethys_landmark.py")
    landmarks_py = read(SRC / "city_all_corps/scripts/landmarks.py")
    shared = sysblock(
        doc("TEMPLATE 1: hq_meridian_v3/scripts/meridian_landmark.py", meridian)
        + doc("TEMPLATE 2: hq_tethys/scripts/tethys_landmark.py", tethys)
        + doc("city_all_corps/scripts/landmarks.py (the built-in city-scale landmarks and landmark_ctx; port from here)", landmarks_py),
        cache=True)
    per: dict[str, str] = {}
    per["halcyon"] = (doc("hq_halcyon/NOTES.md", read(RMG / "hq_halcyon/NOTES.md"))
                      + doc("hq_halcyon/scripts/hq_landmark.py (landmark read check)", read(RMG / "hq_halcyon/scripts/hq_landmark.py")))
    per["solace"] = (doc("hq_solace/NOTES.md", read(RMG / "hq_solace/NOTES.md"))
                     + doc("hq_solace/scripts/hq_build.py (HQ-scale builder)", read(RMG / "hq_solace/scripts/hq_build.py")))
    per["orbital"] = (doc("hq_orbital/NOTES.md", read(RMG / "hq_orbital/NOTES.md"))
                      + doc("hq_orbital/scripts/hq_build.py (HQ-scale builder)", read(RMG / "hq_orbital/scripts/hq_build.py")))
    per["rebel_cell"] = (doc("hq_rebel_cell/NOTES.md", read(RMG / "hq_rebel_cell/NOTES.md"))
                         + doc("hq_rebel_cell/scripts/hq_build_A.py", read(RMG / "hq_rebel_cell/scripts/hq_build_A.py"))
                         + doc("hq_rebel_cell/scripts/hq_build_C.py", read(RMG / "hq_rebel_cell/scripts/hq_build_C.py"))
                         + "NOTE: designer ruling: REBEL_CELL has no landmark building in the city; the fist in red windows is its landmark "
                           "(zoning crest rule). The built-in rebel_cell() in landmarks.py is the mainframe building and its red spot; port that.\n")
    per["aurelian"] = (doc("new_corps/roman/identity.md", read(SRC / "new_corps/roman/identity.md"))
                       + doc("new_corps/roman/NOTES.md", read(SRC / "new_corps/roman/NOTES.md"))
                       + "NOTE: no HQ-scale builder exists for Aurelian (the HQ design pass is item 4 of this batch); build_hq is a stub.\n")
    out = []
    for corp in LM_CORPS:
        cid = f"lm__{corp}"
        if ids and cid not in ids:
            continue
        user = (f"CORP: {corp}\n\n" + doc(f"{corp} sources", per[corp])
                + LM_BRIEF.format(corp=corp, draft=DRAFT))
        out.append(request(cid, [common_block(), shared], user, max_tokens))
    return out


# ---------------------------------------------------------------- item 2: spec audit

AUDIT_COMMON = """TASK: audit the netrun art documents. Output ONE markdown document: the DRAFT line, a heading, a 5-line summary of the worst problems, then the table(s) below. Every row: `#`, `Severity` (BLOCKER / MAJOR / NIT), `Where` (document + section/line refs, both sides of a contradiction), `Finding` (quote the conflicting phrases, max 25 words each), `Suggested fix` (the exact replacement text or ruling to ask for). Rank by severity. Do not pad: prefer 25 real rows to 80 vague ones, but do not stop early; check each section systematically. Mark rows where only the designer can decide as `Q`.
"""

AUDIT_A = AUDIT_COMMON + """SCOPE A (contradictions and cross-references): PIPELINE_SPEC vs DIRECTION_REVIEW vs route_map_graph/decisions (DECISIONS.md, Q4/Q6/Q9 results) vs the main-repo rulings. Look for: numbers that differ between sections (value band, LOD distances, camera parameters, durations, seed streams, budget figures); a rule stated twice with different values; section references that point to a wrong or non-existent section; terms used before they are defined; items the HANDOFF_PACKAGE lists as built or approved that the spec calls open (or the reverse); sections that still describe an approach a later ruling replaced (DR entries later in the log override earlier ones); acceptance checks (section 12) that no section produces the inputs for; modules (2.2) that no rule uses; missing cross-references between 3.5b, 8.x, 9.x and 12.x.
"""

AUDIT_B = AUDIT_COMMON + """SCOPE B (naming, stale names and the open numbers N1-N5): (1) STALE NAMES: THE PANOPTICON must be used, never "Civic Core"/"The Civic Core"; list every stale or conflicting name for each corp's Central Server and each landmark across the spec, DIRECTION_REVIEW, hq notes and GDD (evidence is supplied as grep output; GDD sections are quoted), and propose one name per corp from the GDD 11.7 working names (a made-up one for Aurelian; Tethys is THE BLACK SMOKER). (2) GDD NAMING SECTIONS: where GDD 8.3, 8.4, 8.4b, 8.4c, 8.4d, 11.7 and Appendix A disagree with each other or with the art (corp names, site names such as "Site" that were removed, Tethys Deep vs Atlantis), give the exact amendment. (3) OPEN NUMBERS N1-N5 (spec 14.1): for each, list every place in spec/DIRECTION_REVIEW that depends on it, whether the dependency is consistent, the default currently written, who must decide, and a proposed calibration procedure (a short checklist for the build session) - a second table `Open numbers`.
"""


def build_audit(cache: Path, ids: set[str] | None, max_tokens: int) -> list[dict]:
    dr = read(SRC / "DIRECTION_REVIEW.md")
    dec = read(RMG / "decisions/DECISIONS.md")
    main_dec = read(ROOT / "docs/DECISIONS.md")
    rul = md_section(main_dec, "### 2026-10-16 — Designer rulings on the replan")
    rul2 = md_section(main_dec, "### 2026-10-16 — NA-01")
    pkg = read(SRC / "HANDOFF_PACKAGE/README.md")
    gdd = read(ROOT / "docs/GDD.md")
    gdd_names = "\n\n".join(md_section(gdd, h) for h in ("### 8.3 ", "### 8.4 ", "### 8.4b", "### 8.4c", "### 8.4d", "### 11.7"))
    app_a = grep(ROOT / "docs/GDD.md", r"(?i)civic|panopticon|manifest|genome|renewal|launch control|dispatch|commons array|black smoker|aurelian|tethys|atlantis", cap=80)
    ev = [grep(RMG / f"hq_{c}/NOTES.md", r"(?i)central server|flagged|panopticon|civic core", cap=25)
          for c in ("halcyon", "meridian", "orbital", "rebel_cell", "solace")]
    ev.append(grep(RMG / "hq_meridian_v3/DESIGN.md", r"(?i)central server|manifest|flagged", cap=15))
    ev.append(grep(RMG / "hq_tethys/DESIGN.md", r"(?i)central server|black smoker|flagged", cap=15))
    ev.append(grep(RMG / "PIPELINE_SPEC.md", r"(?i)civic core|panopticon|central server|master manifest|genome|launch control|dispatch|black smoker", cap=60))
    ev.append(grep(SRC / "DIRECTION_REVIEW.md", r"(?i)civic core|panopticon|central server", cap=40))
    shared = sysblock(
        doc("DIRECTION_REVIEW.md (the decision log; later entries override earlier ones)", dr)
        + doc("route_map_graph/decisions/DECISIONS.md", dec)
        + doc("main docs/DECISIONS.md excerpt: designer rulings 2026-10-16 (replan)", rul + "\n\n" + rul2)
        + doc("HANDOFF_PACKAGE/README.md", pkg), cache=True)
    out = []
    for cid, task, extra in (
            ("audit__contradictions", AUDIT_A, ""),
            ("audit__naming_open_numbers", AUDIT_B,
             doc("GDD sections (verbatim)", gdd_names) + doc("GDD grep (naming terms)", app_a)
             + doc("Grep evidence in hq notes, spec and DIRECTION_REVIEW", "\n".join(ev)))):
        if ids and cid not in ids:
            continue
        out.append(request(cid, [common_block(), shared], extra + task, max_tokens))
    return out


# ---------------------------------------------------------------- item 3: vision review

VIS_SYSTEM_EXTRA = "ART BIBLE v2 excerpt (pillars, palette, tokens, typography), the rules the frames are judged against:\n\n"

VIS_TASK = """TASK: review the supplied final frames for corp {corp} (OVERVIEW / DECISION / HOVER, as labelled) as a hostile but fair art director. You can see only these images; do not describe what you cannot see. Judge against: ART_BIBLE v2 rules (supplied), the netrun look (spec 4.1 AAA-2), the value band (spec 12.1: median luma 0.14 +/- 0.03, 25-40 % under 0.10, <= 2.5 % over 0.85 - estimate by eye and say so), landmark ratio (12.2), hover power cut (9.4), the HQ camera (6.4), signage (9.1), and the corp's identity in the spec (8.x).
Output ONE markdown document: the DRAFT line, then
# Vision review: {corp}
## Per frame
For each frame: **What it shows** (2 lines), **Rule breaks** (numbered; each cites the rule/section and where in the frame), **Readability** (can the player find the landmark, the route, the target, the hovered branch; what competes), **Strengths to keep**, **Fix list** (concrete, smallest change first, tagged [art] or [spec]).
## How the set holds together
Overview -> decision -> hover continuity (camera, scale, palette, UI), and whether the frames could be mistaken for another corp.
## Top findings
Exactly 5, ranked, each one line with severity (BLOCKER / MAJOR / NIT).
Confidence: say "uncertain" where the frame is too small or compressed to judge (images are downscaled to <= 1568 px).
"""

SUM_TASK = """TASK: you are given six per-corp vision-review documents (frame-level findings from images you have not seen). Write the CROSS-CORP summary as ONE markdown document: the DRAFT line, `# Vision review: cross-corp summary`, then
## Patterns (rule breaks that recur across corps: rule, corps affected, how often, one fix at the shared-kit level)
## Outliers (a corp whose set breaks from the others, why)
## Set coherence (could the seven HQs sit in one city; the missing Tethys decision/hover and Aurelian frames)
## Top 5 findings (ranked, with corp and severity)
## Recommended order of fixes (shared kit first)
Only use what the six documents say; if two documents contradict each other, say so. Do not invent frame details.
"""


def build_vision(cache: Path, ids: set[str] | None, max_tokens: int) -> list[dict]:
    bible = read(ROOT / "docs/ART_BIBLE.md")
    excerpt = lines(ROOT / "docs/ART_BIBLE.md", 70, 248)
    shared = sysblock(VIS_SYSTEM_EXTRA + excerpt + "\n\n" + doc("ART_BIBLE v2 Appendix A (locked reference images)", md_section(bible, "## 7. Appendix A")), cache=True)
    out = []
    for corp, (folder, files) in FINALS.items():
        cid = f"vis__{corp}"
        if ids and cid not in ids:
            continue
        labels = ["OVERVIEW", "DECISION", "HOVER"] if len(files) == 3 else ["OVERVIEW", "CLOSEUP (Tethys has no decision/hover final yet)"]
        user = images([(f"{corp} {lb}", RMG / folder / f) for lb, f in zip(labels, files)], cache / "img")
        user.append({"type": "text", "text": VIS_TASK.format(corp=corp)})
        out.append(request(cid, [common_block(), shared], user, max_tokens))
    return out


# ---------------------------------------------------------------- item 4: Aurelian design

AUR_TASK = """TASK: write the DESIGN.md draft for the AURELIAN CONCORD HQ netrun (the Circus Aurelius), following the structure and depth of the two existing HQ DESIGN.md files you are given (hq_meridian_v3, hq_tethys): same section order and headings where they apply (concept, what it is not, the named mechanic and how the art shows it, plan and room slots, landmark and ring layout, camera/orbit and the DECISION and HOVER shots, states and their lighting, dressing and signage, mapping the game graph onto the landmark per spec 8.4, scale in the one city per 8.6, build order, acceptance checks per spec 12, open questions).
Designer ruling D10 (supplied): every HQ netrun is UNIQUE and may run longer than 7 layers; the process is draft -> designer ruling -> build in W2. The plan-2 batch draft `hq__aurelian` (supplied) covers the game mechanic (turning gates, VERDICT, Rostrum); do not redesign the mechanic, make the ART DESIGN consistent with it and flag any place where the art in the supplied images and the mechanic draft disagree (room counts, layer count, ring order). Use the supplied Aurelian images (identity, HQ overview, HQ mechanic, building kit, site street) as the visual ground truth; name what you see and what you assume.
Output ONE markdown document starting with the DRAFT line. Include a table of the rooms/slots (id, ring, type, lit state per spec 12.x), the layer count you recommend with a one-line reason, the shot list for OVERVIEW / DECISION / HOVER (camera per spec 6.4, framing, states shown) and the golden-plate list for Aurelian. End with `Q:` lines.
"""


def build_aurelian(cache: Path, ids: set[str] | None, max_tokens: int) -> list[dict]:
    if ids and "aur__design" not in ids:
        return []
    main_dec = read(ROOT / "docs/DECISIONS.md")
    replan = read(ROOT / "docs/handoff/gates/REPLAN_2026-10-16.md")
    shared = sysblock(
        doc("PATTERN 1: hq_meridian_v3/DESIGN.md", read(RMG / "hq_meridian_v3/DESIGN.md"))
        + doc("PATTERN 2: hq_tethys/DESIGN.md", read(RMG / "hq_tethys/DESIGN.md")), cache=True)
    text = (doc("new_corps/roman/identity.md", read(SRC / "new_corps/roman/identity.md"))
            + doc("new_corps/roman/NOTES.md", read(SRC / "new_corps/roman/NOTES.md"))
            + doc("new_corps/roman/boss_wheel_ideas.md", read(SRC / "new_corps/roman/boss_wheel_ideas.md"))
            + doc("DECISIONS 2026-10-16 designer rulings on the replan (D1-D10)", md_section(main_dec, "### 2026-10-16 — Designer rulings on the replan"))
            + doc("REPLAN_2026-10-16.md", replan)
            + doc("plan-2 batch draft hq__aurelian (the game mechanic)", read(ROOT / "docs/handoff/plan2/drafts/hq/aurelian.md")))
    imgs = images([("Aurelian identity board", SRC / "new_corps/roman/identity_board.png"),
                   ("Aurelian HQ overview", SRC / "new_corps/roman/hq_overview.png"),
                   ("Aurelian HQ mechanic", SRC / "new_corps/roman/hq_mechanic.png"),
                   ("Aurelian building kit", SRC / "new_corps/roman/building_kit.png"),
                   ("Aurelian site street", SRC / "new_corps/roman/site_street.png")], cache / "img")
    user = [{"type": "text", "text": text}] + imgs + [{"type": "text", "text": AUR_TASK}]
    return [request("aur__design", [common_block(), shared], user, max_tokens)]


# ---------------------------------------------------------------- item 5: Tethys shots

TSH_TASK = """TASK: specify the missing Tethys DECISION and HOVER finals (the art-pass session delivers them after the reset; D1 and D8). Match them to the other corps' finals: the supplied images show each corp's DECISION and HOVER frame, and the supplied Tethys OVERVIEW and closeup show the look to extend. For each of the two shots give: purpose, camera (orbit pose per spec 6.4: azimuth, elevation, distance or focal length, look-at, any hold), framing (what fills the frame, where the landmark sits, thirds, safe areas for UI), states shown (which rooms/slots lit, which routes powered, the water level and layers visible, the Black Smoker glow, the TARGET marker, the fog/beam state), the DECISION node set (which options are offered and how they read), the HOVER cut (spec 9.4: which branch is lit, the world grade values), UI overlay assumptions, the checks it must pass (spec 12.1 value band, 12.2 landmark ratio, 12.7 composition), and the render budget notes (spec 11.4). Then a COMPARISON TABLE of how each of the other corps' DECISION/HOVER frames are composed (camera elevation estimate, landmark share of frame, UI placement) so the art-pass session can verify Tethys matches; say "uncertain" where you cannot judge from the downscaled images. Also note what is special for Tethys (water, the drowned streets, whales, underwater lighting) and the Tethys-specific risk to the value band.
Output ONE markdown document starting with the DRAFT line; end with `Q:` lines.
"""


def build_tethys(cache: Path, ids: set[str] | None, max_tokens: int) -> list[dict]:
    if ids and "tsh__shots" not in ids:
        return []
    shared = sysblock(doc("hq_tethys/DESIGN.md", read(RMG / "hq_tethys/DESIGN.md"))
                      + doc("hq_meridian_v3/DESIGN.md (shot spec pattern)", read(RMG / "hq_meridian_v3/DESIGN.md")), cache=True)
    text = (doc("new_corps/atlantis/identity.md", read(SRC / "new_corps/atlantis/identity.md"))
            + doc("new_corps/atlantis/NOTES.md", read(SRC / "new_corps/atlantis/NOTES.md")))
    pairs: list[tuple[str, Path]] = [("Tethys OVERVIEW (final)", RMG / "hq_tethys/H_overview_v2.png"),
                                     ("Tethys closeup (final)", RMG / "hq_tethys/tethys_closeup_v2.png")]
    for corp in ("halcyon", "orbital", "rebel_cell", "solace", "meridian"):
        folder, files = FINALS[corp]
        pairs += [(f"{corp} DECISION", RMG / folder / files[1]), (f"{corp} HOVER", RMG / folder / files[2])]
    user = [{"type": "text", "text": text}] + images(pairs, cache / "img") + [{"type": "text", "text": TSH_TASK}]
    return [request("tsh__shots", [common_block(), shared], user, max_tokens)]


# ---------------------------------------------------------------- item 6: golden plates

GOLD_TASK = """TASK: draft the spec section for GOLDEN PLATES and Python/GDScript PARITY, to be inserted into PIPELINE_SPEC (suggest a number, e.g. 12.8 or a new section 15, and the cross-references to add in 8, 11 and 12). Source of the requirement: designer ruling D8 (supplied): hand-offs are glb files plus golden plates (a PNG and a values JSON per plate: median, % under 0.10, landmark ratio, camera params) plus check reports; the build session runs the section 12 checks on Godot captures against those plates and reports drift to the art-pass session; the art-pass session adds a "golden plates" section (plate list and tolerances); the D3 reference is a city_A2-style procedural planner city.
Cover, in spec style (numbered rules, tables, exact parameter names): (1) PLATE LIST: one table, id, what it shows, camera (pose model 6.1), seed(s), corp, state, the per-corp OVERVIEW/DECISION/HOVER set (Tethys and Aurelian pending), the street set, the city set, the storyboard keyframes; (2) PLATE FILE FORMAT: PNG naming, values JSON schema (every field, units, types; use the supplied example *_plate_values.json files as the base and say what to add), glb export contents (spec 11.5), version stamping, where plates live in the repo, how art-pass hands them over; (3) TOLERANCES per check (12.1 value band using the Q4 recommendation 0.14 +/- 0.03 with warn bands, 12.2 landmark ratio, 12.3 determinism, 12.5 beam style, 12.7 composition) and a drift-report format; Godot capture vs Blender plate differences that are expected (tone mapping, fog N5, shadows) and how the compare accounts for them; (4) PYTHON/GDSCRIPT PARITY (12.6 in particular): list every twin pair (occlusion rule 7.3, the hover cut 9.4, the edge arrow 9.5b, LOD reveal 5.2b, art-seed streams 3.5/3.5b, any other pair), the shared test vectors file format (inputs, expected outputs, float tolerance, integer exactness, RNG stream draws), how the vectors are generated once and consumed by both sides, and the CI check that fails when they diverge; (5) the PROCESS: who generates, who verifies, when plates are re-baked, how the designer approves a new golden plate; (6) NEW OPEN NUMBERS you found.
Output ONE markdown document starting with the DRAFT line; the spec section text first (ready to paste), then `## Review notes` (conflicts with existing spec text, with section refs) and `Q:` lines.
"""


def build_golden(cache: Path, ids: set[str] | None, max_tokens: int) -> list[dict]:
    if ids and "gold__spec" not in ids:
        return []
    main_dec = read(ROOT / "docs/DECISIONS.md")
    ex = (RMG / "hq_tethys/H_overview_v2_plate_values.json").read_text(encoding="utf-8")
    q = "\n".join(f"--- {n} ---\n{read(RMG / 'decisions' / n)[:3000]}" for n in ("Q4_value_tolerance.json", "Q6_power_cut.json", "Q9_art_randomness.json"))
    shared = sysblock(
        doc("route_map_graph/decisions/DECISIONS.md", read(RMG / "decisions/DECISIONS.md"))
        + doc("Decision sheet data (Q4, Q6, Q9 json, truncated)", q)
        + doc("Example values JSON (hq_tethys/H_overview_v2_plate_values.json)", ex)
        + doc("DECISIONS 2026-10-16 designer rulings on the replan (D1-D10)", md_section(main_dec, "### 2026-10-16 — Designer rulings on the replan"))
        + doc("DECISIONS NA-01 netrun art spec imported", md_section(main_dec, "### 2026-10-16 — NA-01")), cache=True)
    return [request("gold__spec", [common_block(), shared], GOLD_TASK, max_tokens)]


# ---------------------------------------------------------------- item 7: asset coverage (Haiku)

COV_TASK = """TASK: build a COVERAGE MATRIX for the art asset list rows in your scope against the approved-image index. For every element row (every table row under the headings of your scope) output one matrix row: `ID/Element | Asset-list part | Covering approved image(s) | Coverage (FULL / PARTIAL / NONE) | Gap note`. "Covering image" = a path from the approved-image index (INDEX.md list and the ART_BIBLE Appendix A locked images) that shows that element in its approved look; if none of the listed images can show it, write NONE. Do not invent images; if only the repo-wide locked images (ART_BIBLE Appendix A) could cover it, name the Appendix A entry. Many asset-list items are UI/combat/card items that the netrun-era approved images do not cover: say NONE for those, do not stretch. After the matrix write `## Gaps` (the NONE and PARTIAL rows grouped by theme, with a count per theme) and `## Counts` (rows FULL/PARTIAL/NONE).
Output ONE markdown document starting with the DRAFT line, then a heading naming your scope. Keep gap notes under 15 words. Do not skip rows.
"""


def build_coverage(cache: Path, ids: set[str] | None, max_tokens: int) -> list[dict]:
    asset = read(MAIN_ASSET_LIST)
    idx = read(ROOT / "docs/handoff/netrun_art/INDEX.md")
    pkg8 = md_section(read(SRC / "HANDOFF_PACKAGE/README.md"), "## 8. File index")
    bible = read(ROOT / "docs/ART_BIBLE.md")
    shared = sysblock(doc("approved-image INDEX.md (main)", idx) + doc("HANDOFF_PACKAGE README section 8 (the approved deliverables)", pkg8)
                      + doc("ART_BIBLE v2 Appendix A: locked reference images", md_section(bible, "## 7. Appendix A")), cache=True)
    parts = {"cov__a_f": ("Parts A to F (identity, characters, world, maps, combat, items)", "## Part A", "## Part G"),
             "cov__g_m": ("Parts G to M (screens, interface pieces, icons, stamps, motion, lettering, known gaps)", "## Part G", "## Appendix")}
    head = asset.split("## Part A")[0]
    out = []
    for cid, (label, a, b) in parts.items():
        if ids and cid not in ids:
            continue
        s = asset.index(a + " ") if (a + " ") in asset else asset.index(a)
        e = asset.index(b, s + 10)
        user = doc("Asset list (docs/art_asset.md, main): scope " + label, head + asset[s:e]) + COV_TASK
        out.append(request(cid, [sysblock("You prepare a coverage matrix for the REBEL_CELL art-pass session. US spelling, no emojis. The FIRST line of your answer must be exactly: " + DRAFT + "\n", cache=False), shared], user, max_tokens, model=HAIKU))
    return out


# ---------------------------------------------------------------- build / submit / ingest

GROUPS = {"landmarks": build_landmarks, "audit": build_audit, "vision": build_vision, "aurelian": build_aurelian,
          "tethys": build_tethys, "golden": build_golden, "coverage": build_coverage}
MAXTOK = {"landmarks": 64000, "audit": 32000, "vision": 16000, "aurelian": 48000, "tethys": 32000, "golden": 48000, "coverage": 40000}

OUT_PATH = {  # custom_id -> path under OUT_ROOT
    **{f"lm__{c}": f"landmarks/{c}_landmark.py" for c in LM_CORPS},
    "audit__contradictions": "spec_audit/contradictions.md",
    "audit__naming_open_numbers": "spec_audit/naming_and_open_numbers.md",
    **{f"vis__{c}": f"vision_review/{c}.md" for c in FINALS},
    "vis__summary": "vision_review/SUMMARY.md",
    "aur__design": "aurelian_design/DESIGN.md",
    "tsh__shots": "tethys_shots/SHOTS.md",
    "gold__spec": "golden_plates/SPEC_SECTION.md",
    "cov__a_f": "asset_coverage/MATRIX_A_F.md",
    "cov__g_m": "asset_coverage/MATRIX_G_M.md",
}


def cmd_build(a) -> int:
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ids = set(a.ids.split(",")) if a.ids else None
    only = a.only.split(",") if a.only else list(GROUPS)
    reqs: list[dict] = []
    for g in only:
        reqs += GROUPS[g](out, ids, a.max_tokens or MAXTOK[g])
    name = "retry" if ids else "main"
    p = out / f"{name}.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in reqs) + "\n", encoding="utf-8")
    for r in reqs:
        print(r["custom_id"], r["params"]["model"], r["params"]["max_tokens"])
    print(f"{len(reqs)} requests -> {p} ({p.stat().st_size / 1e6:.1f} MB)")
    return 0


def cmd_build2(a) -> int:
    out = Path(a.out)
    parts = []
    for c in FINALS:
        f = OUT_ROOT / f"vision_review/{c}.md"
        if f.exists():
            parts.append(doc(f"vision review: {c}", read(f)))
    r = request("vis__summary", [common_block()], "".join(parts) + SUM_TASK, a.max_tokens or 16000)
    p = out / "summary.jsonl"
    p.write_text(json.dumps(r) + "\n", encoding="utf-8")
    print(f"vis__summary built from {len(parts)} documents -> {p}")
    return 0


def client():
    import anthropic
    from ingest_drafts import api_key

    return anthropic.Anthropic(api_key=api_key())


def cmd_submit(a) -> int:
    out = Path(a.out)
    cl = client()
    ids_path = out / "batch_ids.json"
    ids = json.loads(ids_path.read_text(encoding="utf-8")) if ids_path.exists() else {}
    for n in a.names:
        reqs = [json.loads(l) for l in (out / f"{n}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        b = cl.messages.batches.create(requests=reqs)
        key = n if n != "retry" else f"retry{sum(1 for k in ids if k.startswith('retry')) + 1}"
        ids[key] = b.id
        ids_path.write_text(json.dumps(ids, indent=1), encoding="utf-8")
        print(f"{key}: {len(reqs)} requests -> {b.id} ({b.processing_status})", flush=True)
    return 0


def strip_fences(t: str) -> str:
    t = t.strip()
    m = re.match(r"^```[a-zA-Z]*\n(.*?)\n```\s*$", t, re.S)
    return m.group(1) if m else t


def cmd_ingest(a) -> int:
    import ast

    out = Path(a.out)
    cl = client()
    ids = json.loads((out / "batch_ids.json").read_text(encoding="utf-8"))
    ledger = out / "ledger.jsonl"
    notes: dict[str, str] = {}
    done: set = set()
    if ledger.exists():
        done = {(j["id"], j["batch"]) for j in (json.loads(l) for l in ledger.read_text(encoding="utf-8").splitlines() if l.strip())}
    for name, bid in ids.items():
        while True:
            b = cl.messages.batches.retrieve(bid)
            if b.processing_status == "ended" or a.no_wait:
                break
            c = b.request_counts
            print(f"{name}: {b.processing_status} processing {c.processing} succeeded {c.succeeded} errored {c.errored}", flush=True)
            time.sleep(a.poll)
        if b.processing_status != "ended":
            print(name, "still", b.processing_status)
            continue
        for r in cl.messages.batches.results(bid):
            cid = r.custom_id
            if (cid, bid) in done:
                continue
            if r.result.type != "succeeded":
                print("FAILED", cid, r.result.type, flush=True)
                with open(ledger, "a", encoding="utf-8") as lf:
                    lf.write(json.dumps({"id": cid, "batch": bid, "status": r.result.type, "cost": 0}) + "\n")
                continue
            m = r.result.message
            text = "".join(bl.text for bl in m.content if bl.type == "text").strip()
            u = m.usage
            tin, cw, cr, tout = u.input_tokens, u.cache_creation_input_tokens or 0, u.cache_read_input_tokens or 0, u.output_tokens
            p = PRICE[m.model if m.model in PRICE else SONNET]
            cost = (tin * p[0] + cw * p[1] + cr * p[2] + tout * p[3]) / 1e6
            status = "ok" if m.stop_reason == "end_turn" else f"TRUNCATED ({m.stop_reason})"
            with open(ledger, "a", encoding="utf-8") as lf:
                lf.write(json.dumps({"id": cid, "batch": bid, "status": status, "in": tin, "cw": cw, "cr": cr, "out": tout, "cost": round(cost, 4)}) + "\n")
            dest = OUT_ROOT / OUT_PATH[cid]
            dest.parent.mkdir(parents=True, exist_ok=True)
            prov = f"model {m.model}, batch {bid}, custom_id {cid}; status {status}; tokens in {tin} cache-write {cw} cache-read {cr} out {tout}; cost ${cost:.3f}"
            if status != "ok":
                print("TRUNCATED", cid, flush=True)
            if cid.startswith("lm__"):
                py, _, nt = text.partition("=====NOTES=====")
                py = py.replace("=====PY=====", "").strip()
                py = strip_fences(py)
                if py.startswith(DRAFT):  # bare first line: make it a comment (drop a following docstring-less duplicate)
                    py = "# " + py
                elif not py.startswith('"""' + DRAFT) and not py.startswith("# " + DRAFT):
                    py = '# ' + DRAFT + "\n" + py
                py = re.sub(r"(?m)\A(# " + re.escape(DRAFT) + r"\n)" + re.escape(DRAFT) + r"\n", r"\1", py)
                try:
                    ast.parse(py)
                    ok = "parses"
                except SyntaxError as e:
                    ok = f"SYNTAX ERROR line {e.lineno}: {e.msg}"
                first, _, rest = py.partition("\n")  # the DRAFT line stays first, the provenance comment second
                dest.write_text(first + f"\n# provenance: {prov}; ast.parse: {ok}\n" + rest + "\n", encoding="utf-8", newline="\n")
                notes[cid] = f"## {cid.split('__')[1]} ({ok}; {status})\n\n{nt.strip()}\n"
            else:
                body = text if text.startswith(DRAFT) else DRAFT + "\n\n" + text
                first, _, rest = body.partition("\n")
                dest.write_text(first + f"\n<!-- {prov} -->\n" + rest + "\n", encoding="utf-8", newline="\n")
    if notes:
        n_path = OUT_ROOT / "landmarks/NOTES.md"
        old = ""
        if n_path.exists():
            old = n_path.read_text(encoding="utf-8")
        # rebuild: keep earlier sections whose id is not re-ingested
        keep = [s for s in re.split(r"(?m)^(?=## )", old) if s.startswith("## ") and not any(s.startswith("## " + k.split("__")[1] + " ") for k in notes)]
        body = DRAFT + "\n\n# Landmark modules: assumptions and open points\n\n" + "\n".join(keep + sorted(notes.values()))
        n_path.write_text(body, encoding="utf-8", newline="\n")
    return 0


def cmd_readme(a) -> int:
    """batch/README.md: index, cost and caveats from the ledger (last entry per id wins; truncated ones count their cost)."""
    out = Path(a.out)
    rows = [json.loads(l) for l in (out / "ledger.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    total = sum(r.get("cost", 0) for r in rows)
    last = {r["id"]: r for r in rows}
    L = [DRAFT, "", "# Netrun art batch round 1 (BATCH_ART1)", "",
         "Drafts for the art-pass session, made with the Message Batches API (Sonnet 5.5; asset_coverage on Haiku 4.5). Plan and surface only:",
         "nothing here was rendered or run. Built by `tools/batch/build_art_drafts.py` from the read-only art-pass clone",
         "(`docs/concepts`, branch `art-pass`). Images were downscaled to <= 1568 px (JPEG q85) before sending, so fine detail may be missed.", "",
         f"Total cost (batch price, all attempts including retries): **${total:.2f}**.", "",
         "| item | file | status | out tokens | cost |", "|---|---|---|---|---|"]
    for cid, path in OUT_PATH.items():
        r = last.get(cid)
        if not r:
            continue
        L.append(f"| {cid} | [{path}]({path}) | {r['status']} | {r.get('out', 0):,} | ${sum(x.get('cost', 0) for x in rows if x['id'] == cid):.3f} |")
    L += ["", "Caveats:", "- `landmarks/*.py` were checked with `ast.parse` only (see the provenance comment); they have never run against the city namespace.",
          "- `vision_review` is a read of downscaled stills by a model: treat each finding as a lead to verify, not a verdict.",
          "- `asset_coverage` is Haiku: spot-check NONE/PARTIAL rows before using the counts.",
          "- Contradiction rows in `spec_audit` quote the spec as of art-pass@7f021c21 (working tree of the clone when built)."]
    (OUT_ROOT / "README.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print(f"README written; total ${total:.3f}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("build", "build2", "submit", "ingest", "readme"):
        p = sub.add_parser(n)
        p.add_argument("--out", required=True)
        if n == "build":
            p.add_argument("--only", default="")
            p.add_argument("--ids", default="")
        if n in ("build", "build2"):
            p.add_argument("--max-tokens", type=int, default=0)
        if n == "submit":
            p.add_argument("names", nargs="+")
        if n == "ingest":
            p.add_argument("--no-wait", action="store_true")
            p.add_argument("--poll", type=int, default=60)
    a = ap.parse_args()
    return {"build": cmd_build, "build2": cmd_build2, "submit": cmd_submit, "ingest": cmd_ingest, "readme": cmd_readme}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
