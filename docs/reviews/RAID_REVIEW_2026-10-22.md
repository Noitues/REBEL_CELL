# Raid review, 2026-10-22 (fresh, critical)

**Verdict: NOT CLEAR. The raid has a real deterministic engine under it, but the screen does not let a player use it. 10 problems, 4 of them P1.**

Reviewer: auditor agent, Opus. Base `main` b73c60fe, branch `raid-review2`. No prior reviews were read. Rules are taken from
`docs/GDD.md` §3.2–3.3, §4.3–4.4, §7, §9.3, §11.5 and A.5. All evidence lives under `D:/rc_tmp/raid_review2/` (paths below are relative to it).

## Verdict

The rules promise a deterministic tower-defense puzzle: you see every threat's path, place assets, and every node shows its exact
outcome before you commit (GDD §7.1). What ships is a forecast box and a pile of paperwork. The map does not show each node's outcome.
That only appears in a hover tooltip after you click a node. Placing a card often changes nothing, or changes things in a way you cannot
judge (TAKEN to DOWN for one more home damage). Stationing an operative showed no forecast change in either run. The threat count
disagrees with itself on one screen (4 units, 0/5 stopped, 2 rows of intel, and a toast that names two more). The verdict is wrong in
tone: a raid that took 60% of the home server and two sites gets the same yellow **CELL HOLDS** stamp as a scratch. Losing the whole
campaign gets a small red dial and a button that says CONTINUE. The first raid is over in **one step, about 7 seconds**, so the
"playout" is a flash. Without words, a player can tell "something bad, red" from "something less bad, orange", and nothing else.
Next to Civilization or XCOM, the lettering is bold and the art direction is strong. The information design is a generation behind.

| Axis | Score /10 | One line |
|---|---|---|
| What / why / when | 4 | Heat countdown on the HUD is good; *when* the raid fires and *why this target* are never said. |
| Outcome predictability | 4 | One headline forecast is honest. Per-node outcomes, card effects and the cost of each loss are hidden or missing. |
| No-words test | 2 | With text scrambled, only colors (red / orange) and three card icons survive. Threats have no silhouettes. |
| Visual quality vs AAA | 5 | Strong stamps, paper and neon. The map read is poor: blue rings tangle over the city and the camera re-frames mid-raid. |
| Decision depth | 3 | In every captured case a single card changed nothing or swapped one loss for another. The station button had no visible effect. |
| Consequences | 4 | DOWN / TAKEN / entry points and the repair price are listed. The tone is wrong, assets lost are not reported, and the Heat sign is inverted. |

## The flow, moment by moment

Shots: `lab_hold/` (Heat 22→26, 2-node network, turret + operative), `lab_lose9/` (Heat 72→76, 9 nodes, nothing placed), `lab_breach/`
(home at 6), `*_scr/` (scrambled text), `bb/shots/` (real mouse clicks on the lose save through `blackbox.py`). Contact sheet:
`flow_sheet.jpg`.

