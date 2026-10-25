VERDICT: The acclaimed systems score 31 to 45 out of 50, with a median of about 37. X scores 32 and Y scores 30. Both are in the bottom third, roughly level with Teamfight Tactics and Kingdom Rush. Those two games make up their lower totals with S (suspense) and V (visuals). X and Y do not.

# Raid rubric calibration: 6 shipped systems vs Prototypes X and Y

Critic: fresh, no prior reviews read. Date: 2026-10-22.
Evidence: `refs/` (screenshots, with sources in `refs/SOURCES.txt`), `CONTACT_SHEET.png` (all 8 side by side), and `XY_SEQUENCE.png` (the full X and Y frame sequences).
Scale: 7 means "a good shipped game does this about this well". Each score is tied to a feature I could see or a rule I know from the system. I did not score on reputation.

## Table

| # | System | W | P | N | D | C | /50 | S | V |
|---|---|---|---|---|---|---|---|---|---|
| 1 | FTL: ship combat + rebel pursuit | 7 | 5 | 7 | 8 | 8 | **35** | 8 | 7 |
| 2 | Into the Breach: one enemy turn | 10 | 10 | 8 | 9 | 8 | **45** | 5 | 8 |
| 3 | Kingdom Rush: one wave | 8 | 5 | 8 | 6 | 6 | **33** | 8 | 8 |
| 4 | Teamfight Tactics: one combat round | 6 | 4 | 6 | 8 | 7 | **31** | 8 | 7 |
| 5 | Invisible, Inc.: guard sweep / alarm | 9 | 7 | 7 | 9 | 7 | **39** | 9 | 7 |
| 6 | Slay the Spire: elite/boss with intents | 9 | 8 | 8 | 9 | 8 | **42** | 6 | 7 |
| 7 | Prototype X: sweep raid (low-fi) | 7 | 8 | 5 | 5 | 7 | **32** | 6 | 3 as shown / 6 layout |
| 8 | Prototype Y: fortress raid (Godot) | 7 | 9 | 4 | 5 | 5 | **30** | 3 | 5 |

### One-line reasons

1. **FTL (35).**
   - **W:** the rebel fleet's red front advances on the sector map every jump, and enemy weapon charge bars show "when" during combat. But an encounter starts the moment you jump, with no lead time.
   - **P:** evasion and accuracy are dice rolls. A "MISS" floats over the hull in `ftl_0.jpg`, and you cannot preview a volley's result.
   - **N:** red rooms, fire and breach icons, and system pips read without words. Weapon names and crew bars need small text.
   - **D:** power routing, room targeting, crew moves, door venting and pause give real depth.
   - **C:** hull and scrap carry across the whole run, and a loss is permadeath.
   - **S:** strong. You watch two charge bars race. **V:** clean, but the UI chrome is cramped.
2. **Into the Breach (45).**
   - **W:** every attack is shown before your move as red target tiles, and `itb_3.jpg` numbers the attack order 1 to 5.
   - **P:** fully deterministic, with hover previews of pushes and damage. It is the ceiling for P.
   - **N:** arrows, red tiles and grid-power pips do most of the work. Weapon effects still need tooltip text, as the "Water Tile" box shows.
   - **D:** pushes, body-blocks and deliberate trades are best in class.
   - **C:** grid power persists across the island and the run, and it is the fail state. It is legible and fair.
   - **S:** low. The enemy phase only confirms what you already know. This is the price of P = 10.
3. **Kingdom Rush (33).**
   - **W:** skull "call wave" icons pulse at the path entrances, the next wave's enemy portraits show on hover, and calling early pays a bonus.
   - **P:** there is no forecast. You learn whether a build holds by losing lives.
   - **N:** it is among the most readable games here: tower silhouettes, paths, and the lives heart (`kr_1.jpg`).
   - **D:** placement plus upgrades plus hero and reinforcements is real but shallow per wave.
   - **C:** lives and star rating only. Nothing carries past the level except stars.
   - **S:** high. Leaks happen live, and so do the panic spells.
4. **Teamfight Tactics (31).**
   - **W:** a round timer and the opponent's name are shown, but you don't know your opponent until the fight loads.
   - **P:** poor. Crits, targeting and item procs make the fight hard to call in advance.
   - **N:** trait icons and star levels help, but a mid-fight board is visual noise. The one source image (Wikipedia, `tft_0.jpg`) shows only an early board.
   - **D:** economy, positioning and comp choices give a lot of depth.
   - **C:** player HP loss persists, and win or loss streaks feed the economy. It is legible.
   - **S:** high. Watching the auto-battle is the hook.
