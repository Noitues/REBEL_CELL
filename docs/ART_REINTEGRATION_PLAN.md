# REBEL_CELL — Art reintegration plan (art-pass → main)

> **Rulings applied: DECISIONS 2026-10-05 pause point 0.** The designer answered §1 as a numbered list on 2026-10-05
> (`docs/DECISIONS.md` "2026-10-05 — Designer rulings: art reintegration, pause point 0"). This
> plan is kept as written; the §1 items those rulings changed (1, 5, 6.2, 6.5, 6.6, 7, 9) are
> struck or annotated in place with the ruling that applies (ART_BIBLE v2 Appendix C #1 and #12
> likewise). Landed on main by ART-0a (ported from art-pass 9a62cec, tag `art-concepts-r43`).

**Status:** draft for the designer (2026-10-05). Nothing in this plan runs until the designer
approves it and answers the "decide first" list (§1).
**Sources:** `docs/concepts/DIRECTION_REVIEW.md` (rounds 1–43, every lock), `docs/concepts/GDD_ART_COVERAGE.md`,
`docs/ART_PLAN.md` (M13 W1–W10), `docs/ART_BIBLE.md` (being rewritten now around the locked
direction; it is **the art source of truth** once the rewrite lands), and on `main`:
`CLAUDE.md`, `docs/MILESTONES.md`, `docs/GAP_ANALYSIS.md` (H20–H24), `docs/DECISIONS.md`,
`docs/TEST_SUITE.md`, `.claude/HANDOFF.md`, `docs/handoff/anim_r7/`.
The process for executing it is in `docs/ART_REINTEGRATION_PROMPT.md`.

---

## 0. Where things stand (measured 2026-10-05)

| | State |
|---|---|
| `main` | `a59dcc2` (pushed). ANIM-R1…R6 merged, 1233 tests green. **ANIM-R7 audits are done and NOT clean** (2 P1, ~29 P2). The R7 fix batches A–E (`docs/handoff/anim_r7/R7_FIX_BATCHES.md`) were **never launched**: the designer paused. One open question blocks A5 (the "→ N LEFT" overkill wording). After a CLEAN audit: H25+, then the MILESTONES "Queued passes". |
| `art-pass` | `c7b5809` (pushed to `origin/art-pass`). Forked from `main` at `8ddfa86`; **424 commits** ahead of main, main is **94 commits** ahead of the fork (ANIM-R5…R7). |
| (a) M13 code | W1–W10 + WF + W9F: 334 files, +36.6k / −3.0k lines; 1414 tests green on art-pass. Implements **ART_BIBLE v1.0** (zine/neon/cyberdeck, the GDD 9.1 three worlds). Touches no `scripts/core/`; schema: `city_look_data.gd` (new), `ui_motion_data.gd`, `ui_motion_entry_data.gd`; `content/config/city_look.tres`, `ui_motion.tres` (+573 lines). |
| (b) Concept rounds | ~43 rounds of concept work under `docs/concepts/` (5,912 tracked files, ≈277 MB: 706 PNG, 347 JPG, 316 GIF, 4,238 Blender/PIL `.py` scripts, 9 stray `.pyc`), plus `docs/art_review/` (≈30 MB tracked M13 review packs). `docs/concepts/.gdignore` exists; `docs/art_review/` has `.gdignore` only in some subfolders. |
| Dry-run merge | `git merge-tree main art-pass`: **37 conflicted files**: `combat_scene.gd`, `wheel_view.gd`, `hq_scene.gd`, `netrun_scene.gd`, `city_map_overlay.gd`, `combat_fx_layer.gd`, `raid_fx_layer.gd`, `dialogue.gd`, `fx.gd`, `settings_panel.gd`, `pause_menu.gd`, `tutorial_overlay.gd`, `toast_note.gd`, `subtitle_strip.gd`, `zine_card.gd`, `zine_panel.gd`, `hud_bar.gd`, `hud_stats.gd`, `modem_sign.gd`, `polaroid.gd`, `stat_icon.gd`, `scroll_hint.gd`, `drip_button.gd`, `ui_motion.tres`, `ui_motion_data.gd`, `strings.csv`, `motion_lab.gd`, `schema_smoke_test.gd`, `test_manifest.json`, and 8 test files (H20/H23/H24 passes, anim R2/R4 city, vertical pass 2). Every one is a view ANIM-R5…R7 reworked for motion. |
| New direction | Locked: Cv2 low-poly triangulated city with E cel shading (toon bands, ink lines); overlay = vinyl stickers (all words and objects) + grease pencil (plans; yellow routes / red threats; near-opaque) + light spill; slices = family C "Screens & Data" CRT screens with white glyphs; D4 "Lens & rail" wheel frame; sticker cards; one unified real-city model for City Grid, raids and netrun transit; MAINFRAME shop; Courier Prime corp paper. Spray, stencil, ransom collage, ink brush and the dripping marker are **rejected**: most of M13's zine look is superseded. |

---

## 1. Decide first (the designer, before any code moves)

Numbered so the designer can answer as a list, as usual.

1. **Plan approval and order.** Proposed order: (a) finish ANIM-R7 (launch batches A–E, merge, R8 audit); (b) stop the
   Animation loop at the first CLEAN audit **or** after R8, whichever comes first, mapping any
   remaining finding into the art batch that rewrites that view (each mapped item stays an
   acceptance line there: nothing deferred); (c) art reintegration (this plan, M14);
   (d) H25+ and the Queued passes after M14, each with its own review loop. Alternative: H25 and
   the Queued passes first, then art. ~~**Recommended: (a)→(b)→(c)→(d)**, because the art batches
   rewrite almost every view H25 would audit.~~
   > **Ruling 1 (DECISIONS 2026-10-05 pause point 0), changed: M14 first.** Port the art pass (M14, ART-0…ART-12) →
   > re-evaluate every ANIM-R7 finding against the ported screens → fix the ones still valid →
   > re-evaluate the horizontal list → H25+ → Queued passes. ANIM-R7 is paused, not dropped.
