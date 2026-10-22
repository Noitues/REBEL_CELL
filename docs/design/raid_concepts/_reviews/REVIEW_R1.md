# Raid design lab: critic review, round 1

Reviewer: fresh critic. I read no earlier reviews. Sources: all six SPECs, the README, and all 60 frames (30 plain, 30 scrambled).
References: `refs/` (Steam CDN screenshots recorded in `refs/SOURCES_R1.tsv`, plus the prior set). I did not score visual polish.

## 1. Score table

| Concept | What/why/when | Predictability | No-words | Decision depth | Consequences | **Total /50** | Verdict |
|---|---|---|---|---|---|---|---|
| A Telegraph | 8 | 8 | 7 | 6 | 7 | **36** | Best base. It is honest to the resolver and plays back exactly what it showed. Its forecast panel drops the home damage. |
| B Siege Lanes | 8 | 6 | 6 | 6 | 8 | **34** | Best read of *where* they come from, and best consequences. The HP-chip stacks are unreadable clutter. |
| C Strength Duel | 7 | 6 | 7 | 3 | 5 | **28** | Clear at a glance and shallow on contact. Its own TAKEN banner breaks its own 2× rule. |
| D Auto-battler Loadout | 6 | 4 | 8 | 7 | 4 | **29** | Best no-words test and the most interesting slotting. It throws the map away, and it shows CLEAN DEFENSE over a node that just took −9. |
| E Countdown + Allocation | 9 | 4 | 6 | 6 | 6 | **31** | Best telegraph of *when*. The gauges contradict themselves, and the execution is a 20 s wipe with nothing to watch. |
| F Plan Ledger | 7 | 6 | 3 | 6 | 4 | **26** | It promises "guaranteed" and then maps damage to DOWN/TAKEN inconsistently. A spreadsheet is the main screen, and watching a cursor walk it is not a show. |

Calibration: Into the Breach's on-board telegraph is the 9–10 bar for predictability (`refs/prior/itb/steam_03.jpg`). Super Auto Pets' two-number unit is the 9 bar for no-words (`refs/super_auto_pets/steam_02.jpg`). The XCOM 2 Avatar clock is the 8–9 bar for "when" (`refs/prior/xcom2/Avatar_Project.jpg`).

Cross-cutting faults:
- **Inconsistent mockup data** appears in A, C, D, E and F. A predictability concept that contradicts its own forecast fails that axis, so I scored the mockup data as drawn.
- **The verdict stamp has the same yellow frame for CELL HOLDS in every concept.** Without words, HOLDS-with-losses is told from a clean result only by teal versus yellow; no icon says what was lost. Put the loss icons (bolt, flag) *in* the stamp.
- **HOLDS is used for damaged nodes** (A Relay 15 > 10, B Firewall striped pips, F Firewall 30-5). A damaged node that holds is exactly what spoils a clean defense. It needs a third state mark ("held, damaged": a teal check with a red notch). Otherwise the clean bonus is hidden behind a word, which fails the no-words test.

---

## 2. Per concept

### A — Telegraph (36)

**Scores.**
- **What/why/when 8.**
  - `1_warning.png`: the Heat bar with its 50 notch and the cobalt shield under it gives the *why*. The "this netrun" track ending in the HQ house gives the *when*. The silhouettes ×3 give the *who*.
  - In the scrambled `1_warning`, all of it survives except "strikes when you return": the house-with-shield icon carries it.
  - It loses 2 because the warning shows no routes yet. You cannot see where they are going until planning.
- **Predictability 8.**
  - `2_planning.png`: numbered strike badges, damage chips, red-striped projected pips and an attack-order panel. This is Into the Breach almost verbatim (sheet s01).
  - `3_forecast.png` tags every node with its end-of-raid result.
  - Penalty: the END OF RAID panel lists Relay, Vault and Proxy but **not HOME 50 > 45**. The home damage first appears on the `5_aftermath` stamp. The one number that ends campaigns is missing from the forecast.
  - The scrubber shows one step at a time, so the player has to scrub six steps to build the picture. Into the Breach only ever shows one turn.