5. **Invisible, Inc. (39).**
   - **W:** the alarm dial ticks each turn and states the next escalation level. Guard vision cones and interest markers show "why".
   - **P:** current cones are deterministic. Spawns, reinforcements and hidden daemons are unknown.
   - **N:** red cones, the alarm ring, and red versus yellow units in the Incognita view (`invis_2.jpg`) read well. Program and daemon effects are text-heavy.
   - **D:** stealing, the stall-or-escape tension, and AP routing are excellent.
   - **C:** captured agents and spent credits persist, though the escalation rules are only clear once learned.
   - **S:** the best here. Peeking around corners and guard turns are tense.
6. **Slay the Spire (42).**
   - **W:** every enemy shows its intent icon, with the exact damage, above its head.
   - **P:** exact for this turn. Your own draws, "unknown" intents and multi-turn boss patterns cost 2 points.
   - **N:** the sword, shield and buff intent icons are a widely copied standard. The card text itself needs reading.
   - **D:** sequencing, block-versus-damage choices, and deck synergy are deep.
   - **C:** HP carries across the act, and relic rewards motivate.
   - **S:** medium, mostly from the draw. **V:** functional. `sts_0.jpg` shows no intent at that moment, so the screenshot under-sells it.
7. **X (32).**
   - **W:** the Heat bar with a cobalt notch at 50 gives the trigger, and the 4×3 asset grid appears at contact. The "why" lives in the footer caption, not on screen.
   - **P:** the forecast is exact per sealed candidate (-13 / +1 / +1, from `3_forecast.png`). It loses 2 points because it shows only a net number and not which node falls. The spoof timing window also adds execution variance.
   - **N:** these are confusable:
     - the numbered circles (beam ID versus candidate ID);
     - dashed versus solid lines;
     - the unlabeled lever icons in the panel (dotted ring, diamond, black disc "x0");
     - the hunter rule, which has no visual.
   - **D:** three single-use levers on 12 nodes, and the forecast already tells you the best reaction. The choice is mostly solved by reading the table.
   - **C:** DOWN until repaired, with repairs drawn from the breach key (19/25 to 11/25). This is persistent, tied to the win condition, and strong.
   - **S:** there is one real moment, the beam-2 unseal plus the SPOOF press.
   - **V:** placeholder vectors as shown. The information layout is sound but sparse.
8. **Y (30).**
   - **W:** three raid cards on top show Heat (26, 51, 76), threat counts and threat chips. Raid 3 is hidden, and a "CORP ADAPTS" strip is shown. But "when" is only a raid ordinal, and the "why" is not on screen.
   - **P:** exact forecast of clean, lost, net and bank-after for every raid. It is near the ceiling.
   - **N:** the threats are three-letter text chips (COU, ENF, BAI, COL, LCK). Node state is the text "SCUFFED -9". The raid beat is narrated in a text log ("FWGUN at ENFORCER: -5"). Job icons are tiny. With the words removed, the raid is unreadable.
   - **D:** 2 buys per visit, 5 piece types, 6 nodes, exact forecast and Undo, so it is solved by trial and undo. The record (`11_record.png`) shows 3/3 CLEAN with a bank that only goes up (14, 31, 51, 61).
   - **C:** the net breakdown is the clearest here. But "clean never nets negative" plus free scuff healing means the shown run lost nothing. Footholds are promised but never seen in the captures.
   - **S:** a hands-off playout of a result you already know exactly.
   - **V:** tidy flat UI. The threats are tiny hexes with no motion language.

## Observed range for acclaimed systems

- **Total /50:** 31 (TFT) to 45 (Into the Breach). The median is about 37, and the 6 games average 37.5.
- **Per axis**, the ranges for the shipped games are:

  | Axis | Range |
  |---|---|
  | W | 6 to 10 |
  | P | 4 to 10 |
  | N | 6 to 8 |
  | D | 6 to 9 |
  | C | 6 to 8 |

- **N:** no shipped game here passes 8. Every one leans on tooltips or text somewhere.
- **X (32)** is above TFT and level with Kingdom Rush. It is 13 below Into the Breach and 10 below Slay the Spire.
- **Y (30)** is below every shipped system.
- **The weakness is hidden by high P.** Both prototypes score at or above Slay the Spire on P, so their totals hide that N and D are below every shipped game. The games X and Y tie with (KR and TFT) earn their place with S = 8 and V of 7 to 8. X and Y have 6 and 3 on S, and 3 to 6 on V.

## What the rubric under- and over-rewards

- **40+ is realistic, but only for one design family.** Into the Breach and Slay the Spire reach it because they are turn-based telegraph games: perfect W and P, with D layered on top. Nothing that "plays out" (FTL, KR, TFT) gets past 35. A target of 40+ for a watched raid effectively says "make it Into the Breach".
- **P and S trade off. This is the clearest finding.**

  | System | P | S |
  |---|---|---|
  | Into the Breach | 10 | 5 |
  | Slay the Spire | 8 | 6 |
  | Invisible, Inc. | 7 | 9 |
  | FTL | 5 | 8 |
  | Kingdom Rush | 5 | 8 |
  | TFT | 4 | 8 |

  Y shows the extreme case: P 9, S 3. Invisible, Inc. is the only system above 7 on both, because its forecast is local (the cones you see now) and the escalation is unknown. Since S sits outside the /50, the rubric pushes designs toward exact forecasts that kill the watch phase.
