# Sweep-raid lab, round 4 (L4)

A playable Godot prototype of the round-4 sweep raid, so a critic can judge suspense, decision depth and readability in motion
with every number coming from one rules engine. A design tool, not part of the game: nothing outside `tools/raid_lab_m10/` is
touched. Brief: `docs/handoff/raid_lab_l4/BRIEF.md`. Rules source of truth: `tools/raid_concepts/sweep_l4.py` (python; it builds
on `sweep_l3.py` and `sweep_l2.py`). The folder name `raid_lab_m10` and the scene `raid_lab_m10.tscn` are kept as the entry point.

**Earlier rounds were replaced, not kept behind a `RULESET` constant.** The L3 code (`l3_*.gd`, `l3_golden.json`) is in git history
(commit fe62f879 and earlier); L2 before that. The critic reviews that drove the last two rounds are
`docs/design/raid_concepts/_reviews/REVIEW_LAB_L2.md` and `REVIEW_LAB_L3.md`.

## Run it

- Play: open `res://tools/raid_lab_m10/raid_lab_m10.tscn` and run the scene (1280x720, text 1.0, mouse and keyboard).
  Windowed runs from a script go through `python tools/run_windowed.py` only.
- Parity check (headless): `godot --headless --path . -s res://tools/raid_lab_m10/parity_check.gd`
- Flow check (headless): `godot --headless --path . -s res://tools/raid_lab_m10/flow_check.gd`
- Captures: `python tools/run_windowed.py --log <log> -- --resolution 1280x720 res://tools/raid_lab_m10/raid_lab_m10.tscn -- --shots=<abs dir> [--leg=0|3|5|8|11|14] [--line=planned|greedy|naive] [--lite] [--scramble] [--spoofview=range|off] [--key=<label>] [--demo=breachfix]`
  plays the whole leg of 3 raids through the lab's own input path (each raid really played: levers, forecast, sweep with the
  spoof decision, aftermath, the between screen with repairs, shop and intensity), following a golden line, saving a numbered PNG
  per screen and per playout beat. `--lite` takes fewer frames, `--scramble` runs the no-words test (see below). `--demo=breachfix`
  takes 3 frames of the breach warning that names a lever (golden naive leg 0 at raid 3 with one ghost put back in the kit, because
  with the golden kit no lever exists there).
  Delivered runs (in `D:/rc_tmp/raid_design_lab/lab_l4/`): `shots/` (leg 0, planned line, 45 frames), `shots_breach/` (leg 0, naive
  line, breach in raid 3, 38 frames), `shots_scrambled/` (leg 5, planned, scrambled, not lite, 43 frames), `shots_breachfix_demo/`
  (3 frames). Every frame was re-read after the last code change. The revealed sealed shape per raid in the captured legs: leg 0
  square, triangle, circle; leg 5 triangle, square, triangle (it differs between raids in every golden leg).

## Rules (as built, from `sweep_l4.py`)

Unchanged from L2: ONE network for the leg of 3 raids (4 x 3 grid, 6 assets of value v, the HOME server with integrity 3);
OK -> DOWN -> TAKEN, a find on HOME costs 1 integrity and 0 is BREACHED; Heat bands (extra known beams from 50 and from 75); the
sealed beam (3 candidates), the hunter, the ghost's +5 Heat, the evade's -10 Heat, repair = v // 2, the spoof acts on beam 2 only.
Unchanged from L3: the leg kit, one shop buy and the run intensity between raids, Heat carries into the score (1.0 per point above 44).

New in L4:

- **No reveal tell.** The corp's real sealed line is `raid.real` (seeded per raid in the golden, never "candidate 0"), and
  `raid.shapes[k]` is the shape drawn for candidate k (0 triangle, 1 square, 2 circle, shuffled per raid). The forecast and the
  reveal both use these; the forecast rows are always in the order triangle, square, circle.
- **Go dark is a kit item.** It starts at 2 per leg, at most 1 asset per raid, still costs that asset's next income, and the shop sells it.
- **Cheaper shop:** ghost 4, decoy 3, spoof 3, dark 3 (one buy between raids, paid after repairs).
- **New tier BATTERED:** home intact and (2+ assets newly DOWN, or any asset newly TAKEN). It sits between HOLDS and DAMAGED.

Leg kit: 2 ghosts, 2 decoys, 2 spoofs, 2 go dark. Per raid: at most 1 ghost, up to 2 decoys, go dark on at most 1 asset. Decoys cost
no Schematics. A spoof leaves the kit only if it is used after the reveal.

| Intensity | Heat | Income |
| --- | --- | --- |
| LOW | +6 | x0.5, rounded down |
| NORMAL | +12 | x1 |
| HOT | +18 | x1.5, rounded down |

