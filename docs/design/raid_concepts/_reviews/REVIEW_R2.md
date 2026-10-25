# Raid concepts, round 2: independent critic review

I read all 12 SPEC / SPEC_R2 files and looked at all 61 r2 frames, both plain and scrambled. I re-ran `sim.py` for the four named plans (BARE, DECOY ONLY, LURE, SHIELD). I also ran `concept_c2_duel.py` and `d2_lane_sim.py`, and read `concept_e2_countdown.py`. I did not open any earlier review, the scoreboard or critic_r1.

## 1. Score table

Scale: 7 means a good shipped game does about this well. 9–10 means best in class. Visual polish is not scored.

| Concept | What/why/when | Predictability | No-words | Decision depth | Consequences | **Total /50** | Verdict |
|---|---|---|---|---|---|---|---|
| **A Telegraph** | 8 | 8 | 7 | 6 | 6 | **35** | The strongest base. The preview is exact, the rules are unchanged, and it already reads as a picture. It needs a simpler resolver, not more UI. |
| **B Siege Lanes** | 8 | 6 | 6 | 6 | 8 | **34** | It has the best consequence beat in the lab (frame 6), but its ribbons hide the nodes they forecast. |
| **D Auto-battler** | 7 | 7 | 7 | 6 | 5 | **32** | The strips are legible and the rules are simple, but they show the fight before it happens, so the playout is a rerun. Four rule changes. |
| **E Countdown** | 9 | 7 | 6 | 4 | 6 | **32** | The best "when" in the lab, attached to the thinnest puzzle: a 6-point knapsack. |
| **F Plan Ledger** | 7 | 7 | 6 | 5 | 7 | **32** | Same data as A, laid out as a spreadsheet. Its rows do not add up to its totals. |
| **C Strength Duel** | 7 | 4 | 6 | 5 | 4 | **26** | It stamps CLEAN DEFENSE over four damaged nodes, and its bar does not show its own thresholds. |

## Cross-cutting findings (these matter more than any single concept)

1. **The resolver is exact but not something the player can reason about.** In LURE and DECOY ONLY, a Decoy on the Firewall walks the Auditor and the Enforcer *through the Home Server*: Proxy → Safehouse → Home. The two paths to FW are the same length, and the tie is broken alphabetically (SAFE < VAULT, `sim.next_hop`). At home they hit and are "spent". A shows this faithfully (`a_telegraph/r2/mockups/3_forecast.png`: arrows Safehouse → Home). But no player would predict "decoy on the firewall routes the enemy through my home".
   - Into the Breach's telegraph is best in class because its rules are guessable *before* you look.
   - A, B and F give a perfect readout of a black box. That turns the puzzle into "drag pieces until the numbers look good".
   - **The fix is a rule fix:** a decoy pull that avoids home, and a stated tie-break shown as an arrow. It is not a UI fix.
