# Raid review, 2026-10-21 (main b9416e91)

**Verdict: the raid is not clear. It tells the player the wrong result, hides the right one, and the playout plays a result the game already decided.**

Scores (1-10): clarity of what / why / when **4** (what 4, why 5, when 3) · outcome predictability **3** · no-words test **2** · visual quality against AAA **4** · decision depth **3**.

1. The rules are deterministic, so the game knows the exact outcome before START DEFENSE. The screen shows only part of it ("HOME -10"). It leaves out the Heat penalty, the reward at stake and whether the raid counts as won or lost. At higher Heat the forecast is folded away behind a MORE tab.
2. The report then stamps a big yellow **CELL HOLDS** on raids the rules score as **lost**. These raids give +5 Heat, no Schematics and add to raids_lost. One example: home 50→16, two nodes TAKEN, zero threats destroyed, and the stamp still says CELL HOLDS. A player cannot learn the raid rules from a screen that misreports the result.
3. The first raid in our lab state could not be won with the starting tools. Two 12-HP Collectors reach home in one step, and a turret hits for 4-6. So the first raid works as a tax that adds Heat, and that Heat brings the next threshold closer. That matches the testers' "piling on" (PB-SOL-1 D-07).
4. The threat map is one red pencil scribble. It shares its red with the player's own netrun TARGET mark and route. Threat HP and damage appear nowhere, so the player cannot work out why a turret did nothing.
5. The playout lasts 1-15 seconds, not the 30-60 the GDD plans. The result chip is visible from the first frame and the text feed runs ahead of the map. The speed controls do nothing useful on a one-step raid.
6. Without words, a player can tell "red lines are coming at my stuff" and nothing else. Every number that matters is text, and the enemy (Solace green) is nearly the same hue as the player's own lime network.
7. The paper, sticker and grease-pencil art direction has real character. The problems are information design, not the art style.

---

## How this was captured

- **Storyboard** (`tools/playtest/storyboard.gd`), plain and `--scramble` (pseudolocalized), 1280x720, text 1.0: `D:/rc_tmp/raid_review/sb*/04_raid_setup.png` (folders deleted after the review; the key shots are copied below).
- **Raid lab** (new tool, `tools/playtest/raid_lab.gd` / `.tscn`). It builds a Solace campaign in code with a private slot and three crew. It brings Heat just under a threshold, then crosses it with the real `HeatRules.add_heat`, so the raid is queued by the rules. It then walks HQ → Grid → Raid Setup → START DEFENSE → playout → report → HQ. Variants:
  - **hold**: Heat 22→26, `raid_heat_25`, home plus one claimed node, a turret placed and one operative stationed.
  - **lose**: Heat 72→76, `raid_heat_75`, a wider network, nothing placed.
  - **breach**: lose with home at 6 integrity.
  - **lose --scramble**: the no-words run.
- **Black-box play** (`tools/playtest/blackbox.py`). The lose state was saved with `--save-default` into the worktree's own ignored `saves/`. I continued it from the title and played it with real mouse clicks: hover a card, click to place, START DEFENSE, the no-crew confirm, the playout, CONTINUE, the report, BACK TO THE GRID.
- All shots are at 1280x720. The key ones are in `D:/rc_tmp/raid_review/shots/` and on the contact sheet `D:/rc_tmp/raid_review/flow_sheet.jpg`.
- **Not captured:** the netrun run-end page at the moment the threshold is crossed, the mid-run raid interlude, and the Heat-band poster animation. Whether JACK IN is blocked while a raid is pending was not tested. JACK IN is visible and lit in shot 04.

---

## The flow, moment by moment

Grades: **clear** / **guessable** / **opaque**, read off the `--scramble` captures, not imagined.

