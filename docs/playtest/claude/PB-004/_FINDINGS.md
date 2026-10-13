# Playtest findings — PB-004 · build 19ad76a3a10c260a760667a0d6dde27156508740 · date not recorded

> Synthesised from 1 Claude playtest report, its screen audit and its motion judgements
> (docs/process/05_CLAUDE_PLAYTESTER.md §9). Every finding names the testers who hit it and the
> evidence (report section, shot or contact sheet). Ingest per doc 04 §3: bugs and clarity items
> become slice items; balance and design items go to the checkpoint for the designer's ruling.

## 1. Headline

- **Coverage:** one motion-focused tester (blue_hour) ran out of time after 15 min, so the campaign is INCOMPLETE. Two netruns were completed. Breaker 1 died on L4 to the Recall Unit, and Breaker 2 was on L1 at quit. Enjoyment was 5.
- **Top frustration:** the RAM readout shows negative values during targeting on nearly every turn. Card plays, picks and clicks also give little visible cause and effect.
- **Stuck points:**
  - A Fine Tune targeting arrow locked in place and was released only with Esc.
  - The training-sim victory banner could be left only through the pause menu.
- **Readability:** the tester reported text_clear: no. "Free Nudge" is unexplained, and map nodes have no prompt and are told apart by colour only. Card descriptions are truncated or too small to read.
- **Pacing:** SEND IT resolutions take 3–5 s each with dead gaps. The tester rated both netrun and campaign length "too long".
- **Trend:** there is no previous batch to compare against. Every finding below comes from a single tester.

| Metric | This batch | Previous (none) |
|---|---|---|
| Testers (novice / intermediate / expert / motion) | 0 / 1 / 0 / 1 (blue_hour is an intermediate-tier motion tester) | – |
| Furthest progress | L4 on Breaker 1 (died to the Recall Unit), 2 netruns completed | – |
| Avg enjoyment (1–10) | 5.0 (n=1) | – |
| Avg RNG fairness (1 fair – 5 cheated) | n/a | – |
| Bugs reported (deduplicated) | 7. The tester counted 10, but polish items were moved to §5. | – |

## 2. Bugs (→ slice items; P1 = fix before the next gate, P2 = next slice)

| ID | Sev | Area | Bug | Testers | Repro (from the reports) | Evidence | Confidence |
|---|---|---|---|---|---|---|---|
| B1 | P1 | combat | The RAM readout dips to -1, -2 or -3 while targeting. It looks like an overdraw and misleads planning. | blue_hour | Start targeting with Fine Tune, Brute Spin or Jolt (seen on nearly every turn). Esc clears it for one turn, then it returns. | blue_hour §4 #1, §6 top_frustration (journal only, no sheet) | single |
| B2 | P1 | combat | Hand card descriptions are cut off by the neighbouring card, so the card effect cannot be read. | blue_hour | Turn 1 hand with Mirror Flip ("Blocked while th..."), or Overdrive next to Fine Tune ("OVERCLOCK your slid... under th..."). | audit 0032, 0033, 0100 | single |
| B3 | P1 | screens | The training-sim victory banner will not dismiss. | blue_hour | Win the training-sim fight. Click the banner, press Enter, click the lower right: nothing happens. Only the pause menu exits. | blue_hour §2 (Fight won/lost), §4 #9; motion/0009, motion/0010 (clicks on the settled FIGHT WON screen, captured right after the sim kill on 0008, showed no reaction) | unconfirmed-input |
| B4 | P2 | combat | The Fine Tune targeting arrow stays locked on one enemy slot. | blue_hour | L1, turn 10, Fine Tune targeting: the arrow stayed on the Daemon's top-right slot. Six clicks did nothing. Esc released it. | blue_hour §4 #2 (journal only) | unconfirmed-input |
| B5 | P2 | combat | The hovered card covers the player HP label. A second value after "60/60 (" is cut off, likely shield or another stat. | blue_hour | Turn 1: hover Brute Spin so it enlarges over the left wheel's HP readout. | audit 0033 | single |
| B6 | P2 | screens | The shop description shows a raw or duplicated string ("> SHIM 8 Shim 8 SHIM: deals damage..."). It looks like an id, display name and label joined together. | blue_hour | Open the Mainframe Shop and read the description panel left of the spinner. | audit 0085 | single |
| B7 | P2 | screens | The pink LOOT sticker covers the greyed PROCEED label, which reads "PRO...ED". | blue_hour | Win a fight and look at the bottom-right Proceed button. | audit 0067 | single |