2. **Merge strategy** (§2): **port, don't merge**. Land the docs on main, salvage the
   direction-agnostic M13 infrastructure by porting it onto main, and drop the superseded M13
   visuals. The `art-pass` branch is kept and tagged, never merged.
3. **Concept archive in main** (§2.1): bring a curated `docs/art_reference/` (locked finals,
   ≈30–60 MB) to main and leave the full 277 MB archive on the `art-pass` tag. Alternatively,
   bring all of `docs/concepts/`. Every agent worktree is a full checkout, and C: has already
   filled up once, so the curated set is recommended.
4. **GDD 9.1 (locked) is superseded.** The "three worlds" (wireframe net, punk zine, cyberdeck) becomes:
   Cv2 cel city + CRT screens + vinyl stickers + grease pencil + light spill. GDD 9.2 changes too:
   "zine elements never cover the wheels" becomes the sticker and pencil layer rules, with the
   standing rule "no UI ever covers grease pencil". This needs a ruling and a GDD 9 rewrite
   citing it.
5. **Slice program names**: display names only, or do they replace the GDD slice-type words? Proposed:
   ~~**display only**. `RC.SliceType` and content ids stay, so saves and replays are unchanged, and
   the GDD 2.6 table gains a "program" column.~~
   > **Ruling 5 (DECISIONS 2026-10-05 pause point 0), changed: no save or replay compatibility.** Internal names (enums,
   > ids, file and class names) follow the new display names; no aliases, no migrations. Saves and
   > replays move to a project folder git ignores (ART-0 S0).
6. **Name collisions** found by the coverage audit, each needing a call:
   - Meridian **PRIORITY** collides with the hub **Priority Routing**.
   - Raid words TAKEN / BREACHED / DOWN / CELL HOLDS vs the GDD's **Seized / Disabled / Holds**.
     > **Ruling 6.2 (DECISIONS 2026-10-05 pause point 0), changed:** the raid words replace the GDD words: Seized → TAKEN,
     > Disabled → DOWN, Holds → CELL HOLDS (a node that holds shows HOLDS), BREACHED = the home
     > server falls. GDD 3.3 / 7.1 / 7.2 updated; code and content follow (ART-0 B).
   - Upgrade "tier I–III" vs the Site tiers T1–T4.
   - VAULT / KEY / SPOOF glyphs vs raid node glyphs.
   - "Modem" (the node) vs the **MAINFRAME** sign.
     > **Ruling 6.5 (DECISIONS 2026-10-05 pause point 0), changed:** the shop node "Modem" is renamed **Mainframe**
     > everywhere (node type, ids, strings, GDD 4.2, 6.3, 11.x); the boss gate therefore needs its
     > own name (D5 proposes Central Server, asked with §3.1).
   - REBEL_CELL's fist crest vs art_asset A2 ("the Cell needs its own identity").
     > **Ruling 6.6 (DECISIONS 2026-10-05 pause point 0):** the art-pass direction stands: the fist crest is the Cell's
     > mark. Telling the player's Cell from the REBEL_CELL corporation is a future concept slice
     > (DECISIONS "Open questions for the designer").
7. **Rendering tech for the unified city** (§5, ART-1 spike): real-time Godot 3D (SubViewport,
   toon + outline shaders, MultiMesh buildings, LOD) vs Blender-baked layered sprites with 2D
   motion. ~~Recommended: run the spike, then choose on measured frame time.~~
   > **Ruling 7 (DECISIONS 2026-10-05 pause point 0), changed: fidelity first, then optimise.** The ART-1 spike picks the
   > technique that reproduces the reference images most faithfully; an optimisation round then
   > brings it inside the §5.2 budget. The budget is a gate, not a reason to change the look.
8. **Mechanics from the concept "game to-do" lists** (§3.2): which are approved, and when.
   Recommended: none are built inside the art batches. Approved ones become their own game passes
   (G-passes) after M14, or interleaved where art depends on them. Until then, the art ships only
   what the current rules have.
9. **The R7 open question:** overkill wording ("→ 0 HP" / "TAKES THE LAST 1 HP" + skull). The
   new forecast format (§3.1 D15) may supersede it.
   > **Ruling 9 (DECISIONS 2026-10-05 pause point 0):** the overkill wording ("→ 1 LEFT") is re-evaluated after the art
   > pass; the HP result chip (D15) may replace that line.

---

## 2. Merge strategy

### 2.1 Recommendation: land the docs, port the infrastructure, re-implement the direction

**Why not `git merge art-pass` into main.**
- There are 37 conflicts, all in views that ANIM-R5…R7 reworked for motion.
- The art-pass side of those conflicts implements a look the designer has since rejected (zine
  paper, drips, spray, Polaroid crew walls, neon-ink city).
- Resolving them means rebuilding ANIM behaviour on top of code that will then be rewritten again.
- The merge would also pull 277 MB of concepts and 4,238 scripts into every agent worktree.

**Why not discard M13.** About a third of it is direction-agnostic and tested:
- the accessibility settings (text scale to 2.0, colour-blind, high contrast, reduce motion,
  resolve speed, glyph sets);
- the visual QA harness and the static and runtime lint;
- semantic colour tokens and the type-scale machinery;
- VFX tiers ("no full-screen flash below T4");
- component states, focus brackets and pad glyphs;
- the modal API (`PageTransition.open_modal` / `after_modals`), `UiWrap.whole_words`, `PaperInk`
  high contrast, and the Steam Deck quality tier.

