# Raid integration plan: from the city raid lab to the whole game

Status: design document for the designer. Nothing here is built, and no rule file, GDD.md or DECISIONS.md is changed.
Author: lead-design pass (Opus), 2026-10-25, on branch `claude/raid-design-lab-2d2e2e` at 3b479b15.
Brief: `docs/handoff/raid_integration/BRIEF.md`. Inputs that were verified are cited by path; where a claim rests on the
explorer digest (`D:/rc_tmp/raid_design_lab/integration/LAB_AND_CITY_INVENTORY.md`) and not on a file read here, it is
marked *(digest)*.

**The target vision (designer, 2026-10-25):**
- a seamless city you zoom in and out of;
- the city is the hacking path: netruns take territory and find exploits against the target;
- the corporation hacks back with raids to eliminate the Cell;
- netruns are micro Slay the Spire runs through buildings toward a target server;
- combat uses wheels and cards, and grows with daemons, slices, firmware and cards.

**The thesis of this plan:**
- **The lab's raid becomes the corp's turn on the city.**
  - The raid is the L14 sweep: typed beams, two sealed routes, a hunter, a hand of cards, one response.
  - It plays on the real City Grid at the RAID band of `CityView3D`.
- **Netruns are how you move on the city.** The lab's CAPTURE phase is exactly that.
- **The two layers feed each other through cards:**
  - netruns bank defense cards (the Armory, reborn as a deck);
  - raids push wound cards back into every netrun deck.
- **The prototype's measured strengths carry over:**
  - the persistence chain, the exhaustive forecast, staged reveals and the deck tie-in;
  - best critic score 39/50 (L15), Fit 8; `SCOREBOARD.md` L14–L17.
- **The known ceilings carry over too.** D and S are rules-limited (R15–R17). They are handled as measured levers after
  the port, not as blockers to it.

---

## 1. The loop in one picture

### 1.1 Zoom levels and the decisions at each

| Level | Where (today) | Player decisions | Time share (target) |
|---|---|---|---|
| **City GRID** (whole city) | `hq_scene.gd` wheel-zooms past `CityConfig.raid_fit_max` (640) into the GRID band (HQ_REDESIGN Q4, `docs/art_review/HQ_REDESIGN/PROPOSAL.md`) | which Site to hack next (`CampaignRules.launchable_sites`) and with which operative; install, repair or upgrade a node; station an operative; patch HOME; build a defense card; clean a wound; read Heat and the next raid (`HeatRules.next_raid`) | ~10% |
| **District RAID** (home ↔ corp HQ) | `CityView3D` RAID band (`band_netrun_below` 200 to `raid_fit_max` 640); today's raid is `hq_scene.gd` `show_raid` / `show_raid_playout` | the corp's turn: place ≤ 2 sentry cards, an optional ghost, read the forecast, launch, respond once after REVEAL A, accept the aftermath | ~20% |
| **Building NETRUN** | `netrun_scene.gd`. Map from `map_generator.gd` + `map_v2.gd` (7 layers, street view, NA-26), `exploit_building_graph.gd` (culture garden) or `solace_hq_graph.gd` (the Genome Core ladder) | the route through the building: elites (+Heat), the optional layer-4 Rack (+Heat, +Schematics, banks assets), shops, rests, the Bloom pace | ~45% |
| **Combat** | `combat_resolver.gd`, `wheel_state.gd` (30 ticks) | alignment, nudges, cards, RAM; rewards from `netrun_scene.gd` `choose_reward` | ~25% (inside netruns) |

### 1.2 State that crosses levels

| State | Owner (today) | Written by | Read by |
|---|---|---|---|
| Territory (Site status CORPORATE / CLEARED / CLAIMED / TAKEN, condition OK / DOWN) | `GridState.sites` (`scripts/state/grid_state.gd`) | netrun completion (`CampaignRules.on_run_completed`), install, raid apply | GRID launchables, raid geometry (routes, streets, value at risk) |
| Exploits (keys) | `CampaignState.exploits` | netrun at a T2 Exploit Site | breach gate (≥ 3, `boss_overrides`); Bloom Virus pace; optionally R11 in raids (§6) |
| Heat (0–100, bands 25/50/75/100) | `CampaignState.heat`, `HeatRules` | netruns (Racks, elites, Exploits, death), raid responses and ghost, sinks | raid triggers (thresholds), raid strength (beams, hand size), netrun modifiers, Bloom pace |
| Run deck, slices, firmware, daemons | `OperativeState` (deck, `slot_slice_ids`, `slot_firmware_ids`, `daemon_ids`) | combat rewards, shops, workshop | combat only (pillar 4: wheel mechanics exist only in combat) |
| **Defense deck (new; the Armory as cards)** | `CampaignState.armory` (exists, `armory_capacity` 6) | Racks and run completion bank assets (`RunState.banked_assets`, GDD 7.3); HQ build | raid DRAW |
| **Wounds (new)** | new `CampaignState.wounds: Array[StringName]` (curse card ids) | raid: each Site that turns TAKEN | raid DRAW (dead cards) and jack-in (curse cards added to the run deck) |
| HOME integrity | `GridState.home_integrity` (50) | raid hits, HQ patch | raid (BREACHED at 0) |
| Operatives (roster, stationing) | `CampaignState.roster`, `GridState` station slot | HQ | netrun launch; raid (station bonus as a card, §2) |

### 1.3 The loop

