# G4 results: H4, the Infected Tide with the real game's numbers

Status: Phase 1 lab measurement (docs/handoff/raid_integration/G4_PHASE1.md; designer "Proceed", 2026-10-25). Nothing
in `scripts/`, `content/`, `scenes/`, GDD.md or DECISIONS.md changed. No commits.

**Oracle:** `tools/raid_concepts/sweep_g1.py`, variant `H4`.
- Its numbers are the `H4` dict; each one can be overridden as `H4_<KEY>`.
- The real numbers are read at import from the content files by the new `g4_real.py`. It also checks that g1_geo's
  Solace graph equals `solace.tres` (no differences).
- The street Bloom curve comes from the new `g4_bloom.py` and is saved in `data/g4_bloom_curve.json`.
- `g1_geo.GraphGeo` takes an optional `n_known` (default 3). H4 draws 4 known beams.

**Reproducibility:**
- H3, H, C-target and D-lattice match the HEAD 9dd67390 module byte for byte (48 campaigns compared).
- `--check` passes for all 17 variants.

**Raw output:** `D:/rc_tmp/raid_design_lab/g4/`:
- `h4_final.json` (H4 as shipped);
- `h4_retry1.json` and `h4_retry99.json` (breach retries);
- `h4_step50.json`;
- the grids `g1/` to `g5/` with their `.txt` tables.

**Runtime:** about 20–24 s per 1,200 campaigns (200 per claim policy x 3 policies x 2 players, 5 workers). The Bloom
curve takes 15 s, the golden 2 s, and the five grids about 4 min.

---

## 1. H4 against the targets (all claim policies pooled, 600 campaigns per cell)

G = skilled player (greedy planner), N = careless player (naive placement, always HOLD, patch and repair only).

| Target | H4 G | H4 N | Met? |
|---|---|---|---|
| Skilled loss 5–15 % | **0.052** (all BREACHED) | | met (at the floor) |
| Careless loss 55–85 % | | **0.512** (all BREACHED) | **missed** (just below) |
| Win 35–60 % | **0.318** | 0.150 | **missed**: one-shot breach. With 1 retry: **0.492** (met); unlimited retries: 0.650 |
| Locked at plan ≤ 0.5 | **0.516** | 0.956 | **missed** (just above) |
| Response decides ≥ 0.4 | **0.365** | 0 | **missed** |
| HOME hit 0.15–0.30 | **0.207** | 0.976 | met |
| Raids per netrun 0.33–0.5 | **0.522** | 0.508 | about (slightly above) |
| Median campaign 12–20 netruns | **13** (won: 11) | 23 (won: 8) | met for G. The keys policy breaches at netrun 8, the GDD's minimum path |

**Other measures:**
- CITY LOST: 0.000.
- Netrun deaths: 1.15 per campaign (0.066 per netrun) for G, 0.73 for N.
- Breach reached: 0.68 (G) and 0.33 (N). Breach success: 0.47 (G) and 0.45 (N).
- Capped at 30 netruns without a breach: 0.27 (G), almost all from the random claim policy.
- SACRIFICE: 13 % of raids. B flip: 0.034. Between entropy: 2.54 (H3: 1.9–2.0).
- INFECTED per campaign: 4.6 (G) and 3.3 (N).

**Per claim policy (G / N):**

| Policy | Loss | Win | Netruns (median) | Locked | Response decides |
|---|---|---|---|---|---|
| greedy | 0.030 / 0.760 | 0.425 / 0.055 | 13 / 23 | 0.43 / 0.96 | 0.30 / 0 |
| keys | 0.025 / 0.085 | 0.440 / 0.390 | 8 / 8 | 0.51 / 0.90 | 0.24 / 0 |
| random | 0.100 / 0.690 | 0.090 / 0.005 | 30 / 26 | 0.56 / 0.97 | 0.44 / 0 |

**INFECTED at the first breach, and the effect on the final run:**