The new ART_BIBLE will need all of these.

**Steps**

1. **Freeze and tag.**
   - Tag `art-pass` as `art-m13-final` (the W9F merge, the last code commit) and as
     `art-concepts-r43` (`c7b5809`). Push both tags.
   - Keep the branch. Never merge it, and never delete the `art/w*` branches without asking.
   - Log in DECISIONS: "M13 (ART_BIBLE v1.0) superseded by the concept direction; ported in part".
2. **ART-0a, docs landing (on main, docs only).** On a branch from main:
   - `git checkout art-concepts-r43 -- <paths>` for:
     - `docs/ART_BIBLE.md` (the rewritten v2, once that agent finishes);
     - `docs/concepts/DIRECTION_REVIEW.md` and `docs/concepts/GDD_ART_COVERAGE.md`;
     - `docs/ART_REINTEGRATION_PLAN.md` and `docs/ART_REINTEGRATION_PROMPT.md`;
     - the curated reference set (decision 3).
   - The curated set is copied into `docs/art_reference/<area>/` with a README that maps each
     image to its DIRECTION_REVIEW lock and to `art-concepts-r43:<original path>`.
   - It includes the glyph set (`round17_slice_system/glyphs/`, 59 PNGs + `index.txt`) and the
     Courier Prime fonts with their OFL.
   - It excludes `__pycache__` / `*.pyc`.
   - Add a `.gdignore` to `docs/art_reference/`.
   - Move `ART_PLAN.md` (M13) to `docs/art_history/ART_PLAN_M13.md`, with a superseded banner.
   - Bring the M13 DECISIONS entries over verbatim under a "M13 art pass (art-pass branch,
     superseded in part)" heading, so the record of what the branch decided survives.
   - Add the M13 box and the new M14 section to MILESTONES.
   - Commit, run the 3 checks, push.
3. **ART-0b, salvage port (code, on branches from main).** Port M13 infrastructure in small
   slices, newest main first, each as its own branch, agent and merge:

   | Slice | From art-pass (see the `art/w*` branches) | Keep | Drop or replace |
   |---|---|---|---|
   | S1 Settings | W9s `test_w9_accessibility_settings.gd`, `settings.gd`, `settings_panel.gd` parts | text scale 2.0, colour-blind modes, high contrast, reduce motion, resolve speed, glyph sets, `city_quality` | panel styling (redone in ART-10) |
   | S2 QA harness + lint | W10 `tools/visual_qa/*`, review-pack tooling, the 53-screen matrix | all of it, re-pointed at main's screens | the baseline images (re-captured) |
   | S3 Tokens and type machinery | W1 `palette.gd` semantic tokens, `ui_theme.gd` type steps, tracking, MSDF switches, the Plex font | the mechanism, names and tests | the values (ART-1 sets the v2 palette and faces) |
   | S4 VFX tiers | W6 `VfxTier`, shader `reduce_effects` uniforms, `test_vfx_tiers.gd` | all | zine-specific shaders |
   | S5 Kit behaviour | W2/WF: component states, focus brackets, `PadGlyph`, `UiTip.for_input`, the `PageTransition` modal API, `UiWrap.whole_words`, `FitScroll` guards, `PaperInk` high contrast | behaviour and tests | zine skins (ART-4 and ART-10 restyle them) |

   - **Port method:** `git checkout art-m13-final -- <file>` only for files that do not exist on main.
     For existing files, apply the M13 diff by hand onto main's version (ANIM behaviour wins).
   - Keep the M13 tests that test behaviour. Drop tests that pin a superseded look, and log each
     one dropped.
   - Each commit says "ported from art-pass <sha>".
   - **Not ported** (superseded by the direction): `card_art.gd`, `portrait_art.gd` (procedural),
     `campaign_end_stage.gd` / `run_end_stage.gd` (zine T4), `city_atmosphere.gd` (neon-ink grade),
     `wheel_bezel.gd`, zine `zine_card.gd` frames, `hologram.gd`, `corp_pattern.gd`, the W8a–d screen
     layouts, `city_look.tres` / `city_look_data.gd`.
   - Each of these is listed in DECISIONS with the art batch that replaces it. A few may be
     reused as starting points; the batch says so.
4. **Conflicts with ANIM work.**
   - Main's motion behaviour always wins: `MotionSkip`, the hold helpers, `ui_motion.tres`
     entries, REQUIRED_IDS, lab demos, AWAITING_FIX.
   - Art batches restyle what moves; they do not remove a motion entry. If a view is replaced,
     its entries move to the new view, with a lab demo exercising them on the real piece.
   - `ui_motion.tres` changes are union-merged with `load_steps = sub_resources + ext_resources + 1`.
   - `strings.csv` is re-exported (`tools/export_text.gd`), then imported.
5. **No main → art-pass sync** and no further work on art-pass. Concept rounds that continue
   (for example site markers v4, Meridian textures) happen on a new `art-concepts` branch from
   `art-concepts-r43`, and land on main as `docs/art_reference/` updates.

---

## 3. GDD and DECISIONS changes required (each one a designer decision before implementation)

CLAUDE.md applies: never silently change the GDD. Each line below becomes:
1. a DECISIONS entry citing the designer's ruling and the DIRECTION_REVIEW round;
2. then a GDD edit citing that entry;
3. then content and strings;
4. then tests.

**Default** = what this plan proposes if the designer says "default". **Blocks** = the batch that
cannot finish without it.

### 3.1 Renames and presentation rules (art batches depend on these)