## 3. Clarity and UX (→ slice items, ranked by how many testers it cost)

| ID | Area | Problem | Testers (of n) | Time lost / what resolved it | Evidence | Suggested direction |
|---|---|---|---|---|---|---|
| C1 | combat | "FREE NUDGE 1" is never explained, and it is unclear whether cards, the Q/E icons or the wheel use it. Wheel icons (sword, burst, wall, 1/0) and values such as 14 burst, 5 wall and +10 have no legend. The Q/E rotate buttons are tiny and labelled only with the letter. | 1/1 (blue_hour) | not recorded | audit 0032, 0033, 0100; §6 text_clear: no | Add a tooltip or tutorial line for Free Nudge, a wheel icon legend and labelled rotate controls. |
| C2 | city | The route map never prompts the player to pick a node. The FIGHT // L1 and L2 hover panel does not say which node it describes, and the TARGET marker points at nothing clear. | 1/1 (blue_hour) | not recorded | audit 0031, 0069, 0099 | Add a "pick a node" prompt, tie the hover panel visually to its node, and anchor TARGET to the route. |
| C3 | screens | The Fight Won screen has no visible Continue or Next control. The "Bank it before the next process wakes up" line hints at an action but offers no control for it. | 1/1 (blue_hour) | Same family as B3 and B7. | audit 0019 | Add an explicit, unobscured continue control. |
| C4 | screens | The tutorial Next button is dimmed grey and looks disabled, while Skip tutorial looks active. Clicks on Next showed no visible reaction. | 1/1 (blue_hour) | Not recorded. 0001 notes the click may have missed the button, so the no-reaction part is unconfirmed-input. | audit 0004; motion/0001, motion/0002; §4 #8 | Style Next as the primary action and give it press feedback. A human should confirm the click target. |
| C5 | screens | The loot screen shows no selected state; only yellow corner brackets on card 1 hint at one. It is unclear whether Continue works before a pick and how it differs from Skip. | 1/1 (blue_hour) | not recorded | audit 0068; motion/0021 (click gave no highlight) | Show a clear selected state, and make Continue and Skip states explicit. |
| C6 | city | Map node types and states are told apart mainly by colour: small, similar ring icons, yellow walked rings against orange next rings, and the same glyph on every node. The MAP KEY is collapsed. | 1/1 (blue_hour) | not recorded | audit 0029, 0031, 0069, 0099 | Give each node type a distinct shape or icon on the map itself, and mark walked and next by more than colour. |
| C7 | screens | Card description text is tiny and thin on busy textured art, and nearly unreadable at 1280x720. | 1/1 (blue_hour) | not recorded | audit 0085 (shop), 0068 (loot) | Add a backing plate behind the text or increase text size and weight. |
| C8 | screens | The shop purchase flow is unclear in four ways. It does not show which wheel slice the preview describes or how to buy. The "TOP 3 ONLY" sticker and the 100 tags have no clear owner. "Slot 1: OVFL 12 + Shunt" is unexplained jargon. | 1/1 (blue_hour) | not recorded | audit 0085 | Link the preview to its slice, add an explicit buy action, and explain the terms. |
| C9 | screens | The numbered menu stickers (1. BREACH, 2. SIMULATE, 3. OVERTHROW) do not clearly map to Continue, Tutorial and New Campaign. BREACH is locked and greyed with no reason given. | 1/1 (blue_hour) | not recorded | audit 0002, 0003 | Either tie the stickers to the buttons or make them clearly decorative, and give a lock reason. |

## 4. Balance and design signals (→ checkpoint items for the designer; never straight into tuning)