### 1. Heat rising toward a raid. Shots 01, 02
- **What the player needs:** "I am at 22, a raid comes at 25, and this run's Rack or flatline will push me over."
- **What the screen says:** a small HEAT 22 COOL bar with unlabeled tick marks. The Heat terminal (a click away) says `NEXT 25 RAID // 30 complication`, which is good. The selected Site card shows `FLATLINE HEAT +11 -> 87` (shot 04), but it never says that this crosses a raid threshold. Nothing on the HQ face counts down to the raid.
- **No-words:** guessable. A bar with a fill and ticks reads as "a meter that gets worse", but not as "a raid at the next tick".
- **Problems:** there is no doom clock or distance-to-raid display. The Rack and flatline Heat on the Site card is not linked to the raid it would trigger. The player who later gets "a raid arrived before I understood the basics" (D-07, tinroof) had no countdown to watch.

### 2. Announcement at HQ. Shots 03, 04
- **What the player needs:** a raid is coming, against what, from where, when, and whether they must deal with it now.
- **What the screen says:** a corp letter ("COLLECTIONS: FIRST NOTICE") slides in at top left with TARGET / UNITS / ENTRY SITES / TRIGGER: HEAT 25 CROSSED. A RAID SETUP [R] button, a tooltip "A raid is queued. While Heat stays at 25 or more, elites are more frequent", an INTERCEPTED corp-news toast at the foot, and the HUD RAIDS 1.
- **Good:** TRIGGER: HEAT 25 CROSSED states the cause plainly.
- **Problems:**
  - ENTRY SITES `10 (A, B, C, D, E, F, G, H, I, J)` lists ten letters that do not appear on the HQ map at Heat 25 (shot 03). For 2 units, ten entry sites is noise.
  - In the real arrival (shot 04, Heat 76), the threat routes **are** drawn on the HQ map in red. In the same red, the player's own route to their netrun **TARGET** is drawn as red dashes, and "TARGET" is written in red pencil next to them. A first-time player reads "TARGET" in red during a raid warning as "this is what they are attacking".
  - JACK IN is still lit. Nothing says whether the raid waits, fires on the next run, or blocks the run.
- **No-words:** guessable. A paper with a red INTERCEPTED stamp says "bad letter". Red lines converging on the heart icon say "attack on home" in shot 04, but nothing tells them apart from the player's own red route.

### 3. Raid Setup, bare. Shots 05 (Heat 25), 07 (Heat 75), 18 (scrambled)
- **What the player needs:** who comes, how strong, along which path, what each of my nodes ends as, and what I can do about it.
- **What the screen says:**
  - Left: the work order (TARGET, UNITS `2 IN 1 WAVE`, `STRENGTH 0%`, `IF IT RAN NOW HOME SERVER 50 > 40`, `THREATS STOPPED 0/2`, `INFECTION POPULATION INFECTED 0% > 0%`) and a pink disc "IF THE RAID RUNS NOW: HOME -10".
  - Right: THREAT INTEL lists each threat as `COLLECTOR > HOME SERVER // T1 Site`, then YOUR NETWORK with `HP 50 → 40 HOLDS`.
  - Bottom: three defense cards (TURRET / ICE LOCK / DECOY), the CREW / MARKET / DEFENSE tabs, START DEFENSE, and 1x / 2x / 4x / SKIP.
- **Good:** the per-node forecast (`HP 50 → 40 HOLDS`) is the right idea, and it is exact.
- **Problems:**
  - At Heat 75 (shot 07) the work order **folds**. The IF IT RAN NOW line and the forecast disc are hidden behind a `> MORE` tab. On the hardest raid of the game, the outcome is off screen.
  - THREAT INTEL never gives a threat's integrity, damage or speed. Collector = 12 HP and 5 damage exists only in content files.
  - The routes at Heat 75 are a knot of red pencil with A / B / C / D letters on top of each other and on top of TARGET.
  - YOUR NETWORK says `3 NODES` and lists one (shots 07, 09). The other two rows are clipped by the panel.
  - `HP 50 → 16 HOLDS` is printed in calm green while the home loses two thirds of its integrity.
  - `STRENGTH 0%` and `POPULATION INFECTED 0% > 0%` are zero-information rows on the first raid.
  - The red `NO CREW STATIONED: 2 alive, 0 stationed. Nobody will help your nodes.` overlaps the `> SAVED` chip (shot 05 and storyboard 04).
  - The speed buttons sit greyed under START DEFENSE before there is anything to play.