- **P is over-rewarded, and an exact forecast earns it too easily.** X and Y both bought P 8 to 9 with a results table. A forecast table that also reports the optimal reaction is cheap to build, and it lowers D, because the decision becomes reading the table. The rubric does not penalize that coupling. Into the Breach earns P = 10 through spatial previews you have to reason about, not a lookup.
- **N is effectively capped at 8.** A target above 8 is unrealistic against shipped games. It is the right axis to press X and Y on, because they sit 3 to 4 points under the floor of the shipped games.
- **C mixes four things:** legible, fair, motivating, persistent. Y is the most legible but the least motivating, and one number hides that. Split C into legibility and stakes.
- **D is under-specified.** It should require that the forecast does not name the best move.
- **S and V are outside the /50,** yet they are why KR and TFT are acclaimed despite scoring 31 to 33. For any "watch it play out" raid, S belongs in the total.

## X and Y: the biggest gap to the best shipped system on each axis

| Axis | X (best shipped) | Y (best shipped) |
|---|---|---|
| W (ITB 10) | The "why" and the hunter rule are told by the footer caption. ITB puts the threat and its order on the board (numbered red tiles). | Raids are ordinals on cards, not a clock in the world. The "why" (heat? corp front?) is absent. ITB and Invisible's alarm dial show cause and countdown in-world. |
| P (ITB 10) | The forecast gives only a net number per candidate, so you cannot see which node falls. ITB previews each tile's outcome on the map. | Nearly there. The gap is the opposite one: it is so exact that it erases S and D (see below). |
| N (ITB / KR / StS 8) | Overloaded number circles and dashed versus solid lines. The levers panel is unlabeled glyphs ("x0"). StS's intents are one glyph plus one number per enemy. | Threats are three-letter text chips, damage state is text, and the raid is narrated by a text log. KR's enemy silhouettes and leaking-unit motion are the bar. |
| D (ITB / Invisible / StS 9) | 3 single-use levers on 12 nodes, and the forecast tells you the best reaction. ITB forces trades between objectives with no right answer handed out. | 2 buys, exact forecast and Undo make the choice trial-and-error solvable. Invisible's "stay for loot vs. alarm" choice has no undo and no oracle. |
| C (FTL / ITB / StS 8) | Closest to the bar. The DOWN cost hits the breach key. The gap: the key bar alone doesn't say which future breach you now can't afford. | The clean-never-negative rule and free healing mean the shown run lost nothing (+14 / +18 / +22). FTL's hull damage and ITB's grid power can't be undone, and that is what makes them land. |
| S (Invisible 9) | One unseal plus one press. Invisible has a tense beat every guard turn. | The outcome is known exactly before the playout. It needs a hidden or semi-hidden element during the watch, like TFT's crits or Invisible's unknown spawns. |
| V (ITB / KR 8) | Placeholder vectors, so no real comparison is possible yet. The layout is fine. | A flat node graph with tiny hexes and no motion language for threats or hits. KR's destination is bold silhouettes, impact effects and readable unit motion. |

Bottom line:
- **X** has the better consequence and suspense spine (sealed line, spoof press, damage to the key).
- **Y** has the better forecast and fortress persistence. But its stakes and its watch phase are both near zero.

Neither is near the shipped median until N and D move. For Y, S also has to move, which means giving back some P.

## Sources (gameplay screenshots, downloaded with curl into refs/)

- FTL `ftl_0.jpg`: https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/212680/ss_052d698926073e8d407a864f0e63a486af24ec0d.1920x1080.jpg
- Into the Breach `itb_3.jpg`, Kingdom Rush `kr_1.jpg`, Invisible, Inc. `invis_2.jpg`, Slay the Spire `sts_0.jpg`: Steam store screenshot URLs listed in `refs/SOURCES.txt`. They came from the Steam appdetails API (appids 590380, 246420, 243970, 646570), and the metadata is in `refs/meta/`.
- Teamfight Tactics `tft_0.jpg`: https://upload.wikimedia.org/wikipedia/en/b/b4/Teamfight_Tactics_Gameplay.jpg (Wikipedia file page https://en.wikipedia.org/wiki/File:Teamfight_Tactics_Gameplay.jpg)
- All 30 downloaded images and their URLs are in `refs/SOURCES.txt`.

Caveats:
- No FTL sector-map (rebel fleet) screenshot was among the store images, so the FTL W score relies on the known rule.
- The TFT image shows no combat in progress.
- The `sts_0` image shows no intent icon at that moment.