| ID | Signal | Testers | Evidence | Question for the designer |
|---|---|---|---|---|
| D1 | Netrun length and campaign length were both rated "too long". A 14-turn fight with 3–5 s resolutions "felt like a lot of watching". | blue_hour | §6 netrun_length, campaign_length; §3 Waiting | Is the length intended? Options: (a) keep it and re-test after M1 shortens resolutions; (b) shorten fights; (c) shorten netruns; (d) keep everything and add mid-run save points. |
| D2 | The tester would skip full SEND IT resolutions after seeing them twice. | blue_hour | §3, focus Q1; motion/0006 | Should resolution pacing be (a) shorter by default for everyone, (b) a player speed setting, or (c) skippable on click? |

## 5. Motion and feel (→ the animation pass queue)

| ID | Moment | Verdict | Sheets | Problem |
|---|---|---|---|---|
| M1 | SEND IT resolution | too slow | motion/0006, motion/0003 | The sequence runs about 4–5 s with idle gaps (0.86–1.36 s and 2.68–3.55 s). Lines and particles are thin and the damage number is tiny. Enemy HP showed no visible reaction, and the red counter-line is subtle. The wheel rotation at 3.12 s is hard to read. |
| M2 | Card played onto a wheel | hard to follow / no animation seen | motion/0007, motion/0004, motion/0016, motion/0017 | The card turns into a small panel with no landing. The yellow burst hides the changing segment, and changed values get no highlight. Some clicks showed no readable motion at all; whether those registered is unconfirmed-input. |
| M3 | Reward reveal and pick | hard to follow | motion/0025, motion/0022 | The picked card flies off to an unclear destination. The other slots go blank white, which may be missing art or an intended dissolve and needs checking. The empty sheet lingers about 1 s, then hard-cuts to the map with no deck-add confirmation. |
| M4 | Map node to fight; button presses | janky or glitchy | motion/0014 | The node and buttons give no press feedback. The cut from map to combat is abrupt, and the combat UI appears fully formed with no entrance. The delay reads as lag. |
| M5 | Shop to map | hard to follow | motion/0026 | A hard cut leads into a mostly empty purple frame and then a blurry zoom-out. Nothing shows the destination, and the screen stays idle for about 4 s afterwards. |
| M6 | Perfect hit | clear but flat | none (§2) | There is no shake, enlarged number or flash, so a Perfect feels like a normal hit. |
| M7 | Nudge/spin and turn change | no animation seen | none (§2, §3) | The wheel rearranges with no highlight on what changed. Turn 4 arrived with no cue. |
| M8 | Tutorial advance during resolution | hard to follow | motion/0003 | The Next click swaps the text abruptly while a full SEND IT plays behind the box, which splits the player's attention. |
| M9 | Flatline to HQ | clear but flat | motion/0027 | A fitting glitch-out is followed by a static CONNECTING TO HQ card (about 0.4 s) and a hard pop into HQ. |

## 6. What worked (keep)

All of these come from a single tester (blue_hour). None has been confirmed by a second tester yet.

- **Training-sim kill:** card out, line, hit, enemy to 0/40, FIGHT WON, DELETED stamp and the wheel shattering (motion/0008).
- **SEND IT order:** the attack line, hit, HP drop and counter-line can be followed (motion/0006).
- **PERFECT sequence:** the tag, line, burst and HP drop (38 to 14) come in a readable order.
- **Targeting arc:** it ties the card to the enemy wheel slot.
- **Theme in transitions:** the jack-in terminal typing, the scan band on START, the glitch-out into CONNECTING TO HQ, and the flatline screen's line.

## 7. Proposed actions

1. **Slice items:**
   - P1 bugs: B1, B2, B3. B3 needs a human repeat first.
   - P2 bugs: B4 (needs a human repeat first), then B5, B6, B7.
   - Clarity: C1, C2, C3, C4 (input part needs a human repeat), C5, C6, C7, C8, C9.
   - Animation queue: M1–M9.
2. **Checkpoint items for the designer:**
   - D1: keep the length, shorten fights, shorten netruns, or add save points?
   - D2: shorter default resolutions, a speed setting, or skip-on-click?
3. **Next batch:**
   - Add novice and expert non-motion testers so findings can reach multi-tester confidence.
   - Have a human repeat the input-dependent items (B3, B4, C4 and the no-reaction clicks in M2).
   - Ask the motion tester to capture the RAM readout (B1), nudge/spin, and the raid playout and City Grid, which were not encountered this time.
   - Allow enough playtime to finish a campaign.