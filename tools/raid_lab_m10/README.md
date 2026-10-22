# Sweep-raid lab, round 3 (L3)

A playable Godot prototype of the round-3 sweep raid, so a critic can judge suspense, decision depth and readability in motion
with every number coming from one rules engine. A design tool, not part of the game: nothing outside `tools/raid_lab_m10/` is
touched. Brief: `docs/handoff/raid_lab_l3/BRIEF.md`. Rules source of truth: `tools/raid_concepts/sweep_l3.py` (python; it builds
on `sweep_l2.py`). The folder name `raid_lab_m10` and the scene `raid_lab_m10.tscn` are kept as the entry point.

**Rounds 1 and 2 were replaced, not kept behind a `RULESET` constant.** The L2 code (`l2_*.gd`, `l2_golden.json`, `l2_extra.json`
and its generator) is in git history (commit 8a354152 and earlier). The L2 critic review that drove this round is
`docs/design/raid_concepts/_reviews/REVIEW_LAB_L2.md`.

## Run it

- Play: open `res://tools/raid_lab_m10/raid_lab_m10.tscn` and run the scene (1280x720, text 1.0, mouse and keyboard).
  Windowed runs from a script go through `python tools/run_windowed.py` only.
- Parity check (headless): `godot --headless --path . -s res://tools/raid_lab_m10/parity_check.gd`
- Flow check (headless): `godot --headless --path . -s res://tools/raid_lab_m10/flow_check.gd`
- Captures: `python tools/run_windowed.py --log <log> -- --resolution 1280x720 res://tools/raid_lab_m10/raid_lab_m10.tscn -- --shots=<abs dir> [--leg=0|3|5|8|11|14] [--line=planned|greedy|naive] [--lite] [--scramble] [--spoofview=range|off] [--key=<label>]`
  plays the whole leg of 3 raids through the lab's own input path (each raid really played: levers, forecast, sweep with the
  spoof decision, aftermath, the between screen with repairs, shop and intensity), following a golden line, saving a numbered PNG
  per screen and per playout beat. `--lite` takes fewer frames, `--scramble` runs the no-words test (see below).
  Delivered runs (in `D:/rc_tmp/raid_design_lab/lab_l3/`): `shots/` (leg 0, planned line, 45 frames), `shots_breach/` (leg 0,
  naive line, breaches in raid 3 at the first beam, 38 frames), `shots_scrambled/` (leg 5, planned, lite, scrambled, 23 frames),
  `shots_hintsoff/` (leg 3, planned, lite, SPOOF HINTS off, 22 frames).

## Rules (as built, from `sweep_l3.py`)

Unchanged from L2: ONE network for the leg of 3 raids (4 x 3 grid, 6 assets of value v, the HOME server with integrity 3);
OK -> DOWN -> TAKEN, a find on HOME costs 1 integrity and 0 is BREACHED; Heat bands (extra known beams from 50 and from 75); the
sealed beam (3 candidates, the revealed one is candidate 0), the hunter, the ghost's +5 Heat, the evade's -10 Heat, repair =
v // 2, go dark (at most 1 asset a raid, no income from it that interval), the spoof acts on beam 2 only.

New in L3:

- **Leg kit.** 2 ghosts, 2 decoys and 2 spoofs for the whole leg. Per raid: at most 1 ghost, up to 2 decoys, go dark on at most
  1 asset. Decoys come from the kit and cost no Schematics. A spoof leaves the kit only if it is used after the reveal.
- **Between raids**, one screen, three choices: repairs (v // 2 each, paid first), ONE shop buy (ghost 6, decoy 4 or spoof 5,
  paid after repairs), run intensity:

  | Intensity | Heat | Income |
  | --- | --- | --- |
  | LOW | +6 | x0.5, rounded down |
  | NORMAL | +12 | x1 |
  | HOT | +18 | x1.5, rounded down |

  Income is the sum of v // 3 over OK, non-dark assets (after repairs), times the multiplier.
- **Heat carries.** The leg score charges 1.0 per Heat point above the start (44): score = bank + sum(v) of assets not TAKEN (a
  DOWN asset less its repair) - 8 per integrity lost - Heat carried. BREACHED = -100.
- **Outcome tiers.** EVADED (nothing touched; Heat -10), HOLDS (assets hit or only a decoy hit, home intact), DAMAGED (home lost
  integrity), BREACHED (home at 0, campaign lost). Stamps, the raid pips in the HUD and the record follow the tier.

## How to play

The leg is golden leg 0 (`--leg=N` for 3, 5, 8, 11, 14). The revealed sealed line is candidate 0 (the corp's real pick in the
python), never random.

