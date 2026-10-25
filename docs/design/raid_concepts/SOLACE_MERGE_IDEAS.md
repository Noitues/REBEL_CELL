# Solace × raid grid: merge ideas

Status: design document for the designer. Nothing is built; GDD.md, DECISIONS.md, scripts/ and content/ are unchanged.
Author: lead-design pass (Opus), 2026-10-25, branch `claude/raid-design-lab-2d2e2e` at e5ead05b (main db350783).
Brief: `docs/handoff/raid_integration/BRIEF_SOLACE.md`. Companion to `INTEGRATION_PLAN.md` (the port plan); this document
answers its biggest risk (R-4, the star grid) and its Q14 (the infection in a sweep).

One measurement was run for this document: a topology probe of the Solace grid,
`D:/rc_tmp/raid_design_lab/integration/solace_geom.py` (and `solace_geom2.py` for moved Exploits). It grows territory
one claim at a time (2,000 campaigns per row) under two crude claim policies and reports what a raid board would see.
It has no rules in it; it only tests the geometry. Its numbers are cited as *(probe)*.

---

## 1. How Solace works today

**The grid** (`content/corporations/solace.tres`, embedded `city_grid`, 32 Sites). It is a star in topology, but its
`map_position`s already lay it out like the lab board turned sideways: HOME at x 0, T1 at x 200, T2 at 430, T3 at 660, the
Genome Core at 900. Ten rows (spokes), three tier columns. `:` marks a `locked_links` pair to the row below.

```
          T1 (x200)        T2 (x430)                T3 (x660)          T4 (x900)
          t1_a ---------- t2_intel [INTEL] ------- t3_core -----+
  +-------  :  \-scrub_records(T1,-5)  :              :           |
  |       t1_b ---------- t2_breach [BREACH] ----- t3_b --------+
  |         :                                                    |
  |       t1_c ---------- t2_virus [VIRUS] ------- t3_c --------+
  |                          :                                   |
HOME ---- t1_d ---------- t2_d ------------------- t3_d --------+---- THE GENOME CORE
(0,330)     :                                         :           |     (boss, HQ ladder)
  |       t1_e ---------- t2_e ------------------- t3_e --------+
  |                          \-burn_the_ledger(T3,-8)            |
  |       t1_f ---------- t2_f ------------------- t3_f --------+
  |         :                :                                   |
  |       t1_g ---------- t2_g ------------------- t3_g --------+
  |                                                   :           |
  |       t1_h ---------- t2_h ------------------- t3_h --------+
  |         :
  +------ t1_i ---------- purge_camera_logs (T1, -5)
          t1_j ---------- wipe_biometrics (T2, -8)
```

- HOME links all ten T1 Sites. Eight spokes are full chains T1 → T2 → T3 → core; `t1_i` and `t1_j` end in Heat objectives.
- Locked cross-links (11): T1 a–b, b–c, d–e, f–g, h–i; T2 intel–breach, virus–d, f–g; T3 core–b, d–e, g–h. The Intel
  Exploit opens them (`ExploitData.opens_locked_links`). GDD 4.1: opened links are raid routes too.
- The three Exploits sit on adjacent spokes a, b, c (T2). A netrun can target any corporate Site that touches the
  territory (`CampaignRules.launchable_sites`; the core only with `min_exploits_for_breach` 3).