| # | Change | Source | Default | Blocks |
|---|---|---|---|---|
| D1 | GDD 9.1 / 9.2 visual baseline replaced (see §1.4) | rounds 1–3, 40 | rewrite GDD 9 around ART_BIBLE v2 | ART-1 |
| D2 | Slice programs: ATTACK = **SHIM**, CRIT = **OVERFLOW**, DEFEND = **DEFRAG**, EVADE = **DETOUR**, HEAL = **HOTFIX**, AFFLICT = **INFECT**; SHIELD = SANDBOX, DEPLOY = TROJAN, MISS = NULL unchanged | rounds 32–34 | display names via strings; enum unchanged; glyph file names updated (`slice_exploit.png` → `slice_shim.png` …) | ART-2 |
| D3 | Meridian: JUDGEMENT retired; RAM-drain slice (GDD 8.4b "Tariffs", `tariff.tres`) shown as **PRIORITY** (stamped box + alarm light); Meridian CRIT shown as **AIRMAIL** | round 18 | display rename; **PRIORITY clashes with Priority Routing**: pick PRIORITY + rename the hub, or another word | ART-2 |
| D4 | INERTIA → **WEIGHT** (anvil); Solace HEAL → **GROWTH** (mitosis) | rounds 14–18 | display rename | ART-2 |
| D5 | "Mainframe Gate" → **Central Server** (GDD 11.7); per-corp names: The Master Manifest, The Genome Core, The Panopticon, Launch Control | rounds 33, 35 | rename; per-corp names as content strings | ART-2, ART-8 |
| D6 | Player-facing **Firmware** everywhere ("MICROCHIPS" strings → FIRMWARE) | rounds 33–34 | yes | ART-3, ART-9 |
| D7 | Shop node: the sign reads **MAINFRAME** (blue neon; takeover sequences NO→MoRE→MAN, I AM→AI, I AM→NO→MAN); the GDD node stays "Modem", or is renamed | rounds 31–34 | keep the node id; player-facing node name MAINFRAME | ART-9 |
| D8 | Precision tier **Partial → WEAK** (GDD 2.4 table) | round 39 | rename the label only | ART-2 |
| D9 | Raid words: TAKEN, BREACHED, DOWN, CELL HOLDS vs GDD Seized / Disabled / Holds | raid rounds 20–23 | the GDD terms stay the rules words; the art words are the on-map stickers, mapped 1:1 in GDD 7.2 | ART-6 |
| D10 | Title verbs: EXFIL replaced; **SIMULATE** for the tutorial; BREACH / DISABLE / OVERTHROW | rounds 31–33 | as locked (main menu option A) | ART-10 |
| D11 | Heat bands re-cut: old FLAGGED → HUNTED, old NOTICED → FLAGGED, new NOTICED = a couple of alarms; Heat shown as "the city reacts" (H1); screen glitch only as an Options extra (`heat_glitch`, exempt from VfxTier) | rounds 19–22 | band names in content and strings; thresholds unchanged | ART-3, ART-5 |
| D12 | RESPIN label (never CHECKPOINT); the undo block shows on UNDO | round 23 | yes | ART-4 |
| D13 | "Always show all nodes" setting; hidden-node visibility rules on the netrun map (nodes not next are hidden; legend hover and node hover reveal) | round 37 | new Settings key (additive) | ART-7 |
| D14 | Netrun presentation rules: unavailable nodes and links white, past nodes grey, TARGET circle, tier shown, Heat shown, irrelevant city greyed, node panel only when decrypted | rounds 34–37 | presentation only, if it matches current rules (verify against GDD 4.2) | ART-7 |
| D15 | Combat HUD v4: forecast and NEXT readouts removed; a this-turn result chip beside each HP (`−6 (4 shield) +4 shield −1 RAM`) with a tooltip breakdown. GDD 2.10 ("the full outcome" before commit) must still hold: the chip **is** the preview | rounds 41–43 | yes; preview == result tests move to the chip | ART-4 |
| D16 | Every card-caused effect stems from the card's slap and dissolve on the target wheel, never from the hand | round 19–20 rule | yes | ART-3 |
| D17 | Boss fight backdrop = the corp HQ; map = close-up (same model, same roads); regular fights at smaller Sites on the real road layout; fight won → the building's lights turn Cell colours | rounds 24–25, 31 | yes | ART-2, ART-5 |
| D18 | REBEL_CELL reading: "the player's home until the betrayal reveal", with home and DISPATCH versions; the fist in red windows with a blackout reveal | rounds 24–34 | presentation of GDD 8.2 / 8.5; no rule change | ART-5 |
| D19 | Courier Prime (OFL) added for corp paper (licence OK) | round 31 | yes | ART-1 |
| D20 | MOMENTUM's dynamic pictogram (the big number switches after a spin) | round 15 | view reads existing state; no rule change | ART-3 |

### 3.2 New or changed mechanics proposed by the concept rounds (game design; never inside an art batch)

Each needs a ruling (approve / reject / later). An approved item becomes a **G-pass**: rules in
`scripts/core/` with tests, content, a balance sim, and then its art. Until then, its art lives
only in `docs/art_reference/` (placeholder library), never in a shipped screen.