```
                       PROFILE (unlocks, ICE records)
                                  |
 +------------------------ CAMPAIGN: one corp (Solace first) ------------------------+
 |                                                                                     |
 |   CITY GRID band  (HQ = the live city; zoom wheel)                                  |
 |   decide: next Site + operative | install / repair / patch | build defense card     |
 |           clean wound | station operative            reads: Heat, next raid, keys   |
 |        |  JACK IN (dive, scene change today)                     ^                  |
 |        v                                                         |                  |
 |   NETRUN (a building / street graph, ~15 min)                    |                  |
 |   decide: route (elite? rack? shop? rest?)    + run deck gets one curse per WOUND   |
 |        |   ^                                                     |                  |
 |        v   | win                                                 |                  |
 |   COMBAT (wheel + cards)  -> cards, firmware, daemons, slices (operative-scoped)    |
 |        |                                                         |                  |
 |        | run completes / Rack captured:                          |                  |
 |        |   Site CLEARED -> claimable  (= lab CAPTURE)            |                  |
 |        |   Exploit +key, Heat +, Schematics +, assets -> DEFENSE DECK               |
 |        v                                                         |                  |
 |   HEAT crosses 25/50/75/100, a claim next to the corp, node built, retaliation     |
 |        |  (mid-run: an interlude; between runs: at HQ)            |                  |
 |        v                                                         |                  |
 |   RAID band: the corp hacks back on YOUR territory (sweep, L14 rules)               |
 |     DECAY -> DRAW hand (defense deck + wounds; +1 card per band) -> PLAN 2 sentries  |
 |     + ghost -> FORECAST (A x B x hunter, exact) -> beam 1 (+1 beam per band)        |
 |     -> REVEAL A -> RESPONSE -> sealed A -> REVEAL B -> sealed B -> hunter           |
 |     -> AFTERMATH: Sites DOWN/TAKEN, HOME -hit, Heat +/-, WOUND per TAKEN ------------+
 |                                                                                     |
 |   WIN: breach the Central Server with >= 3 Exploits.  LOSS: HOME integrity 0       |
 +-------------------------------------------------------------------------------------+
```

The intent of the loop:
- **Netruns are the Cell's move** (gain territory and keys).
- **Raids are the corp's move** (take territory back, wound the Cell's code).
- **Heat is the clock** that decides how often and how hard the corp moves.
- **Cards carry the cost in both directions.**

---

## 2. Mapping table: every lab concept

Lab rules are cited from `tools/raid_concepts/sweep_l8.py` (the oracle) and `docs/handoff/raid_lab_l8/L14_RULES.md`.