| INFECTED at breach | 0 | 1 | 2 | 3 | 4+ |
|---|---|---|---|---|---|
| Share of first breaches (G) | 0.855 | 0.118 | 0.010 | 0.007 | 0.009 |
| Share of first breaches (N) | 0.844 | 0.065 | 0.055 | 0.035 | 0 |
| Success chance (rule) | 0.52 | 0.48 | 0.44 | 0.40 | ≤ 0.36 |
| Measured success, all attempts with unlimited retries (G) | 0.49 (n 594) | 0.51 (111) | 0.41 (32) | 0.38 (21) | 0.34 (61) |

- The mean INFECTED count at the first breach is 0.22 (G) and 0.28 (N). The mean success chance at the first breach
  is 0.511 (G) and 0.509 (N).
- **The final-run scaling (R-F) is real but rarely bites.** About 85 % of breaches carry no INFECTED card, because the
  campaign is short and doses arrive at a steady rate.

---

## 2. The numbers H4 uses

**[R] real (read from content at import):**

| Number | Value | Source |
|---|---|---|
| HOME integrity | 50 | `content/nodes/home_standard.tres` (home_server) |
| HOME hit damage by Heat band (COOL, NOTICED, FLAGGED, HUNTED, PURGE raid) | 5, 10, 13, 29, 43 | each band's Solace raid (`raid_claim`, `raid_heat_25/50/75`, `raid_purge`): summed threat damage, x1.25 from 75 (`rm_major_raid_strength`) |
| PATCH HOME | 1 Schematic per point, every point the bank buys | `home_repair_cost_per_point`, `CampaignRules.repair_home` |
| Starting Schematics | 20 | `starting_schematics` |
| Install a claimed Site | 20 | `node_base_cost` |
| Repair a DOWN Site | 10 | `node_repair_ratio` 0.5 |
| Schematics per completed netrun | rack 10 / 17 / 29 by the Site's tier | `rack_schematics_by_tier` |
| Heat per netrun | rack 2 / 3 / 5 by tier; Exploit +5; objectives −5 / −8 | `rack_heat_by_tier`, `exploit_heat`, solace.tres `heat_change` |
| Death Heat | 10 + tier (tier 4 for the breach) | `death_heat_base`, `HeatRules.death_heat` |
| Clean defense | +5 Heat and the raid's Schematics: 8 (Heat < 50), 12 (50+), 18 (75+), 25 (100) | `clean_defense_heat`, `raid_schematics_by_tier` (D27) |
| Heat purchase at HQ | −7 Heat for 25, +5 each time | `heat_purchase_*` |
| Armory card drop per completed netrun | 40 % (a GUARD card of a random type) | `asset_drop_chance` (R-C: the Armory as cards) |
| Raid Heat thresholds | 25 / 50 / 75 / 100; the first crossing of each queues a raid | GDD 4.3 / 4.4 |
| Extra hand card | at Heat 25, 50 and 75 (hand 4 to 7) | the real thresholds |
| Extra known beam | at Heat 75 and 100 (1 to 3 beams) | the real thresholds (tuned: 50 / 75 / 100 gave locked 0.61) |
| Exploits | held permanently once extracted (`campaign.exploits`); 3 to breach; the breach needs a cleared or claimed T3 next to the Genome Core | `min_exploits_for_breach`, `CampaignRules` |
| Bloom (R-D) | start gap 4000 / 3500 / 3000; pace 500 / 600 / 650 per entry and 100 per fight turn; Heat x 100–160 %; dose push 1000 (max 5000); Virus 75 %, Intel turn 50 %, Breach setback 1000 | `bloom_*` (CampaignConfigData defaults; the .tres sets none) |
| Final run base success | 0.52 | DECISIONS BAL-05: reference boss win 52 % at the shipped 400 HP |

**[A] assumed (no source in the game; stated here):**