- **No-words:** opaque. Scrambled (shot 18), the only things left are the red knot, the house icon in a pink disc, and number pairs inside bracket noise. The defense cards keep their icons (crosshair, snowflake, magnet), and those are the best wordless elements on the screen.

### 4. Raid Setup: placing a defense. Shots 06, 08, 09
- **What the player needs:** to see, before committing, what this asset will do here.
- **What the screen says:**
  - Hovering a card opens a tooltip with the asset's rules. It also opens an **IF PLACED** panel: `TURRET > T1 SITE: T1 SITE TAKEN > HOLDS, HOME SERVER 16 > 25` (shot 08). This is the right mechanism, and the best thing on this screen.
  - Clicking places it on the default node. The routes redraw and the network chip updates (`HP 50 → 25`, shot 09).
- **Problems:**
  - The what-if is **text in a side panel only**. The map does not show where the turret would reach or which threat it kills.
  - In the Heat-25 raid, a turret placed and an operative stationed changed **nothing** on the forecast (shot 06 against shot 05: still HOME -10, THREATS STOPPED 0/2). Nothing says why. The player concludes "defenses don't work".
  - A drag from the card to a node did nothing in my test. Clicking worked.
  - The station count went to 1, but the map shows no operative on the node.
- **No-words:** guessable for "the red lines moved". Opaque for "what did my turret do".

### 5. START DEFENSE and the no-crew confirm. Shot 10
- **The dialog:** "No crew is stationed. Start the defense anyway? Station an operative on a node at HQ first, or the raid hits an unaided network."
- **Problems:**
  - The player **is** at HQ, and the raid setup is an HQ page. "At HQ first" sends them looking for a different screen (C-10: mothball and tinroof lost 4-6 minutes and never found it).
  - The dialog does not say what stationing would change in numbers, although the projection could.
  - Stationing is done from the Site card's `Station Breaker 3` button on the HQ CREW page (shots 01 to 04). The raid setup has no crew on it.
- **No-words:** guessable (a yellow and a pink button, a modal). The choice itself is opaque.

### 6. Playout. Shots 11, 12, 13, 17
- **What the player needs:** to watch their plan work or fail, hit by hit, and understand why.
- **What the screen says:**
  - A zoomed map, threat icons in red rings, RAID IN PROGRESS in the HUD, and a "LIVE RAID FEED" text log with 1x / 2x / 4x / Skip and a step number.
  - A pink disc at top right shows **the result from the first frame** ("IF THE RAID RUNS NOW: HOME -34, 2 TAKEN"). The disc later turns into "RAID RESULT".
- **Problems:**
  - **Length.** The Heat-25 raid is over after **1 step** (shot 11 feed: "Raid over after 1 step(s)"). The Heat-75 raid takes 15. With `raid_move` 0.5 s plus `raid_step_gap` 0.2 s, that is about 1-12 seconds at 1x, against the GDD's 30-60 s. In black-box play the 5-step raid had ended within 2 s of the click. The speed buttons are vestigial.
  - **Feed ahead of the map.** At step 1 the feed already lists both Collectors reaching home and the HP falling 50→45→40. On the map they still sit at the entry. At step 8 the feed reports "T1 Site is DOWN. T1 Site is TAKEN" while the HUD HOME still shows 40 and nothing on the map has changed (shot 12).
  - **Map.** The camera frames a corner. Routes are drawn as many-segment loops for what the feed calls one move ("moves from T1 Site to HOME SERVER"). Threats travel T3 → T2 → T1 through corporate Sites, which reads as wandering.
  - **End frame.** At the end the threats vanish and the routes recolor yellow. TAKEN nodes get a flat **green** fill with two TAKEN stickers (shot 13). Green is Solace's color and also close to the player's lime network color.
  - **Breach.** A small red "BREACHED" in pencil at bottom left and a wall of feed text (shot 17). For the moment the campaign is lost, it is underplayed.
