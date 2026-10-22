# Raid concepts, round 3: critic review (fresh, independent)

Scope: SPEC_R3 for G, C, D, E and F, RULES_PACKAGE.md, all 56 r3 frames (plain and scrambled), the rule code behind the numbers (`sim.py`, `c3_rules.py`, `d3_lane_sim.py`, `concept_e3_countdown.py`), and 13 games' screenshots. Polish is not scored.
Calibration: 7 means a good shipped game does about this well. 9 to 10 means best in class (Into the Breach's telegraph).

## 1. Scores

| Concept | What / why / when | Predictability | No-words | Decision depth | Consequences | **Total** | Verdict |
|---|---|---|---|---|---|---|---|
| **G** Merged Telegraph | 8 | 7 | 6 | 6 | 8 | **35** | The only one built on the real resolver, and it shows. The best base, but there are hidden numbers in the strike values. |
| **E** Countdown + Allocation | 8 | 5 | 5 | 7 | 5 | **30** | It has the best "when" and the only real timing or sacrifice decision. But the rule is an abstract sum, and nothing fights. |
| **D** Auto-battler Loadout | 6 | 7 | 6 | 4 | 5 | **28** | The lane strips are honest, but the map is decoration, and the puzzle has 540 plans. |
| **F** Plan Ledger | 6 | 7 | 6 | 5 | 4 | **28** | It has G's maths behind a spreadsheet. It works as an inspect drawer, not as the screen. |
| **C** Strength Duel | 6 | 5 | 4 | 5 | 5 | **25** | The banners read as a fight but compute a sum. The "clean" result costs 28 integrity, and the playout has nothing in it to watch. |

## 2. Per concept

### G: Merged Telegraph (35)
**Justification**
- **What / why / when 8.** `0_netrun.png` puts the cause (Heat 51 > 50), the countdown dial (2 map nodes) and the three threat chips on the netrun map. This is the clearest "it's coming, because of you, in 2 nodes" in the set.
  - The dial counts *map nodes*, while E's dial counts *netruns*. The same glyph is used for different units, and nothing in the image says which. That keeps this axis from a 9.
- **Predictability 7.** `1_warning.png` draws every fixed route end to end, with per-node outcome tags. `3_planning.png` gives a live "lost 2 > 1" what-if, and the forecast plan rows (`4_forecast.png`) price each plan in the report's own units. That is the Into the Breach contract, nearly. Four numbers break it:
  - **Cascade damage goes undrawn in the warning frame.** SAFEHOUSE −3 and part of VAULT's loss in `1_warning.png` come from the PROXY spill. The spill arrows first appear in `3_planning.png`. A tag with no visible cause is a broken promise.
  - **Shown damage does not match the card.** The draft cards say Turret 4 and Railgun 8. `5_resolution.png` shows −6 and −12. That is `CREW_MULT = 1.5` in `sim.py`, which G never shows: the Breaker sits on RELAY with no ×1.5 mark. F's card shows it; G's does not.
  - **FIREWALL −2 in `7_next_raid.png`** has no route or spill that explains it.
  - **RELAY is TAKEN in `7_next_raid.png` but its pips still show 2 of 3 filled.**
- **No-words 6.**
  - In the scrambled frames, routes, flags with red X, teal checks with red corners and the Heat chip all survive.
  - **Turret, Sentry and Railgun are all crosshairs.** At map scale (`scrambled/4_forecast.png`, the plan-1 row "⌖ ✱ ⌖") the turret and the railgun cannot be told apart.
  - **"2 > 1" chips need words to mean "lost before > after".**
  - **The CLEAN stamp's meaning rides on teal alone.**
- **Decision depth 6.**
  - The draft plus placement gives two real clean plans: plan 1 (patch 8) and plan 2 (patch 38). They make a genuine "cheap or flexible" choice.
  - But the draft (`2_draft.png`) is blind: no card tells you what it would do to *this* raid. Planning is then trial and error over a small space (12,960 plans, ~5 % clean), with the what-if counter as the oracle. That is close to a spreadsheet with a map skin.
- **Consequences 8.**
  - SCUFFED is persistent and priced (`6_aftermath.png`: RELAY −5 → 5, PROXY −3 → 3).
  - `7_next_raid.png` (an unpatched RELAY draws the Enforcer; 3 lost against 2) is the best causal link in the whole lab.
  - What is missing: there is no run-level record of raids survived, and the Heat +5 "reward" moves the next raid closer, a mixed signal (see Barriers).

**Three biggest problems**
1. Hidden modifiers (crew ×1.5, the cascade in the warning frame) mean the shown numbers do not match the cards.
2. The draft is blind: no per-card preview against the current raid.
3. There are only 4 steps of playout. A D26 floor of 20 s means 5 s or more per step, which is padding, not spectacle.

**Three most valuable ideas**
1. The fixed route drawn end to end, with outcome tags on the map (R1 made visible).
2. The next-raid frame: unpatched SCUFFED integrity bends the next route (R3 × C2).
3. Plan rows priced in the report's units before commit (C8), with the clean payout shown net.

**Refs**
- Kingdom Rush route plus wave flag (prior set): `sheet_01`.
- Thronefall icons at the spawn: `sheet_01`.
- PvZ seed select: `sheet_02`.
- Into the Breach numbered order and Super Auto Pets controls: `sheet_03`.
- Backpack Battles wins/tries: `sheet_08`.

**+2 per axis**
- **What / why / when:** one countdown unit across the game (netruns, or nodes with a node glyph inside the dial). Add a raid-size preview (threat count by Heat tier) at the 25/50/75 ticks of the Heat bar.
- **Predictability:**
  - Draw the cascade spills in the warning frame.
  - Print the *effective* damage on each placed piece (turret "6" when boosted) and a ×1.5 badge on the Breaker's node.
  - The forecast must equal the playout, number for number.
- **No-words:** three distinct silhouettes for Turret (crosshair), Sentry (twin barrels) and Railgun (long beam). Replace "2 > 1" with a struck-through count.
- **Decision depth:**
  - Each draft card previews its best single placement's effect ("with this card: lost 2 > 1").
  - Add one threat with a conditional (it skips nodes with ICE, or it targets your highest-value *asset*) so placement is not pure enumeration.
- **Consequences:**
  - A persistent raid record on the campaign map.
  - Reward that does not raise Heat (see D27).
  - Show the net Schematics (+12 − patch).

### E: Countdown + Allocation (30)
**Justification**
- **What / why / when 8.** `1_warning.png` has a big netrun countdown (2), the Heat cause, and the cobalt hatched front waiting at the map edge. "When" here is a resource: two HQ visits (`2_planning.png` → `3_forecast.png`).
- **Predictability 5.** The gauges are exact against `concept_e3_countdown.py` (PROXY notch 30, fill 8 + Railgun 8 = 16, −14). But the gauge is a sum:
  - threat integrity is irrelevant, and turrets never kill anything;
  - ICE is a "+5 fill", not R4's "frozen threat neither moves nor strikes", so the package's rule is not what the player sees;
  - **the frames disagree on Heat.** It is 53 at visit 2, 55 during the playout (`4_resolution.png`), then 56 after a +5 clean payout (`5_aftermath.png`), and 55 + 5 ≠ 56.
- **No-words 5.**
  - The gauge plus cobalt notch reads as "the bar must reach the line", which is good.
  - The playout's sweeping wall (`scrambled/4_resolution.png`) erases who hits whom.
  - The crew-hour "+2 +2 +2" chips are text-dependent.
- **Decision depth 7.**
  - Two visits make allocation over time a real decision.
  - Plan 2 (`3_forecast.png`) gives PROXY up on purpose: patch 0, a netrun to reclaim, a new entry point. That is the only *sacrifice* trade in the lab, the kind of decision that makes Into the Breach and Frostpunk memorable.
- **Consequences 5.**
  - The "clean" plan 1 costs 33 to patch against a +12 payout, so clean is a net loss of 21.
  - There is no next-raid link.

**Three biggest problems**
1. An additive gauge rule is not the game's resolver, so adopting it means a new resolver with no fiction of combat.
2. The playout is a wall sweeping left, which is unwatchable as an auto-battler.
3. The Heat figures disagree across frames, and the clean reward is a net loss.

**Three most valuable ideas**
1. The netrun countdown with two HQ visits (timing as a resource).
2. The deliberate sacrifice plan, priced before commit.
3. Gauges as the per-node "will it hold" read: a notch against a fill.

**Refs**
- Kingdom Rush wave call (prior set): `sheet_06`.
- No-words comparison: `sheet_09`.

**+2 per axis**
- **Predictability:** drive the gauges from `sim.py` (the notch = the strikes the resolver would land), and keep R4 ICE literal.
- **No-words:** draw each threat's icon riding into its notch. Show crew-hours as figures, not "+2" text.
- **Consequences:** add a next-raid frame, and show the net payout.
- **What / why / when:** already high. Add a raid-size tier preview on the dial.
- **Decision depth:** let visit 1 choices lock (installed pieces stay), so the order of the visits matters.

### D: Auto-battler Loadout (28)
**Justification**
- **What / why / when 6.** `1_warning.png` shows the cause and the lineup, but there is no countdown in time.
- **Predictability 7.**
  - The per-lane strips (`3_forecast.png`) match `d3_lane_sim.py` tick by tick: ICE boosted to 3 ticks, Railgun 8 ×2 on the Enforcer, a kill at tick 2, PROXY −9. That is exact.
  - But the map lies. The Collector's arrow runs RELAY → FIREWALL → HOME, against R3 (VAULT 20 is weaker than FW 30; G, C and E all route via VAULT).
  - RELAY, FIREWALL and SAFEHOUSE can never be hit. "Damage in passing" (C5) is gone.
- **No-words 6.** Diamonds, skulls and frozen teal diamonds read. The slot "+" boxes invite drops. The strip is still a table.
- **Decision depth 4.** It has 3 lanes × 2 slots and 540 plans, 10 of them clean. The railgun's "highest damage within 2 hops" is the only coupling. It is mostly a matching exercise.
- **Consequences 5.** The aftermath is fine, but there is no next-raid link, and lanes make the network graph meaningless for the campaign.

**Three biggest problems**
1. The map is decoration, and nodes that are not lanes are immune.
2. The route drawn contradicts the package's own tie-break.
3. The puzzle is shallow (assignment, not geometry).

**Three most valuable ideas**
1. The per-threat tick strip as an exact forecast (G already borrows it).
2. The "drop here" slot preview with a before/after chip (`2_planning.png`, "⚡ → ✓").
3. Lanes ticking side by side read like an auto-battler (Super Auto Pets, Legion TD 2).

**Refs**
- Mechabellum pre-fight board and Legion TD 2 placement: `sheet_05`.
- Super Auto Pets playout controls: `sheet_03`.

**+2 per axis**
- **Decision depth and consequences:** put the lanes back on the graph (the threat walks the route, a lane per *route*), which is G's model.
- **Predictability:** fix the drawn route.
- **What / why / when:** add a countdown.

### F: Plan Ledger (28)
**Justification**
- **What / why / when 6.** `1_warning.png`'s "decrypted orders" panel is good fiction, with icon routes per threat, but there is no netrun countdown frame.
- **Predictability 7.** It has every step for every threat (`2_planning.png`, `3_forecast.png`), and the totals row matches `sim.py`. But it shares G's gaps:
  - SAFEHOUSE 20 > 17 in the bare totals has no ledger cell causing it (the cascade has no row);
  - the ×1.5 crew card is shown but its effect is not.
- **No-words 6.** The icon cells survive scrambling, but reading a 3 × 6 grid is a skill, not a glance.
- **Decision depth 5.** The puzzle is the same as G's, but the spatial reasoning moves to a thumbnail map, so it feels like editing a spreadsheet.
- **Consequences 4.**
  - `5_aftermath.png` carries no SCUFFED marks on the map.
  - Heat stays 51 after a +5 clean payout, which contradicts G's identical run (51 → 56).
  - The Firewall glyph changes to bricks.
  - There is no next-raid frame.

**Three biggest problems**
1. A table is the primary view, which is wrong for a hands-off watch.
2. The aftermath does not persist on the map, and its Heat is wrong.
3. The cascade is missing from the ledger.

**Three most valuable ideas**
1. The ledger as a complete, signed forecast (a drawer in G).
2. Hatched cells for frozen steps, and a skull where a threat dies.
3. "Sign orders" as the commit verb.

**Refs**
- Backpack Battles combat log: `sheet_07`.

**+2 per axis**
- **Overall:** fold F into G as an expandable per-threat drawer. Its scores then become G's.
- **Consequences:** mark the map and fix the Heat.

### C: Strength Duel (25)
**Justification**
- **What / why / when 6.** It has the cause and the routes (`1_warning.png`), but no countdown.
- **Predictability 5.** It is consistent with `c3_rules.py`, but the banner's comparison misleads.
  - The rule is loss = ATK − bonuses, and the banner shows ATK : (integrity + bonuses). PROXY 21 : 26 in `3_forecast.png` reads as a win, yet costs 10 integrity. HOME 15 : 50 in `1_warning.png` costs 15.
  - "Tightest margin 3 on RELAY" is the margin to DOWN, not to holding. RELAY actually loses 12 of 15.
  - ICE is redefined ("cancels the biggest strike") against R4.
- **No-words 4.** Without words, the banner numbers *are* the rule, and the multiplier glyph "×3" is still a letter (`scrambled/2_planning.png`).
- **Decision depth 5.** It has 127 clean plans of 12,960, but all bonuses are additive, so the plan is arithmetic.
- **Consequences 5.** The clean stamp lands on 28 points of damage (`5_aftermath.png`: −12, −10, −6), a net loss of 16 against +12. "CLEAN DEFENSE" is cheapened.
- **Hands-off fit is the worst of the set.** `4_resolution.png` is a bar filling 14/21 against 26. Nothing moves, dies or blocks.

**Three biggest problems**
1. A sum dressed as a duel misleads, both in the banner reading and in the playout.
2. "Clean" includes near-DOWN nodes and is a net loss.
3. It needs its own resolver, and the threats' integrity is meaningless.

**Three most valuable ideas**
1. A single "how close" margin per node (worth adding to G's tags as a pip count).
2. A biggest-first, home-last duel order as a *camera* order for G's playout.
3. A banner per target with small banners on the nodes passed (it visualises C5).

**Refs**
- Backpack Battles watched fight: `sheet_04`.

**+2 per axis**
- **Predictability and consequences:** change the banner to "ATK − bonus = loss" with the pips struck through.
- **Hands-off fit:** make the playout real hits.
- **Decision depth:** these changes turn C into G, which is the honest recommendation.

## 3. Ranking and recommendation
**Ranking:** G (35) > E (30) > D (28) = F (28) > C (25).

**Take forward:** **G**, and **E** as a donor rather than a rival.

**Steals:**
- **G steals from E:**
  - the netrun countdown with two HQ visits (allocation over time);
  - the priced sacrifice plan, shown as a plan row ("give up PROXY: patch 0, 1 netrun to reclaim, +1 entry point");
  - the per-node notch-against-fill gauge as a hover read, fed by `sim.py`.
- **G steals from F:** the ledger as a drawer per threat, with hatched frozen cells and skulls.
- **G steals from D:** the "drop here: ⚡ → ✓" chip on the slot while dragging.
- **G steals from C:** a margin pip on each HOLDS tag ("held with 3 to spare"), and the biggest-first camera order in the playout.

**Prototype first: G.** Its numbers come from `sim.py`, a mirror of `raid_resolver.gd`, so the prototype tests the real rules plus five toggles. It does not invent a resolver, as C, D and E all would. The package's metrics (0 retargets, 0 home surprises, 57.6 % one-move change) were measured on exactly this model. Build it with the forecast exposing `route` per threat, as the migration notes say, and make "the forecast equals the playout" the first rule test.

**Rule-change cost, by item:**

| Item | Verdict |
|---|---|
| R1 fixed routes | Worth it; essential. Without it no telegraph is true. |
| R2 home is never a corridor | Worth it; cheap. |
| R3 weaker-node tie | Worth it. It is what makes the next-raid frame work. |
| R4 ICE blocks the strike | Worth it. One meaning per glyph. |
| R5 3-of-5 draft | Worth it *only* with per-card previews. A blind draft adds a guess, not depth. |
| C1 clean = home untouched, nothing DOWN or TAKEN | Worth it. Show the net payout, or SCUFFED-heavy "clean" plans become traps (C, E). |
| C2 SCUFFED priced | Worth it; best value in the package. |
| C3 cascade | Cut it rather than draw it. It is the one hidden-cause source left in G. If kept, it must be in the warning frame. |
| C7 on return | Worth it. E's two-visit form is better still. |
| C8 price before commit | Worth it. |
| C's, D's and E's own resolvers | Not worth it. Each costs a new resolver and loses the fiction. |

## 4. Barriers (what keeps G below 9 on any axis). All are designer decisions.

| # | Barrier | Axis capped | Change that lifts it | Cost |
|---|---|---|---|---|
| B1 | **D27: a clean defense *gains* Heat (+5).** The reward pulls the next raid closer, and the payout screen shows a "bad" orange flame as a prize. | Consequences, what/why | Clean pays Schematics and *holds* Heat (+0), or lowers it (−3). Any damage still pays nothing. | Economy retune of the Heat curve. D27 is revised. |
| B2 | **D27 is binary ("any damage gains none")** while ~95 % of plans are not clean. Most plans tie at zero payout, so the gradient for "a better bad plan" is only the patch price. | Decision depth, consequences | A graded payout: +12 for clean, +6 if home is untouched and ≤ 1 node DOWN, 0 otherwise. Or always show the net (payout − patch) as the plan's score. | A small economy change. The forecast already computes it. |
| B3 | **C1: SCUFFED counts as clean**, so a "clean" plan can be a net loss (G plan 2: 38 patch against +12; C −16; E −21). The stamp lies about value. | Consequences | Show CLEAN with its net Schematics. Or clean requires a total patch ≤ the payout. | View work, or one rule line. |
| B4 | **D26: a step-locked 20–40 s playout** against a 4-step raid gives 5–10 s per step, which is padding, or else it breaks the floor. | Hands-off fit, no-words | Lock to *beats* (each numbered shot or strike is ~1 s), so the length follows the event count and is capped at 40 s. Add a rewind (Super Auto Pets has one). | View timing. D26 is reworded. |
| B5 | **D28: the verdict is only CELL HOLDS or BREACHED.** A raid that loses two nodes and a clean one both read "CELL HOLDS". The mockups already add CLEAN DEFENSE as a de facto third word. | Consequences | Make it official: three tiers (CLEAN / HOLDS with loss icons / BREACHED). The node tags stay DOWN or TAKEN. | A ruling change and strings only. |
| B6 | **Cobalt threats on a navy field.** The thin cobalt routes go dim under overlays (`2_draft.png`). Threat HP pips are light blue, next to the teal HOLDS and the cobalt TAKEN flag: four blues. | No-words | Keep cobalt, but give the routes a white core with a moving dash. Make threat HP pips white, and keep blue for threat identity only. | Low; view only. |
| B7 | **C3: the cascade is a hidden damage source** (SAFEHOUSE −3 with no arrow in `1_warning.png`). | Predictability | Cut the cascade (the lab's metrics hardly need it), or draw it in every frame. | A resolver line and tests, or view work. |
| B8 | **Hidden multiplier (`CREW_MULT` 1.5).** The cards say 4/8, the playout says 6/12. | Predictability, no-words | Show effective values on placed pieces, with a ×1.5 badge on the node. Or make the Breaker additive (+2). | View, or a content tweak. |
| B9 | **Content: turret, sentry and railgun share one silhouette.** | No-words | Distinct silhouettes per piece. | Art (art-pass owns the look). |
| B10 | **Content scale: 3 threats, 5 pieces, 6 nodes**, so the plan space is brute-forceable (12,960) and the what-if counter solves it. | Decision depth | One conditional threat per corp (it avoids ICE, or targets the highest asset value), or one node rule (FW gun reach), so placement has geometry, not just arithmetic. Keep the setup at a few minutes. | Content and resolver work, a new rule test. |
| B11 | **R5's blind draft.** | Decision depth | A per-card preview of its best effect on this raid. | View only. The sim already enumerates. |
| B12 | **C7 lands the raid always on return**, so timing is not a decision. | What/why, decision depth | E's two HQ visits: the raid is announced 2 netruns out, and visit 1 placements persist. | A campaign-flow change. GDD 4.4 is revised. |
| B13 | **The playout's ceiling under hands-off (rule 4 of the pitch).** With zero input, satisfaction relies on legible cause and effect only. | Hands-off fit | Numbered shots (Into the Breach), a kill-cam on the biggest hit, rewind and skip. No new rule is needed. | View. |

With B1–B4, B7, B8 and B11, G's predictability and consequences can reach 9. Decision depth needs B10 and B12 to pass 7.

## 5. Sheets built (`D:/rc_tmp/raid_design_lab/critic_r3/`)
- `sheet_01_route_telegraph.jpg`: G warning, Kingdom Rush wave call, Thronefall spawn icons.
- `sheet_02_draft_vs_preview.jpg`: G draft, PvZ Choose Your Plants, Rogue Tower card draft.
- `sheet_03_playout_order.jpg`: G resolution, Into the Breach numbered order, Super Auto Pets replay controls.
- `sheet_04_duel_vs_real_fight.jpg`: C forecast and resolution, the Backpack Battles fight.
- `sheet_05_lanes_pre_fight.jpg`: D forecast, the Mechabellum pre-fight board, Legion TD 2 placement.
- `sheet_06_countdown.jpg`: E warning and resolution, Kingdom Rush wave call.
- `sheet_07_ledger_vs_log.jpg`: F forecast and aftermath, the Backpack Battles combat log.
- `sheet_08_aftermath_persistence.jpg`: G aftermath and next raid, the Backpack Battles wins/tries.
- `sheet_09_no_words.jpg`: scrambled G forecast, C planning and E planning (the crosshair collision).
- `contacts/*.jpg`: reference contact sheets used for picking.

New downloads: `refs/legion_td2/` (8) and `refs/itb_r3/` (6), cited with reused prior URLs in `refs/SOURCES_R3.tsv`.