1. **Contact.** The raid's strength by Heat band (three rows with the beams each brings), a Heat -> line 50 -> line 75 -> beams
   chain, the network's status counts, what the run between raids did (intensity, Heat, income, repairs, the buy) and the KIT tray.
2. **Plan.** The kit tray (remaining ghosts, decoys, spoofs; pips go hollow for what the plan takes), then the levers (keys 1 2 3,
   then click a node; click a placed lever or Z to take it off). The grid shows the known beams live (the ghost's +5 Heat can push
   the raid over a line and add a beam), the 3 sealed candidates and the hunter's columns. "Spoof: after the reveal..." sits under
   the levers.
3. **Forecast** (Enter). Per sealed line (shape triangle, square, circle): the result **if you hold the spoof** (chips: DOWN, TAKEN,
   HOME -1, BREACH), the **best a spoof can do** (a range, no node named), and the nodes **a spoof could save** (small circles with
   the node's value). On the grid every such node carries a teal chip (the line's shape, then a skip-chevron). The forecast never
   names the best spoof; the player picks. HOME pips show the worst case and the best case with a spoof. With the toggle SPOOF HINTS
   = OFF the forecast shows only the hold result.
4. **Playout**, hands-off: beam 1, the known extras, beam 2 unseals, the spoof decision (a click on the lit line or H to hold; every
   option lists its result, none is highlighted; skipped when the kit holds no spoof), beam 2, the hunter turns, the hunter beam.
   A touch that empties HOME ends the sweep at that touch ("HOME BREACHED"): no spoof decision follows, the spoof stays in the kit.
   Speed 1x/2x/4x (keys 1 2 4), SKIP (S) runs on but stops at the spoof decision.
5. **Aftermath.** The tier stamp (EVADED / CELL HOLDS / CELL DAMAGED), status changes stamped on the nodes, the ledger (kit before ->
   after, Heat before / ghost / evaded / after, HOME pips, network counts, leg value now, **Heat carried**). A breach goes to the
   full-screen BREACHED card (no score: the campaign is gone).
6. **Between raids** (one screen): 1 click DOWN assets to repair; 2 one shop buy (keys 1 2 3, or NO BUY); 3 run intensity (keys L N H):
   each card shows its Heat, its income and the next raid's Heat and known beams. The ledger shows Schematics (after the raid,
   repairs, shop, **BANK NOW**, income last, next raid) next to Heat (after the raid, the run, next raid, the beams, Heat carried),
   and "Leg value after this step" which counts the pending income. A pick the bank cannot cover is refused with the reason
   (repairs and the buy are paid before income).
7. **Leg record.** Raid by raid: tier, Heat before -> after and the beams, a mini map (**ring = changed in this raid, dim =
   carried over**), what changed, HOME pips, kit used, the between step (intensity, repairs, buy, next raid's Heat and beams, Heat
   carried so far) and the score formula with Heat carried.

Marks, one per meaning: **ghost** = a yellow dashed ring (and a small flame); **spoof** = a teal skip-chevron (the spoof key, the kit
tray, the decision marks, "could save" chips); **sealed beam** = a dashed line capped by a shape (triangle, square, circle) with a
`?` badge; **decoy** = a yellow diamond; DOWN = white bolt on a grey node; TAKEN = cobalt corp marker; go dark = a black disc. Tier
colors: EVADED teal, HOLDS neutral light, DAMAGED orange, BREACHED red (pips follow the tier). A legend row sits under the grid.

Toggles (strip at the bottom, or F1 F2): SPOOF HINTS (RANGE: the forecast shows could-save nodes and the range; OFF: hold only),
CURRENCY label (Schematics, Scrap, Credits; label only).

**The scramble** (`--scramble`) replaces each word (a run of letters) by random letters of the same length, seeded by the word:
the same word gives the same noise, but there is no letter-to-letter mapping to decode. Digits, glyphs and case pattern stay.

## What is ported

| GDScript | Python (`tools/raid_concepts/sweep_l3.py`, `sweep_l2.py`) |
| --- | --- |
| `l3_rules.gd` (`L3Rules.sweep`, `resolve`, `between` / `between_parts`, `score`, `tier`, `why_not`, `naive_decide`, `naive_repairs`, `spoof_options`) | `sweep`, `resolve`, `between`, `score`, `tier`, the caps of `allocations`, `naive_leg`; `spoof_options` is the lab's forecast (it re-uses `resolve` per skip) |
| `l3_state.gd` | `State` (with the kit) |
| `l3_config.gd` | the constants of both files, checked against the golden `config` |
| `l3_data.gd` | loads `data/l3_golden.json` |
| `l3_model.gd`, `l3_play.gd` | lab state (plan, undo, kit tray, forecast, the between picks) and the playout state machine; they only call the rules |