**The Bloom in a netrun** (`scripts/core/bloom_rules.gd`, `scripts/state/bloom_state.gd`, `NetrunSession.bloom_*`). A
virus front trails the operative in thousandths of a layer. Start gap by tier T1–T4: 4000 / 3500 / 3000 / 2500 (HQ 3000).
Front advance per node entry by tier: 500 / 600 / 650 / 700 (HQ 700); per fight turn 100, paid at fight end by every
fight class (S3); HQ ACROSS +500. Heat band multiplier (S2) 100 / 110 / 125 / 140 / 160 %. Keys (S6): Virus pace × 75 %,
Intel turn cost × 50 %, Breach a one-time −1000 setback and a free ACROSS. Bands by gap: CREEPING > 2000, CLOSE ≤ 2000,
CATCHING ≤ 1000, CAUGHT ≤ 0 (the operative dies through the normal death path, Q24.1). **Doses:** bought at a Mainframe
for 15 Cycles (`bloom_dose_price`), held, used any time outside combat: push the front back 1000, gap clamped to 5000.
Ward rests (HQ rungs 5 and 8, the culture garden's I1 rest) push for free or use a held dose. Doses are run-scoped: an
unused dose is lost at run end.

**The infection timer** (`scripts/core/solace_raid_rules.gd`, `SolaceCampaignTheme.infection_bp`; DECISIONS 2026-10-19
WH-12 and Solace v2 S1). One campaign figure in basis points, 0–10000. It moves **only inside raids**: each resolution step
adds `raid_infection_bp_base` 50 + `raid_infection_bp_per_threat` 100 × living threats; at 10000 the raid ends **CITY
LOST** (campaign lost). It falls on a raid that CELL HOLDS with no TAKEN node (−1000, −100 per threat destroyed), on a
Heat objective Site completion (−1500), and on every completed netrun for each active Proxy Relay (−1500, through the
node passive). A 10-step raid with three living threats adds 35 %. There are no steps in a sweep, so this rule has no
home in the lab model (INTEGRATION_PLAN Q14).

**Raids** (`raid_resolver.gd`, the step auto-battle of GDD 7.2). Solace has eight triggers (`raid_heat_25/50/75`,
`raid_purge`, `raid_claim`, `raid_retaliation`, `raid_story`, `raid_node_built`), each firing once (GDD 4.3–4.4). HOME
integrity 50. Heat is inverted (D27, 2026-10-22): a clean defense gains +5 Heat and pays Schematics; any damage gains
nothing. Verdict CELL HOLDS / BREACHED (D28). Heat sources after SOLACE_BAL_r2: Exploit +5, Racks +2/3/5/8, death 10 + tier;
sinks: four one-shot objective Sites (−5, −5, −8, −8), Proxy Relay −1 per run, purchase −7 for 25 (+5 each).

**Win and loss.** Win: breach the Genome Core with 3 Exploits. The breach is the HQ ladder (`solace_hq_graph.gd`): Clinic
Gate, 9 rungs on two towers (WARD, BILLING; ACROSS costs 500), ward rests at rungs 5 and 8, the Account Manager at rung 9,
the crown fights the Genome Core (400 HP), with the HQ Bloom. Loss: HOME integrity 0 (BREACHED), CITY LOST, or abandon.
Measured pace (SOLACE_BAL_r1/r2): the reference policy takes 24–60 runs (mean 45 before r2) against GDD 11.8's 24, with
3–7 raids; the Bloom kills 0–2 operatives per campaign, so it does not set the length.

**What the probe says about this grid** *(probe; 8 claims, the middle of a campaign)*:

| Claim policy | Spokes holding Sites | Value inside the plan's 3 candidate spokes | A real cross-link joins 2 owned candidate Sites |
|---|---|---|---|
| random adjacent claims | 5.7 | 70 % | 52 % |
| keys first (Exploits on a, b, c, as today) | 3.0 | 100 % | 100 % |
| keys first, Exploits moved to spokes b, e, h | 3.0 | 100 % | **0 %** |

Two findings drive the concepts below. First, **the north wedge (spokes a, b, c) is already almost the lab board**: three
routes, three tier columns, cross-links a–b at all three tiers and b–c at T1. A player who rushes keys plays on it. Second,
**a player who does not rush keys spreads over 5–7 spokes**, the plan's three candidate spokes then hold only 64–74 % of
what they own, and half the time no real street joins them. Where the Exploits sit decides the raid board.

---

## 2. Four merge concepts

Shared assumptions (from INTEGRATION_PLAN, not repeated per concept): the L14 sweep (typed beams, sealed A and B, the
hunter, a hand of ≤ 2 sentries plus ghost, one RESPONSE, an exact 3 × 2 × 2 forecast), the defense deck (the Armory as
cards), wounds as curse cards injected at jack-in, DECAY (DOWN → TAKEN at the next raid), all randomness drawn from the
`raids` stream when the raid is queued, every number in `campaign_config.tres`. "BASE" below means the plan's Phases
1–4. Lab baselines are from `D:/rc_tmp/raid_design_lab/sweep_l14.json`: greedy `response_decides` 0.53 (so about 47 % of
raids are LOCKED at PLAN), greedy breach 0 %, naive breach 100 %, greedy wounds 0.45 per leg.

### Concept A: CONTAGION SWEEP (the plan as written, infection counted per hit)

**The infection timer.** The campaign figure (S1) stays, but it is fed by sweep events instead of steps:
`raid_infection_hit_bp` per HIT on an owned Site (800), per HOME hit (1500), per Site turned TAKEN (500 more). The decays
stay: EVADED −1000 (the old "CELL HOLDS" decay), Heat objective −1500, Proxy Relay −1500 per run. CITY LOST at 10000. The
cadence is unchanged: Heat thresholds and the other GDD 4.4 triggers, plus the plan's pressure trigger (a raid every 3
runs when none fired). Heat bands add a beam and a card at 50 and 75 (lab R13). Doses stay inside netruns.

**The grid.** No content change. Per raid, `SweepGeometry` picks the 3 spokes with the most live value as routes and builds
streets from cross-links (locked ones included, Q3) plus "tier rings" drawn across the three chosen spokes.