| Lab concept | Place in the full game | Replaces / merges / extends (paths) | Verdict | Reason |
|---|---|---|---|---|
| **Districts** (4×3 cells, values 4–12, NEUTRAL / OK / DOWN / TAKEN) | **Sites** of the corp's City Grid | Merges with `SiteData` (`scripts/data/site_data.gd`) and `GridState` status and condition. NEUTRAL = CORPORATE or CLEARED-unclaimed; OK / DOWN = CLAIMED + Condition; TAKEN = TAKEN. A cell's value v = the installed node's value (install cost by type; config table) | **ADAPT** | The four states already exist with the same words (GDD 3.3). Real Sites have no per-raid income, so "value" becomes the node's install value plus an Exploit-Site bonus. |
| **Routes** (rows, reach HOME) | **Spokes**: a link path from an entry Site to HOME through owned Sites | New `SweepGeometry` (scripts/core) on `GridState.next_hop` / `distance` / `neighbors` | **ADAPT** | GDD 3.1: "raids start from corporate Sites adjacent to your territory and travel along links". |
| **Streets** (columns, never reach HOME) | **Cross-links**: the paired `locked_links` between neighboring chains, plus the tier ring across the selected spokes | `SweepGeometry`; reads `SiteData.locked_links` / `GridState.opened_links` | **ADAPT** (designer call, Q3 in §3) | The Solace Grid is a star: HOME links 10 T1 spokes, each a chain T1→T2→T3→core (`content/corporations/solace.tres`). Cross-links pair neighbors (t1_a–t1_b, t1_d–t1_e …). Streets are the only source of beam overlap, which made placement a choice in the lab. |
| **The 4×3 board** itself | The RAID-band view of **three spokes × tiers 1–3**, with the core as the 4th column | Lab x=0..2 ↔ T1..T3; x=3 ↔ the approach to the boss Site (no owned Sites there in practice); lab HQ (x=4) ↔ `the_genome_core`; lab HOME (x=−1) ↔ `home` | **ADAPT** | See §2.1 for the exact rule and its risk. |
| **HQs** (ours amber left, corp cobalt right) | The Cell's home (A2 territory `centre` → `rebel_cell`) and the corp HQ compound in `CityView3D` | Real HQs: `city_solace_district.gd`, `hq_compound_stage.gd`, `hq_solace_*` shaders *(digest)*. The lab's procedural towers in `l8_board.gd` are dropped | **KEEP** (concept), **DROP** (lab meshes) | The game already renders both HQs at the RAID band; beams leave the real corp HQ. |
| **CAPTURE** (claim 1 adjacent cell; 2 after HOT) | **A netrun.** Completing a run at a launchable Site clears it, and claiming it is the existing install | `CampaignRules.launchable_sites` (corporate Sites next to the territory) and `on_run_completed` already implement "adjacent to owned" | **ADAPT: CAPTURE becomes a netrun** (decided) | The vision: "netruns gain territory". HOT's double capture is dropped (one Site per run). |
| **Sentries** (typed D/N/E; block a same-type beam) | **Defense cards placed on claimed Sites** for this raid; built-in sentries on Firewall Relays | `DefenseAssetData` (`scripts/data/defense_asset_data.gd`) gains `raid_type` and `raid_verb`; the Firewall Relay's built-in turret (GDD 3.2) becomes a permanent typed sentry | **ADAPT** | Keeps GDD 7.3's "assets" as the things you place. The integrity / damage / range fields retire with the step resolver. |
| **The deck hand** (8-card dummy deck, hand 4 +1 per band, redrawn each raid, nothing consumed) | **The Cell's DEFENSE DECK**: a campaign-scoped raid sub-deck (the Armory as cards) | Reuses `CampaignState.armory` (Array of asset ids) as the deck; `armory_capacity` 6 → deck rules; start list from the home-server variant (`HomeServerVariantData`, GDD 3.4) | **ADAPT: a raid sub-deck, not the run deck** (decided; see §2.2) | Measured lab balance holds (8 cards, 2 SHIFT, 1 JAM), and the Fit tie-in survives through banking and wounds. |
| **Wounds** (each TAKEN adds a dead card; −5 at leg end; CLEAN for 4) | **Real curse cards**: `CardData` with `offered = false` (the `content/cards/bug.tres` pattern: 0 RAM, drain 1 RAM, exhaust) | New `CampaignState.wounds`; injection at jack-in reuses `NetrunSession._apply_bug_cards` (`scripts/core/netrun_session.gd` ~l.997); removal reuses Mainframe card removal (`remove_card`) plus an HQ CLEAN verb | **ADAPT: wounds become real curse cards** (decided) | One state, two readers: a dead draw in raid hands (as the lab measured) and a curse in every netrun deck (the cross-layer cost the vision asks for). |
| **Sealed beam A** (one of 3 routes, typed by permutation, revealed before RESPONSE) | Kept as is, on spokes | `SweepRules` (new), hidden draw from the `raids` stream | **KEEP** | The strongest S lever measured (`RECOMMENDATION.md`, R1). |
| **Sealed beam B** (one of the other two, revealed after RESPONSE) | Kept; needs ≥ 3 candidate spokes, otherwise it degrades (see §6 R-4) | `SweepRules` | **KEEP** | L14 R1 ruled by the designer 2026-10-24. |
| **The hunter** (hound; 2 sealed street candidates, revealed last; JAM cancels it) | Kept, on cross-links / tier rings; its type and glyph come from a Solace threat (the Collections theme, GDD 8.3) | Threat resources in `content/threats/` keep the identity and art; `RaidData.waves` is replaced by a sweep pattern | **KEEP** | Its identity is already the most legible piece in the lab captures. |
| **Responses** HOLD / REDEPLOY (SHIFT, +2) / DEPLOY (any card, +2) / SACRIFICE (TAKEN, shield HOME) / JAM (JAM card, +2, no hunter) | Kept; Heat costs in `campaign_config.tres` | `SweepRules.response_options` | **KEEP**; R16 per-response costs come later (Phase 7) | They are the post-reveal decision. "Responses differ only in tier" is the R16 lever, not a port blocker. |
| **Ghost** (kit of 2; hides a cell or HOME; +5 Heat) | Kept as a Cell verb with a per-campaign charge; a stationed **Ghost** operative adds a charge | `RECOMMENDATION.md` Ghost lever; config `raid_ghost_heat` | **KEEP** | A cheap Heat-for-safety trade that is easy to read. |
| **Heat bands** (+1 beam and +1 card at 50 and at 75; Heat term in the score) | GDD 4.3 FLAGGED / HUNTED bands; replaces "raid strength +25%" at 75 | `HeatRules.band_levels`; the threshold table in `campaign_config.tres` | **KEEP** (amends GDD 4.3) | Lab EXTRA_AT 50 and STRONG_AT 75 are already the GDD's majors. |
| **Intensity** (LOW / NORMAL / HOT: Heat +6/12/18, income, perks) | **Netrun choice and Heat.** Which Site (tier, Exploit, Heat objective), elites, the layer-4 Rack, Burner firmware: the real netrun's Heat sources (GDD 11.5) | Nothing to build: `HeatRules.add_heat` and `CampaignRules.clear_preview` already price a run's Heat | **DROP as a UI, ADAPT as meaning** (decided) | The lab's intensity stood in for "how hard you ran". The perks go: FREE_REPAIR because repairs cost Schematics (GDD 3.3), EXTRA_CAPTURE because a run claims one Site. |
| **The between step** (repair, build a GUARD card for 3, CLEAN for 4, intensity) | **HQ verbs** at the GRID / RAID band: REPAIR (exists), BUILD a defense card (new), CLEAN a wound (new), PATCH HOME (exists) | HQ verb slot stickers (HQ_REDESIGN Q11: CLAIM / REPAIR / UPGRADE / PATCH) gain BUILD and CLEAN | **ADAPT** | It fits the existing verb-slot UI and the Schematics economy (GDD 11.4). |
| **DECAY** (DOWN → TAKEN at the next raid, plus a wound) | Kept: a DOWN Site not repaired before the next raid falls | Amends GDD 3.3 (today DOWN persists until repaired, and only a hit turns it TAKEN) | **KEEP** (designer call, Q6) | It is the first link of the praised persistence chain, and many netruns between raids give room to repair. |
| **HOME pips** (3) | `GridState.home_integrity` (50); each HOME hit removes `raid_home_hit_damage` (config, default 17: three hits breach) | `RaidOutcome.Verdict.BREACHED` (D28) | **ADAPT** | It keeps GDD 3.2's 50 and the patch price (1 Schematic per point). |
| **Score** (bank + values + exploits − HOME − Heat − wounds) | **None in the game.** Kept as the measurement metric of the oracle and of `CampaignSimulator`'s raid policy | `scripts/core/campaign_simulator.gd` | **DROP** (in game), **KEEP** (in tools) | Real consequences are the campaign state itself. A visible score would be a second economy. |
| **Forecast** (per A: a 2×2 table of B × hunter outcomes, exact, assuming HOLD) | The raid PLAN screen; GDD 7.1's "exact projected outcome" becomes "exact per sealed candidate" | `RaidOutcome.project` extends to the candidate table; preview = the same `resolve` | **KEEP** | P is 8–9 in every round; preview == result is a rule-6 test. |
| **Tiers** BREACHED / DAMAGED / EVADED / BATTERED / HOLDS | `RaidOutcome.Tier` (today CLEAN / AMBER / DOWN / TAKEN) plus the D28 verdict (CELL HOLDS / BREACHED) | `scripts/core/raid_outcome.gd`, `scripts/ui/kit/raid_verdict.gd` | **ADAPT** (Q8) | Map EVADED → CLEAN, HOLDS → DOWN tier, BATTERED → TAKEN tier (or ≥ 2 DOWN), DAMAGED → AMBER, BREACHED → verdict. The lab's five glyph shapes (L16) are presentation. |
| **R14 hint** (+3 Heat for the best response) | None | — | **DROP** | Reverted in L15 after it misled players (`SCOREBOARD.md` L14). |