- **No-words 7.**
  - The scrambled `2_planning` and `3_forecast` stay readable: numbered badges, arrows, red rings, check and bolt tags.
  - The yellow "PROXY −9 → −0" what-if tag survives because it is digits.
  - It loses points on the asset cards, whose stats are lost (scrambled "4 sau, imbwf 1"), and on the stamp.
- **Decision depth 6.**
  - Four pieces on six nodes, with ordering mattering (ICE first, then turret), is a real small puzzle.
  - In the shown scenario, ICE on the Enforcer is the obvious first move. I saw no frame where two placements trade off against each other.
  - The depth depends on content, not on the UI.
- **Consequences 7.**
  - `5_aftermath.png`: the stamp's cost line, the DOWN bolt left on the map, and the cost card with the missed clean bonus "(CLEAN = +5, +12)". That last item is a good motivator.
  - The TAKEN entry arrow is in the SPEC but in no frame.

**Biggest problems.**
1. The forecast omits the home-integrity delta. The forecast must list every changed node, home first.
2. Scrubbing six steps is homework. There is no "whole raid at once" summary view: a ghosted overlay of all routes, with each node's total damage.
3. A damaged node shows HOLDS, with nothing to say it breaks clean.

**Most valuable ideas.**
1. Numbered in-step strike order with an attack-order panel. The board then plays back exactly what was shown.
2. The scrubber cells carry tiny silhouettes, so the raid's shape is visible at a glance.
3. The drag-time delta tag at the target (PROXY −9 → −0).

**Refs.** Into the Breach `prior/itb/steam_03.jpg` (sheet s01); Backpack Battles outcome `backpack_battles/steam_02.jpg` (sheet s12).