```
 HQ beams from the Genome Core, right to left; rows are the 3 chosen spokes this raid
            T1        T2        T3
 route 1  [t1_b]----[t2_br]---[t3_b ]----< core
             |         |         |          <- streets: cross-links if they exist,
 route 2  [t1_e]----[t2_e ]---[t3_e ]----<     otherwise a ring drawn by rule
             |         |         |
 route 3  [t1_h]----[ .  ]----[ .  ]----<
   ^ HOME
```

**One raid.** Heat 52 (2 beams, hand 5). DECAY: `t2_e` was DOWN, goes TAKEN, +1 wound, +500 infection. Draw 5 (one is the
wound). Place an N sentry on `t1_b`, a D sentry on `t1_e`; read the 12-row forecast (each row now also shows the infection
delta, e.g. "+16 %"). Launch; REVEAL A on route 3; REDEPLOY the SHIFT card to `t1_h`; REVEAL B route 1 (blocked); the
hunter runs the T1 ring and hits `t1_h`'s neighbor. Aftermath: 1 HIT, infection +8 %, HOME untouched, CELL HOLDS.

**One campaign arc.** Infection starts at 0. A typical damaged raid adds 8–25 %; an EVADED raid removes 10 %; the four
Heat objectives and a Proxy Relay remove 15 % each. Five bad raids in a row lose the city before HOME falls.

**Keeps / fixes.** Keeps everything the plan keeps (forecast, persistence chain, deck tie-in). Fixes nothing in the caps by
itself: raids still lock at PLAN, and the infection delta is a second readout of the same hits, so responses still differ
by one axis (severity). R15–R17 wait for Phase 7.

**Changes.** `scripts/core/solace_raid_rules.gd` (event-based rise, ~80 lines changed), `SweepRules.forecast` rows carry the
delta, three config fields in `scripts/data/campaign_config_data.gd` (the two step fields retire for sweep corps), tests
`test_solace_raid_rules.gd` and the plan's `test_sweep_preview.gd` (infection preview == result). **Size: BASE + about 1
agent day.**

**Risks and measurement.** (1) The star geometry (probe: 52 % real streets for a spread player; rings drawn by rule look
like beams jumping across the city). (2) Infection is a second HOME bar with no identity: both losses come from the same
hits. *Measure:* the Phase 1 graph oracle (`sweep_g1.py`) over 200 Solace snapshots with an infection counter. *Gate:*
the plan's Phase 1 gates, plus greedy CITY LOST ≤ 5 % and naive 30–70 % over 7-raid campaigns, plus "the best response by
tier differs from the best by infection" in ≥ 15 % of raids (otherwise the figure adds no decision).

### Concept B: THREE WARDS (the city regrouped into three routes; one infection meter per ward)

**The grid.** The ten spokes are regrouped into three **wards**, which are the lab's three routes, and the tier columns are
the lab's columns. A board cell is a **block**: the Sites of one ward at one tier.

```
 Corp beams leave the Genome Core and run a ward right to left. Streets are the tier columns.
                    T1 block             T2 block                T3 block
 NORTH ward  [t1_a t1_b t1_c]  [t2_intel* t2_b t2_c]      [t3_core t3_b t3_c]   <--+
 (a b c)          |   +scrub        |                          |                    |
                  |  (c-d new)      |  (virus-d exists)        |  (t3_c-t3_d new)    |
 MID ward    [t1_d t1_e t1_f t1_g] [t2_d t2_e* t2_f t2_g]  [t3_d t3_e t3_f t3_g] <--+-- THE GENOME CORE
 (d e f g)        |                 |   +burn_the_ledger      |                    |
                  |  (g-h new)      |  (t2_g-t2_h new)        |  (g-h exists)       |
 SOUTH ward  [t1_h t1_i t1_j]  [t2_h* wipe_biometrics]    [t3_h]               <--+
 (h i j)          +purge_camera_logs
   ^ HOME                                     * = the ward's Exploit (one per ward, moved)
```

- **Content:** the Exploits move so that each ward holds one: Intel stays on `t2_intel`, Breach moves to `t2_e`, Virus
  to `t2_h` (ids renamed, `t2_breach` → `t2_b`, `t2_virus` → `t2_c`). Four locked links are added on the ward borders
  (c–d T1, t3_c–t3_d, g–h T1, t2_g–t2_h), so every tier column is a connected street.
- **Why move the keys:** *(probe)* with the keys on a, b, c a key-rushing player owns one ward only (the board collapses to
  one route). With the keys on b, e, h the same player owns all three wards and 7.35 of 9 blocks at 8 claims, with 1.09
  Sites per block: almost exactly the lab's one-district-per-cell shape. A random-claim player owns 2.85 wards and 4.6
  blocks at 8 claims, so the board is never empty.