| Assumption | Value |
|---|---|
| Schematics from unspent Cycles per netrun | +4 |
| Elites fought per netrun | 2 (+2 Heat) |
| Netrun death chance outside the Bloom | 3 % |
| The breach: success | max(0.05, 0.52 − 0.04 x INFECTED) |
| Bloom netrun model (g4_bloom.py) | 7 layers: fights on layers 1, 2, 4, 6, 7, and on 5 half the time. One-phase fights take 3–5 turns, two-phase fights (rack, elite) 5–9. One Mainframe dose is bought when the run would otherwise be caught, and it is used just before the step that would catch. Caught = death |
| Cleared Sites | wait at HQ: they are installed (20 each) after PATCH, REPAIR and CLEAN. Until then a cleared Site counts as territory but is not a raid target (as in the real raid, which hits claimed nodes only) |
| CLEAN | 10 Schematics per INFECTED card (an HQ verb the game does not have yet; the price of one repair) |

**The R-D curve** (`data/g4_bloom_curve.json`, 2,000 runs per cell):
- **Rule:** the start gap is `start_gap(tier) − n x entry_pace(tier, band, Virus)`. One step is one node entry's front
  advance, the unit the Intel ladder preview counts in (`BloomRules.ladder_gaps`).
- **Monotone:** the published curve is the running maximum over n.
- **Catch chance with no Exploit keys** (n INFECTED = 0 / 1 / 2 / 3 / 4):

| Tier | COOL | FLAGGED (50+) | HUNTED (75+) |
|---|---|---|---|
| T1 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / .03 / .28 | 0 / .02 / .24 / .24 / .57 |
| T2 | 0 / 0 / 0 / 0 / .01 | 0 / .11 / .11 / .44 / .96 | .26 / .26 / .76 / 1 / 1 |
| T3 | 0 / 0 / 0 / .15 / .15 | .15 / .15 / .67 / .99 / 1 | .24 / .90 / 1 / 1 / 1 |

- **With all three Exploit keys** the catch chance is 0 up to 4–7 INFECTED cards. The keys are permanent, so the
  Bloom risk lives in the T2 and T3 runs before the keys are held.
- **R-D measured:** INFECTED cards are rare at netrun time. At 100 % (one step per card) the death rate is 0.066 per
  netrun; at 50 % it is 0.059 (`h4_step50.json`). Doubling the step (200 %) adds about +0.06 skilled loss through the
  death Heat (grid g5).

---

## 3. Tuning (within the rulings; grids of 60 campaigns per policy, `g4/g1.txt`–`g5.txt`)

| Number | H3 | H4 | Why |
|---|---|---|---|
| Known beam route chance after raid 3 | 0.1 | **0.0** | HOME hit 0.32–0.38 → 0.21–0.26; locked −0.06. Raids 1–3 keep 60 % routes |
| Extra known beams | Heat 50 / 75 (lab) | **75 / 100** | Locked 0.55 → 0.50 |
| DISCARD (+2 Heat) | on | **off** | It erased the INFECTED count (it was a G3 lever, not a ruling). Off: INFECTED at breach 0.06 → 0.23 |
| DOSE card | every 2nd netrun | **every 4th** | Every 2nd cures all of it; every 8th lowers win to 0.28 and raises skilled loss to 0.08 |
| Raid cadence | 2 netruns | **2** | 3 gives 0.40 raids per netrun, but careless loss falls to 0.25 |
| Heat raids (first crossing of 25 / 50 / 75 / 100) | — | **on** | Off: careless loss 0.20. They are the 29 / 43 damage raids |
| The PURGE raid's damage (43) | — | **only for the raid the first crossing of 100 queues** | Applying it to every raid at Heat 100 gave skilled loss 0.32 (Heat pins at 100) |
| Breach retry | — | **0** (the brief: the campaign ends at the breach) | See section 4 |
| Kept from H3 | | | B rule "any", spread on 2+ Sites lost, DOSE auto-spent (≤ 2 per DECAY), SACRIFICE once per 2 raids, early routes 60 % in raids 1–3, MAX_PLACED 2 |

**Tried and rejected:**
- Early routes 90 % or for 5 raids: HOME hit 0.29–0.35, locked 0.59–0.66.
- CLEAN 25 with fewer doses: INFECTED at breach 1–2.5, but skilled loss 0.07–0.52 through death Heat.

---

## 4. Targets that need a rule change (not tuning)