2. **"Clean" is defined three ways.**
   - The brief says nothing damaged.
   - `sim.py` says home intact and no new DOWN or TAKEN; scuffed is ignored, and `damaged` is computed but unused.
   - C says no DOWN or TAKEN and home loss 0, and f5 hardcodes `clean = True`.

   Under any of these, the shared scenario has **no clean defense** (README; and D's own search finds a 30-damage minimum). The +5 / +12 incentive is then pure decoration in this scenario. Pick one definition, and tune the Armory or the threats so that a clean defense exists but is hard.
3. **What SCUFFED costs and how long it lasts is undefined.** A's LURE leaves Proxy at 3/15 and Safehouse at 8/20 ("nothing lost"). That makes Proxy the guaranteed "weakest" target and an instant DOWN in the next raid. Yet the patch cost (`r2_kit.repair_cost`) charges only for home loss and DOWN nodes. Every concept says "scuffed keeps −N", and none says what it costs to clear it.
4. **The 50 % cascade appears in no telegraph cell.** BARE: Safehouse −3, home −3 and Vault −3 all come from cascades, and no arrow or cell shows them (`f_plan_ledger/r2/mockups/2_planning.png`; also A frame 2's Safehouse −3).
5. **No-words leaks shared by all concepts.**
   - Multipliers are letters: "x2" becomes "e2", "x1.5" becomes "u1.5", "x4" becomes "k4" in the scrambled frames.
   - D's kill mark is a letter: the red "X" becomes "N" (`d_autobattler_loadout/r2/scrambled/2_planning.png`).
   - E's dial unit is a letter: the "x" becomes "c".
   - In C and F, HOLDS and SCUFFED share a plain check in places; F's totals show home 50>30 with a plain check.

## 2. Per concept

### A — TELEGRAPH (35)

**Scores.**
- **What/why/when 8.** `1_warning.png` has the Heat chain 51 > 50, the dial, two-number chips with route glyphs, and dashed routes. "When" is two map nodes until home, which is clear.
- **Predictability 8.** Every number matches the sim:
  - BARE −20;
  - the DECOY what-if, −20 > −12 and lost 4 > 0;
  - LURE −9 with the Enforcer at home on 17 HP;
  - the step 3/5 board in `4_resolution.png`: Auditor killed at home, Enforcer held, Collector at 6/12 on FW.

  It is held back from 9–10 by the unguessable routing and the hidden cascade (cross-cut 1 and 4).
- **No-words 7.** The scrambled frames lose only DOWN, TAKEN, ALL and CLEAN, and their icons (bolt, flag and X, check) carry the meaning. The CLEAN box (`scrambled/3_forecast.png`) is the weakest part: a threat → home → 17 reads as "17 damage", not "17 HP left".
- **Decision depth 6.** There are real trade-offs: LURE (home −9, 4 scuffed) against SHIELD (home 0, 2 DOWN, 2 TAKEN), side by side, with coin and netrun costs. That is a good, honest dilemma. But with an exact preview and four pieces, the search is brute force.
- **Consequences 6.** The stamp, loss icons and missed payout are good. Scuffed persistence is not priced, and `5_aftermath.png` has no "next raid" beat.

**Biggest problems.**
1. It is exact on rules the player cannot predict, which invites trial-and-error.
2. The scrubber is a timeline of 10 cells of tiny silhouettes (`2_planning.png`) that nobody will read. ALL does all the work.
3. The scuffed cost is invisible (Proxy 3/15 "nothing lost").

**Most valuable ideas.**
1. The ALL view, with end-of-raid tags on every node.
2. The what-if delta chip (home −20 > −12, lost 4 > 0).
3. Plan compare with the cost in coins and netruns.

**Refs.** Into the Breach, `prior/itb/steam_03.jpg` (order badges; SOURCES_R1 itb row) → `sheet_A_vs_itb.jpg`. The Last Spell `steam_02`, Dome Keeper `steam_00` (SOURCES_R2) → `sheet_warning_vs_lastspell.jpg`.

**What would raise each axis by 2.**
- **What/why/when:** show the dial and the threat chips on the netrun map too, so the player knows while choosing the next node.
- **Predictability:** make the resolver guessable:
  - decoy paths never pass home;
  - the tie-break is drawn;
  - cascades are shown as a dashed red spill arrow with −N.
- **No-words:** replace "17" in the CLEAN box with that threat's HP pips at home. Draw multipliers as stacked glyphs.
- **Decision depth:** let a real clean defense exist. Add one more Armory choice than there are slots (pick 3 of 5), so the choice is in the drafting as well as the placement.
- **Consequences:** price scuffed (patch cost per −N) and add B's "next raid" frame.

### B — SIEGE LANES (34)

**Scores.**
- **What/why/when 8.** Same warning kit as A, with numbered arrival dots.
- **Predictability 6.** The numbers are sim-true:
  - SHIELD: home 50>50, FW and Relay DOWN, Vault and Proxy TAKEN, skulls 3/3, coin −12 = 8 + 4;
  - step 5/10: the Auditor shot at home, the Enforcer hitting Relay for 9.

  But in `3_forecast.png` the ribbons cover Vault, Proxy and Firewall, and you cannot tell which ribbon is which threat. The Enforcer's lane runs Depot → Proxy → Vault → Relay → FW → Home, drawn on top of two other lanes. The "width = HP" narrowing is barely visible.
- **No-words 6.** Icons survive scrambling, but the occlusion is worse with no labels.
- **Decision depth 6.** Same piece set as A. The reach rings (`2_planning.png`) are a good aid.
- **Consequences 8.**
  - `5_aftermath.png` shows each loss with its fix as an icon path: a netrun hex, or coins.
  - `6_next_raid.png` shows the TAKEN nodes as new Solace entries one hop from home at Heat 76. That is the only frame in the lab that makes a loss *persist into play*.

**Biggest problems.**
1. The ribbons sit on the nodes (cobalt over cobalt-taken nodes).
2. Lane identity is lost where lanes share links.
3. The committed demo plan is the 2-TAKEN one. The frames never show why a player would choose it.

**Most valuable ideas.**
1. Frame 6: losses reshape the next raid.
2. Reach rings while a piece is held.
3. Arrival-step dots on the route.

**Refs.** Kingdom Rush `prior/kr/LostEmp_Wave_01.png` (SOURCES_R1 kr row), Thronefall `steam_02` (SOURCES_R1) → `sheet_B_vs_wave_preview.jpg`. Defense Grid 2 `steam_05` (range highlight) and Backpack Battles `steam_02` → `sheet_aftermath_vs_backpack.jpg`.

**What would raise each axis by 2.**
- **What/why/when:** put the dial on the netrun map.
- **Predictability:** draw thin, offset route lines beside the links, KR-style. Put the HP numbers at the arrival dots, not in the ribbon width. Use one hue shade per threat.
- **No-words:** use a silhouette at the head of each route instead of an unlabelled ribbon.
- **Decision depth:** same as A.
- **Consequences:** show a run-level ledger (raids survived, nodes lost) as Backpack Battles does with wins and tries.

### C — STRENGTH DUEL (26)

**Scores.**
- **What/why/when 7.** Banners on every node at the warning are a good per-node "who hits what".
- **Predictability 4.** The frames contradict the rule:
  - `1_warning.png` shows checks on home (loss 15), Vault (9), Relay (5) and Firewall (2). The sim says all four are SCUFFED, and home takes −15.
  - The caption says "21:23 = HOLDS", but the code gives Proxy loss 10, which is SCUFFED.
  - `3_forecast.png` and `5_aftermath.png` stamp **CLEAN DEFENSE** over FW −12, Relay −5, Vault −9 and Proxy −10.
  - The margin bar shows ATK : (integrity + bonus), but TAKEN uses loss ≥ 2 × integrity, which the bar cannot show.
  - The Decoy's 12 > 0 in the aftermath belongs to no rule.
- **No-words 6.** The numbers survive scrambling; the meaning of the verdict icons does not.
- **Decision depth 5.** Flat bonuses, and the answer is obvious: stack everything on Proxy. The crew aura is the only spatial idea.
- **Consequences 4.** A clean stamp on a damaged board is unfair and teaches the wrong thing.

**Biggest problems.**
1. The clean and scuffed verdicts are self-contradictory.
2. The bar does not encode the thresholds.
3. The duel playout (`4_resolution.png`) is four static bar fills with no suspense: every ATK is below DEF.

**Most valuable ideas.**
1. Itemised duel card lines (Civ-style).
2. "Tightest margin: Proxy 5" as a single risk number.
3. A crew aura that rewards adjacency.

**Refs.** Civilization VII `prior/civ7/combat_preview_civ7.png` (SOURCES_R1 civ7 row) → `sheet_C_vs_civ7.jpg`.

**What would raise each axis by 2.**
- **What/why/when:** show the dial and the routes more prominently than the banners.
- **Predictability:** one verdict per banner, from one comparison. Draw the bar with notches at integrity and at 2 × integrity, and fill it with the loss.
- **No-words:** use the shared SCUFFED mark.
- **Decision depth:** make bonuses depend on position (reach, routes) so that stacking one node starves others.
- **Consequences:** obey one clean definition.

**Rule-change cost.** Four changes for a model the lab's own frames cannot keep consistent. **Not worth it.**

### D — AUTO-BATTLER LOADOUT (32)

**Scores.**
- **What/why/when 7.** The lineup chips at the sites are good. The site label is covered by the chips (`1_warning.png`).
- **Predictability 7.** The strips are exact and match `d2_lane_sim`:
  - home −15 after 3 Decoy soaks;
  - Vault −6, with the Auditor dead on tick 3;
  - Proxy −9, frozen for 3 ticks, killed on tick 5.

  Every hit carries its number. But the docstring says "the Firewall's own gun 3", and the code has no Firewall lane: the Firewall, a scenario feature, is erased. "A threat alive at tick 6 TAKES the node" even when the node is undamaged, which is surprising.
- **No-words 7.** Strips and diamonds are pure icon, except that the kill "X" is a letter.
- **Decision depth 6.** The Breaker's map-adjacency aura is a real spatial puzzle (`2_planning.png`, the +2 / +1 teal links). The space is small (4 pieces, 3 lanes), and the Breaker on Vault is the dominant answer.
- **Consequences 5.** "Turret 10" wear is unexplained. The cracked-slot persistence from the base SPEC is not shown in any frame.

**Biggest problems.**
1. The pre-fight strip *is* the fight, so the playout (`4_resolution.png`, threats parked beside their nodes) has no watch-value.
2. Lanes delete routes, passing damage and the Firewall, so the map stops mattering except for adjacency.
3. Home takes six strikes instead of one. That is a hidden rebalance.

**Most valuable ideas.**
1. A numbered per-threat strip as the clearest "how it dies" readout in the lab.
2. Map adjacency as synergy.
3. Speed controls consistent with the genre.

**Refs.** Super Auto Pets `steam_02`, The Bazaar `steam_00` (SOURCES_R1) → `sheet_D_vs_autobattlers.jpg`. Note that SAP and The Bazaar do *not* pre-show the result; their fun is the reveal.

**What would raise each axis by 2.**
- **What/why/when:** move the chips off the labels and add the dial.
- **Predictability:** keep routes, and let the strip show passing hits as their own cells.
- **No-words:** use a glyph kill mark.
- **Decision depth:** more pieces than slots, plus a second synergy axis.
- **Consequences:** show wear and cracked slots on the HQ map.

**Rule-change cost.** Four changes. Only the adjacency aura is worth stealing.

### E — COUNTDOWN + ALLOCATION (32)

**Scores.**
- **What/why/when 9.**
  - A two-netrun dial, top centre.
  - A hatched front that advances (`1_warning.png` → `3_forecast.png`, where Heat 51 → 53 shows the cost of waiting).
  - Live outcome tags from the first frame.

  This is the best "when" in the lab, close to the XCOM 2 doom clock.
- **Predictability 7.** The notch and fill rule is simple and matches `outcome()`: plan 1 gives home −11 and Proxy −11. The gauges are cramped and overlap their tags. In `4_resolution.png` Proxy shows full pips beside a −11 tag.
- **No-words 6.** The hard-call card (+1 circle, flame +4, crew +3) reads. The dial's unit glyph is a letter.
- **Decision depth 4.**
  - Turret = 6, ICE = 5, and an hour = 2 are all the same currency, so the pieces have lost their identity.
  - The notches are fixed at the warning, so splitting hours over two visits is bookkeeping; the netrun in between changes nothing on the board.
  - Evacuating Proxy is an obvious, dominated call.
- **Consequences 6.** "Next at 75" and the patch cost are good. Turret wear "10" is unexplained.

**Biggest problems.**
1. It is a knapsack, not a puzzle.
2. The two-visit split adds no decisions.
3. Heat keeps rising during the countdown (55 at the strike), and what happens if it crosses 75 before the raid lands is unspecified.

**Most valuable ideas.**
1. A raid announced N netruns ahead, with the clock visible in the other mode.
2. A front that advances per netrun.
3. Go dark, which trades Heat for time.

**Refs.** XCOM 2 `prior/xcom2/steam_07.jpg` (SOURCES_R1 xcom2 row) and Frostpunk `prior/frostpunk/-30Endless…png` → `sheet_E_vs_doomclock.jpg`. Dome Keeper (SOURCES_R2) → `sheet_warning_vs_lastspell.jpg`.

**What would raise each axis by 2.**
- **Predictability:** give each gauge a fixed lane beside its node, with no overlap.
- **No-words:** use a glyph for the unit.
- **Decision depth:** make the netrun in between *change the raid*. A netrun on a Solace site removes or weakens a chip; a scouted node reveals a hidden third threat. Give the pieces back their verbs (reach, hold, pull) instead of flat fill.
- **Consequences:** show what the countdown cost in Heat.

**Rule-change cost.** "Announced N netruns ahead" is worth taking on its own, grafted onto A. The rest is not.

### F — PLAN LEDGER (32)

**Scores.**
- **What/why/when 7.** The decrypted dossier (`1_warning.png`) shows each threat's full path as node icons. That is the clearest "where" in the lab. The countdown moves to a corner.
- **Predictability 7.** The cells match the sim step for step:
  - BARE Collector: Relay −5, FW −5, Home −5;
  - SHIELD: the hatched ICE holds, and skulls at home on steps 4, 6 and 10.

  But the rows do not add up to the totals: Safehouse 20>17 and the extra −3 on home and Vault come from invisible cascades, and FW 30>0 is 27 + a cascade of 4.
- **No-words 6.** Readable but dense: 30 cells of tiny HP bars. The DECRYPTED stamp is a word.
- **Decision depth 5.** Same pieces as A, presented as a grid. The player optimises a spreadsheet.
- **Consequences 7.** A receipt on the map, with each loss and its fix: hex → home 1 hop, or coins.

**Biggest problems.**
1. Hidden cascades break the ledger's promise of a guarantee.
2. The reading load is too high for a 3–5-per-campaign event.
3. Map and ledger compete for attention during planning; the map shrinks to a minimap.

**Most valuable ideas.**
1. The dossier's path-as-icon rows.
2. A totals row as a receipt.
3. The SIGN ORDERS framing.

**Refs.** Frostpunk wiki table `prior/frostpunk/Winterhome_-_Temperature.png` (prior set) and Rogue Tower `steam_07` (SOURCES_R1) → `sheet_F_vs_table_forecast.jpg`.

**What would raise each axis by 2.**
- **What/why/when:** put the big dial back.
- **Predictability:** give cascades their own cells.
- **No-words:** drop the HP bars from the cells and keep only the −N and the skull.
- **Decision depth:** see A.
- **Consequences:** add the next-raid beat.

## 3. Ranking and what to take forward

**Ranking:** A (35) > B (34) > D, E, F (32) > C (26).

**Take forward: A and B**, merged into one design. Both use today's resolver, with zero rule changes, and both are already sim-true.

- **A as the base:**
  - ALL view;
  - end tags;
  - what-if delta;
  - plan compare.
- **Steal from B:**
  - reach rings;
  - arrival-step dots instead of the 10-cell scrubber;
  - **frame 6**, the next raid reshaped by losses, as the aftermath's last beat.

  Drop B's ribbons.
- **Steal from F:** the dossier path rows as the warning card.
- **Steal from E:** the countdown shown on the netrun map, and optionally "announce one netrun ahead". This is a cheap rule change and worth it.
- **Steal from D:** the numbered per-threat strip as the hover readout for one threat. Map-adjacency aura for the Breaker, if a designer wants more spatial depth.
- **Required rule work before any of this is fun** (cross-cut 1–3):
  - decoy paths avoid home;
  - a visible tie-break;
  - shown cascades;
  - one clean definition;
  - a priced scuffed state;
  - a scenario where a clean defense exists.

**Build A first as the playable prototype.** It needs no resolver change, `sim.py` already produces every number, and the hands-off playout is literally the telegraph played back. A prototype exposes the real risk within a day: whether players can reason about the routing or only read it. That test decides whether the rule fixes above are needed before B's lanes are layered on.

**Hands-off fit.**
- A and B carry the agency in planning, and watching confirms a forecast; that is satisfying if the board stays readable.
- D's and F's playouts replay a grid the player has already read.
- C's and E's playouts are static meters.

**Campaign fit.** A + B plans in under 2 minutes with four pieces. E's two-visit split adds friction for no decision.

## 4. Sheets built (D:/rc_tmp/raid_design_lab/critic_r2/)
- `sheet_A_vs_itb.jpg`: A forecast vs Into the Breach's attack order.
- `sheet_B_vs_wave_preview.jpg`: B forecast vs Kingdom Rush route, Thronefall icons.
- `sheet_C_vs_civ7.jpg`: C duel card vs Civ VII combat preview.
- `sheet_D_vs_autobattlers.jpg`: D forecast vs Super Auto Pets battle, The Bazaar board.
- `sheet_E_vs_doomclock.jpg`: E warning vs XCOM 2 Avatar clock, Frostpunk forecast.
- `sheet_F_vs_table_forecast.jpg`: F ledger vs Frostpunk table, Rogue Tower priority.
- `sheet_aftermath_vs_backpack.jpg`: B aftermath and next raid vs Backpack Battles.
- `sheet_warning_vs_lastspell.jpg`: A warning vs The Last Spell, Dome Keeper.

**New reference images:** `refs/the_last_spell/` and `refs/dome_keeper/`, both from Steam. Their URLs are in `refs/SOURCES_R2.tsv`. All other references reuse the existing images, cited from `refs/SOURCES_R1.tsv` or marked "prior set".