- **Hits on a block:** a beam that reaches a block HITs its most valuable live owned Site (ties by Site id). That is GDD
  3.2's "raids prioritise the Vault" made into the targeting rule. A sentry on any Site of a block guards the block.

**The infection timer.** Three meters, one per ward (0–100 %), which are the S1 figure split by place.
- **Rise:** +2 % per completed netrun in every ward (the clock: "the longer you delay, the more die"); +8 % per HIT in the
  ward; +15 % to the ward a HOME hit came through.
- **Fall:** a Heat objective Site cures **its own ward** by 15 %; a Proxy Relay cures its ward by 5 % per run; an EVADED
  raid cures every ward by 5 %.
- **A ward at 100 % falls.** Every Site in it goes TAKEN (one wound each), and it becomes a corp ward: its beams enter
  the next raid one column deeper. **CITY LOST** when two wards have fallen (`wards_lost_for_city` 2).
- **Doses become QUARANTINE.** New defense card verb DOSE (two in the start deck; an unused netrun dose banks one at run
  completion). RESPONSE gains QUARANTINE w (spend a DOSE card): ward w's meter does not rise this raid and its Sites cannot
  go TAKEN (they stop at DOWN). It is the lab's SACRIFICE turned inside out: you protect a place, not HOME.
- **Cadence:** unchanged GDD 4.4 triggers, plus one raid the first time any ward crosses 50 %.

**One raid.** Meters N 30 %, MID 55 %, S 10 %. Heat 52, hand 5 (one DOSE, one SHIFT, one wound). Plan: a D sentry on the MID
T2 block (`t2_e` holds Breach), an N sentry on the NORTH T1 block. The forecast now shows, per row, the tier and the three
meter changes. REVEAL A: SOUTH. The table says HOLD costs SOUTH +16 % and one DOWN; QUARANTINE SOUTH costs the DOSE and
nothing else; REDEPLOY saves the Site but leaves MID open if B is MID. The player keeps the DOSE and REDEPLOYs. REVEAL B:
MID, blocked. The hunter takes the T1 column and hits `t1_h`. Aftermath: SOUTH +8 %, everything else unchanged.

**One campaign arc.** The player rushes Intel (NORTH) first; SOUTH, untouched, creeps +2 % per run. At run 10, SOUTH is
at 35 % and the Virus key is there, so the player must go south. The Heat objective Sites become ward medicine
(`purge_camera_logs` and `wipe_biometrics` both cure SOUTH), so "which Heat Site" is now a spatial choice. A neglected ward
falls around run 25–30 and then pushes beams deeper into the others: losing a ward is survivable; losing two is CITY LOST.

