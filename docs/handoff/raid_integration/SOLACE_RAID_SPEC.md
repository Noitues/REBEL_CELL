# Solace raid spec: the Infected Tide (H5), the contract for the scripts/core port

**Status:** frozen from the G4 oracle, variant H5:
- the designer rulings R-A to R-H (DECISIONS 2026-10-25, "Solace raid: the Infected Tide");
- the Phase 1 rule changes (DECISIONS 2026-10-25, "Phase 1 rule changes"): a HOME hit infects, one breach retry,
  DIVERT, and Heat raids reset the cadence.
- **[H6]** the designer rulings of 2026-10-26 (DECISIONS "CITY LOST at raid end (R-I), known beams aim at owned Sites
  (R-J)"): the oracle is now variant `H6`, the golden `solace_raid_golden.json` is H6 and the H5 golden is kept as
  `data/solace_raid_golden_h5.json`. The items marked **[H6]** below; everything else is H5.

Measurements and reasons: docs/design/raid_concepts/G4_RESULTS.md (section 6 for H5).

**Sources of truth:**
- **Oracle:** `tools/raid_concepts/sweep_g1.py`, variant `H5` (with `g1_geo.py` and `g4_real.py`). The Python is the
  source of truth; this file describes it.
- **Golden:** `tools/raid_concepts/data/solace_raid_golden.json`, written by `solace_raid_golden.py` (H5).
  - The H4 golden of commit 82322009 is kept as `data/solace_raid_golden_h4.json`, from `--variant H4`.
- **What H5 changes from H4:** the items marked **[H5]** below.

The port is Phase 2 (INTEGRATION_PLAN). Nothing here changes `raid_resolver.gd` for the other corps.

Names below:
- The new classes are `SolaceTideRules` (static functions, `scripts/core/solace_tide_rules.gd`), `SolaceTideBoard`
  (the board's lines, `scripts/core/solace_tide_board.gd`) and `SolaceTideState` (`scripts/state/solace_tide_state.gd`).
- Python names are in brackets.

---

## 1. Data shapes (plain Dictionaries and Arrays, JSON-compatible; the golden uses the same forms)

**Board** (built once per campaign from `CityGridData`, never from Python) [`g1_geo.GraphGeo`]:
- **Site:** the `SiteData.id` (StringName). HOME is `"home"` in the grid and `"HOME"` in traces. The Genome Core is
  the boss Site, never a raid target.
- **Route pool:**
  - every simple path from the boss Site to HOME with at most `solace_tide_route_max_links` (5) links;
  - it uses base and locked links alike (R-B: corp beams may use locked links);
  - each path is listed core side first, without the core or HOME, and the list is sorted.
  - The golden's `graph.route_pool` lists the 29 Solace paths.
- **Chains and spokes:**
  - a spoke is the chain T1 → T2 → T3 that starts at one HOME link;
  - objective Sites are not on a chain;
  - the T3 "ring" of a set of spokes is their T3 Sites in spoke order (likewise T1 and T2).
- **Street pool** for a raid [`street_pool`]:
  - first the T1, T2 and T3 rings over the spokes of the 3 candidates;
  - then, for every other spoke holding a live owned Site, its segment T3 → T2 → T1 (if it has at least 2 Sites);
  - duplicates are dropped, and the order is kept.
- **Line:** `{kind: "ROUTE"|"STREET", cells: Array[StringName] (scan order), type: "D"|"N"|"E", home: bool}`. A route
  reaches HOME after its cells; a street never does.

**Cards** [`START_DECK`, `add_infected`]:
- **Card:** `[id: String, type: String, verb: String]`. Cards are kept sorted by id.
- **verb GUARD / SHIFT / JAM:** type is D, N or E. The card is placeable as a sentry of that type. SHIFT can be
  spent on REDEPLOY and JAM on JAM / JAM_B.
- **verb WOUND = INFECTED:** type holds the Site it is tied to (`"HOME"` for a HOME hit [H5], or `"-"`). The id is
  `"w%03d"` from the counter `inf_n`. It is a dead draw.
- **verb DOSE:** type `"-"`, id `"x%d"` from `dose_n`. Not placeable. It counts as healthy for CITY LOST and is
  spent only at DECAY.
- **Armory drop:** `"a%02d"` from `asset_n`, verb GUARD.
- **Start deck:** 8 cards. The oracle's deck is the lab deck: s0 D GUARD, s1 D GUARD, s2 N GUARD, s3 N GUARD,
  s4 E GUARD, s5 D SHIFT, s6 E SHIFT, s7 N JAM.
  - R-C maps the Armory and the stationed operatives' class cards onto these. The mapping is a port task, listed in
    section 9.

**SolaceTideState** (inside `SolaceCampaignTheme`; replaces `infection_bp`, R-G):
- `deck: Array` (cards) and the id counters `inf_n`, `dose_n`, `asset_n`.
- `ghost: int` (the kit: `solace_tide_ghost_start` 2).
- `lost_since_raid: int`, `last_lost: StringName`, `last_sac: int` (the raid index, −9 at start), `raid_n: int`,
  `netruns_since_raid: int`.
- `purge_queued: bool` (Heat 100 crossed for the first time since the last raid), `dose_spent: int`.
- `breach_fails: int` **[H5]**: failed Genome Core breaches since the Exploits were last taken.

**Campaign fields the tide reads** (they exist already):
- `heat`, `schematics` (the oracle's `bank`), `grid` (Site condition OK / DOWN / TAKEN; CLEARED = the oracle's
  `pending`), `exploits` (`held`), the HOME integrity, and the Heat thresholds fired.
- The golden's `state_json` names them: `home`, `bank`, `owned`, `pending`, `held`, `crossed_heat`.

**Place:** `{sentries: {site: card_id}, ghost: null | "HOME"}`.

**Response:** one of:
- `["HOLD"]`;
- `["REDEPLOY", from, to]`;
- `["DEPLOY", type, site]`;
- `["SACRIFICE", site]`;
- `["JAM"]`;
- `["JAM_B"]`;
- `["DIVERT", known_index, cells]` **[H5]**.

**Trace entry:** `[beam, site_or_"HOME", kind]`:
- beam is `known0`..`known2`, `sealed_a`, `sealed_b` or `hunter`;
- kind is `block`, `hit`, `home` or `shield`.

---

## 2. Phases, in order

**Campaign loop** [`campaign_h4`]. Each netrun n = 1 .. `solace_tide_netrun_cap` (30; the oracle's cap, not a game
rule):
1. **BREACH or NETRUN.**
   - A breach is possible when 3 Exploits are held (`min_exploits_for_breach`) and a cleared or claimed T3 Site touches
     the Genome Core.
   - Then the player may launch the final netrun (the game's existing boss run). R-F: its strength scales with the
     INFECTED count (section 5).
   - **One retry [H5]:**
     - a failed breach is a death (death Heat at tier 4, as today) and `breach_fails += 1`;
     - while `breach_fails <= solace_tide_breach_retries` (1), the breach can be tried again on a later netrun;
     - the failure after that **spends the held Exploits** (the corp patches them): `exploits` is emptied and
       `breach_fails = 0`.
   - **Re-taking the Exploits [H5]:**
     - each Exploit is re-taken by a completed netrun on its Exploit Site: the Site stays the Cell's, and the run is
       launchable while the Site is live and its Exploit is not held;
     - the Exploit Heat is paid again;
     - with 3 Exploits held again, the breach has its two attempts again.
   - Otherwise a netrun clears one Site (section 6). Claims are next to the territory: a claimed **or cleared** Site
     counts (`CampaignRules.touches_territory`) **[H5; the H4 oracle counted claimed Sites only]**.
2. **Raid queue.** `netruns_since_raid += 1`. A raid fires after the netrun when either holds:
   - `netruns_since_raid >= solace_tide_raid_every` (3 [H5]);
   - or the netrun crossed a raid Heat threshold (25 / 50 / 75 / 100) for the first time.

   One netrun queues at most one raid. **Every raid, a Heat-threshold raid included, resets `netruns_since_raid` to
   0** (the Phase 1 rule; the H4 oracle already did this).
3. **The raid**, then the HQ step (section 7).

**The raid** [`raid`, `play_one`]:
1. **DECAY** (every raid after the first) [`decay`].
   1. Every owned DOWN Site goes TAKEN, and each adds an INFECTED card tied to it (R-H). `lost_since_raid` also counts
      them.
   2. Spread: `spread = lost_since_raid >= solace_tide_spread_min` (2). Then set `lost_since_raid = 0` and
      `dose_spent = 0`.
   3. Doses, up to `solace_tide_doses_per_decay` (2) times, while a DOSE card is held and (spread or INFECTED > 0):
      - remove the lowest-id DOSE card (`dose_spent += 1`);
      - if spread is pending, cancel it;
      - else remove the highest-id INFECTED card.
   4. If spread is still pending, add one INFECTED card tied to `last_lost` (it does not count as a loss).
   5. Check CITY LOST. **[H6, R-I]** Not any more: DECAY never ends the campaign; CITY LOST is checked only at the
      close (step 10). `SolaceTideRules.loss_margin(state)` tells the PLAN how many more INFECTED cards end the city.
2. **DRAW** [`GraphGeo.draw`]: the board's lines for this raid, from the `raids` stream (section 4).
   - **Candidates:** the route pool sorted by (most live owned Sites on the path first, then a random key); the first
     `solace_tide_candidates` (3) are the sealed candidates (R-B, P-target).
   - **Types:** a shuffled permutation of D, N, E gives the 3 candidates distinct types.
   - **Real A:** a uniform pick among the 3. The drawn real B is not used: the corp picks B by rule (step 7).
   - **Known beams:** `1 + len(solace_tide_beam_heat)` (3) are drawn. Each is:
     - a route (uniform from the pool, uniform type) with chance `solace_tide_early_route_pct` (100 [H5]) in raids
       0 .. `solace_tide_early_raids` − 1 (4 [H5]), and `solace_tide_known_route_pct` (0) after;
     - else a street (uniform from the street pool, uniform type).
     - **[H6, R-J]** "uniform from the pool" is uniform among the paths of that pool through the most live owned Sites
       (the P-target count, pool order kept); the whole pool when no path crosses one (`SolaceTideRules.most_owned`).
   - **Hunter:** a uniform type, then 2 distinct streets sampled from the street pool (both if fewer), and a uniform
     real one of the two.
3. **HAND** [`make_ctx`]:
   - the deck ids, sorted, are shuffled from the `raids` stream;
   - the hand is the first `hand_size(heat)` ids, where
     `hand_size(heat) = solace_tide_hand_base (4) + count of solace_tide_hand_heat (25, 50, 75) <= heat`.
4. **PLAN** [`placements`]:
   - **Sentries:** up to `solace_tide_max_placed` (2) hand cards whose verb is GUARD, SHIFT or JAM, at most one per
     Site.
   - **Where:** only on live owned Sites (OK or DOWN) that lie on one of this raid's lines (`rel`: known, candidates
     and both hunter streets).
   - **Distinct placements:** placements are distinct by the (type, verb) signature per Site. A signature uses its
     lowest free id.
   - **Ghost:** none, or HOME when `ghost > 0`. HOME is then skipped by every beam, at +`solace_tide_ghost_heat` (5)
     Heat and −1 ghost.
   - **Order:** as the Python generator lists them (the golden's `n_placements`).
5. **Known beams are shown** **[H5]**: `1 + count of solace_tide_beam_heat (75, 100) <= heat + ghost Heat` of them, in
   draw order. They are shown here but fire after the RESPONSE (step 7b), so a response can act on them. In H4 they
   fired here.
6. **REVEAL A and the corp's lean.**
   - `lean = b_rule(pre-response board, tie 0)`.
   - The board shows real A, the other two candidates and the lean.
7. **RESPONSE** [`response_options`, `respond`]. Options are listed in this order:
   - HOLD;
   - REDEPLOY from every sentry Site to every target, if a SHIFT card is in the response hand;
   - DEPLOY t to every target, for each type t of a non-INFECTED response-hand card (the card used is the lowest id of
     that type);
   - SACRIFICE (see below);
   - JAM and JAM_B, if a JAM card is in the response hand;
   - **DIVERT [H5]**, if a SHIFT card is in the response hand: for each fired known beam i, and each of its DIVERT
     targets in pool order, `["DIVERT", i, cells]`.

   **Terms:**
   - **Targets:** live `rel` Sites without a sentry.
   - **Response hand:** the hand minus the placed cards.
   - **SACRIFICE:**
     - **when:** only if HOME is not ghosted, not yet hit, and `raid_n − last_sac >= solace_tide_sacrifice_gap` (2);
     - **targets:** every live `rel` Site, plus the cheapest live owned Site off every line;
     - **effect:** the Site goes TAKEN now, its sentry is removed, and HOME is shielded this raid.
   - **DIVERT [H5]:**
     - it bends known beam i onto `cells`: the beam keeps its kind, type and whether it reaches HOME;
     - **DIVERT targets** of a beam are the other paths of its own pool that **start or end at the same Site**: the
       route pool for a route (same first Site = where it leaves the Genome Core, or same last Site = where it enters
       HOME), this raid's street pool for a street;
     - the board shows them as the beam's bend options. The golden lists them per raid (`divert_neighbors`).
   - **Cost:** REDEPLOY, DEPLOY, JAM, JAM_B and DIVERT cost +`solace_tide_card_response_heat` (2) Heat. HOLD and
     SACRIFICE are free.
   - **The corp's B pick:**
     - the board after the response is scored with `b_rule(…, tie = lean)`;
     - JAM_B flips the pick to the other candidate.
   - **`b_rule`:**
     - for each of the two non-A candidates, count the live owned Sites on the route before its first sentry of any
       type;
     - the candidate with more of them is the pick, and a tie keeps the tie value;
     - the corp sees sentries, not their types ("any").
7b. **Known beams fire [H5]** (SCAN), a DIVERTed one along its new cells. The B pick (step 7) is made before they
    fire, on the board after the response.
8. **Sealed A, then sealed B** fire (SCAN).
9. **Hunter:** the real hunter street fires unless the response was JAM.
10. **Close** [`close`]:
    - **INFECTED:** each Site newly TAKEN this raid adds an INFECTED card tied to it, in Site-id order.
      `lost_since_raid += n`, and `last_lost` = the lowest of those Site ids.
    - **HOME infects [H5]:** if HOME was hit (not shielded, not ghosted), one more INFECTED card tied to `"HOME"` is
      added after them. It is not a lost Site: it does not count toward the spread or `last_lost`.
    - **Heat:** + ghost Heat, + card-response Heat.
    - **Clean defense:**
      - **when:** HOME is not lower and no Site changed condition;
      - **reward:** +`clean_defense_heat` (5) Heat and `raid_schematics_by_tier[max(0, band − 1)]` Schematics;
      - **bands:** COOL 0, NOTICED 1, FLAGGED 2, HUNTED 3, PURGE 4.
    - Heat is clamped to 0..`heat_max`.
    - Then check BREACHED (HOME 0) and CITY LOST.
    - Set `purge_queued = false`. If the response was SACRIFICE, set `last_sac = raid_n`.

**SCAN (one line)** [`scan`]. Walk `cells` in order, skipping the ghost Site:
- **Block:** a sentry whose card type equals the line type → `block`, and the beam stops.
- **Hit:** otherwise, the cell's live owned Site not yet hit this raid:
  - OK → DOWN, or DOWN → TAKEN (a TAKEN Site loses its sentry);
  - trace `hit`, and the beam goes on.
- **HOME:** a route that reaches HOME, while HOME is not ghosted and not yet hit this raid:
  - if HOME is shielded: trace `shield`;
  - else HOME loses `home_dmg` (the trace says `home`).
- **HOME damage:** HOME is hit at most once per raid. `home_dmg`:
  - is `solace_tide_home_hit_damage_by_band[min(3, band)]` at the raid's starting Heat;
  - is index 4 (the PURGE raid) only for the raid the first crossing of 100 queued.

**Tiers** [`tier`], checked in this order:
1. **BREACHED:** HOME 0.
2. **DAMAGED:** HOME lower.
3. **EVADED:** no beam touched anything and no Site was taken.
4. **BATTERED:** at least 2 Sites newly DOWN, or at least 1 newly TAKEN.
5. **HOLDS:** otherwise.

**Verdict words** (`RaidOutcome.Verdict`):
- **CELL HOLDS:** the campaign survives the raid.
- **BREACHED:** HOME 0.
- **CITY LOST** (new, R-E): INFECTED cards outnumber healthy cards. DOSE cards count as healthy. It is checked after
  DECAY, after the raid, and after each netrun. **[H6, R-I]** Only after the raid (the close), BREACHED first.

---

## 3. The corp path rule and the corp's lean

- **P-target (R-B):** the 3 sealed candidates are the routes through the most live owned Sites (a random key breaks
  ties).
- **Every line** runs from the Genome Core to HOME, through any links, locked links included. This is the
  designer's rule: every raid line starts at the corp HQ and ends at ours.
- **B is chosen after the response** by the readable rule in section 2, step 7:
  - the lean is shown at REVEAL A;
  - a response that moves or adds a sentry can flip B (measured: 3.4 % of skilled raids);
  - JAM_B always flips it.

---

## 4. Seeds and RNG streams (no global randi / randf)

| Draw | Stream | Order (fixed) |
|---|---|---|
| Lines | `RngService` stream `raids` (already in `RngStreams.STREAM_NAMES`) | Candidate sort keys (one per pool path, in pool order), the type permutation, real A, the drawn B, known beams (route chance, then the route or street, then the type), hunter type, hunter streets, real hunter |
| Hand | the same `raids` stream, after the lines | One shuffle of the sorted deck ids |
| Armory drop | the netrun's `rewards` stream (existing rack asset drop, `asset_drop_chance`) | |
| Netrun death, breach result | not rolled: they are the real netrun's outcome | |

- **The Python streams differ** (`random.Random("raid:<seed>:<raid>")` and so on). The parity test therefore **feeds
  the golden's draws** (`draw`, `hand`) to the port's resolve functions and never compares RNG output.
- **Port self-checks:** the port's own draw is checked for legality (3 distinct candidates of distinct types, from the
  top of the pool order) and for seeded replay.

---

## 5. R-D and R-F: the netrun links

- **R-D:** BloomRules.begin gets the INFECTED count n. The start front moves n steps closer:
  `front_milli = −(start_gap(tier) − n × entry_pace(tier) × solace_tide_infected_front_step_pct / 100)`.
  - `entry_pace` is the existing scaled node pace (Heat band, Virus key), the unit of `ladder_gaps`.
  - `step_pct` is 100.
  - A start gap of 0 or less is CAUGHT at the first entry (the existing latch).
  - The golden's `checks.bloom_start_gap` lists (tier, band, Virus, n, entry_pace, start gap).
  - INFECTED cards never enter the netrun combat deck.
- **R-F:** the oracle uses success = max(0.05, 0.52 − 0.04 × INFECTED).
  - 0.52 is BAL-05's reference boss win. The −0.04 per card is an assumption.
  - **The port needs a concrete mechanic.** Proposal: `solace_tide_boss_hp_pct_per_infected` on the Genome Core (via
    `CampaignRules.boss_overrides`), calibrated with `CampaignSimulator` until the reference win falls about 4 points
    per card.
  - Open question for the designer; the default is that proposal.
- **Breach retry [H5]:** see section 2, step 1. In the oracle a failed breach at `breach_fails > 1` empties
  `held`; the port empties `campaign.exploits` and must re-show the Exploit Sites as launchable re-take runs.
- **Doses (R-F revised):** a DOSE card arrives every `solace_tide_dose_every` (4) netruns (counted on every netrun,
  deaths included). DOSE cards are spent automatically at DECAY. Each cures one INFECTED card or blocks the spread.

---

## 6. Netrun and HQ effects the tide needs (oracle side, mostly existing rules)

**Netrun** [`netrun_h4`, `h4_clear`]:
- **Death:** a netrun death (Bloom caught, or 0 HP) adds `death_heat_base` + tier Heat (existing). No Site is
  cleared.
- **Completion:**
  - rack Heat and Schematics by tier, plus the Exploit (+`exploit_heat`, permanent) and objective `heat_change`
    (existing);
  - the Site becomes CLEARED (territory). It is installed (claimed) at the HQ step when Schematics allow;
  - one Armory card drops with `asset_drop_chance`.

**HQ step after each raid** [`between_h4`, `between_options_h4`]. Options are (repair, build, patch), in this order:
- **repair:** none, or each DOWN Site in id order;
- **build:** none, then CLEAN (if INFECTED > 0), then COOL (if Heat > 0);
- **patch:** false, then true.

The step applies, in this order:
1. **PATCH:** every HOME point the Schematics buy (`repair_home`).
2. **REPAIR:** one DOWN Site (`node_base_cost` × `node_repair_ratio`).
3. **CLEAN** (new: `solace_tide_clean_price` 10, removes the highest-id INFECTED card) or **COOL** (the existing
   Heat purchase).
4. **Install** CLEARED Sites in id order while `node_base_cost` is affordable.

There is no card build: healthy cards come from the Armory drops (R-C).

---

## 7. Config keys (all new keys go in `campaign_config.tres` / `CampaignConfigData`; defaults = H4)

| Key | Default | Oracle name |
|---|---|---|
| `solace_tide_route_max_links` | 5 | `_paths(..., 5)` |
| `solace_tide_candidates` | 3 | `keyed[:3]` |
| `solace_tide_hand_base` | 4 | `HAND_BASE` |
| `solace_tide_hand_heat` | [25, 50, 75] | `HAND_HEAT` |
| `solace_tide_beam_heat` | [75, 100] | `BEAM_HEAT` |
| `solace_tide_max_placed` | 2 | `MAX_PLACED` |
| `solace_tide_ghost_start` | 2 | `GHOST_START` |
| `solace_tide_ghost_heat` | 5 | `GHOST_HEAT` |
| `solace_tide_card_response_heat` | 2 | `SPOOF_HEAT` |
| `solace_tide_early_raids` | 4 [H5] | `EARLY_RAIDS` |
| `solace_tide_early_route_pct` | 100 [H5] | `EARLY_ROUTE` |
| `solace_tide_known_route_pct` | 0 | `KNOWN_ROUTE` |
| `solace_tide_home_hit_damage_by_band` | [5, 10, 13, 29, 43] | `home_hit_damage_by_band` |
| `solace_tide_spread_min` | 2 | `SPREAD_MIN` |
| `solace_tide_doses_per_decay` | 2 | `DOSES_PER_DECAY` |
| `solace_tide_dose_every` | 4 | `DOSE_EVERY` |
| `solace_tide_sacrifice_gap` | 2 | `SAC_GAP` |
| `solace_tide_clean_price` | 10 | `CLEAN` |
| `solace_tide_raid_every` | 3 [H5] | `RAID_EVERY` |
| `solace_tide_home_hit_infects` | true [H5] | `HOME_INF` |
| `solace_tide_breach_retries` | 1 [H5] | `BREACH_RETRY` (with `BREACH_LOSE` 1) |
| `solace_tide_divert` | true [H5] | `DIVERT` |
| `solace_tide_infected_front_step_pct` | 100 | `INF_STEP_PCT` |
| `solace_tide_boss_hp_pct_per_infected` | to calibrate (section 5) | `BREACH_K` (0.04 of win) |
| `solace_tide_start_deck` | the 8 cards in section 1 (until the R-C mapping) | `START_DECK` |

**Notes:**
- The HOME damage table must equal its derivation from the raid content: the threat damage of `raid_claim`,
  `raid_heat_25/50/75` and `raid_purge`, ×1.25 from 75. Check this in `tools/schema_smoke_checks.gd`.
- **Existing keys used unchanged:** `clean_defense_heat`, `raid_schematics_by_tier`, `death_heat_base`,
  `exploit_heat`, `rack_*_by_tier`, `node_base_cost`, `node_repair_ratio`, `home_repair_cost_per_point`,
  `heat_purchase_*`, `asset_drop_chance`, `min_exploits_for_breach`, the Heat thresholds and the `bloom_*` keys.
- **Not ported** (oracle only): the planner weights (`H4_*_V`, `H4_*_W`), `P_COMBAT`, `CYCLE_SCHEM`, `ELITE_RUN`,
  `BREACH_*` and `CAP`.

---

## 8. Scripts touched

| Script | Change |
|---|---|
| `scripts/core/solace_tide_board.gd` (new) | Route pool, chains, rings, street pool, from `CityGridData` |
| `scripts/core/solace_tide_rules.gd` (new) | draw, hand, placements, launch (known beams), response_options, respond, b_rule, scan, play (A, B, hunter), close, tier, decay, between_options, between, forecast (HOLD over A × B slot × hunter) |
| `scripts/state/solace_tide_state.gd` (new) + `solace_campaign_theme.gd` | The state in section 1; `infection_bp` retired (R-G) |
| `scripts/data/corporation_data.gd` | `raid_model: StringName` (`&"resolver"` by default, `&"tide"` for Solace): the per-corp switch. Rule 8: smoke check + DECISIONS |
| `scripts/core/campaign_rules.gd` | `project_raid` / `fight_raid` branch on `raid_model`. The raid queue for the tide: cadence + Heat thresholds (section 2). The Solace HQ step gains CLEAN. `boss_overrides` reads the INFECTED count |
| `scripts/core/raid_resolver.gd` | Unchanged; still used by every corp whose `raid_model` is `resolver` |
| `scripts/core/solace_raid_rules.gd` | Retired for Solace (step infection, cure: R-G); delete once no view reads it |
| `scripts/core/bloom_rules.gd` | `begin(..., infected: int)` moves the start front (section 5) |
| `scripts/core/raid_outcome.gd` | `Verdict.CITY_LOST` (R-E); the tide's tier words |
| `scripts/data/campaign_config_data.gd`, `content/config/campaign_config.tres` | The keys in section 7 |

---

## 9. Save fields

`SolaceCampaignTheme.to_dict` / `from_dict` gain the tide block:
- `deck` as `[[id, type, verb], …]`;
- `inf_n`, `dose_n`, `asset_n`, `ghost`;
- `lost_since_raid`, `last_lost`, `last_sac`, `raid_n`, `netruns_since_raid`;
- `purge_queued`, `dose_spent`.

`breach_fails` **[H5]** is saved too. `infection_bp` is dropped. Save compatibility is not required (ruling 2026-10-05); the port reports the format
change.

**Open port items:**
- the R-C card mapping (Armory asset → type and verb; a stationed operative's class card);
- the R-F boss mechanic.

---

## 10. Tests the port needs

1. **Golden parity** (`tests/unit/test_solace_tide_parity.gd`, fast). For every `campaigns[*].steps` RAID phase, feed
   `before`, `draw` and `hand`, and check:
   - `after_decay`;
   - `n_placements` and that `place` is in `placements`;
   - the response options;
   - `lean` and `b_pick`;
   - `trace`, `home_dmg`, `tier` and `after_raid`;
   - `forecast_hold` (12 tiers);
   - `between_options`, then `between` → `after`.

   Also check every `random_raids` and `random_betweens` entry, and every `checks` table.

   NETRUN and BREACH phases are oracle abstractions: check only their state effects on completion (Heat, Schematics,
   Exploit, CLEARED, Armory drop) and on death (death Heat).
2. **Preview equals result.** For random states, the forecast row for (A, B slot, hunter) under HOLD, and under each
   response option (DIVERT included [H5]), equals `play` with the same inputs. Also: the shown lean equals the B the corp picks under HOLD.
3. **Seeded replay.** The same campaign seed and inputs give the same draws, hands and states (the `raids` stream). A
   save and load mid-campaign continues identically.
4. **Rewind never crosses a checkpoint.** The raid is one checkpoint: PLAN and RESPONSE can be undone before the
   resolve, never after; DECAY is never undone.
5. **Rule tests:**
   - **[H5]** a HOME hit adds one INFECTED card tied to HOME (none when shielded or ghosted, and it does not count for
     the spread);
   - **[H5]** DIVERT: the targets per beam (start or end at the same Site, pool order); a DIVERTed beam scans its new
     cells; the B pick is unchanged by the known beams;
   - **[H5]** breach: one retry; the second failure empties the Exploits; a re-take run restores one;
   - DECAY → TAKEN + INFECTED;
   - spread and dose order;
   - CITY LOST at INFECTED > healthy (DOSE counts as healthy);
   - HOME hit at most once per raid;
   - the PURGE damage only on the first crossing of 100;
   - SACRIFICE gap;
   - clean-defense Heat and Schematics;
   - Bloom start gap with n INFECTED (golden `checks.bloom_start_gap`).
6. **Per-corp switch:** a non-Solace corp still runs `RaidResolver`, and its existing raid tests pass unchanged.