1. **Win 35–60 %: the breach-retry rule (a ruling).**
   - Ending the campaign at the first breach (the brief) gives 0.32. The real game's unlimited retries (a failed boss
     run is a death) give 0.65.
   - **One allowed retry gives 0.49**, with skilled loss 0.05 and careless loss 0.51 unchanged.
   - **Proposal:** "a failed Genome Core breach can be retried once; a second failure ends the campaign".
   - Alternatives: base success below 0.52 (a boss rebalance), or a costlier failure (the death plus INFECTED cards).
2. **Careless loss 55–85 % (0.51).**
   - The careless player loses only by BREACHED: HOME hit in 98 % of raids, at most one hit per raid.
   - Every lever that adds HOME pressure also raises locked and lowers response-decides (grids g1 and g4).
   - **Rule options:**
     - more than one HOME hit per raid (each unblocked HOME route deals its band damage);
     - or the careless player's undefended raid adds INFECTED (a HOME hit adds one).
3. **Response decides ≥ 0.4 (0.365) and locked ≤ 0.5 (0.516): G3's finding stands.**
   - The response can only act on the sealed routes and the hunter. The known beams are already fixed at PLAN.
   - **A response that can stop or divert a known beam** (for example SHIFT onto a known route after REVEAL A) is the
     rule change both need.
4. **The infection layer barely matters with real numbers** (R-D, R-E, R-F).
   - CITY LOST never happens.
   - 85 % of breaches carry no INFECTED card.
   - The doses plus CLEAN (the price of one repair) outpace about one lost Site per raid in a 13-netrun campaign.
   - If the designer wants the deck infection to shape the campaign:
     - make doses scarcer (a dose only from Heat objectives or exploit buildings);
     - or add a rule that infects without losing a Site (a HOME hit or a DOWN Site at the raid's end adds an
       INFECTED card).
   - Tuning alone (doses every 8th netrun) costs win and skilled loss first.
5. **Raids per netrun 0.52.**
   - The cadence of 2 plus the four Heat raids sit just above 0.5. A cadence of 3 fixes it but halves careless loss.
   - Acceptable as "about 0.5", unless the Heat raids count toward the cadence (a rule: a Heat raid resets the
     cadence counter).

---

## 5. Port contract and golden

- **Port contract:** `docs/handoff/raid_integration/SOLACE_RAID_SPEC.md` (H4 frozen).
- **Golden:** `tools/raid_concepts/solace_raid_golden.py` writes `tools/raid_concepts/data/solace_raid_golden.json`.
  - 8 seeded campaigns, 164 phases.
  - 120 random legal raids and 80 random HQ steps.
  - Rule checks.
  - The golden asserts that each campaign ends where `sweep_g1.campaign("H4", ...)` ends.
  - It regenerates byte for byte.

---

## 6. H5: H4 plus the Phase 1 rule changes (designer approved, DECISIONS 2026-10-25 "Phase 1 rule changes")

**Oracle:** `sweep_g1.py` variant `H5`. Its numbers are the `H5` dict, overridable as `H5_<KEY>`.
- H4, H3 and the other variants match commit 82322009 byte for byte (90 campaigns).
- `--check` passes for 18 variants.
- The H4 golden regenerates byte for byte as `data/solace_raid_golden_h4.json`.

**Raw output:** `D:/rc_tmp/raid_design_lab/g5/` (`h5_final.json`, `h5_re2.json`, the grids `t1`–`t5`).

**Runtime:**
- 28 s per 1,200 campaigns;
- 5 grids at 60 campaigns per policy: about 5 min;
- the golden: 3 s.

**The rules as simulated:**
1. **A HOME hit adds one INFECTED card** tied to HOME. It is not a lost Site, so it does not count toward the spread.
2. **The breach allows one retry.**
   - Each failure is a death (death Heat at tier 4).
   - The second failure spends the held Exploits.
   - Each Exploit is re-taken by a completed netrun on its Exploit Site, while the Site is still the Cell's.
   - With 3 Exploits again, the breach has two attempts again.