**Keeps / fixes.** Keeps the forecast (exact; the meters are deterministic), the persistence chain (DECAY → wound → dead
draw, plus a ward's fall), the deck tie-in (DOSE cards from netrun doses). **Fixes R16** (responses differ only in tier):
each response moves a different ward's meter, so a 3-tier menu no longer collapses to one row. **Partly fixes R15:**
QUARANTINE is chosen after A with B unknown and makes a ward safe whatever B is. It does not add a tool after B.

**Changes.**
- Content: `content/corporations/solace.tres` (Exploit fields on three Sites, 2 renames, +4 `locked_links`), the
  culture garden's KeyLot follows the Virus Site (`exploit_building_for`, `exploit_building_reach_lots`), five tests that
  name `t2_breach` / `t2_virus` (12 files mention the ids). A DOSE defense card.
- Schema (rule 8): `SiteData.ward: int` (−1 = none), smoke-checked; the alternative is a config table by Site id.
- Core: `scripts/core/ward_rules.gd` (new, about 250 lines: blocks, meters, fall, cures); `SweepGeometry` ward mode (about
  150 lines); `SolaceCampaignTheme.ward_bp: PackedInt32Array` replacing `infection_bp`; `CampaignRules._infection_cure_events`
  made per ward.
- **Size: BASE + about 4 agent days**, plus an art-pass check of the moved Exploit buildings.

**Risks and measurement.** (1) Blocks with 3–4 Sites may read as "a district" in the city but as "a list" on the board.
(2) Three meters plus HOME plus Heat is a lot to read (W axis). (3) Moving the Exploits touches the story beats' order
(beats reveal in Exploit order; text unchanged) and the KeyLots. *Measure:* `sweep_g1.py` with ward geometry on the
Phase 1 snapshots, re-exported with the moved keys. *Gate:* the plan's Phase 1 gates; overlap is 100 % by construction;
`ward_split` (the best response changes with which ward a row protects) ≥ 35 %; greedy wards fallen ≤ 0.2 per campaign,
naive ≥ 1.

### Concept C: BLOOM TIDE (the netrun's Bloom, scaled up to the city, is the campaign clock)

This is the designer's original Solace sentence (DECISIONS 2026-10-18) taken literally: "the longer the player delays, the
more die; if the player is too slow the city is infected." The timer runs on the campaign's time (netruns), not inside
raids. **New system, flagged:** a campaign-scope front. It reuses `BloomRules`' arithmetic and band names, but the state
and the map view are new.

**The infection timer.** A second `BloomState`-shaped record on the campaign, `SolaceCampaignTheme.tide` (milli-columns).
- **The front starts at the Genome Core** (column 4000) and moves toward HOME (column 0). Column = tier ring: T3 = 3000,
  T2 = 2000, T1 = 1000. The HUD figure "INFECTION n %" = (4000 − front) / 40, so the S1 percentage survives as a word.
- **Pace per netrun** (completed, failed or patrol), by the Site's tier: T1 100, T2 130, T3 160; the breach run 0. Death
  adds 150. Multiplied by the Heat band (`bloom_pace_heat_pct_by_band`, the S2 table as is) and by the Virus key (75 %).
  The Breach key pushes the tide back 500 once, when taken. Intel shows the exact run count to the next column.
- **Doses** push it back (`tide_dose_push_milli`): a Heat objective Site 300 (replaces the −15 %), a Proxy Relay 50 per run,
  an EVADED raid 200 (replaces the CELL HOLDS decay), the HQ verb DOSE (12 Schematics, +4 each), and **every netrun dose
  still unused when a run completes pushes 100.** That last rule ties the two Blooms: Cycles spent on doses either save
  the operative or slow the city.
- **Bands** reuse the netrun names by the front's distance to HOME: DORMANT ≥ 3000, CREEPING, CLOSE ≤ 2000, CATCHING ≤
  1000, **CAUGHT at 0 = CITY LOST.** It is the same rule as the street: the Bloom reached you.
- **What the front does to the grid:** an owned Site the front reaches goes DOWN ("infected"; no passive), and normal
  DECAY makes it TAKEN at the following raid unless it is repaired or a dose pushes the front back past it (then it is OK
  again). A netrun launched at a Site behind the front starts its street Bloom 1000 closer: the city's infection is where
  the building's infection starts.
- **Cadence:** the first time the front crosses each whole column (3000, 2000, 1000) a **Tide raid** queues, on top of the
  GDD 4.4 triggers. That is 3 raids paced by time, which answers the plan's R-1 (raids too rare against 24–45 runs)
  without an invented "every 3 runs" trigger.

**The grid.** Tiers as columns becomes a rule, not a picture: the front is a vertical line across the city.

```
          T1 col (1000)   T2 col (2000)   T3 col (3000)     core (4000)
 route 1   [ OK ]--------[ OK ]------//[ DN ]------------<
 route 2   [ OK ]--------[ OK ]------//[    ]------------<   beams start AT the front, not at the HQ
 route 3   [    ]--------[ OK ]------//[ DN ]------------<
   ^HOME                             //
                              front 2650 (INFECTION 34 %, CREEPING)
                              tongue candidates: the T2 column, the T1 column
```

- Rows are the three wards of Concept B (recommended) or the plan's three chosen spokes. The beams start at the front, so
  they get shorter and hit fewer columns as the tide is pushed back, and longer as it advances.
- **The hunter becomes the Tongue:** its two sealed candidate streets are the first two columns inward of the front. No
  content link is needed for a street: the front is continuous by rule, so the R-4 overlap risk is gone.

**One raid.** Front 2950 (just crossed 3000: a Tide raid). Heat 52, hand 5. DECAY turns last raid's DOWN `t1_e` TAKEN
(+1 wound). The T3 Site `t3_b`, reached by the front, is DOWN. Plan: two sentries; the forecast table is the usual 12 rows.
REVEAL A, RESPONSE (HOLD), REVEAL B. **New late slot (R15): FIELD DOSE**, after REVEAL B and before the Tongue's reveal,
for one held dose: the front goes back 150 (half an HQ dose), so the Tongue's candidates shift one column outward (T2 and
T3 instead of T1 and T2) and the T1 column, where the player holds three Sites, is out of its reach. The player can spend
the dose now (protect this raid) or keep it for the HQ (300 of tide later). Aftermath: the dose is spent, the Tongue hits
`t2_d`, front 2800.

**One campaign arc.** Fast path (8 runs: 3 × T1, 3 × T2, T3, breach) at Heat ~110–125 %: about 1000 of tide, front ≈ 3000
at the breach, INFECTION ≈ 25 %, one Tide raid. Average campaign (24 runs): about 3500 of pace minus ~1400 of doses
(four objective Sites, a Proxy, two EVADED raids, a few banked netrun doses) → front ≈ 1900 at the breach, CLOSE,
INFECTION ≈ 50 %, three Tide raids; the T3 and T2 Sites taken early are under the tide and must be held with doses or
let go. The old reference campaign (45 runs, mostly farming spent Heat Sites) would reach CAUGHT: being too slow is
punished by the city, which is the designer's sentence. The breach run itself is the Genome Core ladder with its HQ Bloom;
nothing there changes.

