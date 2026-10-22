# Raid lab L2: the M10 sweep lab, round 2 (brief)

## Goal
Update the existing playable lab `tools/raid_lab_m10/` to the round-2 rules. The designer delegated the rulings
(2026-10-22). The key change: a find now lands on the network and a raid can lose the campaign. Everything stays under
`tools/raid_lab_m10/`. Never touch `scripts/`, `content/`, `scenes/` or the GDD. Keep the round-1 code working behind
a `RULESET` constant (`"m10"` / `"l2"`, default `"l2"`), or replace it if keeping it costs more than a day. Say which
in the README.

## Source of truth (python, read-only)
- `tools/raid_concepts/sweep_l2.py`: the rules: `make_leg`, `State`, `sweep`, `resolve`, `between`, `score`,
  `allocations`, `naive_leg`, `greedy_leg`, `planned_leg`.
- Golden: `tools/raid_lab_m10/data/l2_golden.json` (from `tools/raid_concepts/l2_golden.py`):
  - 6 legs with the planned and greedy lines step by step;
  - 200 random single-raid resolutions.

## Rules (read `sweep_l2.py` for the exact behavior)
- **One network for the whole leg** of 3 raids: a 4 × 3 grid with 6 assets (value v) plus the HOME server (3
  integrity).
- **Asset status:** OK, DOWN or TAKEN.
  - A find on an OK asset makes it DOWN: no income, repair = v // 2 between raids.
  - A find on a DOWN asset makes it TAKEN (lost for the leg; beams pass through TAKEN cells).
  - A find on HOME costs 1 integrity. **At 0 the campaign is lost (BREACHED)**: a full-screen campaign-lost end, not
    a normal aftermath.
- **Heat sets the raid's strength:**
  - beam 1, the sealed beam 2 (3 shaped candidates) and the hunter always run;
  - at Heat ≥ 50 an extra known beam is added, and at Heat ≥ 75 a second one, both scanned after beam 1;
  - the Heat meter shows the bands and what each adds.
- **Levers:**
  - 1 ghost (+5 Heat at placement; it can hide HOME);
  - 1 decoy (−3 Schematics);
  - go dark on at most 1 asset (no income this interval).
  - Between raids: repair DOWN assets.
- **Spoof:** a choice after the reveal; beam 2 skips one node.
- **Hunter:** it turns down the column of the first touch (a find or a decoy); otherwise it takes its own line.
- **EVADED:** nothing touched at all (a decoy counts as a touch). Reward: Heat −10.
- **Between raids:** Heat +12; income = sum(v // 3) over OK, non-dark assets.
- **There is no key any more.** One ledger: Schematics (bank), Heat, home integrity, and asset status.

## Screens to change (keep what works: forecast on the grid, ledger, beat-by-beat playout, toggles bar)
- **Contact.** The raid's strength by Heat band, drawn: which extra beams come, and why (Heat).
- **Plan / forecast.**
  - Per candidate, mark each node by the outcome it would suffer: DOWN, TAKEN, or HOME −1.
  - The forecast **includes the held spoof**: show the range with and without your best spoof, or mark which node the
    spoof could save on each line.
  - Show home integrity as pips, with the projected loss.
- **One visual vocabulary:**
  - the diamond means only the decoy (candidate shapes: triangle, square, circle);
  - DOWN uses the GDD mark (white bolt on a greyed node);
  - TAKEN is a cobalt corp marker;
  - threats and beams stay cobalt (designer ruling).
- **Aftermath.** The ledger (bank, Heat, home), with status changes stamped on the nodes. CELL HOLDS / BREACHED.
- **Between raids.** A repair step: click DOWN assets to repair, within the bank. Statuses persist on the same network.
- **Leg record.** Raid by raid: status changes, home integrity, Heat band.

## Checks
- **`parity_check.gd` (headless):** every step of every golden leg line, plus all 200 random raids. Compare touches,
  status, Heat, bank, home integrity and score. Exit non-zero on any mismatch.
- **`flow_check.gd` (headless):**
  - play golden leg 0's planned line through the model;
  - play a naive line until it breaches (a seeded leg where `naive_leg` breaches);
  - the forecast for the revealed candidate with the chosen spoof equals the result;
  - the ledger reconciles.

## Captures
Write to `D:/rc_tmp/raid_design_lab/lab_l2/`:
- the full leg 0 on the planned line (`shots/`);
- a breach leg (`shots_breach/`);
- a scrambled set (`shots_scrambled/`).

Windowed runs only via `python tools/run_windowed.py --log <file> -- <args>`. Review your own captures. Fix overlaps
and clipped text, re-read every frame after fixes, and make sure each raid in a leg is actually played (not
auto-repeated).