Income is the sum of v // 3 over OK, non-dark assets (after repairs), times the multiplier.

**Leg score** = bank + assets kept - HOME lost x 8 - Heat carried. Assets kept = the value of assets not TAKEN, a DOWN asset less its
repair (v // 2). Heat carried = Heat above the start (44), 1.0 per point; it is always shown as that positive number and subtracted
in the formula. **A breach has no leg score: BREACHED ends the campaign** (the python returns -100 as a sentinel for the planner;
the lab never shows it as a score).

**Outcome tiers**, stamps and the raid pips follow them: EVADED teal (nothing touched, Heat -10), HOLDS neutral light (assets hit
or only a decoy hit, fewer than 2 newly DOWN and none TAKEN), BATTERED amber, DAMAGED orange (HOME lost integrity), BREACHED red
(HOME at 0, campaign lost).

## How to play

The leg is golden leg 0 (`--leg=N` for 3, 5, 8, 11, 14). The corp's real sealed line is seeded per raid: the player sees three
candidates (a different shape on each, shuffled per raid) and learns which was real only at the reveal.

1. **Contact.** The raid's strength by Heat band (three rows with the beams each brings), a Heat -> line 50 -> line 75 -> beams
   chain, the network's status counts, what the run between raids did (intensity, Heat, income, repairs, the buy) and the KIT tray.
2. **Plan.** The kit tray (remaining ghosts, decoys, spoofs, go dark; pips go hollow for what the plan takes), then the levers (keys
   1 2 3, then click a node; click a placed lever or Z to take it off). The grid shows the known beams live (the ghost's +5 Heat can
   push the raid over a line and add a beam), the 3 sealed candidates and the hunter's columns. **Each lever draws its effect:**
   - ghost: the dashed ring, the beams pass behind the node, and every line that reaches it gets a yellow detour round the node;
   - decoy: every beam that reaches it stops at a bar before the diamond (known beams, sealed candidates and hunter columns);
   - go dark: a black node with its income chip struck in red.

   **The hunter's rule is a glyph, not a word:** each hunter column is dashed with down chevrons, and an arrow leaves the first
   touch and turns down that column (one arrow when the first touch is known, one per candidate when it depends on the sealed
   line; the arrow stays on the grid through the playout and the aftermath).
   **A red BREACH warning** sits above the grid when the forecast shows BREACH on every sealed line even with the best spoof,
   before launch. It names the fewest extra levers that clear every line (and rings their nodes), or says that no lever left in
   the kit avoids it. The playout still plays to the HOME touch.
3. **Forecast** (Enter). Per sealed line in the order triangle, square, circle: the result **if you hold the spoof** (chips: DOWN,
   TAKEN, HOME -1, BREACH), the **best a spoof can do** (a range, no node named), and the nodes **a spoof could save** (small circles
   with the node's value). On the grid every such node carries a teal chip (the line's shape, then a skip-chevron). The forecast
   never names the best spoof. **"worst" counts everything:** the lowest-scoring line's DOWN, TAKEN and HOME loss ("worst: 2 DOWN, 1
   TAKEN, HOME -1"), and the same for the best case with a spoof. With SPOOF HINTS = OFF only the hold result shows.
4. **Playout**, hands-off: beam 1, the known extras, beam 2 unseals (the real line lights, the others fade), the spoof decision (a
   click on the lit line or H to hold; every option lists its result, none is highlighted; skipped when the kit holds no spoof),
   beam 2, the hunter turns (its arrow grows from the first touch), the hunter beam. A touch that empties HOME ends the sweep at that
   touch ("HOME BREACHED"): no spoof decision follows, the spoof stays in the kit. Speed 1x/2x/4x (keys 1 2 4), SKIP (S) runs on but
   stops at the spoof decision.
5. **Aftermath.** The tier stamp, status changes stamped on the nodes, the ledger (kit before -> after for all four items, Heat
   before / ghost / evaded / after, HOME pips, network counts, **assets kept now** and **leg value rebuilt from the numbers**:
   "= bank 6 + assets kept 26 - HOME lost 0 x 8 - Heat carried 17"). A breach goes to the full-screen BREACHED card (no score).
6. **Between raids** (one screen): 1 click DOWN assets to repair; 2 one shop buy (keys 1 2 3 4, 0 or NO BUY); 3 run intensity (keys
   L N H): each card shows its Heat, its income and the next raid's Heat and known beams. **Committed choices are marked:** a picked
   repair, buy and intensity get a check and a frame; the defaults (NORMAL, NO BUY) say "default" until clicked. The ledger shows
   Schematics (after the raid, repairs, shop, bank now, **INCOME (next run)** for the selected intensity, next raid) next to Heat
   (after the raid, the run, next raid, the beams, Heat carried), and assets kept and the leg value after this step with every term
   of the formula beside it. A pick the bank cannot cover is refused with the reason.
7. **Leg record.** Raid by raid: tier, Heat before -> after and the beams, a mini map (**ring = changed in this raid, dim = carried
   over**), what changed, HOME pips, kit used (4 items), the sealed line's shape (revealed), assets kept after the raid, the between
   step and Heat carried so far, and the score formula (or "CAMPAIGN LOST: the leg has no score").

**The HUD on every screen** shows Heat, the raid pips (tier colors), HOME integrity, the bank, and **ASSETS KEPT** live (with "was N"
while a raid or a between step changes it). On the between screen the bank's change is labelled "net +N"; a bare "+N" always
means one thing in its place (Heat beside the flame, income beside the coin).

Marks, one per meaning: **ghost** = a yellow dashed ring (and a small flame); **spoof** = a teal skip-chevron; **sealed beam** = a
dashed line capped by a shape (triangle, square, circle) with a `?` badge; **decoy** = a yellow diamond; DOWN = white bolt on a
grey node; TAKEN = cobalt corp marker; go dark = a black disc. Tier colors: EVADED teal, HOLDS neutral light, BATTERED amber,
DAMAGED orange, BREACHED red. A legend row sits under the grid.

Toggles (strip at the bottom, or F1 F2): SPOOF HINTS (RANGE: the forecast shows could-save nodes and the range; OFF: hold only),
CURRENCY label (Schematics, Scrap, Credits; label only).

**The scramble** (`--scramble`) replaces each word (a run of letters) by random letters of the same length, seeded by the word:
the same word gives the same noise, but there is no letter-to-letter mapping to decode. Digits, glyphs and case pattern stay.

## What is ported

| GDScript | Python (`tools/raid_concepts/sweep_l4.py`, `sweep_l3.py`, `sweep_l2.py`) |
| --- | --- |
| `l4_rules.gd` (`L4Rules.sweep`, `resolve`, `between` / `between_parts`, `score`, `tier`, `real_cand`, `shape_of`, `why_not`, `naive_decide`, `naive_repairs`, `spoof_options`) | `sweep`, `resolve`, `between`, `score`, `tier`, `real_pick`, `shape_perm`, the caps of `allocations`, `naive_leg`; `spoof_options` is the lab's forecast (it re-uses `resolve` per skip) |
| `l4_state.gd` | `State` (with the kit, dark included) |
| `l4_config.gd` | the constants of the three files, checked against the golden `config` |
| `l4_data.gd` | loads `data/l4_golden.json` (incl. each raid's `real` and `shapes`) |
| `l4_model.gd`, `l4_play.gd` | lab state (plan, undo, kit tray, forecast, worst case, breach warning and its lever search, the between picks and their committed flags) and the playout state machine; they only call the rules |

The view is `raid_lab_m10.gd` (placeholder `_draw()` visuals; glyphs and the scramble in `l4_glyphs.gd`). Deterministic `RefCounted`
rules, no randomness anywhere in the lab: the real line and the shapes are read from the golden, and the scramble uses a local
`RandomNumberGenerator` seeded by the word. The lever search of the breach warning is a bounded deterministic search (order ghost,
dark, decoy; cells in grid order).

## Parity status: PASS

`parity_check.gd`: the config constants (incl. the 4-item kit, the new prices, intensities, max decoys, Heat carry); every step of the
planned, greedy and naive line of the 6 golden legs (18 lines, 54 steps: state before incl. kit, touches, tier incl. BATTERED, state
after the raid, the between step with repairs / intensity / buy, state after, score, the lab's naive policy reproducing the naive
line on the corp's real line); each raid's `real` and `shapes` (a candidate index, a permutation of the three shapes, read back by
`real_cand` / `shape_of` / `cand_of_shape`, and the real line wears more than one shape across the 18 raids: shapes 1, 0, 2); all 200
random single-raid resolutions (touches, tier, state, score) and all 200 random between steps; every golden allocation passes the lab's
lever validation (kit and caps). Result: 2246 checks, 0 failed, `PARITY PASS`, exit 0 (non-zero on any mismatch). Log:
`D:/rc_tmp/raid_design_lab/lab_l4/parity.log`.

`flow_check.gd`: PASS (296 checks): kit (go dark included) and caps, decoys free, undo, the heat bands and the ghost pushing a raid over a
line, the forecast (no best-spoof key, could-save nodes lie on the sealed line, `saves` iff a node saves, nothing offered with an empty
spoof kit, one line per shape), the tiers (BATTERED both ways, an already-TAKEN asset does not count, DAMAGED beats BATTERED), the seeded
real line and shapes (a permutation per raid, the revealed shape differs between raids in all 6 golden legs, the real line is not always
candidate 0), the between step (repair-then-buy budget, one buy, intensity incomes, refusals, finish, committed flags), the scramble,
golden leg 0 on its planned line through the model (touches, tier, state, forecast for the chosen spoof = the real sweep, chosen node in
the could-save set, worst case = the lowest-scoring line with its DOWN / TAKEN / HOME counts, ledger and between ledger reconcile, the
leg value rebuilt from bank + assets kept - HOME lost x 8 - Heat carried at every aftermath and between step, the kit is conserved
including dark, leg score = golden), the naive line on all 6 legs ending as the golden (breach on legs 0, 5, 8; the sweep is cut at the
HOME touch; no decision before beam 2 when HOME falls first), the breach warning (a certain breach exists in all 3 naive breach legs at
raid 3; where a lever is named, placing it clears every line), and the scene driven through its own input path (a planned raid with the
between screen and a full naive breach leg to the record and a new leg). Log: `D:/rc_tmp/raid_design_lab/lab_l4/flow.log`.

The headless flow check does not draw (no renderer); every `_draw` path is exercised by the windowed captures, whose logs are
scanned for script errors (0).

## Findings (rules ambiguities) and known gaps

- Python resolves the whole sweep even after HOME hits 0. The lab cuts the playout at the HOME touch, so a breach raid keeps only the
  touches it showed; the rules result (score -100 sentinel, kit) is unchanged. A golden naive breach step that records a spoof use is
  not reproduced in the kit when HOME falls before beam 2 (the spoof stays in the kit); nothing after a breach reads the kit.
- **The breach is settled at the forecast in all three naive breach legs (0, 5, 8)** and no allocation avoids it in legs 0 and 8
  (checked against `sweep_l4.allocations` by brute force: every allocation breaches on at least one line, with no spoof left). In leg 5
  go dark on the (3, 1) asset plus the spoof avoids it. The warning says so before launch; the playout still runs one beam to the HOME
  touch. The remaining "one-beam climax" is a rules fact (the ghosts were spent in raids 1 and 2), not a presentation gap.
- A spoof used on a node that nothing would touch still spends the item (python: `spoof is not None`). The forecast marks only nodes
  whose skip strictly beats holding (or avoids a breach); a skip that merely drops a repeated decoy touch is not a "save".
- Python `between` silently skips a repair or buy the bank cannot pay; the lab refuses the pick with the reason, same result.
- The planner's golden lines now use go dark in 12 of the 18 planned raids (2 per leg) and never buy (all planned `buy` are None except one
  spoof in leg 3 raid 2), so the shop price cut moved one buy, not the economy; HOT is chosen in legs 3, 5, 8, 11, 14 (once each).
  Go dark as a kit item still shows as "used when it is free": the kit holds 2 of a 3-raid leg, so it is rationed to 2 raids.
- Planned leg 0 scores 15 (L3: 19) and ends with 3 raids BATTERED: with the severity tier the planner's best line is a leg of
  BATTERED stamps (DOWN assets only, nothing TAKEN, HOME never touched). A critic should read the tier as honest, but it means the planned line is
  never "CELL HOLDS".
- Heat carries into the score only above 44 (`max(0, Heat - 44)`); the +12 run after the last raid is not applied.
- A decoy is a touch: a sweep whose only contact is a decoy is HOLDS (not EVADED, no Heat -10). Python repeats the decoy touch once
  per beam that reaches it; the lab dedupes it on screen (the rules list keeps every touch).
- The hunter's first touch can be a decoy; a touch on a hidden (ghost or dark) cell does not count.
- When nothing is touched the hunter takes its own line and the lab still says "OWN LINE" in words (no glyph yet: it shows in the
  scrambled run as noise).
- The turn arrow sits on a ring round the first touch and ends beside the column, not on it (the column is drawn 40 px away at the
  node's x, and shifts 14 px when it coincides with another line). It reads as "turns down", but is not drawn exactly on the column.
- The breach warning's lever search considers up to 4 extra levers and 1200 forecasts; a plan with a full kit and a certain breach
  (which the golden lines never reach) could report "none" when the budget runs out.
- Three known beams (Heat 75 and up) still crowd the grid: badges are nudged apart but the hunter's `3` badge can sit on a node
  glyph. Heat is never capped (python has no cap); the meter is drawn to 100.
- Candidate end shapes are triangle, square and circle (the diamond is reserved for the decoy).
- Placeholder vector visuals, no animation polish beyond pulses and beam heads, no sound, no save, no text scale or gamepad (out of
  scope).