**To raise each axis by 2.**
- **What/why/when → 10.** Draw the routes faint on the warning frame (steal B's lanes and wave flags). Add E's netrun countdown dial.
- **Predictability → 10.**
  - Add a "ALL STEPS" scrubber cell that overlays the cumulative damage per node.
  - Put home first in the end-of-raid panel.
  - Show a held-damaged state.
- **No-words → 9.**
  - Asset cards show stats as glyphs: crosshair 4, reach ring 1, snowflake ×2 steps.
  - The stamp carries the loss icons.
- **Decision → 8.**
  - Show a "CLEAN NEEDS" gap (from B) so there is a target to optimise toward.
  - Make one scenario where turret coverage and ICE timing compete for the same node.
- **Consequences → 9.** Draw the TAKEN new-entry arrow on the map in the aftermath. Show it again on the *next* raid's warning frame.

**Rule-change cost.** One presentation rule: make the in-step order visible. Free, and worth it.

---

### B — Siege Lanes (34)

**Scores.**
- **What/why/when 8.**
  - `1_warning.png` is the best warning frame of the six. "🔥51 → shield RAID ON RETURN TO HQ" is pure icon and digits and survives the scrambling intact.
  - Wave flags at each entry with silhouettes and ×N; the lanes are drawn *at warning time*. This is the Thronefall / Kingdom Rush convention (sheets s02, s03).
  - It loses points because "when" is a word plus an icon, with no countdown.
- **Predictability 6.**
  - The result panel in `3_forecast.png` (IF THE RAID RUNS, 50 > 50, Proxy TAKEN, skulls 2/3, **CLEAN NEEDS: Enforcer 25 more dmg**) is excellent.
  - The HP ledger chips are a failure. They stack and overlap the nodes: Vault and Proxy each have 2–3 chips piled over the pips in `2_planning`. A chip's leading number is a step number, but it reads as an HP value. The player can't read the per-tick story from them.
  - `4_resolution` shows Proxy as a DOWN bolt at step 3 when the forecast says TAKEN. That is probably a transient state, but nothing says so.
- **No-words 6.**
  - The lanes, arrows and wave flags survive.
  - The routing hints ("shortest to home / richest / weakest") are words, and they are lost in the scrambled `1_warning`. That is the *why it goes there*, so it is a real loss.
  - The reach polygon and yellow tracer lines in `2_planning` read as noise.
- **Decision depth 6.**
  - The "covers 3 lanes · 4 / step" hover is the right idea: coverage is the TD decision.
  - Decoy rerouting with an instant lane redraw is good.
  - It is the same piece set as A, so the depth is equal.
- **Consequences 8.**
  - `5_aftermath.png`: the TAKEN pencil X, a **NEW ENTRY dashed lane stub** toward Safehouse that persists into the next raid's map, and a LOST card naming each loss once with its fix ("PROXY: RECLAIM NETRUN").
  - This is the only concept where a loss visibly changes the next raid's geometry.

**Biggest problems.**
1. The HP chip stacks: unreadable, overlapping nodes, and the step and HP numbers are confusable.
2. The reach polygon crosses every node and lane. There is no clean range ring like Defense Grid 2's green route overlay (sheet s04).
3. The routing intent is text only.

**Most valuable ideas.**
1. CLEAN NEEDS: the gap to a clean defense, with its payout dimmed. It turns the reward into a target.
2. Lanes and wave flags at warning time.
3. A NEW ENTRY lane that persists into the next raid.

**Refs.** Thronefall `thronefall/steam_02.jpg` (s02); Kingdom Rush `prior/kr/LostEmp_Wave_01.png` (s03); Defense Grid 2 `defense_grid2/steam_05.jpg` (s04); Rogue Tower `rogue_tower/steam_09.jpg` (s13).

**To raise each axis by 2.**
- **What/why/when → 10.** Add a countdown and a routing glyph on each wave-flag silhouette: a house for "shortest to home", a coin for "richest", a cracked shield for "weakest".
- **Predictability → 8.**
  - Replace the chip stacks with **one** HP bar riding each lane, with a skull at the death tick. Kingdom Rush and Rogue Tower put the information on the path, not in boxes beside it.
  - Add A's numbered strike badges.
- **No-words → 8.** Use the routing glyphs, and a ring range indicator instead of the polygon.
- **Decision → 8.** Same as A: stage a coverage-versus-timing conflict.
- **Consequences → 10.**
  - Show the new entry *on the next raid's warning frame*.
  - Put the LOST card's fix as an icon path (Proxy → netrun icon).

**Rule-change cost.** None. Pure presentation of today's resolver.

---

### C — Strength Duel (28)

**Scores.**
- **What/why/when 7.** `1_warning.png`: SIEGE DECLARED, Heat 51 > 50, on return, three targets by icon. The banners show who hits what at once. It is clear but not exceptional.
- **Predictability 6.**
  - The banners and the duel card in `2_planning` are the Civ VII preview (sheet s05), and they are legible.
  - **The concept fails its own maths.** The SPEC says TAKEN at ATK ≥ 2 × DEF, but `1_warning` labels Proxy 27 vs 15 TAKEN, and 27 < 30.
  - In `3_forecast`, Proxy DEF 28 = 15 + 8 (turret) + ? and Vault 24 = 20 + ? (ICE shown as +4?). The itemised lines that would explain them are not shown for the final state.
  - In the aftermath, Heat shows 55 on the bar and "51 > 56" in the panel.
- **No-words 7.** The numbers and the two-colour margin bar survive the scrambling. The banner border colour separates HOLDS (teal) from TAKEN (cobalt). There is no flag icon on a TAKEN banner.
- **Decision depth 3.**
  - Three banners. Two hold trivially (home 15 vs 50, Vault 9 vs 20). One real decision: stack Proxy.
  - Flat DEF modifiers turn the puzzle into addition, with no ordering, no geometry and no reach.
  - It is the "single obvious answer" case the rubric warns about.
- **Consequences 5.** The clean stamp and payout are good, and so is "next raid 75" in `5_aftermath`. The HOLDS ticks as a persistent record are noise. Home taking no damage unless ATK > 50 makes home never feel threatened.

**Biggest problems.**
1. Its own TAKEN rule is contradicted on frame 1.
2. One decision per raid, made by adding numbers.
3. Routes are deleted, so the city map becomes a backdrop and the network's geography stops mattering.

**Most valuable ideas.**
1. Itemised duel lines (attack versus defense contributions).
2. "Tightest margin" (Proxy margin 1): a single risk number to look at.
3. Duels play home last, for tension.

**Refs.** Civ VII `prior/civ7/combat_preview_civ7.png` (s05); Civ VI siege `prior/civ6/City_under_siege_Civ6_.png`.

**To raise each axis by 2.**
- **What/why/when → 9.** Add a countdown and a route sketch.
- **Predictability → 8.**
  - Fix the maths.
  - Keep itemised lines visible for every banner, not just the selected one.
- **No-words → 9.** Give TAKEN, DOWN and HOLDS icons on each banner.
- **Decision → 5.** Only by putting geography back: assets have reach and banners compete for them. That is concept A.
- **Consequences → 7.** Show home attrition, and drop the HOLDS-tick litter.

**Rule changes.**
1. No travel: **not worth it.** It deletes the network.
2. ATK/DEF thresholds: **not worth it.**
3. Flat modifiers: **not worth it.**
4. Duel-locked playout: neutral.

The duel card is worth stealing as a hover on any node in A or B.

---

### D — Auto-battler Loadout (29)

**Scores.**
- **What/why/when 6.** `1_warning.png`: the incoming lineup cards point at their target nodes, with "HEAT 51 > 50 : SOLACE SENDS 3". The why and when are only in the text box. *Where they come from* is reduced to a non-interactive inset map.
- **Predictability 4.**
  - The tick strips are a nice idea: the Bazaar-style timeline is exact.
  - **The frames contradict the verdict.** `3_forecast` shows cobalt diamonds (their hits) on the Proxy strip at ticks 1 and 3 and on the Collector strip, and says CLEAN DEFENSE. `4_resolution` shows Proxy taking **−9** with pips 3 → 2. A clean defense means nothing damaged, so the forecast's own data disproves its headline.
  - The diamonds carry no damage numbers.
- **No-words 8.**
  - It survives scrambling best. The HP and damage discs and the speed chevrons are SAP's convention (sheet s06), and the slot frames with "+" are universal.
  - It loses points on lane results, which are word chips in boxes coloured teal or cobalt, and on the "+1 hold" synergy chip.
- **Decision depth 7.**
  - Slots plus adjacency synergies (operative + ICE = +1 hold; operative + turret = +2) create combos that flip a lane. This is the only concept with *build* depth rather than placement depth.
  - Free re-slotting until commit is right for a roguelite.
  - Risk: the synergy table becomes the real game, and the network the window dressing.
- **Consequences 4.** `5_aftermath.png` has no map, only the inset. The "lineup after" wear list is good. The cracked-slot persistence is invisible in every frame. It is the weakest "persistent on the map" of the six.

**Biggest problems.**
1. The CLEAN verdict contradicts the shown hits and damage.
2. It leaves the city map: the campaign's main board shrinks to a thumbnail during the most consequential event.
3. The lane model removes damage in passing and makes adjacency between nodes meaningless, except for the "move a unit across adjacent lanes" exception, which no frame shows.

**Most valuable ideas.**
1. Two-number unit cards for threats: the best no-words element in the lab.
2. Slot synergies with a drag-time "lane flips" tag ("WITH ICE: DOWN > HOLDS").
3. A per-lane tick strip as an exact, glanceable timeline.

**Refs.** Super Auto Pets `super_auto_pets/steam_02.jpg` (s06); The Bazaar `the_bazaar/steam_00.jpg` (s07); Mechabellum `mechabellum/steam_03.jpg` (s11). The Bazaar previews the opponent *and the stakes* (rewards); Mechabellum fights on the board you deployed on, not on an abstraction.

**To raise each axis by 2.**
- **What/why/when → 8.** Put the lineup cards *at the Solace sites on the real map*, with arrows along the routes.
- **Predictability → 6–8.**
  - Fix the data.
  - Put the damage number in every diamond.
  - Make the lane result show the clean/not-clean state.
- **No-words → 10.** Use icon lane results (check, bolt, flag) instead of words.
- **Decision → 9.** Keep the synergies but anchor the slots to map nodes, so adjacency on the map *is* adjacency for synergy.
- **Consequences → 6.** The aftermath happens on the real map, and the cracked slot is drawn on the node.

**Rule changes.**
1. Lane model: **not worth it.**
2. Node slots: **worth it**, as a cap per node in A or B. It gives placement a budget shape.
3. Adjacency synergies: **worth trying** in A or B, where map adjacency is real.
4. Cracked slot: worth it, but it must be visible on the HQ map.

---

### E — Countdown + Allocation (31)

**Scores.**
- **What/why/when 9.**
  - `1_warning.png`: a big countdown dial ("2 NETRUNS"), a hatched cobalt front at the map edge that moves in (compare `3_forecast` with `1`), and Heat 51 > 50 in the card.
  - The dial and the front fully survive scrambling.
  - This is the XCOM 2 doom-clock and Frostpunk storm pattern (sheets s08, s09), and it fits a campaign that alternates netruns and HQ.
- **Predictability 4.**
  - The idea (notch = strike, fill = you) is the simplest possible. The frames still contradict it.
  - Relay's gauge fill sits *below* its notch of 5 in `3_forecast`, yet the node is tagged HOLDS. In `4_resolution` the Relay gauge drains to empty (−5), and `5_aftermath` still says HOLDS. By the SPEC (below the notch = DOWN, empty = TAKEN), Relay should be DOWN or TAKEN.
  - Threats are invisible: no silhouettes, no routes, only a number. You know *how much* but not *who*, so you can't reason about counters.
- **No-words 6.** The dial, the front and the gauges are good. The hard calls ("EVACUATE / GO DARK") are cryptic when scrambled; the "+1" disc doesn't say "delay at a Heat cost". The crew-hours row reads as people icons, which is fine.
- **Decision depth 6.**
  - Strategic tension across netruns, and Evacuate (sacrifice for a refund) and Go dark (Heat for time) are real campaign choices.
  - Tactically, filling gauges is a knapsack with one currency. The solution is mechanical once the notches are known.
- **Consequences 6.** The named trades ("PROXY TAKEN · REFUND +6") and the foreshadowing ("NEXT STRIKE AT HEAT 75") are good. Heat climbing 51 → 53 → 55 over the countdown is a nice touch, showing that netruns cost Heat.

**Biggest problems.**
1. The gauges contradict the outcomes (Relay).
2. No threats on screen: the raid has no actors, so there is nothing to watch. `4_resolution` is a hatched line sliding over static gauges, about 20 s of very little.
3. A new currency (crew-hours plus a 3:1 Schematics conversion) on top of Heat, Schematics and Armory. That is budget creep in a game with a few minutes of setup.

**Most valuable ideas.**
1. Announce the raid N netruns ahead, with a countdown dial and an advancing front.
2. Hard calls as one-off triage (Evacuate, Go dark).
3. "Next strike at Heat 75" in the aftermath.

**Refs.** XCOM 2 `prior/xcom2/Avatar_Project.jpg` (s08); Frostpunk `prior/frostpunk/steam_09.jpg` (s09); Frostpunk storm `prior/frostpunk/Nansen_s_Storm_Watch.png`.

**To raise each axis by 2.**
- **What/why/when → 10.** Put silhouettes riding the front.
- **Predictability → 6.**
  - Fix the gauge data.
  - Show the threats and their routes behind the notch: why is the Proxy notch 27? Because the 9 × 3 Enforcer.
- **No-words → 8.** Use icon hard calls: a flag with a coin arrow for Evacuate; a moon with a Heat drop for Go dark.
- **Decision → 8.** Drop crew-hours. Let the netrun *choice* between raids be the allocation: which netrun reward fills which defense.
- **Consequences → 8.** Show the front's next start position on the HQ map after the raid.

**Rule changes.**
1. Announce N netruns ahead: **worth it.** It is the best single change in the lab, and it can sit on top of A or B unchanged.
2. Crew-hours and gauge DEF: **not worth it.**
3. Hard calls: **Go dark worth testing; Evacuate maybe.** It is a small rule and a strong flavour.
4. Removing routes and steps: **not worth it.**

---

### F — Plan Ledger (26)

**Scores.**
- **What/why/when 7.** `1_warning.png`: an intercepted-dossier card with who → target, HP, damage, routing, the why (Heat 51 > 50) and the when (on return). It is clear and flavourful, but there is no map, so *where* is missing.
- **Predictability 6.**
  - "Guaranteed" is the promise, and the totals row (`3_forecast`) is the strongest per-node answer of the six.
  - The damage → verdict mapping is inconsistent. `2_planning`: Vault 20-18 is TAKEN while 2 integrity remains. `3_forecast`: Safehouse 20-27 is DOWN while 7 over. A player can't infer the rule from the receipt.
  - The notation "50-0" reads as a score or a range, not "integrity minus damage".
  - The totals row (one cell per *node*) sits directly under the step columns 1–6, so the axes collide visually.
- **No-words 3.**
  - The kill mark is a typed "X", and it scrambles to a red **"N"** (scrambled `3_forecast` and `4_resolution`). Even the death mark fails the test.
  - The totals verdicts are words, distinguished only by border colour.
  - The dossier's routing column is words.
- **Decision depth 6.** Cell-level ICE and a Decoy that sacrifices the Safehouse to save Proxy (`3_forecast`) are real trade-offs, and the only ones shown as such in the lab. It is spreadsheet-precise, which is the rubric's "spreadsheet" warning.
- **Consequences 4.** The receipt and the "PAID" strip (`5_aftermath`) are fine. Map persistence is one bolt on a minimap.

**Biggest problems.**
1. The DOWN/TAKEN mapping is inconsistent under a "guaranteed" banner.
2. The main screen is a grid, and the city map is a minimap. Watching (`4_resolution`) means a cursor walks columns while a small map replays, so the hands-off part has no spectacle.
3. It fails the no-words test even on the kill mark.

**Most valuable ideas.**
1. The totals row: one compact per-node result strip.
2. The decoy-as-sacrifice framing: it shows a chosen loss, not just avoided ones.
3. The "intercepted dossier" fiction for the warning.

**Refs.** Backpack Battles combat log `backpack_battles/steam_05.jpg` (s10). Even an auto-battler that exposes its full trace hides it behind a toggle and keeps the board as the main view.

**To raise each axis by 2.**
- **What/why/when → 9.** Put the dossier over the map with the routes drawn.
- **Predictability → 8.** Use one consistent rule for the verdict, the notation "50 → 50", and a totals row set apart from the step columns.
- **No-words → 5.** Use drawn icons for kill, hold and verdict.
- **Decision → 8.** Keep the sacrifice framing; it is not enough to beat the board-based concepts.
- **Consequences → 6.** Show the aftermath on the full map.

**Rule change.** ICE on a threat at a step: **not worth it.** It detaches ICE from place, which makes A and B's spatial reading worse, and it exists only to suit the grid.

---

## 3. Ranking and recommendation

**Ranking:** A (36) > B (34) > E (31) > D (29) > C (28) > F (26).

**Fit with hands-off execution.**
- **B and A watch best:** tokens move along routes, and the forecast comes true on the same board.
- D's side-by-side lanes are watchable in the way SAP is, but abstract.
- C's three duels are short theatre.
- E (one sweep) and F (a cursor on a grid) give the player almost nothing to watch for 20–25 s.

**Fit with the campaign.**
- B and C have the fastest setup.
- A risks scrubbing homework unless it gets an all-steps view.
- E spreads the decision across netruns, which is the best structural fit for 3–5 raids a campaign, but it adds a currency.
- F is the slowest.

**Take forward:**
1. **A Telegraph**, as the base: resolver-true, exact, the Into the Breach model.
2. **B Siege Lanes**, as the second track.

These two share a resolver and will likely converge into one design. That is fine: they are the two that keep the city network as the board, and both are zero rule cost.

If the designer wants the second slot to be a genuinely divergent bet, take **D** instead. Only do that after its CLEAN contradiction is fixed and its lanes are anchored to the real map.

**Steals:**
- **A ← B:**
  - lanes and wave flags at warning time;
  - CLEAN NEEDS (the gap to clean, payout dimmed);
  - the NEW ENTRY lane stub that persists into the next raid;
  - the LOST card with its fix.
- **A/B ← E:** the **N-netrun countdown dial and advancing front**. Worth its rule change on its own; it needs no other part of E. Optionally **Go dark** as one hard call.
- **A/B ← D:**
  - two-number threat cards (HP disc, damage disc, speed chevrons) in the wave panel and the attack-order panel;
  - the drag-time "flips" tag;
  - later, map-anchored slot caps and synergies.
- **A/B ← C:** "tightest margin" as a single risk readout, and the itemised duel card as a node hover.
- **A/B ← F:** a compact per-node totals strip as the forecast summary, with home first, and the dossier fiction for the warning card.
- **All concepts:**
  - a "held, damaged" node state distinct from clean HOLDS;
  - loss icons inside the verdict stamp;
  - drawn (not typed) kill marks.

Round 2 must also regenerate the mockups from one consistent simulation. Four of the six concepts currently contradict their own forecast, and a predictability review can't be passed on hand-placed numbers.

## 4. Sheets built (`D:/rc_tmp/raid_design_lab/critic_r1/`)

| Sheet | Ours | Reference |
|---|---|---|
| `s01_A_attack_order_vs_itb.jpg` | A 2_planning | Into the Breach (prior set) |
| `s02_B_wave_flags_vs_thronefall.jpg` | B 1_warning | Thronefall steam_02 |
| `s03_B_wave_flags_vs_kr.jpg` | B 1_warning (scrambled) | Kingdom Rush LostEmp_Wave_01 (prior set) |
| `s04_B_reach_vs_dg2.jpg` | B 2_planning | Defense Grid 2 steam_05 |
| `s05_C_duel_vs_civ7.jpg` | C 2_planning | Civ VII combat preview (prior set) |
| `s06_D_lineup_vs_sap.jpg` | D 3_forecast (scrambled) | Super Auto Pets steam_02 |
| `s07_D_preview_vs_bazaar.jpg` | D 1_warning | The Bazaar steam_00 |
| `s08_E_countdown_vs_xcom2.jpg` | E 1_warning | XCOM 2 Avatar Project (prior set) |
| `s09_E_sweep_vs_frostpunk.jpg` | E 4_resolution | Frostpunk steam_09 (prior set) |
| `s10_F_ledger_vs_bpb_log.jpg` | F 3_forecast | Backpack Battles steam_05 |
| `s11_D_resolution_vs_mechabellum.jpg` | D 4_resolution | Mechabellum steam_03 |
| `s12_A_aftermath_vs_bpb_outcome.jpg` | A 5_aftermath | Backpack Battles steam_02 |
| `s13_B_route_vs_rogue_tower.jpg` | B 3_forecast | Rogue Tower steam_09 |

The per-game contact sheets are in `critic_r1/contact/`. Downloaded images are in `refs/<game>/`, with URLs in `refs/SOURCES_R1.tsv`. Families covered:
- **Tower defense:** Bloons TD 6, Defense Grid 2, Orcs Must Die! 3, Thronefall, PvZ, Dungeon Defenders, Rogue Tower, Kingdom Rush Vengeance.
- **Auto-battlers:** Super Auto Pets, Backpack Battles, The Bazaar, Mechabellum.

The scripts are in `critic_r1/tools/`.