3. **DIVERT.**
   - At RESPONSE, spend a SHIFT card (+2 Heat) to bend one known beam onto another path of its pool that starts or
     ends at the same Site.
   - To make that possible, **the known beams are shown at PLAN but fire after the RESPONSE** (H4 fired them before
     REVEAL A).
   - The forecast and the response list include every DIVERT target.
4. **Heat raids reset the cadence counter.**
   - The H4 oracle already reset the counter after every raid. So H4's 0.52 raids per netrun already included this;
     the change adds nothing by itself.
   - The rate came down only by tuning the cadence to 3.

**Oracle fix (H5 only, so H4 reproduces):**
- In H4, a cleared but not yet installed Site was not territory for the next claim. The real rule
  (`touches_territory`) counts claimed or cleared Sites.
- In H5 it counts. Before the fix, H5 campaigns stalled after the third Exploit: win 0.65 with breach reached 0.78,
  but only on the keys and greedy paths.

### H5 against the targets (all claim policies pooled, 600 campaigns per cell)

| Target | H5 G | H5 N | Met? | H4 G / N |
|---|---|---|---|---|
| Skilled loss 5–15 % | **0.107** (all BREACHED) | | met | 0.052 |
| Careless loss 55–85 % | | **0.642** (BREACHED 0.590, CITY LOST 0.052) | met | 0.512 |
| Win 35–60 % | **0.637** | 0.355 | **missed** (slightly high) | 0.318 / 0.150 |
| Locked at plan ≤ 0.5 | **0.576** | 0.980 | **missed** | 0.516 |
| Response decides ≥ 0.4 | **0.436** | 0 | met | 0.365 |
| HOME hit 0.15–0.30 | **0.165** | 0.987 | met | 0.207 |
| Raids per netrun 0.33–0.5 | **0.388** | 0.400 | met | 0.522 |
| Median campaign 12–20 netruns | **15** (won: 11) | **13** (won: 10) | met | 13 / 23 |

**Other measures:**
- **CITY LOST** now happens: 0.052 for N (0 for G).
- **INFECTED per campaign:** 5.8 (G) and 10.2 (N), against 4.6 and 3.3 in H4.
- **Netrun deaths:** 3.3 per campaign for both players (0.178 per netrun for G, 0.240 for N), against 1.15 and 0.73 in
  H4.
  - The HOME-hit INFECTED cards move the Bloom (R-D), and the early raids now always aim at HOME.
  - **This is the largest change H5 makes.**
- **Breach:** reached 0.77 (G) and 0.66 (N); success 0.49 (G) and 0.32 (N).
- **Breach failures:** 4 % of G campaigns end at the cap after losing their Exploits.
- **Capped at 30 netruns:** 0.215 (G), almost all from the random policy.
- **Responses (G, 4,262 raids):**

| HOLD | DEPLOY | SACRIFICE | JAM | JAM_B | DIVERT | REDEPLOY |
|---|---|---|---|---|---|---|
| 1,614 | 1,464 | 823 | 180 | 90 | **49 (1.1 %)** | 42 |

- **Response decides** rose from 0.365 to 0.436, but mostly because the known beams now fire after the response: a
  SACRIFICE shield or a DEPLOY now also meets them. DIVERT itself is rarely the best response.
- **Other:** SACRIFICE 19 % of raids; B flip 0.03; between entropy 2.55.

**Per claim policy (G / N):**

| Policy | Loss | Win | Netruns (median) | Locked | Response decides |
|---|---|---|---|---|---|
| greedy | 0.155 / 0.435 | 0.815 / 0.565 | 12 / 11 | 0.61 / 0.98 | 0.40 / 0 |
| keys | 0.125 / 0.525 | 0.870 / 0.475 | 9 / 10 | 0.65 / 0.98 | 0.34 / 0 |
| random | 0.040 / 0.965 | 0.225 / 0.025 | 30 / 19 | 0.52 / 0.98 | 0.50 / 0 |

With H5's costs, the greedy claim planner heads for the Exploits as the keys policy does. For the careless player the
two policies give identical rows (checked: the same claims, netrun by netrun).

