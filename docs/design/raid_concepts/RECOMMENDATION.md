# Raid design lab: recommendation (2026-10-22)

## The pick: MANHUNT, a sweep raid (rules M9c / M10)

**The loop:**
- **Contact is caused by your Heat.** When it crosses a threshold, Solace's front reaches the cell.
- **What you ran is what you must hide.** The assets you hauled this sector sit on your network.
- **The sweep.** Solace sweeps the network with three beams:
  - beam 1 is shown in full;
  - beam 2 is **sealed**: one of three candidate lines, told apart by shape and revealed during the playout;
  - beam 3 is a **hunter** that turns down the column of the first thing found.
- **You plan with scarce levers, each in its own currency:**
  - one GHOST (costs Heat);
  - one DECOY (costs Schematics; stops a beam);
  - GO DARK (costs the node's next income).
- **One SPOOF is held for after the reveal:** that beam skips one node.
- **Results.** Found assets go DOWN and stay down until repaired; the repair comes off the core key. Evading entirely
  pays a reward.

**Why it wins:**
- **It fits the premise better than defending a fortress.** The cell evades and hides; it doesn't build towers. Every
  critic who scored Fit rated it above the Bastion lab (6 against the lab's 4).
- **It is the only family where suspense rose with the rules.** M9c reached suspense 7 and depth 7 (R9 critic), and
  the critic named it the build pick. The H7 Bastion lab, played, got suspense 2.
- **The numbers back it** (MEASURE_R8.md):
  - the reveal changes the outcome on 53% of networks;
  - holding the spoof until after the reveal beats committing it on 60%;
  - "hide the biggest" is best on only 13% of networks;
  - decoys appear in 77% of near-best plans.
- **It sits where shipped games sit.** On the calibrated scale (REVIEW_CALIBRATION.md), acclaimed systems score 31–45.
  Watched raids like FTL, Kingdom Rush and TFT score 31–35 and are carried by suspense and visuals. Manhunt scores
  28–32 on the /50 with low-fi mockups. Its gap is in suspense (6, target 8) and visuals (3–5, target 7), which a
  playable build and real art address. More mockup rounds do not: critic noise is ±3, about the size of every change
  since R3.

**Runners-up:**
- **H7 Bastion.** A Godot lab exists (`tools/raid_lab_h7`, parity PASS). Predictability 9, but depth 4 and suspense
  2: an exact forecast plus undo makes it a solvable puzzle.
- **S9 Spinner** (the designer's ring siege). Best fit to the wheel verb. It needs pillar 4 amended, and its stakes
  measured flat. It could serve as the Heat-100 last stand at HQ.

## Rule changes: each a designer decision
1. **Raid shape.** The sweep replaces placement-plus-threat-routing as the raid. GDD 7.1–7.2 would be rewritten.
   - It stays inside pillar 4 ("deterministic graph auto-battles with a planning phase") if beams run along the
     network's links (see the migration).
2. **The spoof.** A choice after the reveal (pick the node the beam skips) is the lab's default and stays inside
   pillar 4. A timed press is the alternative and needs pillar 4 amended.
3. **The sealed beam.** Hidden information during the raid playout. GDD 7.1 promises an "exact projected outcome";
   it becomes an exact outcome per candidate line, plus the range.
4. **Scarce levers with separate currencies.**
   - Ghost: +5 Heat.
   - Decoy: 3 Schematics.
   - Go dark: the node's next income.
   - The new costs go in `campaign_config.tres`.
5. **DOWN persists until repaired.** The repair is the asset's value, against GDD 3.3's 50% of install cost. The lab
   has both behind a toggle.
6. **The key.** The repair comes off the run's progress toward the corp core. GDD 1.3 says you win with Exploits, so
   either the key is counted in Exploits or repairs cost Schematics.
7. **Evading pays a reward and lowers Heat (−10).** This contradicts D27 (a clean defense gains Heat).
8. **The verdict stays D28** (CELL HOLDS / BREACHED). BREACHED happens when the sweep finds the home server and
   empties its integrity.
9. **Survivor ids become unique** (Bastion only). The H7 lab found that duplicate survivor ids collapse two survivors
   into one fighter.

10. **A decoy-only contact counts as EVADED** (found by the M10 lab). A sweep that touches only a decoy pays the evade
    reward, and the decoy's cost still stands.
11. **The spoof acts on beam 2 only, after the reveal.** The rules allow it on any beam; the lab applies it to beam 2.
12. **A key at 0.** The key cannot go below 0, and a loss beyond it is shown as UNPAID. What an unpaid loss means is
    open: it could carry over, or count toward a breach.
13. **Numbers invented in the M10 lab** (all in `tools/raid_lab_m10/m10_config.gd`):
    - between raids, a run adds +12 Heat and +12 key, less dark income;
    - the evade reward's Heat −10 is applied on top of the ghost's +5;
    - press timing: the window is ±0.22 s.

## Migration sketch (after the designer rules; nothing here is built)
- **Data (`scripts/data`, `content/raids`, `content/threats`).** A corp's raid content becomes **sweep patterns**:
  - beam count;
  - the hunter rule;
  - the sealed-candidate count by Heat band.
  These are a new `SweepPatternData` schema (a minimal schema change, logged in DECISIONS, checked in
  `schema_smoke_checks.gd`). Threat resources stay as the beams' identity and art (cobalt silhouettes).
- **Core (`scripts/core`).** A pure `SweepResolver` (RefCounted, `RngService` stream for the corp's reveal pick)
  replaces `RaidResolver`'s movement and fire loop.
  - **Beams on the graph.** A beam is an ordered path of claimed nodes along links from a corp Site, so the abstract
    4 × 3 grid becomes the real network.
  - **The hunter** follows links from its first find.
  - **Kept:** `RaidOutcome` and D28 verdicts.
  - **Tests:** the preview must equal the real result for every candidate; seeded replays; tie-breaks by content id,
    then node id.
- **State (`scripts/state`).** Hidden and dark flags per node for the raid. DOWN already persists. A spoof token.
  Heat and Schematics charges at placement.
- **UI.**
  - The Raid Setup screen becomes the sweep plan: forecast marks on the network map, the key-bar bracket, the lever
    tray.
  - The playout reuses `RaidBeats` step-locking (D26): beam 1, unseal, spoof decision, beam 2, hunter.
  - The look goes to art-pass (RDL-001).
- **Save.** A save version bump for the per-raid hidden and dark flags and the spoof token.
- **Config.** All lever costs, the evade reward and the candidate counts in `campaign_config.tres`.
- **Order.**
  1. Designer rulings.
  2. A playable lab with real data on the City Grid network (`tools/raid_lab_m10`, being built now).
  3. A critic on the lab in motion.
  4. Schema, resolver and tests.
  5. UI.
  6. Art.

## Open risks
- **It is small.** It is a 6-asset, 3-line puzzle with one reaction. Depth may need corp-specific sweep patterns (two
  beams that interact, a reroute on decoys) to hold up over a campaign.
- **Suspense rests on one reveal per raid.** If the lab in motion still reads as flat, add a second decision point:
  the hunter's column chosen after beam 2 resolves (R10 critic).
- **Scarcity is the precondition** for both the reveal and the spoof mattering. Generous levers halve every effect
  (measured).