### 2.1 How the lab's 4×3 grid maps onto real Sites (decided)
- **Columns = tier rings.** Lab x = 0, 1, 2 ↔ T1, T2, T3 (link distance from HOME on a chain). The lab's x = 3 has no
  owned counterpart (the T3→core approach), and the corp HQ is the boss Site.
- **Rows = the candidate spokes.** For each raid, `SweepGeometry.candidates`:
  1. takes the spokes (chains from HOME) that hold at least one live owned Site;
  2. orders them by the live value at risk (descending), then by the T1 Site id;
  3. keeps the first `raid_sealed_candidates` (3).
  - With fewer than 3 such spokes, it pads with the nearest corporate spokes, which hold no owned cells. A beam there
    can still reach HOME, so it is never empty.
  - The **route** of a spoke runs from its outermost Site inward to HOME (the lab's right-to-left row).
- **Streets = cross-links.** A street is a path of Sites across spokes at one tier, made of the content's
  `locked_links` (locked or open) plus ring adjacency by `map_position` angle around HOME.
  - **The designer decides** whether the corp may use locked links. GDD 4.1 today makes only opened links raid routes.
  - Streets never include HOME.
- **Beam 1 and the extras** use the same route and street generators. Every draw comes from the `raids` stream when the
  raid is queued, so the forecast and the result read one saved draw.
- **Exploit cells** ↔ the three T2 Exploit Sites (`t2_intel`, `t2_breach`, `t2_virus`).
  - Holding one adds `raid_exploit_value` to its value at risk.
  - Losing one does NOT remove the Exploit already taken (open question Q10).

### 2.2 Why the raid uses a campaign defense deck, not the operative's run deck
- **There is no single run deck.**
  - `OperativeState.deck` belongs to one operative. There are 2+ operatives (GDD 5.4), each with a deck, and permadeath
    deletes a deck.
  - A raid between runs would have no canonical deck, and a mid-run raid would use a different one. The same raid
    would then play differently depending on when Heat crossed.
- **Combat cards are wheel verbs.** Giving 71 cards a second raid face (type + verb) doubles content and makes every
  reward pick a two-axis choice. It also blurs pillar 4 ("wheel mechanics exist only in combat").
- **The lab's balance is tied to deck shape.**
  - It was measured on 8 cards with 6–7 placeable, 2 SHIFT and 1 JAM (greedy 0% breach, naive 100%; wounds 0.45 per
    leg; `SCOREBOARD.md` L14).
  - Run decks of 10–25 cards with no raid faces would remove that calibration.
- **The Fit gain survives:**
  - **Netruns feed the deck.** Assets banked on Rack capture or run completion (GDD 7.3, `RunState.banked_assets`)
    become defense cards.
  - **Raids feed back.** A wound is a curse card in the next netrun's deck.
  - **Stationed operatives each add one class card to the hand** (Q7 default: Breaker = a GUARD of any type,
    Ghost = +1 ghost charge, Rigger = a free repair after the raid, Botnet = +1 hand size). This replaces the
    step-resolver station bonuses of GDD 5.2.

### 2.3 Is `raid_resolver.gd` replaced, wrapped or kept? (decided: replaced per corp, behind a switch)
- **A new pure `SweepRules` / `SweepResolver` replaces `RaidResolver.resolve` as the raid for any corp whose
  `raid_model` is `&"sweep"`. Solace is first.**
  - `RaidResolver` stays intact for the other corps (on hold under "one corp at a time") until each is ported. Then it
    retires with its 30-step loop, cascade and integrity damage (TECH_SPEC 7).
- **Not wrapped.**
  - A sweep has no steps, no threat HP and no ranges. Wrapping would leave two models in one result type and make
    `RaidBeats` lie about phase order.
- **Not kept as the projection engine.**
  - The sweep's own `resolve` is its projection, exactly as in the lab (`forecast` = `resolve` over every candidate).
  - Rule 6 needs the preview and the result to be the same code.
- **What carries over from today's raid code:**
  - `RaidOutcome` (verdict, tier, `project`, `aftermath`, `entry_points`);
  - `RaidVerdict` words;
  - `RaidBeats` step-locking (fed by sweep events);
  - `CampaignRules` raid queueing (`pending_raids`) and `default_entry_sites`;
  - `HeatRules` thresholds;
  - the netrun interlude hook (`NetrunSession._maybe_raid_interlude`).

---

## 3. GDD conflicts, as proposed DECISIONS.md open questions

Each item names the GDD section and gives a recommended default. None is applied. When the designer rules, the
GDD changes go in one GDD v1.0 §7 rewrite, logged in DECISIONS.

- **Q1. §1.2 pillar 4, "Raids are deterministic graph auto-battles with a planning phase."**
  - The sweep stays deterministic (its hidden draws are seeded and saved) and graph-bound. It adds hidden information
    and one decision during the playout (RESPONSE).
  - *Default:* amend to "Raids are deterministic graph sweeps with a planning phase and one response; hidden lines are
    drawn when the raid is queued."
- **Q2. §7.1 Setup Phase (asset placement, "exact projected outcome" per node) and §7.2 Resolution (step loop, 30-step
  cap, cascade, "threats still on a node leave it TAKEN").**
  - *Default:* rewrite §7 as the L14 sweep for corps with `raid_model = sweep` (Solace).
  - The projection becomes exact per sealed candidate (the forecast table).
  - §7.2's step loop stays documented as the legacy model until it retires.
- **Q3. §4.1 "Cross-links … Opened links are routes for raids too" (raids use only opened links).**
  - Streets need cross-links. If raids use only opened links, a fresh campaign has no streets, so no hunter and no
    beam overlap.
  - *Default:* the corp's beams may run any cross-link, locked or not. Locks gate the Cell's netruns, not the corp's
    own network. Intel then shows the hunter's type early (R11, cheap).
- **Q4. §7.3 Armory & Persistence (locked): Armory max 6; deployed assets persist on their node.**
  - *Default:*
    - unlock §7.3;
    - the Armory becomes the defense deck (start 8 cards from the home variant, no cap, or a config cap of 16);
    - assets are placed per raid from the hand and return to the deck after it.
  - "Unbanked assets are lost on death" stays.
- **Q5. §7.2 Heat (D27, 2026-10-22: a clean defense gains +5 Heat and pays Schematics; damage gains none) against the
  lab's EVADED −10 Heat.**
  - The two rules point opposite ways: D27 makes a perfect defense raise the next raid, while the lab rewards evasion.
  - *Default:*
    - keep D27's Schematics payout for EVADED and HOLDS;
    - Heat: EVADED −`raid_evade_heat` (10, the lab number), any other survived tier 0;
    - card responses and the ghost cost Heat as in the lab.
  - Measure it in the Phase 3 sim against D27 as a config switch.
- **Q6. §3.3 Node Loss States.**
  - Today DOWN persists until repaired (50% of install), and TAKEN needs "a threat on the node at raid end, or a DOWN
    node hit again".
  - *Default:* keep "hit on DOWN → TAKEN" (it is the lab's rule too) and add DECAY. A Site still DOWN when the next
    raid starts goes TAKEN and adds a wound. Repair stays 50% of install.
- **Q7. §5.2 station bonuses (asset damage +50%, threat delay, regen per wave, free asset per raid).**
  - These have no meaning without steps and damage.
  - *Default:* they become one class card in the raid hand (§2.2), scaled by rank through `station_bonus_multiplier`.
- **Q8. §3.3 / §7.2 words (D28: CELL HOLDS / BREACHED; a node that survives HOLDS) against the lab's five tiers.**
  - The lab uses HOLDS as a raid tier.
  - *Default:*
    - the verdict stays D28;
    - the tier words become EVADED, HOLDS, BATTERED, DAMAGED (the stamp's second line);
    - a node that survives is "OK", to free HOLDS.
  - `docs/process/agent_rules/city.md` must list the new words (stale today, inventory A).
- **Q9. §4.3 Heat table "75: raid strength +25%" and §11.9 ICE "raid strength +15%", "raids gain a second wave",
  "TAKEN Sites spawn stronger raids".**
  - *Default:*
    - 50 and 75 each add a beam and a card (lab R13);
    - ICE raid strength becomes "+1 sealed candidate type shown later" (the hunter type is hidden until REVEAL B);
    - "second wave" becomes a second hunter at ICE 16+;
    - a TAKEN Site becomes a beam origin (R7 step 2).
  - Every one of these is config.
- **Q10. §11.7 Exploits.**
  - Should a TAKEN Exploit Site lose its Exploit?
  - *Default:* no. Keys are kept (the win path stays stable); the Site is valued higher in the forecast.
- **Q11. §11.4 / §11.5 / §11.8 economy and pacing.**
  - Today: raid win Schematics by tier, "clean raid defense +5 Heat", "raid ≈ 5 min, 3–7 raids per campaign".
  - *Default:* keep the reward table (paid on EVADED / HOLDS) and keep 5 min as the raid target. The time split
    follows §6 R-1.
- **Q12. §3.2 Remote Node Types.**
  - Integrity 15–30 has no role in the sweep. Firewall Relay = "built-in turret"; Vault Terminal = "raids prioritise it".
  - *Default:*
    - integrity stays only as the repair price basis;
    - the Firewall Relay holds a permanent sentry of a type chosen at install;
    - the Vault adds its value to the spoke-ordering rule (§2.1), so it is more often a candidate.
- **Q13. §11.9 ICE 11 Bug card / Appendix A.**
  - A new curse card ("BACKDOOR", wound) is content.
  - *Default:* the Bug's effect set (0 RAM, drain 1, exhaust) with a new id, so ICE Bug counts and wounds stay
    separate. It is removable at a Mainframe in a run, which also removes it from `campaign.wounds`. That makes netruns
    a way to heal raid damage.
- **Q14. Solace raid infection (DECISIONS 2026-10-19 WH-12, not in the GDD).**
  - The figure rises per step with living threats, and CITY LOST at the threshold. There are no steps in a sweep.
  - *Default:* infection rises `raid_infection_hit_bp` per HIT and per HOME hit, CITY LOST unchanged. Alternative:
    drop it for Solace, since wounds already carry the Collections theme.
- **Q15. §1.3 / §4.2 netrun structure ("7 layers") against the vision's "traverse individual buildings".**
  - It is out of raid scope.
  - Flag only: building graphs exist for the culture garden and the HQ ladder alone (`exploit_building_graph.gd`
    KINDS = culture_garden).

---

## 4. Exists vs build

### 4.1 Reuse as is (no change, or a call-site change only)
- **City and bands:**
  - `scripts/city3d/city_view_3d.gd` (pick, `lot_at`, project / unproject, HQ beams, the `map_band` signal);
  - `city_config.gd` (`raid_fit_max`, `band_netrun_below`);
  - `city_iso_camera.gd`, `city_lod.gd`, `raid_zoom_fit.gd`, `raid_uplink_pads.gd` *(digest)*.
- **HQ as the city:**
  - `scripts/ui/hq_scene.gd` band zoom (~l.2781–2851) *(digest)*;
  - the verb-slot stickers;
  - `kit/site_marker_layer`, `kit/city_minimap` *(digest)*.
- **Campaign rules:**
  - `scripts/core/campaign_rules.gd` (`launchable_sites`, `on_run_completed`, `clear_preview`, raid queueing,
    `jack_from_site`);
  - `heat_rules.gd` (`add_heat`, `forecast`, `next_raid`, `band_levels`);
  - `grid_state.gd` (status, condition, `next_hop`, `distance`, `link_key`, `opened_links`).
- **Outcome words and timing:**
  - `scripts/core/raid_outcome.gd` (verdict, `aftermath`, `entry_points`);
  - `scripts/ui/kit/raid_verdict.gd`;
  - `scripts/ui/kit/raid_beats.gd` (the step-locked timeline; fed new event kinds).
- **Determinism:** `scripts/autoload/rng_service.gd` and `scripts/core/rng_streams.gd` (the `raids` stream already
  exists).
- **Cards and decks:**
  - `content/cards/bug.tres` (the curse pattern);
  - `NetrunSession._apply_bug_cards` and `remove_card` (`scripts/core/netrun_session.gd`);
  - `CampaignState.armory`, `RunState.banked_assets`.
- **Sims:** `scripts/core/campaign_simulator.gd` (the balance sims, `campaign_focus_corp`).
- **Content:** `content/corporations/solace.tres` (32 Sites, 3 Exploits, cross-links) and the Solace raid triggers
  (`content/raids/raid_claim.tres`, `raid_heat_25/50/75.tres`, `raid_node_built.tres` … the non-prefixed set).

### 4.2 Port (lab → game, with oracle parity)
- **Rules.**
  - `tools/raid_lab_city/l8_rules.gd` (1,560 lines) → `scripts/core/sweep_rules.gd`:
    `hand`, `decay`, `placements`, `response_options`, `resolve`, `trace`, `forecast`, `tier`, `between` pieces.
  - The 4×3 lattice is replaced by `SweepGeometry`. Python `random.Random(seed + k)` is replaced by draws from the
    `raids` stream, made once at queue time and saved.
- **Parity.**
  - `tools/raid_lab_city/parity_check.gd` (1,402 lines) → `tests/unit/test_sweep_parity.gd` (fast tier);
  - `tools/raid_lab_city/data/l8_golden.json` → `tests/data/sweep/lattice_golden.json`.
- **Oracle.** `tools/raid_concepts/sweep_l8.py` stays the oracle for the lattice. A graph oracle `sweep_g1.py` (new,
  tools/) makes the Solace goldens.
- **Policies.** The lab's `greedy_leg` / `naive_leg` → a raid policy in `CampaignSimulator` (the reference player plus
  a careless player) for breach rates.
- **Presentation** (raid-lab-owned look, exception per memory):
  - from `tools/raid_lab_city/raid_lab_city.gd` and `l8_board.gd`: the hand row, the deck strip with wounds, the
    forecast table (L15 inline results, LOCKED, ghost reasons), the response rows (L17 honest guard line), typed
    vehicles (drone swarm, netrunner worm, enforcer convoy), BLOCK / HIT effects, the hound glyph, the five tier shapes;
  - into `scripts/ui/raid/` on `CityView3D`.

### 4.3 New
- **Schema** (rule 8: minimal, smoke-checked, logged):
  - `DefenseAssetData.raid_type` and `raid_verb`;
  - `RaidData.sweep` (a `SweepPatternData`: beam count by band, candidate count, hunter type and candidates, origin
    rule) *or* sweep fields on `RaidData`. Pick the smaller one at port time.
- **State:**
  - `scripts/state/raid_sweep_state.gd`: hidden draws, hand, placement, phase, response; saved;
  - `CampaignState.wounds`, `CampaignState.ghost_charges`.
- **Core:** `SweepGeometry` (spokes, streets, candidates); `SweepRules`; `SweepResolver.apply`, which writes to
  `CampaignState`.
- **Content:**
  - the BACKDOOR wound card;
  - start defense-deck lists per home variant;
  - `raid_type` / `raid_verb` on the 8 assets: turret, ICE lock, decoy, sentry, railgun, flak array, tar pit,
    honeypot node.
- **Config** (`campaign_config.tres` + `CampaignConfigData`):
  - `raid_model_by_corp`, `raid_sealed_candidates`, `raid_hand_base`, `raid_max_placed`;
  - `raid_ghost_heat`, `raid_response_heat`, `raid_evade_heat`, `raid_home_hit_damage`;
  - `raid_build_price`, `raid_clean_price`, `raid_exploit_value`, `raid_infection_hit_bp`.
- **UI:**
  - HQ verbs BUILD and CLEAN;
  - the raid PLAN / FORECAST / LAUNCH / RESPONSE / AFTERMATH screens on the RAID band;
  - the sweep interlude in `netrun_scene.gd`;
  - TextDb keys for every word.
- **Save:** a version bump (compatibility is not required, ruling 2026-10-05) for `wounds`, `ghost_charges`, the defense
  deck's meaning and `raid_sweep_state`.

---

## 5. Phased plan

**Lanes** (per "route cheapest first"):
- **BATCH:** Batch API (Haiku or Sonnet) for patch-shaped drafts and test boilerplate.
- **AGENT:** a Sonnet `fix-rules` / `fix-visual` / `fix-mechanical` agent in its own worktree.
- **CAPTURE:** a Sonnet agent with windowed Godot via `tools/run_windowed.py`.
- **OPUS:** design or critique only.

**Rules for every slice:**
- deterministic (`RngService` streams passed in);
- no magic numbers (config);
- every rule tested (preview == result, seeded replay, rewind never crosses a checkpoint);
- ties by content id, then node id;
- `QUICK=1 bash tools/precommit.sh --base main` green before hand-back.

### Phase 0: Rulings and branch base (no game code)
- **0a.** The designer answers the top five calls (the hand-back list) and Q1–Q14. Unanswered items take the defaults
  above, logged under "Open questions for the designer".
- **0b.** Merge this branch into main. It is tools and docs only: 461 files under docs/design, 74 under
  tools/raid_concepts, plus the raid labs; no scripts/ or content/ file. Leave out the uncommitted `project.godot`
  change (someone else's).
  - *Acceptance:* main parses; the fast tier is green; the `tools/raid_lab_city` parity check still passes from main.
  - *Lane:* AGENT (fix-mechanical).
- **0c.** One DECISIONS entry, "Raid: the sweep model (Solace)", carrying the rulings.
  - *Lane:* BATCH draft, orchestrator review.

### Phase 1: The graph oracle (tools only; Python)
- `tools/raid_concepts/sweep_g1.py` generalizes `sweep_l8.py`:
  - it takes the geometry as input (spokes, streets, values, exploits) instead of the 4×3 lattice;
  - it keeps the L14 rule set and the L13 / L14 metrics;
  - it adds an overlap metric: the share of owned Sites on ≥ 2 candidate lines.
- An exporter writes Solace territory snapshots from `CampaignSimulator` campaigns (one at each queued raid) to JSON.
- **Acceptance:**
  - (1) on the lattice fixture, `sweep_g1.py` reproduces `l8_golden.json` exactly (regression);
  - (2) over 200 Solace snapshots: greedy breach 0%, naive breach ≥ 40%, `response_decides` ≥ 45%, mean distinct
    placements ≥ 3, overlap ≥ 30%;
  - (3) a fail on (2) blocks Phase 2 and goes to the designer with the content fix (§6 R-4).
- *Tests:* the oracle's own golden; no Godot. *Lane:* BATCH (port draft) + AGENT (run, measure).

### Phase 2: Core port (scripts/core, scripts/state, scripts/data)
- **2a.** `SweepGeometry` + its tests:
  - `test_sweep_geometry.gd`: candidate order, padding, street rules, ties by id, and the Solace golden from Phase 1.
- **2b.** `SweepRules` / `SweepResolver` port, `RaidSweepState`, the config fields, the schema fields with smoke checks.
- **Tests (fast tier, added to `tests/test_manifest.json`):**
  - `test_sweep_parity.gd`: the lattice golden plus 3 Solace goldens, field by field, as `parity_check.gd` did;
  - `test_sweep_preview.gd`: for every A × B × hunter × legal response, `forecast` == `resolve` == `apply` state;
  - `test_sweep_replay.gd`: a seeded campaign replay of 3 raids matches its hash;
  - `test_sweep_rewind.gd`: PLAN undo works and can never cross the LAUNCH checkpoint; the hidden draws are unchanged
    after a quit and reload;
  - `test_sweep_ties.gd`.
- **Acceptance:** all green; no other test changes; the non-Solace corps are byte-identical (`raid_model` switch).
- *Lane:* AGENT (fix-rules, Sonnet), with BATCH for test boilerplate.

### Phase 3: Campaign wiring, Solace only
- **Raid lifecycle:**
  - the existing raid triggers queue a sweep raid with its hidden draws (the `raids` stream);
  - `SweepResolver.apply` writes Sites, HOME, Heat, Schematics and wounds;
  - DECAY runs at raid start.
- **Cards and decks:**
  - the defense deck reads `armory`, and banking adds cards;
  - wounds are injected at jack-in (the `_apply_bug_cards` pattern), and Mainframe removal clears the campaign wound;
  - HQ rules for BUILD and CLEAN (prices in config);
  - station bonuses become hand cards.
- **Save and sims:**
  - a save version bump;
  - a `CampaignSimulator` raid policy (greedy / careless).
- **Tests:**
  - `test_sweep_apply.gd` (the projection's deltas == the applied campaign);
  - `test_wound_cards.gd` (TAKEN → wound → curse in the next run deck → Mainframe removal clears it);
  - `test_defense_deck.gd`;
  - `test_save_sweep.gd` (quit at PLAN and at RESPONSE resume exactly);
  - `test_raid_model_switch.gd`.
- **Acceptance:**
  - 200 Solace sims finish;
  - reported: raids per campaign, breach rate per policy, wounds per campaign, Heat at breach, and the share of
    campaign minutes in raids (the §6 R-1 estimate);
  - every number lands in a DECISIONS entry.
- *Lane:* AGENT (fix-rules).

### Phase 4: Vertical slice UI (Solace): THE FIRST PLAYABLE TARGET
- **The flow:** the HQ RAID band hosts the sweep:
  1. a hand row at the bottom; select a card, then a Site marker;
  2. G for the ghost, Z to undo, Enter to see the forecast;
  3. the forecast table and the LAUNCH confirm (the L16 / L17 guard lines);
  4. the playout through `RaidBeats` with the lab's beam, vehicle and hound effects;
  5. response rows with inline results;
  6. the AFTERMATH stamp (D28 verdict + tier) and wound cards flying to the deck strip.
- **The look and its limits:**
  - the board is the real Solace territory in `CityView3D`, not `l8_board.gd`;
  - "Grid stays night" (`city.md`) holds; the lab's brighter look is limited to beams and markers (§6 R-6).
- **Acceptance (the vertical slice):**
  - a fresh Solace campaign (`campaign_focus_corp = solace`) reaches its first Heat-25 raid;
  - the raid plays on the city at the RAID band with mouse and keyboard;
  - the shown forecast row equals the played result;
  - a TAKEN Site adds a BACKDOOR card that appears in the next netrun's draw pile;
  - quit at RESPONSE and Continue resumes there.
- **Tests:** one flow test, `test_flow_raid_sweep.gd` (headless, bounded waits), plus the capture sheet (D20). No view
  unit tests.
- *Lane:* AGENT (fix-visual) + CAPTURE.

### Phase 5: The mid-run interlude and the zoom seam
- The netrun interlude (`NetrunSession._maybe_raid_interlude`, `RunState.Phase.RAID`) plays the same sweep:
  1. jack-out zoom from the street to the RAID band;
  2. the raid;
  3. a dive back to the same node.
- It keeps the HQ_REDESIGN Q3 rule: you may jack in with a raid pending.
- *Acceptance:* the interlude raid == the HQ raid for the same state (a test on the core); the flow test passes; the
  capture sheet is made.
- *Lane:* AGENT (fix-visual) + CAPTURE.

### Phase 6: Measure the real build
- A fresh calibrated critic on motion captures of the real build (per "critic runs fresh, with screenshots").
- One batch of Claude playtesters, Solace only.
- *Acceptance:* total ≥ 39 (the lab best) with Fit ≥ 8. If the total is below that, the gap list goes to Phase 7, not
  to more polish.
- *Lane:* OPUS critic, playtester agents.

### Phase 7: Rule levers with real cards (R17 → R16 → R15)
- **R17, richer cards.** The 8 assets get one second effect each from existing verbs. Examples:
  - decoy: a ghost charge;
  - ICE lock: JAM;
  - tar pit: blocks two types;
  - honeypot: a free SACRIFICE with no wound.
- **R16:** per-response costs on Heat, wounds and value.
- **R15:** SHIFT acts after REVEAL B, *or* JAM also cancels sealed B (measure both).
- **The method for each:** oracle round in `sweep_g1.py` → golden → port → re-measure → critic.
- *Acceptance per lever:* `response_decides` or the share of non-LOCKED raids rises by ≥ 10 points with no greedy
  breach.
- *Lane:* BATCH (oracle rounds) + AGENT (port).

### Phase 8: Out of raid scope (flagged, not planned here)
- seamless GRID ↔ NETRUN in one scene (a tech spike);
- building-scale graphs for ordinary Sites (the vision's "traverse buildings");
- card upgrades and slice rearranging (missing today);
- GDD v0.9 content counts;
- the other corps' sweep patterns (on hold).
- After Phase 6, `RaidResolver` retires for Solace. It is deleted only when the last corp is ported.

---

## 6. Risks and open questions (each with a recommended default)

- **R-1. The time split between raids and netruns.**
  - GDD 11.8 sets netrun ≈ 15 min, raid ≈ 5 min, 3–7 raids per campaign.
  - SOLACE_BAL_r1 measured 24–60 runs per reference campaign (DECISIONS 2026-10-20). Thresholds fire once, so raids
    become rare relative to runs and the corp's turn disappears from the loop.
  - *Default:* target one raid per 2–3 netruns, with raids at about 20% of campaign minutes (§1.1). Keep the
    threshold raids. Add a config "pressure" trigger: a raid every `raid_runs_between` completed runs (3) when none fired.
  - Phase 3 measures it. Changing the trigger needs a GDD 4.4 amendment, so it is a designer question.
- **R-2. R15–R17 once real cards exist.**
  - The critics put D and S as rules-limited at 6 and 5–6 (L15–L17).
  - Real assets give richer cards for free (R17), and real geometry changes how often raids are LOCKED at PLAN.
  - *Default:* port L14 unchanged, measure on Solace geometry in Phase 1 and Phase 3, then apply R17 → R16 → R15 in
    that order in Phase 7. Do not port a lever the lab never measured.
- **R-3. Seamless zoom tech.**
  - `CityView3D` already zooms continuously across GRID and RAID in one model (`city_spike_report.md`, 2.5–2.8 ms per
    frame) *(digest)*.
  - Netrun and combat are separate scenes joined by `RunManager.go_to_netrun` / `go_to_hq` and the jack Fx.
  - *Default:* GRID ↔ RAID is seamless now (HQ_REDESIGN Q4). RAID ↔ NETRUN stays a scene change, masked by the
    jack-in dive. A one-scene spike is Phase 8 and is not a dependency of the raid.
- **R-4. Real geometry may kill overlap.**
  - The Solace Grid is a star (10 spokes). Early territory is 2–4 T1 Sites on different spokes, so routes are
    disjoint and one sentry per route is obvious.
  - *Default:* Q3's "corp uses locked cross-links" plus tier rings. If Phase 1 overlap is < 30%, propose a content
    change (one cross-link per T1 pair) to the designer. Never change the rules in scripts/ to hide it.
- **R-5. Save migration.**
  - Compatibility is not required (ruling 2026-10-05).
  - *Default:* bump the version; a pre-sweep save with `pending_raids` loads with those raids requeued under the sweep
    model (hidden draws made on load from the `raids` stream). A save mid-old-raid restarts that raid at PLAN. Say so
    in each report.
- **R-6. Look ownership.**
  - The art-pass owns the Godot look; the raid lab owns its own look (designer 2026-10-22). The lab's brightness
    conflicts with "Grid stays night".
  - *Default:* the raid's beams, markers, cards and hound are raid-lab-owned. The city stays the art-pass night city. A
    comparison sheet goes to the art-pass mailbox before merge.
- **R-7. Branch base.**
  - This branch is 71 commits ahead of its merge-base with main, and main is 165 ahead of that base.
  - The branch touches no `scripts/` or `content/` file, so conflicts are unlikely, but main's
    `scripts/data/campaign_config_data.gd` moved.
  - *Default:* Phase 0b merges this branch into main first. Every integration slice is cut from main
    (`raid-int/<phase>`), never from this branch.
- **R-8. A dual model during migration.**
  - Two raid models live side by side until every corp ports.
  - *Default:* one switch (`raid_model_by_corp`). A test pins non-Solace byte-identity. No code path mixes the two
    results.
- **R-9. Critic noise and plateau.**
  - ±3 noise; presentation plateaued at 36–39.
  - *Default:* gate on measured rule metrics (Phase 1, 3, 7 acceptance), not on the critic total. Use the critic only
    at Phase 6 and after each lever.
- **R-10. Stale lab docs mislead porters.**
  - `docs/handoff/raid_lab_l8/SPEC.md` still says one sealed beam and HOT ×1.5; the lab README still mentions SCAN.
  - *Default:* the port reads `sweep_l8.py` + `L14_RULES.md` only. Phase 0b adds a one-line "superseded by L14_RULES"
    note to SPEC.md.
- **R-11. Wound punishment stacks.**
  - A wound is a dead raid draw *and* a curse in every netrun deck.
  - *Default:* both, behind `wound_into_run_deck` (on). Phase 3 measures netrun win-rate impact per wound. If it costs
    more than one Elite's worth, it injects only into the next run instead.