**INFECTED at the first breach (R-F now bites for the careless player):**

| INFECTED at first breach | 0 | 1 | 2 | 3 | 4 | 5 | 6+ | Mean | Mean success chance |
|---|---|---|---|---|---|---|---|---|---|
| G | 0.752 | 0.220 | 0.006 | 0.009 | 0.011 | 0 | 0.002 | 0.32 | 0.507 |
| N | 0 | 0.071 | 0.098 | 0.106 | 0.348 | 0.335 | 0.043 | 3.94 | 0.362 |

### H5 tuning (within the rulings; grids `t1`–`t5`, 60 campaigns per policy)

| Number | H4 | H5 | Why |
|---|---|---|---|
| Raid cadence | 2 | **3** | Cadence 2 gives skilled loss 0.17–0.26 (the deaths add Heat) and 0.53 raids per netrun. Cadence 3: loss 0.09–0.12, 0.38–0.39 raids per netrun |
| Early raids drawing known routes | 3 at 60 % | **4 at 100 %** | At cadence 3, HOME hit falls to 0.10. 4 raids at 100 % restores 0.15–0.17 |
| Known route chance after the early raids | 0.0 | 0.0 | 0.1–0.3 raise locked to 0.53–0.70 |
| DOSE card | every 4th netrun | every 4th | Every 3rd changes little (loss ±0.01) |
| CLEAN | 10 | 10 | 6 lowers skilled loss by about 0.02 at cadence 2 only |
| Beams at Heat | 75 / 100 | 75 / 100 | 100 only: locked does not fall (0.52–0.63) |

**Sensitivity (200 per policy):** H5 at cadence 2 with H4's early routes (`h5_re2.json`) gives skilled loss 0.193,
win 0.52, locked 0.515, response decides 0.42, HOME hit 0.19, 0.53 raids per netrun, careless loss 0.84.

### What still needs a ruling (H5)

1. **Win 0.64 (target 35–60 %).**
   - One retry plus re-taking the Exploits makes the breach hard to miss. Breach reached: 0.77 pooled, and every keys
     or greedy skilled campaign reaches it.
   - **Measured option: the second failure ends the campaign** (instead of spending the Exploits; `h5_lose0.json`):
     - win 0.568 (met);
     - but skilled loss falls to 0.013 and careless loss to 0.335, because campaigns end before the late raids.
     - So it trades one target for two.
   - Other options:
     - the R-F scaling counts more than the 0.04 per card assumed;
     - or the boss is weaker than BAL-05's 52 % reference.
   - Tuning within the rulings cannot move it: every grid cell gave 0.57–0.74.
2. **Locked at plan 0.58 (target ≤ 0.5).**
   - The four early raids that always aim at HOME are fixed at PLAN for the outcome tier: a HOME route is DAMAGED
     whatever you place, unless a sentry of its type sits on it.
   - Every grid cell with HOME hit ≥ 0.15 had locked ≥ 0.55; HOME hit and locked trade on this graph.
   - Ruling options:
     - count "locked" on the tier excluding HOME damage;
     - or let PLAN see the known beams' types only after placement;
     - or lower the HOME-hit target to about 0.10–0.12, where locked is about 0.48.
3. **DIVERT is used in 1.1 % of skilled raids.**
   - The real lift in response-decides came from moving the known beams after the response.
   - If DIVERT should be a common play, it needs a wider target set (for example any path sharing one Site) or no
     SHIFT cost. Both are ruling changes.
4. **Netrun deaths tripled (3.3 per campaign; 0.18 per netrun for G).**
   - The HOME-hit INFECTED cards plus the literal R-D step (one entry pace per card) make the street Bloom lethal at
     FLAGGED and HUNTED.
   - If that is more than intended, use `solace_tide_infected_front_step_pct` 50 (a tuning value the spec exposes;
     `h5_step50.json`):
     - deaths 2.8 per campaign (0.151 per netrun);
     - skilled loss 0.065, careless loss 0.588, win 0.66.
     - Other targets are unchanged within ±0.02.
   - The designer's call: R-D says "one step".