| # | Moment | Shot | What the player needs | What the screen says | No-words | Problems |
|---|---|---|---|---|---|---|
| 1 | Heat rising | `lab_hold/01_hq_before.png` | How close the next raid is | HUD: `22 COOL`, tick marks, tag `RAID AT 25 · 3 AWAY` | guessable | Good. This is the best moment in the flow. The tag is tiny (about 9 px) and sits under the bar. |
| 2 | Heat terminal | `lab_hold/02_heat_terminal.png` | What happens at 25, how to cool down | `NEXT 25 RAID // 30 complication`, `SCRUB HEAT -7` | opaque | Fine for readers. "Suspect file", "In force: nothing yet" is flavor at the cost of clarity. |
| 3 | Raid announced | `lab_hold/03_hq_raid_pending_toast.png`, `lab_lose9/03…` | That a raid is coming, when, from where, how big | Paper card "COLLECTIONS: FIRST NOTICE": `WO 25-SB-452`, `UNITS 2 IN 1 WAVE`, `ENTRY SITES 10 (A, B, C, D, E, F, G, H, I, J)`, `TRIGGER HEAT 25 CROSSED`; a toast; the HUD tag already says `RAID AT 50 · 24 AWAY` | guessable | No *when* (before the next run? now?). JACK IN stays on screen next to RAID SETUP (`bb/shots/0005.png`). Ten entry letters for two units read like ten attackers. At Heat 76 the HUD says `RAID AT 100 · 24 AWAY` while a raid is pending, which reads as "safe for 24". |
| 4 | Grid with raid pending | `lab_hold/05_grid_raid_pending.png`, `bb/shots/0005.png` | Where the threats will come from | Blue dashed lines on the HQ map | opaque | Threat routes are blue, the same family as the Cell's links. The GDD calls for red grease pencil (§9.3). |
| 5 | Raid Setup: work order | `lab_lose9/06_setup_bare.png` | How many threats, how strong | `UNITS 4 IN 1 WAVE`, `STRENGTH +25%`, `THREATS STOPPED 0/5`, `DOWN / TAKEN 1/1`, `LINK FROZEN` | guessable | **4 vs 5** on the same card. Which link is frozen is never shown. |
| 6 | Forecast chip | same, and `crop_forecast_lose.jpg` | Will I survive, what do I lose | `IF THE RAID RUNS NOW: CELL HOLDS / HOME 50 → 20 (-30) / 1 TAKEN / 1 DOWN / INFECTED 0% → 22%` | guessable (color) | Honest headline. **Which** node is taken is not named. "INFECTED" is defined nowhere on screen. The Schematics / Heat consequence is missing. |
| 7 | THREAT INTEL | same, and `bb/shots/0006.png` | Who is coming, along which path | Rows `A COLLECTOR HP 15 DMG 6 > HOME SERVER // T1 Site`; a third row (ENFORCER 31 / 11) appears only after a second; the rest are behind `MORE` | opaque | The toast names "an Enforcer and a Lockdown Unit". The first frame of intel shows neither. On the map, threats are blue rings with letters and `x2`, with no unit shape. |
| 8 | YOUR NETWORK | same | Which of my nodes are at risk | `3 NODES`, then one row: `HOME SERVER HP 50 → 20 HOLDS` | opaque | It says 3 and lists 1. The node that will be TAKEN is not in this panel. |
| 9 | Crew & stationing | `lab_hold/06_setup_bare.png`, `bb/shots/0011.png` | What stationing does | Red alarm `NO CREW STATIONED… Nobody will help your nodes.`, `> STATION BREAKER 3 HERE` | opaque | "Here" points nowhere. Stationing Breaker 3 changed **nothing** in the forecast (`bb/0010` → `bb/0011`; `lab_hold/06` → `07`). The alarm is loud for an action with no visible payoff. |
| 10 | Defense cards and effect words | `lab_hold/08_setup_card_effect.png`, `bb/shots/0008.png`, `0010`, `0012` | What a card will do on this node | Card: `TURRET INT 10 x1 HITS 4 · REACH 1 first in path`; a strip at the bottom: `no change: the threat is too strong` / `TAKEN > DOWN / HOME SERVER 20 > 19` | guessable | The what-if sits about 400 px from the node. One click on a card places it on the selected node at once, with no target step (`bb/0012`). Every captured what-if was "no change" or a sideways trade. |
| 11 | START DEFENSE | `lab_lose9/09_start_confirm.png`, `lab_breach/09_start_confirm.png` | Last chance, stated in stakes | `CONFIRM // NO CREW`: "No crew is stationed. Start the defense anyway?" | opaque | On the breach save the forecast says BREACHED (campaign lost). The confirm still only talks about crew. |
| 12 | Playout | `lab_lose9/10…14`, `bb/shots/0014–0021`, `lab_hold/10–12` | Cause and effect, step by step | Camera zooms and re-frames per step. Damage floaters stack on the home node. The `LIVE RAID FEED` text log narrates. A dashed dial says `RAID IN PROGRESS: --` | opaque | The **text log carries the story**, not the map. The hold raid lasts 1 step and 7 s (`lab_hold.log`: "planned 6.9 s, measured 7.0 s"). The lose raid lasts 12 steps and 26 s at 1x. Assets firing are not distinguishable on the map. |
| 13 | Verdict | `lab_hold/12_playout_end.png`, `crop_dial_hold.jpg`, `lab_breach/12_playout_end.png` | Did I win, what did it cost | 160 px dial `RAID RESULT: CELL HOLDS / NO HEAT · HOME -10` (text clips the circle). A HUD pill repeats it. Breach: `BREACHED` in red grease pencil, `CONTINUE` | guessable | The verdict is too small. Campaign loss is staged like a normal result. |
| 14 | After-action report | `lab_hold/14_report.png`, `lab_lose9/18_report.png`, `crop_report_lose.jpg` | What I lost and what it costs to fix | Solace paper: `SITES TAKEN 1 (T1 SITE)`, `NODES DOWN (REPAIR) T1 SITE (10 SCHEMATICS)`, `NEW RAID ENTRY POINTS T1 SITE`, `HOSTILE HOME SERVER 20/50`, `HOME SERVER 50 > 20 HOLDS`, `T1 SITE (SAFEHOUSE) 20 > 0 DOWN`, `T1 SITE 20 > 0 TAKEN`, then a yellow `CELL HOLDS` stamp | guessable | Home is listed twice ("HOSTILE HOME SERVER" is the corp's view and reads like an enemy server). Two rows are both called "T1 SITE". The stamp has the same color for -10 and -30 with 2 sites lost. The **destroyed turret** and the **returned operative** are not reported (`bb/0025`). |
| 15 | HQ / city after | `lab_lose9/19_hq_after.png`, `bb/shots/0025.png`, `lab_hold/16_grid_after.png` | What changed on my map | `ENTRY POINT` scrawl and a red X on the taken node. Safehouse card `0/20 DOWN`, `REPAIR 10 SCHEMATICS`. `DEFENSE ARMORY 1/6` | guessable | This is the second-best moment. The repair is one click away. The lost turret is silent, and so is the clean-defense reward you missed. |

## Top 10 problems (ranked by player impact)

1. **P1 — The map does not forecast per node.** GDD §7.1 requires every node to show HOLDS / DOWN / TAKEN during setup. The setup map
   (`lab_lose9/06_setup_bare.png`) shows none. The forecast box says "1 TAKEN / 1 DOWN" without naming the nodes. The only per-node read
   is a hover tooltip after a click (`bb/shots/0010.png`: "T1 Site: integrity (HP) 20 → 0 in the raid. DOWN"). The player cannot plan
   against a loss they cannot locate. *Technique:* Into the Breach paints every threatened tile red with striped hazard fill and
   numbers the attack order on the board (`refs/itb/steam_03.jpg`, `refs/itb/steam_00.jpg`). Civ VI hangs the siege state on the city
   banner itself (`refs/civ6/City_under_siege_Civ6_.png`). Sheet: `compare_defense_planning.jpg`.
2. **P1 — Card and station effects are invisible or cannot be judged.** In every captured case a placement gave "no change", or swapped one
   loss for another: turret on T1 Site turned "1 TAKEN / 1 DOWN, home −30" into "2 DOWN, home −31" (`bb/0008`, `bb/0010`). Adding an
   ice lock flipped it back (`bb/0012`). Stationing Breaker 3 changed nothing (`bb/0011`, `lab_hold/07`). The player is given no basis to
   prefer TAKEN or DOWN, because their costs (reclaim netrun vs 10 Schematics repair, entry point vs none) are not on the setup screen.
   *Technique:* Civ VI / VII put both sides' numbers and every modifier line next to a verdict word ("MAJOR VICTORY") before you commit
   (`refs/civ6/Theological_combat_Civ6_.png`, `refs/civ7/combat_preview_civ7.png`). XCOM 2 itemises HIT / DAMAGE 4–6 / CRIT
   (`refs/xcom2/steam_04.jpg`). Sheet: `compare_outcome_forecast.jpg`.
3. **P1 — The threat count contradicts itself.** One screen shows `UNITS 4 IN 1 WAVE`, `THREATS STOPPED 0/5`, two intel rows, and a toast
   naming an Enforcer and a Lockdown Unit (`lab_lose9/03`, `lab_lose9/06`). The denominator moves to `0/4` after a turret is placed
   (`bb/0010`). Hold: `ENTRY SITES 10 (A…J)` for 2 units (`lab_hold/03`). A first-time player cannot answer "how many are coming?".
   *Technique:* Kingdom Rush shows the wave as a counter (`WAVE 10/17`, `refs/kr/steam_04.jpg`) and draws each wave's route with a
   single numbered entry flag (`refs/kr/LostEmp_Wave_01.png`). Sheet: `compare_threat_warning.jpg`.
4. **P1 — Campaign loss is staged as a normal result.** On the breach save, setup already forecasts `BREACHED` (`lab_breach/06`). The
   START DEFENSE confirm only warns about crew (`lab_breach/09`). The result is a 160 px dial plus `CONTINUE`. "Campaign lost." appears
   only in the text feed (`lab_breach/12`). *Technique:* XCOM 2 stamps "Failed!" across a red panel and names the consequence card
   ("Reinforcements") (`refs/xcom2/steam_06.jpg`). Sheet: `compare_consequences.jpg`. (Caveat: the lab disables scene switching, so a
   campaign-over screen may follow in the real flow. The 120-frame shot `lab_breach/14_campaign_end.png` still shows the dial.)
5. **P2 — The verdict's tone is flat.** The report's yellow `CELL HOLDS` stamp is identical for home −10 (`lab_hold/14`) and for
   home −30 with a site DOWN and a site TAKEN (`lab_lose9/18`). GDD §7.2 says the stamp's color shows how well. The playout dial is
   orange in both, and its second line clips the circle (`crop_dial_hold.jpg`). *Technique:* Civ's verdict banner changes word and
   color with the margin (MAJOR VICTORY on green, `refs/civ7/combat_preview_civ7.png`). Sheet: `compare_consequences.jpg`.
6. **P2 — "When" is never stated.** The notice gives trigger, target and units, but not when the raid fires. JACK IN stays available
   beside RAID SETUP (`bb/shots/0005.png`). Right after the raid queues, the HUD tag jumps to the *next* threshold (`RAID AT 50 · 24
   AWAY`, `lab_hold/03`; `RAID AT 100`, `lab_lose9/03`), which reads as "safe". *Technique:* XCOM 2's Avatar pip bar sits top-center
   and fills (`refs/xcom2/steam_07.jpg`). Frostpunk pins the temperature dial top-center and the objective "Survive the first storm" at
   the lower left (`refs/frostpunk/steam_14.jpg`). Sheet: `compare_threat_warning.jpg`.
7. **P2 — Threats have no identity on the map.** Threats are blue rings with letters, plus `x2` stacks, tangled over the Cell's yellow
   links (`lab_lose9/06`, `bb/0006`). Blue is not "enemy" anywhere else in the UI. The GDD asks for red grease pencil (§9.3). Unit types
   exist only in the intel text. *Technique:* Slay the Spire puts a single icon plus a number over each enemy (sword + "7",
   `refs/sts/steam_02.jpg`; icon set `refs/sts/Intent_Attack4.png`, `Intent_Defend.png`, `Intent_Buff.png`). Into the Breach uses red
   arrows from each attacker (`refs/itb/steam_00.jpg`). Sheet: `compare_defense_planning.jpg`.
8. **P2 — The playout is told in a text log, with a moving camera.** The camera re-frames each step (`lab_lose9/10` vs `14`;
   `bb/0015`–`0019`). The board loses its anchor. Turret shots are only legible as "Turret on T1 Site hits Auditor for 4" in the feed. The
   first raid lasts **1 step / 7 s** (`lab_hold/10–12`, `lab_hold.log`), shorter than the GDD's 30–60 s and too short to read.
   *Technique:* Into the Breach keeps the board fixed and shows HP pips on every unit (`refs/itb/steam_05.jpg`). They Are Billions
   keeps the camera and raises an on-screen alert with a minimap ping (`refs/tab/steam_10.jpg`). Sheet: `compare_resolution_playout.jpg`.
9. **P2 — The report omits losses and repeats rows.** The destroyed turret and the operative sent back to reserves are not reported. HQ
   shows `DEFENSES ICE LOCK` and `ARMORY 1/6` afterwards (`bb/0025`). Home appears twice (`HOSTILE HOME SERVER` and `HOME SERVER`).
   Two different nodes are both "T1 SITE" (`crop_report_lose.jpg`). *Technique:* XCOM 2's after-mission screen names the single
   consequence that matters with its icon (`refs/xcom2/steam_06.jpg`). Frostpunk turns a consequence into a named event with a choice
   (`refs/frostpunk/Fear_of_the_Storm_-_Panic_spreads.png`). Sheet: `compare_consequences.jpg`.
10. **P3 — Jargon with no definition: INFECTED %, WO numbers, STRENGTH %, NO HEAT.** "INFECTED 0% → 22%" (`crop_forecast_lose.jpg`)
    is not explained anywhere in the flow. "NO HEAT" reads as good news, but under the inverted R2 rule (GDD §7.2) it means you
    *missed* +5 Heat and the Schematics payout. The player is never told what a clean defense would have paid. *Technique:* Civ VI
    spells each modifier as a signed line ("−2 Damaged unit", `refs/civ6/Theological_combat_Civ6_.png`). Sheet:
    `compare_outcome_forecast.jpg`.

Also seen: `ERROR: ContentLookup: unknown content id ''` in `lab_lose9.log` / `lab_lose9_scr.log` during the 9-node playout. In setup, the
1x / 2x / 4x / SKIP buttons show (dimmed) before anything plays.

## AAA comparison

| Job | Ours (shot) | Theirs (shot) | Technique we lack | Sheet |
|---|---|---|---|---|
| Threat warning | HUD tag `RAID AT 25 · 3 AWAY`, paper notice (`lab_hold/01`, `03`) | XCOM 2 Avatar bar `refs/xcom2/steam_07.jpg`; Frostpunk −50 °C + SURVIVE `refs/frostpunk/steam_14.jpg`; Kingdom Rush path + flag `refs/kr/LostEmp_Wave_01.png`; Bad North boats `refs/badnorth/steam_02.jpg` | A persistent top-center clock for the *pending* threat; the attackers visible on the map | `compare_threat_warning.jpg` |
| Defense planning | Blue ring tangle, hover-only node outcome (`lab_lose9/06`, `bb/0010`, `bb/0012`) | ITB numbered attack order + red tiles `refs/itb/steam_03.jpg`, `steam_00.jpg`; StS intent `refs/sts/steam_02.jpg`; KR towers on path `refs/kr/steam_04.jpg` | On-board telegraph per threat and per target; placement shown where it acts | `compare_defense_planning.jpg` |
| Outcome forecast | `CELL HOLDS / HOME 50→20 / 1 TAKEN 1 DOWN` (`crop_forecast_lose.jpg`); bottom-strip what-if (`crop_whatif_bb.jpg`) | Civ VI preview `refs/civ6/Theological_combat_Civ6_.png`; Civ VII `refs/civ7/combat_preview_civ7.png`; XCOM 2 `refs/xcom2/steam_04.jpg` | Before / after for each side, itemised causes, a verdict word whose color tracks the margin, next to the target | `compare_outcome_forecast.jpg` |
| Resolution playout | Re-framing camera, text feed (`lab_lose9/10`, `14`, `lab_hold/12`) | ITB fixed board + HP pips `refs/itb/steam_05.jpg`; Bad North on-island fight `refs/badnorth/steam_05.jpg`; TAB alert + minimap `refs/tab/steam_10.jpg` | A stable camera; damage and kills drawn on the units, not in a log | `compare_resolution_playout.jpg` |
| Consequences | Same yellow stamp for every hold; breach = dial + CONTINUE (`lab_lose9/18`, `lab_breach/12`, `bb/0025`) | XCOM 2 "Failed!" + named consequence `refs/xcom2/steam_06.jpg`; Civ VI siege on banner `refs/civ6/City_under_siege_Civ6_.png`; Frostpunk event `refs/frostpunk/Fear_of_the_Storm_-_Panic_spreads.png` | Graded verdict; loss staged as loss; every lost thing named once, with its fix | `compare_consequences.jpg` |

Where we are level or ahead: the paper / stamp language (INTERCEPTED, DECRYPTED, CLASSIFIED) has more personality than any of the five
reference UIs. The Heat HUD's countdown tag (`RAID AT 25 · 3 AWAY`) is as direct as XCOM's pip bar.

## No-words test (scrambled text)

`lab_hold_scr/`, `lab_lose9_scr/`. Every Control's text becomes asterisks. What survives: the forecast panel's color (orange vs red),
the house icon, integrity numbers (`50 > 20`, `20 > 0`) in red, three card icons (crosshair, snowflake, hook), the baked-in stamps
(DECRYPTED, RAID SETUP), and letter rings A / B on the map. What is lost: the outcome (CELL HOLDS vs BREACHED differ only by text and
an orange-to-red shift, with the same house icon), which node falls, what each threat is, what a card does, and the whole report
(`lab_lose9_scr/18_report.png` is a wall of brackets). A non-English player can guess "defend the house, it gets hurt". They cannot
plan. Grades: forecast guessable, threats opaque, cards guessable, playout opaque, verdict opaque, report opaque.

## Gameplay judgement

- **Real choices?** The engine allows them: placement changed outcomes in `bb/0008`–`0012`. As presented, though, a choice is a
  gamble between labels whose costs are off-screen. The hold raid has 2 Collectors with 12 HP against a 4- or 6-damage turret. No
  single available card could change its outcome (`lab_hold/09` "no change").
- **Effect visible before commit?** Partly. The headline updates, but per-node results need a hover. Station shows no effect.
- **Certain, probabilistic or opaque?** Certain in rules, opaque in presentation. Determinism is the raid's best feature and the UI
  hides it.
- **Pacing.** A 7 s one-step raid after a 3-panel setup is anticlimactic. 26 s for 12 steps is close to right.
- **Cause legible?** Yes for Heat → raid (`TRIGGER HEAT 25 CROSSED`, HUD tag). No for "why this node": routing rules
  ("weakest node", "highest-value node") are written but never drawn.
- **Fair and motivating?** The R2 inversion (a clean defense *gains* Heat) is not communicated anywhere, so "NO HEAT" reads as a win.
  This is a **designer decision**: either show "missed: +12 Schematics" on a damaged hold, or reconsider rewarding a clean hold with
  Heat at all.

## Recommendations

Quick wins (view and text only, no rule change):
1. Draw per-node outcome badges on the setup map (HOLDS / DOWN / TAKEN with the after-integrity), as GDD §7.1 already requires.
2. Name the nodes in the forecast chip ("TAKEN: T1 Safehouse"), and put the cost next to each ("repair 10 ⧉", "reclaim run").
3. Move the card what-if next to the hovered node, and require a target click after the card click (no instant placement).
4. Make one threat count the single source for the notice, the tally and the intel (show all rows, no `MORE` for ≤ 5).
5. Color threat routes red as the GDD says. Give each threat type a silhouette icon on the map.
6. Grade the stamp: clean, damaged and heavy loss get different colors and words. Breach gets its own full-screen beat, and the
   START DEFENSE confirm on a BREACHED forecast must say "this loses the campaign".
7. Report: list lost assets and returned crew; drop the duplicate home row; disambiguate same-name sites.
8. Define INFECTED (or hide it until it matters). Replace "NO HEAT" with "Damaged: no reward (clean would pay +5 Heat, +12 ⧉)".
9. Keep the HUD tag on the pending raid ("RAID PENDING · resolves before next run") until it resolves.

Structural:
1. Lock the camera during playout to the setup framing. Draw damage numbers and kills on the units. Make the feed optional.
2. Give the raid a minimum readable length (hold the first contact; slow step 1). **Designer decision** if it touches step rules.
3. Make stationing visible: an on-map aura and a forecast delta. If it truly does nothing in a case, say why.
4. Before / after preview per placement, Civ-style: two columns (threats, nodes) with signed modifier lines.
5. **Designer decision:** the inverted clean-defense Heat (+5) and "damage pays nothing" rule needs either a clear on-screen
   explanation or a rethink. As shown, it punishes the player for a perfect defense without telling them.

## What works

- The Heat HUD countdown (`RAID AT 25 · 3 AWAY`) and the threshold ticks.
- The forecast box is honest and updates live after a placement (`bb/0010`).
- The repair is offered right where the damage is, with a price (`bb/0025`).
- The paper / stamp art direction has real character.

## Evidence index

- Contact sheet: `D:/rc_tmp/raid_review2/flow_sheet.jpg`
- Comparison sheets: `D:/rc_tmp/raid_review2/compare_threat_warning.jpg`, `compare_defense_planning.jpg`,
  `compare_outcome_forecast.jpg`, `compare_resolution_playout.jpg`, `compare_consequences.jpg`
- Captures: `lab_hold/`, `lab_lose9/` (`--size=9`), `lab_breach/`, `lab_hold_scr/`, `lab_lose9_scr/`, `bb/shots/` (blackbox on a
  `--save-default` lose save), `sb/04_raid_setup.png` and `sb_scr/04_raid_setup.png` (storyboard, plain and scrambled). These show
  the same setup layout over an empty dark backdrop, with the same "1 NODE" network listing home only.
- Reference screenshots (`refs/`), all viewed; sources in `refs/SOURCES.tsv`:
  - Civ VI: `civ6/Theological_combat_Civ6_.png` (civilization.fandom.com/wiki/File:Theological_combat_(Civ6).png),
    `civ6/City_under_siege_Civ6_.png` (…/File:City_under_siege_(Civ6).png)
  - Civ VII: `civ7/combat_preview_civ7.png` (…/File:Combat_preview_(Civ7).png)
  - XCOM 2: `xcom2/steam_04.jpg`, `steam_06.jpg`, `steam_07.jpg` (store.steampowered.com/app/268500)
  - Into the Breach: `itb/steam_00.jpg`, `steam_03.jpg`, `steam_05.jpg` (store.steampowered.com/app/590380)
  - Slay the Spire: `sts/steam_02.jpg` (store.steampowered.com/app/646570); intent icons `sts/Intent_Attack4.png`, `Intent_Defend.png`,
    `Intent_Buff.png` (slaythespire.wiki.gg)
  - Frostpunk: `frostpunk/steam_14.jpg` (store.steampowered.com/app/323190), `Fear_of_the_Storm_-_Panic_spreads.png`
    (frostpunk.fandom.com)
  - Kingdom Rush: `kr/LostEmp_Wave_01.png` (kingdomrushtd.fandom.com), `kr/steam_04.jpg` (store.steampowered.com/app/246420)
  - Bad North: `badnorth/steam_02.jpg`, `steam_05.jpg` (store.steampowered.com/app/688420)
  - They Are Billions: `tab/steam_10.jpg` (store.steampowered.com/app/644930)
- Not found as a screenshot: Frostpunk's dedicated storm-countdown widget (only the temperature dial plus the "Survive the first storm"
  objective were found), and an in-combat Slay the Spire screenshot with several intents (one enemy with "7" was found, plus the
  official icons).