- **No-words:** opaque. In the scrambled version (shot 19), a green blob and two stickers say "something happened here". Nothing else carries meaning. The feed is the only explanation, and it is text.

### 7. Report. Shots 14, 15, 20
- **What the player needs:** did I win, what did it cost, what do I fix now.
- **What the screen says:** the corp's AFTER-ACTION REPORT with UNITS DEPLOYED / DESTROYED, SITES RECLAIMED, HOSTILE HOME SERVER, SUSPECT FILE (HEAT) 76 > 81, a per-node HOLDS / TAKEN list, and a big yellow **CELL HOLDS** sticker beside a red CLASSIFIED stamp. Exit is BACK TO THE GRID.
- **Problems:**
  - **CELL HOLDS on lost raids.** Shot 14: 4 units / 0 destroyed, 2 nodes TAKEN, home 50→16, Heat +5, so the rules record a lost raid, and the stamp says CELL HOLDS. Shot 15: Heat 25 raid, 2/0, home -10, Heat +5, also lost by the rules (`RaidResolver.apply`: not won, so `raids_lost += 1` and `lost_raid_heat`), and the stamp again says CELL HOLDS.
  - The GDD term (7.2: "a survived raid ends CELL HOLDS") collides with the rules' won / lost. The player is congratulated and punished on the same screen.
  - There is no reward line when won and no "LOST: +5 Heat" line when lost. The Heat change is labeled SUSPECT FILE (HEAT) without a cause.
  - "HOSTILE HOME SERVER" (the player's own home, in the corp's words) reads as an enemy server.
  - Two rows are both "T1 SITE". Since W0 SITENAMES removed Site names, the player cannot tell which node fell.
  - GDD 7.2 says the summary shows **repair costs and new entry points**. Neither is on the report.
- **No-words:** misleading, which is worse than opaque. Scrambled (shot 20), what remains is a yellow sticker, which reads as good, and red numbers, which read as bad.

### 8. Consequences at HQ and on the Grid. Shot 16 (and black-box `bb/0038`)
- **What the screen says:** HUD HOME 16/50 and Heat 81 HUNTED. A TAKEN Site's card says `STATUS TAKEN`, `reclaim`. Small red flags sit on the lost nodes. A damaged Vault's card shows `12 / 20`.
- **Problems:**
  - Damage is not drawn on the map (no cracked or DOWN look on a damaged but working node).
  - No repair prompt, no "your home is at 16/50, patch it?" prompt, and no new entry-point marker.
  - The next raid threshold (85 / Purge 100) is not called out, though Heat just jumped 5 because of this raid.
- **No-words:** guessable (red flags on two nodes).

---

## Top 10 problems, ranked by player impact

1. **The verdict contradicts the rules.** CELL HOLDS is stamped on raids that are scored as losses (+5 Heat, no reward, `raids_lost`). The player learns the wrong lesson every raid. Evidence: `shots/14_lab_lose_16_report.png`, `shots/15_lab_hold_16_report.png`, `scripts/core/raid_resolver.gd` `apply()`.
   *Fix technique:* XCOM's mission debrief grades the result in one word (Flawless … Poor) that matches the consequences. Into the Breach shows the exact grid-power loss at mission end. Use one verdict word derived from won / lost / breached, colored to match: **REPELLED +8** / **OVERRUN +5 HEAT** / **BREACHED**.