| # | Proposal | Source | Notes |
|---|---|---|---|
| G1 | **Inner-ring redesign**: ACCELERATOR becomes a sub-needle that triggers the outer slice it points at; a drone hangar segment (two drones); a double-status segment (or CORRUPT = "double status effect"); AOE segments (adjacent or global); operatives start with 1–2 blank segments; ×2 possibly moves to Firmware | rounds 39–40 | GDD 6.4; schema change to segments; balance sim |
| G2 | **Satellites**: a new satellite overwrites an occupied slice; satellites can't be nudged (except as a drone-class ability); multi-drone on one slice (the hangar) needs a damage rule; status stacks show ×N | rounds 39–41 | GDD 2.7 |
| G3 | **Parasite ring**: a partial third ring as a boss mechanic that can latch onto either wheel; it pops up when the needle settles on it, and its sub-slice fires (it may reuse effects, e.g. a heal that heals the boss); never hit, never guards | rounds 39–41 | new mechanic; GDD 2.x + 8.x |
| G4 | **New slice types and states**: PHISHING, SHIELD (separate from SANDBOX), ENCRYPT, RECON; BURN, TORCH and DISSOLVE programs; a program for the mask background; KILL PROCESS; slice states FROZEN, LOCKED, BURNING, EMPOWERED (FROZEN on a slice misrepresents the wheel-level Freeze); SANDBOX's purpose ("block one whole attack" / "block next status" vs GDD shield cap 15) | rounds 10–16 | GDD 2.6, 2.9; `RC.SliceType` |
| G5 | **Slice upgrade tiers I–III** (`SliceData` has no tier); corp tiers 1–3 by enemy rank | rounds 13–16 | schema change; ties to Queued "Card upgrades" |
| G6 | **Exploits expansion**: one per boss buff (incl. ROOTKIT, HIJACK, CIPHER); map badges per tier-2 Site; Breach vs a one-pointer boss (never offered, or "boss starts stunned"); Virus picks slices at random | rounds 38–40 | GDD 11.7; Exploits stay on T2 Sites (round 36) |
| G7 | **Gates**: rim gates that trigger when the pointer rotates through them | round 15 | design not started; art deferred by the designer |
| G8 | **Station bonuses** for Wrecker, Phantom, Overclocker and Hivemind (damage boost, slow radius, sniper, drone operator), each with a levelled version; station levelling (map onto rank?) | raid rounds 21–22 | GDD 5.2–5.4 |
| G9 | **Raid**: EXPOSED (a spotlit node takes extra damage); higher Heat = more and stronger waves and routes; no Heat escalation during a raid; decoy destroyed / route reverts (needs defence damage); raid intel decrypted or not at high Heat; path rules (no re-route during execution); threat vehicle types and upgrades (FAST, HEAVY, SPECIAL, LANDER, FLYING; not on the to-do list) | raid rounds 19–23 | GDD 4.3, 7.x; `ThreatData` |
| G10 | **Raid zoom** fits the player's network size | round 37 | presentation + camera rules; can be ART-6 if no rule changes |
| G11 | **Netrun rules**: runs go from any owned node to any unowned node across a border link (no cap); nodes never revisited; transit path for Site runs and a building climb / overhead compound for HQ runs; seized and disabled nodes de-power their links | rounds 32–37, 43 | GDD 4.1–4.2; verify against the current generator |
| G12 | **HQ mechanics** (good for now; revisit in playtest): Meridian crane/train cycle (telegraphed container, train stays a turn, links remade); Solace two strands with crossovers (semi-random node sets); Halcyon switchback 6-5-4-3-2-1 with shortcuts (max 2) and the eye sweep; Orbital missile loop (sabotage 3, the 4th launch destroys the base); DISPATCH finale **Sync Strike** (3 runners, 3 locks) + mirror combats through the chapter | rounds 42–43 | large; GDD 8.x, 11.7; map generator |
| G13 | **HQ actions without the HQ room** (dropped): how Heat, patching, repairs, recruiting and the Black Market are represented | round 42 | presentation; ART-5/ART-10 need the answer |
| G14 | **Shop**: the slice wheel sells the top 3; the top slice is cheaper (80 vs the GDD's flat 100); a campaign upgrade adds nudges to the shop wheel; removal via the recycle bin replaces SHRED; replacing a socketed firmware destroys the old chip (confirm) | rounds 33–34 | GDD 6.3, 11.x; config values |
| G15 | Server Rack "flash" (upgrade a slice a tier / swap from the Rack drawer) | round 31 | not on the to-do list; GDD 4.2 says a Rack banks Schematics |
| G16 | Card type band WHEEL / HACK / SYSTEM | round 31 | not on the to-do list; `CardData` has no type |

---

## 4. M14 — Art direction v2: batch breakdown

### 4.1 Shape (the same loop as H20–H24 and ANIM-R1…R7)

Each **ART-n** batch runs:
1. **Brief.** The orchestrator writes `docs/handoff/art_n/ART_n_BATCH.md`. It holds parallel agent
   areas (file-ownership matrix, as ART_PLAN §3), each item citing an ART_BIBLE v2 section and a
   reference image in `docs/art_reference/`. Every agent first reads a common rules file
   (`process/fix_agent_common_rules.txt`, re-targeted at ART).
2. **Build** in worktrees (`isolation: "worktree"`): small commits per acceptance item
   (`ART-n <area>: <criterion>`), tests, a DECISIONS entry "Art direction — ART-n <area>".
3. **Merge**, one branch at a time, into main:
   - `git merge --no-ff`, union-resolve;
   - `godot --headless --path . --import`;
   - `checks.sh` (full suite ×3, smoke, validate);
   - push if green;
   - SendMessage the still-running agents about what changed in their files.
4. **Capture.**
   - Timeline entry `docs/timeline/<date>_<NN>_art<n>_*.png` with a README row (next tag after
     `16_h23`, i.e. `17_…`).
   - Side-by-side sheets **reference vs in-game** in `docs/art_review/ART-n/` (with `.gdignore`),
     at text scale 1.0 / 1.6 / 2.0, mouse and pad, reduce effects, greyscale.
   - All windowed runs go through `python tools/run_windowed.py`.
5. **Audit round ART-Rn.** Three auditors, each doing its own work (no sub-agents), reporting
   only, with the verdict line CLEAN only if there is no P1/P2:
   - **vertical**: plays every touched flow end to end at 1.0 / 1.3 / 1.6 / 2.0, mouse and pad,
     reduce effects; compares with the reference images; preview == result; save/resume;
   - **horizontal**: codebase rules (Signal Up / Call Down, no magic numbers, motion entries,
     translations once, no game RNG in views, perf budget) across all corporations and classes;
   - **naive reviewers**: a beginner plus a non-English reader, from the captures; they report
     understanding %.
6. **Fix batch** from the audit (nothing deferred, P3s included), then the next audit, until CLEAN.
7. **Designer review.** Pause and report the acceptance checklist plus a numbered list of open
   questions. Apply the rulings first, then start the next batch.

Common acceptance for every batch:
- 3 checks green (full suite, never only the fast tier);
- new tests in `tests/test_manifest.json`;
- layout tests at 1.0 / 1.6 / 2.0;
- reduce effects = end state;
- headless never waits;
- motion values in `ui_motion.tres` with a lab demo;
- no colour or size literals (tokens);
- the runtime lint is clean;
- GAP_ANALYSIS gets an ART-n row;
- the perf budget is met in a windowed profile (§5.2).

### 4.2 Batches (in order)

**ART-0 — Rulings, landing, salvage** (§1–§3)
- DECISIONS entries for §1 and §3.1. The GDD 9 rewrite.
- **ART-0n names pass:** strings and content display names for D2–D8 and D11–D12, glyph files
  renamed, `export_text`, a test that no old player-facing word remains.
- The docs landing (§2.1 step 2). Salvage slices S1–S5 (§2.1 step 3).
- Acceptance: the full suite is green with the ported M13 tests; the QA harness runs on main's screens.
- Timeline: `17_art0` (the baseline before the new look).

**ART-1 — Foundations**
- Palette v2 tokens.
- Faces: ART_BIBLE v2 decides Anton / Share Tech Mono / Plex / Permanent Marker. Courier Prime
  is added with its OFL and the fonts README.
- Theme. Type steps at 2.0.
- The material kit as shaders and components:
  - **CRT screen** (scanline, phosphor, bezel);
  - **vinyl sticker** (die-cut edge, sheen, peel / slap);
  - **grease pencil** (near-opaque, thick, saturated yellow / red, dark under-shadow; drawn-on
    stroke; the "never covered by UI" rule as a lint check);
  - **light spill**;
  - **cel / toon** ramp and ink outline.
- The glyph pipeline (§6).
- **The render-tech spike** for the unified city (§5.1), with a recommendation.
- Acceptance:
  - kit sheet capture vs `round3_overlay/combined_v2`, `round33_ui_chrome/ui_kit.png` and
    `typography.png`;
  - every shader has a `reduce_effects` uniform and a VfxTier;
  - lint rule: no UI node's rect over a pencil stroke.

**ART-2 — Combat wheel stack**
- D4 "Lens & rail" frame with phase pips (`round13_wheel_details/d4.png`).
- C "Screens & Data" slices with the glyph atlas and program names.
- Tiers rendered for tier I only until G5.
- State overlays for the **existing** statuses: CORRUPTED (glitch), OVERCLOCKED, PARASITE (bug),
  ENCRYPTED if it exists. FROZEN / LOCKED / BURNING / EMPOWERED wait for G4.
- Firmware socketed die at the hub side (`round34_firmware_daemons/firmware_socket.png`).
- Satellites as mini-wheels with the blended dock and collapsed drones that bloom on hover
  (`round41_wheel_stack/combat_typical_v4.png`, `combat_worst_case_v4.png`); the z-order and
  conflict rules from round 41 NOTES.
- Hub cores, Mk2 and enemy hubs; the breach lockdown waterline; the player defeat drain
  (`round40_hub_inner_ring/`).
- Inner ring bezel and textures extending into the slices (current segments only).
- Corp skins for all five kits and boss phase treatments (`round18_corp_wheels/`, rounds 15–19).
- The animated card-play preview with ghost blades, ghost drones and no trace arrows (round 17).
- Precision landings Perfect / Good / WEAK (`round39_landing_exploits/landing_*.gif`).
- Combat backdrop: the target-building close-up, day (cooler) / night, the HQ for bosses
  (`round11_combat_target/`, round 26 framing, Meridian facing the boom, the REBEL_CELL canyon
  `round34_rebel_cell/`).
- Acceptance:
  - the worst-case clutter fixture renders legibly at 1.0 and 1.6;
  - preview == result still holds;
  - wheel draw time is within budget.

**ART-3 — Cards and FX**
- Sticker cards: peel, slap, dissolve A bit-stream (`round19_combat_fx/card_play_v2.gif`,
  `dissolve_A_bitstream.gif`). The hover preview.
- Binary damage shards (hit and crit).
- The locked effect set:
  - block / shield walls (shots from the outer arc onto a wall at the hub);
  - heal; drone deploy / attack / destroyed v3 (HP counter to 0); enemy defeated v2;
  - corrupt apply v4 / tick v3; evade v4; phase change v3 (bits from the phase pip);
  - respin; nudge and resistance; RAM gain from the TURN banner.
- Temporary word stickers dissolve into bits.
- Daemon sigils, rack and trigger; firmware trigger.
- Heat on the combat screen, 3 bands (H1, the city reacts).
- Acceptance:
  - every FX has an entry in `ui_motion.tres`, a lab demo and its reduce-effects end state;
  - flash limiter (≤3/s) test;
  - the D16 origin rule tested.

**ART-4 — HUD**
- Combat HUD v4: nudges aligned above the wheels; CELL-9 sticker over RAM; boss keys A/D;
  result chips in the D15 format with tooltip; SEND IT as a vinyl sticker; RESPIN / UNDO.
- Map HUD and top bar.
- Toasts, tooltips, buttons (yellow CANCEL), and the modal and dialog kit (abandon dialog: both
  buttons stickers).
- Acceptance:
  - GDD 2.10 holds: chip == resolve for all enemies × seeds (re-use the H23/H24 sweeps);
  - pad reachability;
  - fits at 2.0.

**ART-5 — Unified city model and motion**
- One city model for City Grid, raids and netrun transit (`round40_city_unified/three_views_v3.png`,
  `city_grid_v3.png`).
- Pan, continuous zoom and the minimap.
- Individual buildings from one kit.
- Grid brightness as round 42; translucent darker buildings in the raid and netrun views.
- Landmarks:
  - Meridian container castle (texture A, moat, gantry keep, train);
  - Solace lit helix + hospital;
  - Halcyon Court + the eye scan + the Justice statue;
  - Orbital in-ground silo + TV station;
  - REBEL_CELL red-window fist with the blackout reveal (`round34_rebel_cell/map_fist_reveal.gif`).
- City motion: sky lanes, flying cars with 3 LOD tiers, helicopters and drones with spotlights,
  searchlights, holo billboards; day / night / suspicion.
- Heat lights (calm, centred on hardened nodes).
- Site markers v4 with a plain-language legend; Exploit badges on T2 Sites with the tag on hover.
- De-powered links for seized and disabled nodes, if G11 is approved; otherwise the current rules.
- Fight-won lights.
- Acceptance:
  - each corp's Grid capture vs the reference;
  - motion layers pause under reduce motion;
  - LOD switches at the configured zooms;
  - 60 fps at 1080p on the target PC, and the Deck tier;
  - logic-side tests headless (projection, picking, label placement); render verified windowed.

**ART-6 — Raid**
- The raid on the unified city.
- Circuit-inlay lime links. The node status key. Node health (the fill drains north to south,
  the outline and icon stay lit).
- Building nodes as uplink pads.
- Vehicle models and icons v4: health disc, corp dashed status ring with heading, type shapes.
- Path rules: solid active, dashed what-if, decoy scribble.
- The card drag model: parked sticker, pencil arrow, snap circle yellow / red X.
- DOWN wipe, TAKEN mark v2, slower BREACHED, CELL HOLDS sticker, the EXPOSED spotlight (visual
  only if G9 is approved).
- R3 class beacons. Slow field under the units. Freeze crystals. Repair rise.
- Panels "by fiction" (E): holo with a decrypted corp seal, the work order, and Speed / Skip in
  the panel medium.
- The raid report as a classified corp document. Raid zoom fit (G10).
- References: `round20_raid_*`–`round23_raid_*`, `round40_city_unified/raid_gifs/`.
- Acceptance:
  - the raid verdict sweep still matches `raid_verdict`;
  - reading holds never shortened at 2x / 4x (R7 C4);
  - every changing state has a capture.

**ART-7 — Netrun**
- Transit v3: straight cable-run paths, a solid walked path, a lighter city
  (`round38_netrun_transit/transit_v3.png`).
- Node states A: outline rings white / orange / lime.
- Hidden nodes and the always-show option (D13). TARGET. Tiers. Calm Heat.
- The operative dossier on corp paper. Decrypted node panels.
- The jack-in transition: terminal connect → window despawns → wheel spins up → lens zoom
  (≈4.4 s, skippable; `round37_netrun/transition_mix.gif`).
- Dressed-room node backdrops (`round36_netrun/node_backdrop.png`).
- Acceptance:
  - the route sweeps for every corporation still pass (labels, you-are-here, fits);
  - the transition skips with one press (STYLE 5.1).

**ART-8 — HQ runs**
- The overhead compound per corp (`round43_hq_mechanics/hq_*_compound.png`).
- The Central Server breach look.
- Static layouts on the current rules first. The moving parts (crane/train, strands, switchback
  eye, silo loop, Sync Strike) land with G12.
- Acceptance: each corp's HQ run is playable and captured; the boss backdrop matches the city
  model (D17).

**ART-9 — Shop, rewards, events, dialogue, portraits**
- The MAINFRAME shop: F1 Tenement facade (pinker spill, no dangling cables), sign v4 with its
  sequences, layout v5, the offscreen slice wheel with the top-3 price tags (pricing per G14 or
  the current flat price), the recycle bin (if G14) or the current removal.
- FIRMWARE / Daemon shelves. A more colourful LEAVE sticker.
- Rewards: peel from the loot sheet (`round31_reward_event/reward_reveal.gif`).
- Events as drawn (`event_screen.png`).
- Dialogue: cel bust on a CRT feed. DISPATCH is voice-only.
- Operative portraits v2 with states and contexts and rookie variants (`round39_portraits/portraits_classes_v2.png`).
- Acceptance: the shop and event sweeps (affordability, outcome rows == deltas) still hold.

**ART-10 — Menus, title, settings**
- Title option A with the verbs (D10) and SIMULATE.
- Abandon dialog. Options on the v2 kit (incl. `heat_glitch`, always-show nodes).
- Codex, stats, achievements, pause, campaign slots, the new-campaign picker.
- Corp paper in Courier Prime.
- References: `round33_ui_chrome/title_screen.png`, `title_screen_alt_simulate.png`, `abandon_dialog.png`.

**ART-11 — Campaign lost and dossier**
- Campaign lost = **A, ransomware lock**.
- The campaign summary as a corporate dossier with polaroids and auditor post-its, and the
  audit report.
- Campaign won in the same language.
- Run end (FLATLINED / JACKED OUT / HOME FELL) restyled.

**ART-12 — Final sweep**
- The full QA matrix (all screens × 1.0 / 1.6 / 2.0 × mouse / pad × reduce effects × high
  contrast × greyscale × colour-blind).
- A perf profile on the target PC and the Deck tier.
- Skins (the M12 box: procedural palette skins on the v2 tokens).
- A last vertical / horizontal / naive audit to CLEAN.
- Log "M14 complete" in DECISIONS. Then H25+ and the Queued passes, and the approved G-passes
  in the order the designer sets.

**G-passes** (after the rulings in §3.2, each its own loop):
- rules + tests + content + `simulate_campaign` numbers, then the art for it from `docs/art_reference/`;
- suggested order: G11 netrun rules, G6 Exploits, G2 satellites, G1 inner ring, G4/G5 slices and
  tiers, G3 parasite ring, G14 shop, G8/G9 stations and raid, G12 HQ mechanics, G7 gates.

---

## 5. Risks, performance and the asset pipeline

### 5.1 Risks

| Risk | Mitigation |
|---|---|
| **Headless has no RenderingDevice.** ANIM-R4 shipped a grey city that three green runs missed. | Every render change is verified windowed (`run_windowed.py`, Movie Maker; mkdir the frame dir first; grep the log for ERROR); the vertical auditor reads frames. Logic (projection, picking, layout, LOD choice) is tested headless. |
| **The unified 3D city** is a new rendering tech for the project. | An ART-1 spike: one district in Godot 3D (toon + inverted-hull or post-process outline, MultiMesh) vs a baked-layer version; measure frame time at 1080p and the Deck tier; the designer chooses. |
| **Scope**: 43 rounds of locks. | Batch acceptance lists only locked items with a reference image; "in progress" and UNEXPLORED items stay out until locked. |
| **Mechanic-dependent art.** | Art for unapproved mechanics never ships (§3.2); the batch says which items wait on which G-pass. |
| **Conflicts with ANIM.** | Port, don't merge; ANIM behaviour wins; motion entries move with their views; union-merge `ui_motion.tres` / REQUIRED_IDS / lab DEMOS / manifest / strings. |
| **Disk** (C: filled once; ~40 worktrees ≈100 MB each). | Curated reference set; captures at 800×450 or crops; delete capture folders after reading; `df -h /c` before big captures (stop under 5 GB); ask before removing merged worktrees. |
| **Renames break saves or replays.** | Display names only; ids unchanged; a seeded replay test before and after the names pass. |
| **Translation.** | Every new word through `tr()` once; re-export `strings.csv`; pseudolocale check. |
| **Suite runtime grows** (1233 → more). | New tests in the right tier; `--update-times`; merged sweeps (TEST_SUITE consolidation rules). |
| **Licences.** | Courier Prime OFL text shipped beside the font; fonts README; Blender-made assets are ours. |

### 5.2 Performance

- The target from TECH_SPEC 10: 60 fps at 1920×1080. Resolution logic stays under 1 ms. Shaders
  stay optional and off under reduce effects.
- **Budgets** (set in ART-1, in config):
  - city frame ≤ 8 ms on the target PC;
  - wheels + FX ≤ 4 ms in the worst-case clutter fixture;
  - draw calls and material count per screen;
  - texture memory (the R7 finding: the sky fallback holds up to 48 MB).
- **LOD**:
  - cars at 3 tiers (dot + line → translucent box → model + speed line);
  - building detail by zoom; Grid labels by zoom (existing GRID_FITS rules);
  - drones collapsed by default, blooming on hover;
  - city quality tiers (`city_quality`, Deck = 1).
- **Shaders**:
  - one uber-material per medium (CRT, sticker, pencil, toon) with uniforms, not per-object
    shaders;
  - bake static lighting and city bakes (`CityBakeCache` already prebakes);
  - glitch / heat effects opt-in.
- **Profiling:**
  - windowed frame profiles per batch (`run_windowed.py` + Godot's monitors to a log);
  - a test that LOD choice and tiers come from config.

### 5.3 Asset pipeline

- **Blender 5.2** (`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`, headless
  `-b --python`).
  - The concept scripts in `art-concepts-r43:docs/concepts/*/scripts/` are the starting point.
  - Production exports go through versioned scripts in `tools/art_pipeline/` (not under docs):
    - glTF 2.0 for the city kit, landmarks, vehicles, the shop facade and HQ compounds (if 3D
      is chosen);
    - otherwise PNG layer sheets at 2× with an atlas JSON.
  - Each export has a manifest (source script, commit, settings) and a validator in
    `tools/validate_content.gd` or a sibling.
- **Glyphs:**
  - `docs/concepts/round17_slice_system/glyphs/` holds 59 PNGs + `index.txt`: slices, specials,
    states, statuses, pictos and placeholders.
  - Production copies go to `assets/glyphs/`, renamed to the program names (D2–D4), with
    placeholders excluded.
  - Prefer vector: export SVG from the generating scripts and import as MSDF / scalable textures,
    so glyphs stay crisp at 2.0 and in the 60 px mini-wheels.
  - One atlas plus an id → glyph table in content. A test that every slice type, status,
    pictogram and Exploit has a glyph.
- **Fonts:**
  - `assets/fonts/` keeps the faces ART_BIBLE v2 names, adds `CourierPrime-Regular/Bold.ttf` +
    `OFL_CourierPrime.txt`, and updates the README.
  - MSDF on where the bible says.
- **GIF references** (motion) map to `ui_motion.tres` entries. Each batch records the
  reference GIF beside each entry id in its DECISIONS entry.
- **Review packs** go to `docs/art_review/ART-n/` with `.gdignore` and stay small (crops, contact
  sheets).