The view is `raid_lab_m10.gd` (placeholder `_draw()` visuals; glyphs and the scramble in `l3_glyphs.gd`). Deterministic `RefCounted`
rules, no randomness anywhere in the lab (the scramble uses a local `RandomNumberGenerator` seeded by the word).

## Parity status: PASS

`parity_check.gd`: the config constants (incl. kit, prices, intensities, max decoys, Heat carry); every step of the planned, greedy
and naive line of the 6 golden legs (18 lines, 54 steps: state before incl. kit, touches, tier, state after the raid, the between
step with repairs / intensity / buy, state after, score, and the lab's naive policy reproducing the naive line); all 200 random
single-raid resolutions (touches, tier, state, score); all 200 random between steps; every golden allocation passes the lab's
lever validation (kit and caps). Result: 2119 checks, 0 failed, `PARITY PASS`, exit 0 (non-zero on any mismatch). Log:
`D:/rc_tmp/raid_design_lab/lab_l3/parity.log`.

`flow_check.gd`: PASS (214 checks): kit and caps (1 ghost / 2 decoys / 1 dark a raid, empty kit refusals), decoys free, undo, the heat
bands and the ghost pushing a raid over a line, the forecast (no best-spoof key, could-save nodes lie on the sealed line, `saves`
iff a node saves, nothing offered with an empty spoof kit), the between step (repair-then-buy budget, one buy, intensity incomes,
refusals, finish), the scramble, golden leg 0 on its planned line through the model (touches, tier, state, forecast for the chosen
spoof = the real sweep, chosen node in the could-save set, ledger and between ledger reconcile, the kit is conserved, leg score =
golden), the naive line on all 6 legs ending as the golden (breach on legs 0, 5, 8; the sweep is cut at the HOME touch; no
decision before beam 2 when HOME falls first), and the scene driven through its own input path (a planned raid with the between
screen and a full naive breach leg to the record and a new leg).

The headless flow check does not draw (no renderer); every `_draw` path is exercised by the windowed captures, whose logs are
scanned for script errors (0).

## Findings (rules ambiguities) and known gaps

- Python resolves the whole sweep even after HOME hits 0. The lab cuts the playout at the HOME touch (the brief's "no spoof
  decision after a breach"), so a breach raid keeps only the touches it showed; the rules result (score -100, kit) is unchanged. A
  golden naive breach step that records a spoof use is not reproduced in the kit when HOME falls before beam 2 (the spoof stays in
  the kit); nothing after a breach reads the kit.
- A spoof used on a node that nothing would touch still spends the item (python: `spoof is not None`). The forecast marks only nodes
  whose skip strictly beats holding (or avoids a breach); a skip that merely drops a repeated decoy touch is not a "save".
- Python `between` silently skips a repair or buy the bank cannot pay; the lab refuses the pick with the reason, same result. Repairs
  and the buy are budgeted together, so the python's order (repairs, then buy) always agrees.
- The planner never buys anything in the 6 golden legs (all `buy: None`) and mostly picks LOW or NORMAL (HOT in leg 3 raid 1 and
  leg 5 raid 2): the shop looks dominated by repairs and income at these prices, and with 3 raids a buy after raid 2 only helps
  raid 3. Go dark is used in nearly every planned raid (it has no kit cost, only forgone income): the L2 "use it every raid"
  line survives for go dark.
- Heat carries into the score only above 44 (`max(0, Heat - 44)`); a low-Heat leg earns no bonus, and the +12 run after the last
  raid is not applied (the record's Heat is the Heat after raid 3).
- Planned leg 0 scores 19 (L2: 45) because 17 Heat is carried: HOT is rarely right, which is the intended trade, but the score
  scale moved, so L2 comparisons need the offset.
- The naive line breaches on legs 0, 5, 8 in raid 3 (HOME 1 -> 0) as in L2, now with two DAMAGED stamps before it.
- A decoy is a touch: a sweep whose only contact is a decoy is HOLDS (not EVADED, no Heat -10). Python repeats the decoy touch once
  per beam that reaches it; the lab dedupes it on screen (the rules list keeps every touch).
- The hunter's first touch can be a decoy; a touch on a hidden (ghost or dark) cell does not count.
- Heat is never capped (python has no cap); the meter is drawn to 100.
- Candidate end shapes are triangle, square and circle (the diamond is reserved for the decoy).
- Three known beams (Heat 75 and up) still crowd the grid: badges are nudged apart but the hunter's `3` badge can sit on a node
  glyph.
- Placeholder vector visuals, no animation polish beyond pulses and beam heads, no sound, no save, no text scale or gamepad (out of
  scope).