2. **The forecast is incomplete and sometimes hidden.** At Heat 75 the forecast folds behind MORE. It never shows the Heat penalty, the reward, or won/lost, only home HP. Evidence: `shots/07_lab_lose_06_setup_bare.png`, `shots/05_lab_hold_06_setup_bare.png`.
   *Fix:* Into the Breach previews every consequence of the enemy turn (building hits, grid power) before you act ([Game Developer, Road to the IGF](https://gamedeveloper.com/game-platforms/road-to-the-igf-subset-games-i-into-the-breach-i-); [Prototypr UX piece](https://blog.prototypr.io/into-the-breachs-ux-makes-you-feel-smart-a9cb03210757)). One always-visible outcome block: verdict word, Home Δ, nodes lost, Heat Δ, Schematics. Never fold it.
3. **Defenses can change nothing and the screen does not say why.** Threat stats are hidden. Evidence: `shots/06_lab_hold_07_setup_defended.png` (turret placed and operative stationed: forecast still HOME -10, 0/2), THREAT INTEL rows with no HP or damage.
   *Fix:* Slay the Spire's intent shows the number with the icon (attack 12) ([Roy Tang](https://roytang.net/2019/02/slay-the-spire/), [Untapped StS2 guide](https://sts2.untapped.gg/guides/how-to-read-enemy-intent)). Civ VI's combat preview puts both strengths and every modifier side by side ([Civ wiki, Combat (Civ6)](https://civilization.fandom.com/wiki/Combat_(Civ6))). Put HP and damage on each threat marker (a pip bar). Have IF PLACED say "kills 0 of 2: Collector 12 HP, turret 4 per step".
4. **The threat map is unreadable spaghetti and shares its red with the player's own target.** Evidence: `shots/04_bb_0006_hq.png`, `shots/07_lab_lose_06_setup_bare.png`, `shots/09_bb_0017_placed.png`.
   *Fix:* Into the Breach gives each enemy one short arrow to one tile. Civ VI's lenses dim everything not relevant to the question ([loyalty lens guide](https://forums.civfanatics.com/resources/civ-vi-loyalty-guide.27114)). A raid lens: hide the netrun TARGET and its route, give each threat its own path offset and an arrowhead, put the threat icon on the path (not just a letter), and highlight the path when hovering its THREAT INTEL row.
5. **The playout is a non-event that spoils itself.** It runs 1-15 s, the result is shown from frame one, the feed runs ahead of the map, and the HUD lags. Evidence: `shots/11_lab_hold_09_playout_step01.png`, `shots/12_lab_lose_11_playout_step08.png`.
   *Fix:* Bad North and They Are Billions make the wave itself the readable event: each attacker is visible arriving and each hit lands where you look ([Nintendo World Report hands-on](https://www.nintendoworldreport.com/hands-on-preview/47533/bad-north-switch-hands-on)). Either (a) play one step per beat with the hit numbers on the map and the feed in step with them, or (b) admit it is a summary and cut it to a 3-second stamp sequence. Do not keep a long cutscene with speed buttons.
6. **The first raid is likely unwinnable with starting tools and feeds Heat.** This is a tax, and a spiral. In the hold lab state, 2 × 12-HP Collectors reach home in one step, the turret hits for 4-6, and the raid is lost with +5 Heat (26→31, which crosses the 30 complication). The testers called it "piling on" (D-07). **Designer decision.**
   *Fix:* Frostpunk's storm and XCOM 2's Avatar clock are forewarned threats that the player can push back by preparing ([PC Gamer XCOM 2 guide](https://www.pcgamer.com/xcom-2-guide)). Make the first raid winnable with the starting armory (Collectors that need 2 steps, or a free first-raid ICE LOCK). Or make a held-but-not-repelled raid cost no Heat.
7. **Stationing is not on the screen that asks for it.** The confirm says "at HQ first" while the player is at HQ. The crew are not on the raid setup and the station button lives on a Site card in another tab. Evidence: `shots/10_bb_0020_confirm.png`; PB-SOL-1 B-07 / C-10.
   *Fix:* XCOM 2's pre-mission squad select is on the mission screen. Show the crew portraits on the raid setup with drag-to-node, and say in the confirm what stationing would change ("+N: HOME 40 → 45").
8. **The no-words test fails at every decision.** Verdict, forecast, threat stats and feed are all text. Enemy green is close to the player's lime. Evidence: `shots/18_lab_lose_scr_06_setup_bare.png`, `shots/19_lab_lose_scr_14_playout_end.png`, `shots/20_lab_lose_scr_16_report.png`.
   *Fix:* Slay the Spire's intent icons and XCOM's shield colors (blue safe, red or yellow flanked) carry the decision without words ([XCOM 2 Steam discussion on shields](https://steamcommunity.com/app/268500/discussions/0/412447331650282099); [UFOpaedia cover](https://ufopaedia.org/Cover_(EU2012))). Put an outcome icon on each node on the map (shield = holds, bolt = DOWN, flag = TAKEN, skull = BREACHED) and give the enemy a hue the Cell never uses.
9. **No countdown from Heat to the raid.** The link between the player's choices and the raid is only in a tooltip and the terminal. Evidence: `shots/01_lab_hold_01_hq_before.png`, `shots/02_lab_hold_02_heat_terminal.png`.
   *Fix:* XCOM 2's Avatar bar is always on screen and becomes a red countdown. FTL draws the rebel fleet's next-jump border on the sector map ([FTL Wikipedia](https://en.wikipedia.org/wiki/FTL:_Faster_Than_Light); [Steam thread on the fleet "cloud"](https://steamcommunity.com/app/212680/discussions/0/828936718810691367)). Show "RAID IN 3" on the Heat bar and mark it on the Site card when a run's Heat would cross a threshold ("FLATLINE +11 → 87 · RAID").
10. **Consequences evaporate after the report.** There are no repair costs or new entry points (both required by GDD 7.2), no damage on the map, and node names are ambiguous ("T1 SITE" twice). Evidence: `shots/14_lab_lose_16_report.png`, `shots/16_lab_lose_17_hq_after.png`.
    *Fix:* Civ VII's launch UI was criticised for exactly this: players "discover missing units" after the fact ([Steam discussion](https://steamcommunity.com/app/1295660/discussions/0/591762563949168802); [CGM on the UI fixes](https://www.cgmagonline.com/news/civilization-vii-quality-of-life-updates)). Add a damage look on map nodes, a REPAIR (cost) action on the report, and name the node by position or type ("Vault, north").

---

## AAA comparison

| Technique | Game | How it works | What we do | Gap |
|---|---|---|---|---|
| Combat preview with both sides' strength and modifiers | Civilization VI | Hovering an attack shows both strengths, every +/- modifier and the expected damage before you commit | IF PLACED panel on card hover, home and node HP only; threat stats hidden | No threat HP or damage, no "why", text only |
| Lenses | Civilization VI | One overlay answers one question; everything else dims | Raid routes drawn over the full city with the netrun TARGET still visible | No raid lens; same red for enemy and own route |
| Perfect telegraph | Into the Breach | Every enemy shows exactly what it will hit; you see the outcome of your move before committing | Exact projection exists, but folded, incomplete, and not drawn on the map | The data is there; the telegraph is not |
| Intent icons with numbers | Slay the Spire | An icon over each enemy plus a damage number | Threat letter in a red ring; no number | No per-threat strength on the map |
| Cover / flank shields | XCOM 2 | Shield color says safe / flanked at the move tile, with no words | HOLDS / DOWN / TAKEN as words in a side list | No per-node outcome icon on the map |
| Doom clock | XCOM 2 (Avatar) | Always visible; becomes a red countdown; the player can push it back | Heat bar ticks; "NEXT 25 RAID" inside a terminal | No visible distance to the next raid |
| Storm countdown | Frostpunk | Temperature forecast for coming days beside the main gauge | None | Raid arrival is a surprise |
| Pursuit border | FTL | Fleet front and next-jump border drawn on the map | Entry letters A-J listed, not drawn on the HQ map | No spatial "where from" until Raid Setup |
| Wave as the game | Bad North / They Are Billions | Attackers arrive visibly and each hit reads in place | 1-15 s playout, feed ahead of map, result shown first | Neither a readable fight nor a quick summary |
| Honest debrief | XCOM 2 / Into the Breach | One-word grade or exact losses matching the consequences | CELL HOLDS on lost raids | Wrong verdict |

---

## Recommendations

### Quick wins (UI, text, icon, layout)
1. Derive the report stamp from `RaidResult.won` / `campaign_lost`: **REPELLED +N** / **OVERRUN (+5 HEAT)** / **BREACHED**. Keep CELL HOLDS only for a repelled raid. *(If CELL HOLDS must mean "survived" per GDD 7.2, that is a **designer decision**; the screen still needs the won / lost word.)*
2. A never-folding outcome block on Raid Setup: verdict word, Home Δ, nodes DOWN / TAKEN, **Heat Δ**, **Schematics**. The MORE fold may hide the flavor rows only.
3. Threat HP and damage on THREAT INTEL rows and as a pip bar on each map marker.
4. IF PLACED in words of effect: "kills 1 of 2", "TAKEN → HOLDS". Draw the asset's reach on the map while hovering.
5. Hide the netrun TARGET mark and its route on the raid pages and whenever a raid is pending. Give the threat paths a hue no Cell element uses.
6. Color the forecast chips by severity (HOLDS with loss over 25 % in amber, DOWN in orange, TAKEN in red). Do not show green "HOLDS" for 50 → 16.
7. Fix the YOUR NETWORK clipping (3 NODES listing 1), the NO CREW line overlapping SAVED, and the duplicate "T1 SITE" names on the report.
8. The no-crew confirm should say "Station from the CREW tab" (or offer a STATION button) and show the projected gain.
9. "RAID AT 25 (3 away)" on the Heat bar. A RAID tag on any Site card whose Heat would cross a threshold.
10. Add repair costs and new entry points to the report (GDD 7.2 already requires them).

### Structural (flow or mechanic)
1. **Decide what the playout is** (**designer decision**). Either it is a readable, step-locked fight (one beat per step, hits on the map, feed in sync, result hidden until the end, about 20-40 s), or it is a 3-second summary and the speed controls go. Today it is neither.
2. **First-raid winnability** (**designer decision**). Tune so the starting armory can repel the 25 raid, or make a survived-but-not-repelled raid cost no Heat. Today the first raid is a guaranteed loss that pushes Heat toward the next threshold.
3. **Bring the crew onto Raid Setup** (portraits, drag to node, the projection updates). This is where the in-flight STATION button is heading.
4. **Per-node outcome icons on the map** (shield / bolt / flag / skull) in setup and playout. This one change turns the no-words grade from opaque to guessable.
5. **A raid lens** on HQ when a raid is pending: threat paths, entry Sites and nodes at risk, everything else dimmed.

### On the in-flight `raid-setup-fix2` (sheet `D:/rc_tmp/raid_setup/sheet_r2.jpg`)
Moving "IF THE RAID RUNS NOW: HOME -10" off the paper onto a CRT chip, and adding `STATION Breaker 1 HERE`, are steps in the right direction. They fix legibility of one number and the C-10 dead end. They **miss the core problems**:
- The chip still shows only Home Δ: no Heat penalty, no reward, no won / lost.
- The report still stamps CELL HOLDS on losses.
- Threat stats are still hidden.
- The route knot and the red TARGET are unchanged.
- The playout is untouched.

The r2 "after" frame also adds a large flat lime fill over the claimed node, which is the same hue family as Solace's enemy green. Ship the STATION button. Do not count the round as fixing raid clarity.

---

## What works
- The corp work order and after-action report as diegetic papers, the INTERCEPTED / CLASSIFIED stamps, and the grease-pencil letters. The art direction has a voice no AAA comparison has.
- TRIGGER: HEAT 25 CROSSED on the work order states the cause plainly.
- The resolver is deterministic and the projection is exact. The IF PLACED hover panel is the right mechanism, and only its presentation is short.
- The defense card icons (crosshair, snowflake, magnet) survive the no-words test.
- The DOWN / TAKEN / HOLDS vocabulary is short and consistent between setup, feed and report.

---

## Artifacts
- Contact sheet: `D:/rc_tmp/raid_review/flow_sheet.jpg` (20 key shots, in flow order, the last three scrambled).
- Shots: `D:/rc_tmp/raid_review/shots/NN_*.png` (named by source run).
- Lab tool: `tools/playtest/raid_lab.gd`, `tools/playtest/raid_lab.tscn` (committed on `raid-review`, coordinator-approved).