**Keeps / fixes.** Keeps the exact forecast (the front's position is known; its pace per run is a preview the GRID band
can print: "next run at T2: +162, 3 runs to the T2 column"), the persistence chain (front → DOWN → DECAY → wound → dead
draw; it adds one link at the start), the deck tie-in (field doses, banked netrun doses, curses). **Fixes R15:** the field
dose is a live decision after REVEAL B. **Fixes R16:** a response now trades on time (tide), not only tier. **Fixes R-1
and R-4** (cadence, overlap). The look exists: Bloom A Necrosis is approved and ported for the street and the HQ
(DECISIONS 2026-10-22); the city GRID band needs it as a fourth skin (art-pass owns it).

**Changes.**
- State: `scripts/state/solace_campaign_theme.gd` gains `tide_front_milli`, `tide_columns_crossed`; `infection_bp`
  retires (save version bump; compatibility is not required).
- Core: `scripts/core/tide_rules.gd` (new, about 200 lines: pace, push, bands, crossing → raid queue, infected Sites),
  called from `CampaignRules.on_run_completed` and the death path; `solace_raid_rules.gd` reduced to the HUD figure;
  `NetrunSession` start gap reads the tide (`BloomRules.begin` gains a `start_cut` argument); the field-dose response in
  `SweepRules` (about 120 lines); the Tongue's street rule in `SweepGeometry` (about 60 lines).
- Config: `tide_start_milli`, `tide_pace_milli_by_tier`, `tide_death_milli`, `tide_dose_push_milli`,
  `tide_field_dose_push_milli`, `tide_netrun_dose_milli`, `tide_proxy_milli`, `tide_evaded_milli`, `tide_dose_price`
  (+ increment), `tide_behind_front_gap_cut_milli`, `tide_raid_columns`.
- Content: none required (Concept B's key move is optional here). A `raid_tide.tres` trigger resource.
- View: the front on the GRID / RAID bands of `CityView3D` (art-pass, through `BloomLook`'s pattern), an INFECTION chip.
- Tests: `test_tide_rules.gd` (pace, push, clamp, crossing fires once, CAUGHT = CITY LOST), `test_tide_preview.gd` (the GRID
  band's run preview == the applied pace), the plan's sweep tests with the late slot.
- **Size: BASE + about 5 agent days**, plus the art-pass skin. The timer part (not the sweep part) can be built and
  measured **on today's step raids before the port**, because it lives on campaign time.

**Risks and measurement.** (1) Two clocks (Heat and the tide) with the same multiplier could feel like one punishment
twice. (2) A front that infects owned Sites may feel unfair if it is not forecast on the GRID band before every launch.
(3) Pacing: the 8-run path must stay safe and the 45-run crawl must fail. *Measure (cheap, no oracle):* replay the
reference policy's run logs (`balance.py --trace` `run_end` lines: tier, Heat, death) through a 60-line Python tide model.
*Gate:* reference policy median INFECTION at breach 35–65 %, CITY LOST ≤ 10 %; the fast seeds ≤ 30 %; 2–3 Tide raids per
average campaign. *Measure (oracle):* `sweep_g1.py` with the Tongue and the field dose. *Gate:* greedy breach 0 %; greedy
`response_decides` + late-slot decides ≥ 0.63 (lab 0.53 + 10 points); field dose used in 25–60 % of raids (not always,
not never).

### Concept D: CARRIER DECK (the infection lives in the cards; the board is rebuilt as the lab lattice)

**The grid.** The Solace grid is rebuilt so the raid board **is** the lab board: three districts per route, one board
Site per district (an **anchor**), and the rest of the GDD 4.1 Site count hangs off the anchors as **annexes**.

```
                  T1 district             T2 district              T3 district
 INTEL route   (A1)=annex,annex ------ (A2*)=annex,annex ------ (A3)=annex,annex ---<
                 |                       |                         |
 BREACH route  (B1)=annex,annex ------ (B2*)=annex,annex ------ (B3)=annex,annex ---<-- THE GENOME CORE
                 |                       |                         |
 VIRUS route   (C1)=annex,annex ------ (C2*)=annex,annex ------ (C3)=annex,annex ---<
   ^ HOME      9 anchors (the board) + 18 annexes + 4 Heat objectives + HOME + core = 33 Sites
```

- Anchors are the 3 × 3 lattice with every street link (no locked streets for the corp). Annexes (Vault, Safehouse,
  Proxy slots) are off the board: they can only be lost when their anchor goes TAKEN. Lab x = 3 (the approach column) is
  dropped; the oracle runs with W = 3.
- The lab's calibration transfers one to one (one Site per cell, three routes, full streets).

**The infection timer.** The infection is the defense deck. **New system, flagged:** spreading cards.
- Every TAKEN adds an INFECTED card (the plan's wound, Solace-named). At each raid's DECAY, if the deck holds any
  INFECTED card, one more is added (the Bloom grows) unless a DOSE card is spent at that moment.
- INFECTED cards in the run deck are curses (the Bug pattern) with one Solace line: drawing one advances the street Bloom
  by 200. A Mainframe removal in a netrun clears it from the campaign too.
- **CITY LOST** when INFECTED cards ≥ the healthy cards in the defense deck (the city is more sick than not).
- **DOSE cards**: bought in netruns (the 15-Cycle dose), banked at run completion if unused; a Heat objective Site gives
  one. In a raid a DOSE is a response after REVEAL B (CURE: remove one INFECTED card and stop this raid's spread) or is
  spent at DECAY.
- Cadence: unchanged GDD 4.4 triggers plus the plan's pressure trigger.

**One raid.** Deck 10 healthy + 3 INFECTED + 1 DOSE. DECAY: spread, or spend the DOSE? The player keeps it. Draw 5: two
INFECTED (dead). Plan with three live cards: two sentries; the forecast shows each row's "+n INFECTED". REVEAL A, REDEPLOY;
REVEAL B; late slot: CURE with the DOSE (−1 INFECTED) or HOLD the DOSE for the next DECAY. Aftermath: one TAKEN → +1
INFECTED; 4 INFECTED against 10 healthy.

**One campaign arc.** The first TAKEN (raid 2) starts the spread: +1 per raid from then on. Players buy doses in netruns
for the city, not the operative, and clean INFECTED cards at Mainframes. A careless player hits CITY LOST around raid 6–7;
a careful one ends with 1–3 INFECTED.

**Keeps / fixes.** Keeps the forecast, the chain (it becomes exponential-flavored but deterministic), and has the strongest
deck tie-in of the four (Fit). **Fixes R17** (richer cards: DOSE, CURE, INFECTED with a street effect) and **R15** (CURE
after B). It fixes the geometry by construction.

**Changes.** Content: rewrite the `city_grid` of `content/corporations/solace.tres` (33 Sites; about 400 of its 707
lines regenerated by a tool), story/KeyLot placements, every test and tool that names Solace Site ids (12 files), the
city layout's territory mapping (CITY_A2 Solace district, art-pass). Schema: `SiteData.annex_of: StringName`. Core:
spread rule in `SweepRules` DECAY (about 80 lines), CITY LOST by deck ratio, the CURE response, the INFECTED draw hook in
`NetrunSession` (about 40 lines), anchor/annex loss in `SweepResolver.apply`. **Size: BASE + about 7 agent days**, the
most of the four, and the only one that changes the art's map.

**Risks and measurement.** (1) The content rewrite fights the approved Solace district layout (A-069/A-070) and GDD 4.1's
"each T1 opens exactly one T2". (2) Spread is a snowball; a player behind may be unable to recover. (3) Dead draws hurt
twice (raid hand and run deck; plan R-11). *Measure:* `sweep_l8.py` with W = 3, 7-raid legs, the spread and DOSE cards.
*Gate:* greedy CITY LOST ≤ 5 %, naive ≥ 40 %; greedy `dead_draws` ≤ 1.0 per hand; DOSE used in 30–70 % of raids;
greedy INFECTED at campaign end 1–3.

---

## 3. Comparison against the vision

Critic axes are estimates against the lab's best (L15: W 8, P 9, N 6, D 7, C 9 = 39; S 5; Fit 8), not measurements.

| | A Contagion Sweep | B Three Wards | C Bloom Tide | D Carrier Deck |
|---|---|---|---|---|
| **Seamless city** | Rows change every raid; rings drawn by rule cross the city | Wards are real city areas; one stable board | The front is a line on the city at every zoom; the same Necrosis skin at room, building and city scale | Strong board, but the map is rebuilt against the approved district |
| **Netruns as captures** | Unchanged | Unchanged; Heat Sites become ward medicine | Unchanged; plus the city sets the building's Bloom start, and unused doses slow the city | Unchanged; annexes are captures the board does not show |
| **The corp hacks back** | Raids only | Raids + a creeping per-ward clock | Raids + a visible tide between raids; Tide raids paced by time | Raids + a spreading deck |
| **Infection identity** | Weak (a second HOME bar) | Medium (meters by place) | **Strongest** (the same Bloom, the designer's "too slow → city lost") | Strong (infected cards) |
| **Fixes R15 / R16 / R17** | – / – / – | partly / yes / – | yes / yes / partly | yes / partly / yes |
| **Board risk (R-4)** | High (probe: 52 % real streets) | Low (100 % by construction, keys moved) | Low (the Tongue needs no link) | None (lattice) |
| **Build cost** | BASE + 1 day | BASE + 4 days + content move | BASE + 5 days + art skin (timer first, no port needed) | BASE + 7 days + content rewrite + art |
| **Expected critic** | 37–39 (S 5, Fit 8) | 39–41 (D +1, W −1, S 6) | 40–43 (D +1, C +1, S 6–7, Fit 8–9) | 39–42 (D +1, Fit 9, W −1) |

---

## 4. Recommendation

**Build Concept C (BLOOM TIDE) on Concept B's board (the three wards with one Exploit each), without B's per-ward
meters. Skip A; keep D's DOSE and CURE cards as the Phase 7 R17 candidate.**

Why:
1. **It is the designer's own Solace sentence.** The 2026-10-18 ruling describes a timer driven by delay; today's rule
   moves only inside raid steps, which the sweep removes. The tide restores the intent and S1's "may diminish to zero"
   (doses push it back).
2. **One Bloom at three scales.** The room (CAUGHT kills the operative), the building (the street front), the city (the
   tide). The Necrosis look is approved and already ported twice; the rules reuse `BloomRules`' arithmetic and the S2 / S6
   rulings unchanged. That is the cheapest way to an identity no other corp has.
3. **It answers the plan's two worst risks** with rules that are themed instead of invented: R-1 (raids too rare) through
   Tide raids, R-4 (no overlap on the star) through the Tongue running along the front. The wards (keys moved to b, e, h)
   make the board stable and lab-shaped *(probe: 7.35 of 9 blocks, 1.09 Sites per block at 8 claims for a key-rusher)*.
4. **It is the only concept with a live decision after REVEAL B** that trades on an axis the tier hides (the field dose
   spends campaign time to save this raid). That targets S (5) and D (7), the two axes the critics say are rules-limited.
5. **It can start before the sweep port.** The tide lives on campaign time, so it can replace the step infection on today's
   raids, be paced with the reference policy's logs, and then gain the Tongue and field dose when the sweep lands.

B's per-ward meters are dropped because three meters plus HOME, Heat and the tide would cost W. D's lattice rewrite is not
worth fighting the approved district for; D's cards are kept for R17.

**Order of work** (lanes per "route cheapest first"):
1. BATCH: the 60-line tide model over existing `balance.py --trace` logs; tune the pace and dose numbers to the gate in
   Concept C. No game code.
2. AGENT (fix-rules): `TideRules` + state + Tide raid trigger + the netrun start-gap cut, on today's raids; retire the step
   infection for Solace. Tests as listed.
3. AGENT (fix-rules): the ward board in `SweepGeometry` and the Exploit move in `solace.tres` (with the plan's Phase 1–2).
4. AGENT: the Tongue and the field dose in `SweepRules`, oracle first (`sweep_g1.py`).
5. Art-pass: the Necrosis skin on the GRID / RAID bands (mailbox request), then CAPTURE and a fresh critic (plan Phase 6).

### Designer decisions needed (each with the default this document assumes)

| # | Decision | Default |
|---|---|---|
| S-M1 | Which concept | C on B's board, without per-ward meters |
| S-M2 | The step infection (WH-12) retires for Solace and the tide replaces it; the HUD keeps the word INFECTION and a % | Yes |
| S-M3 | Tide raids: one the first time the front crosses each whole column (3 raids), on top of the GDD 4.4 triggers | Yes; a crossing after a dose does not raid again (GDD 4.3 "first time") |
| S-M4 | Pace per netrun T1 / T2 / T3 = 100 / 130 / 160 milli-columns, death +150, × the S2 Heat table, Virus × 75 %, Breach −500 once | Yes, then tuned by step 1 |
| S-M5 | Dose sources: Heat objective 300, Proxy 50 per run, EVADED raid 200, HQ verb 12 Schematics (+4), each unused netrun dose 100 | Yes |
| S-M6 | An owned Site reached by the front goes DOWN (then DECAY), and comes back OK if a dose pushes the front past it | Yes |
| S-M7 | A netrun at a Site behind the front starts its street Bloom 1000 closer | Yes |
| S-M8 | CITY LOST at front 0 stays a campaign loss with its own verdict word, separate from BREACHED | Yes |
| S-M9 | The field dose: a late response after REVEAL B, one per raid, pushes 150 (half an HQ dose) | Yes |
| S-M10 | Move the Exploits so each ward has one (Breach → `t2_e`, Virus → `t2_h`; ids renamed) and add 4 ward-border locked links | Yes (art-pass checks the culture garden's lot) |
| S-M11 | The corp's beams use locked links (plan Q3) | Yes |
| S-M12 | Wounds keep the plan's BACKDOOR card; Solace shows it as "INFECTED RECORD" (display only) | Yes |
