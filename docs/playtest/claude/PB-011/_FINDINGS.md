# Playtest findings — PB-011 · build 19ad76a3a10c260a760667a0d6dde27156508740 · 2026-10-12

> Synthesised from 1 Claude playtest report, its screen audit and motion judgements
> (docs/process/05_CLAUDE_PLAYTESTER.md §9). Every finding names the testers who hit it and the
> evidence (report section, shot or contact sheet). Ingest per doc 04 §3: bugs and clarity items
> become slice items; balance and design items go to the checkpoint for the designer's ruling.

## 1. Headline

- **This is a thin batch.** Only 1 report came in. saltlamp (expert, strategist, pacing_length) is on the tester list but filed no report.
- **mothball, the keyboard-only raids tester, never completed a netrun:**
  - 3 netruns started, all 3 ended in flatline;
  - 1 raid survived (CELL HOLDS);
  - the session ended INCOMPLETE after 45 min;
  - the Save & Quit confirm then stopped responding to keys and mouse. This is the same failure as PB-010 B5.
- **Keyboard coverage outside combat is the main complaint.**
  - In combat the keys work: 1–5, Q/E, Space, Z, R, H and Esc.
  - Many confirm, continue and back buttons have no key or ignore Enter/Esc. Examples: route nodes, loot, firmware pick, HQ tabs, the raid screens, the tutorial and the title screen.
  - The enemy-wheel nudges are mouse-only. A keyboard player therefore cannot push the enemy needle.
- **Raids read as fair but as a tax.** The setup projection matched the playout exactly. However, with every Breaker flatlined and an empty armory there was nothing to place, so the raid puzzle is still untested.
- **The trend is flat.** PB-011 ran on the same build as PB-010. Almost every finding recurs: the Quit freeze, the unexplained RAM readout, clipped cards, the route map, crew recovery, raid wording and Heat. The FIGHT lines are now logged and show 0.00 Perfects per turn, so all difficulty signals remain tester skill-limited.

| Metric | This batch | Previous (PB-010) |
|---|---|---|
| Testers (novice / intermediate / expert / motion) | 0 / 1 / 0 / 0 (saltlamp listed, no report) | 3 / 3 / 1 / 1 |
| Furthest progress | mothball: 3 netruns started, 0 completed, T1, 1 raid survived, Home 40/50, Heat 39 | No Site cleared. Most netruns: copperjack (6 started). Campaign lost: halfmoon |
| Avg enjoyment (1–10) | 4.0 (n=1) | 3.4 (n=8) |
| Avg RNG fairness (1 fair – 5 cheated) | 3.0 (n=1) | 2.9 (n=7) |
| Bugs reported (deduplicated) | 7 raw → 3 (4 folded into clarity) | 69 raw → 15 |

## 2. Bugs (→ slice items; P1 = fix before the next gate, P2 = next slice)

| ID | Sev | Area | Bug | Testers | Repro (from the reports) | Evidence | Confidence |
|---|---|---|---|---|---|---|---|
| B1 | P1 | screens | **Recurs PB-010 B5.** The Save & Quit confirm stops responding to A, Enter, B and the mouse, so the game cannot be exited. Earlier in the same session the dialog accepted A/B. The report does not say whether the save was written. | mothball (PB-010: gridlock, neon_moth) | 1. At 42.7 min, open Save & Quit. 2. Press A, Enter or B, or click. 3. Nothing responds for the rest of the session (to 45 min). The freeze followed a raid: the raid report was open at 37.5–39.5 min. | mothball §1, §4, §6, §7#1, 0310.png | single (recurring; same dialog worked earlier, so not an input artefact) |
| B2 | P2 | city | The HQ CREW tab does not open when all Breakers are flatlined. The free recruit sits under MARKET instead. See C5. | mothball | 1. Flatline all Breakers. 2. At 24.3–24.7 min, on HQ, click CREW, press Enter, press Tab. 3. Nothing happens. | mothball §3, §7#2, 0180.png (PB-010 B14, C6) | unconfirmed-input (needs a human repeat) |
| B3 | P2 | screens | On the Locked Ward event, key 3 shows no selection on "Ghost past". The mouse works. | mothball | 1. At 29.2 min, open the Locked Ward event. 2. Press 3. 3. No visible selection appears. | mothball §4, §7#6, 0216.png (cf. PB-010 C8) | unconfirmed-input (needs a human repeat) |

Area = combat | city | screens | rules (docs/process/agent_rules). Confidence: confirmed (2+ testers
or clean steps) · single (one tester, plausible) · unconfirmed-input (a click or drag that "did
nothing": posted input is not a real mouse; needs a human repeat before any fix).

## 3. Clarity and UX (→ slice items, ranked by how many testers it cost)

| ID | Area | Problem | Testers (of n) | Time lost / what resolved it | Evidence | Suggested direction |
|---|---|---|---|---|---|---|
| C1 | screens | **Recurs PB-010 C11.** The keyboard path has gaps. These have no key or no shown key: <br>• JACK IN, NEW CAMPAIGN, TUTORIAL, START, CONTINUE <br>• route node selection <br>• tutorial NEXT/FINISH/Skip <br>• loot Continue/Skip <br>• firmware pick <br>• HQ CREW/MARKET/DEFENCE tabs <br>• START DEFENSE <br>• raid playout Continue <br>• pause Abandon/Quit options <br>• enemy-wheel nudges (mouse-only) <br>The raid report's BACK TO THE GRID ignores Enter and Esc. The SEND IT [Space] hint shows inconsistently. | 1 of 1: mothball | About 1.3 min at the raid report, resolved by clicking. The mouse was the fallback elsewhere. This is the tester's top frustration and top change. | mothball §4, §6, §7#3, confusion log 38.2m, 0272.png | Show a key hint on and bind every confirm, continue and back button, using Enter = confirm and Esc = back. Add keyboard route selection and enemy-wheel nudge keys. |
| C2 | combat | **Recurs PB-010 C1.** Combat numbers are unexplained: <br>• the RAM readout shows (-1)/(-2) beside 12/12; <br>• the red -3/-6 chips, the "?" by HP, the "6" marker and the "5 3" tag have no legend. | 1 of 1: mothball | Unresolved from 12.9 min onward. | mothball §2, §4, §7#4, confusion log, 0108.png; audit 0132 | Label each chip in place. Explain reserved or negative RAM where it is shown. |
| C3 | combat | **Recurs PB-010 C2.** Card faces are hard to read: <br>• text is tiny and clipped ("Mirror Flip: Blocked while th…"); <br>• Fine Tune covers Overdrive's text; <br>• RAM cost appears only as a "Not enough RAM" message (Brute Spin needs 2). | 1 of 1: mothball | Never resolved. | mothball §2; audits 0010, 0132 | Fit the full text on the card. Show the RAM cost on the face. Keep neighbouring cards from overlapping it. |
| C4 | city | **Recurs PB-010 C7.** The netrun route map is hard to read: <br>• node types differ mainly by colour, and the walked/next states do too; <br>• there is no "pick a node" prompt; <br>• the numbered next nodes and the TARGET scrawl are unexplained; <br>• nodes blend into the cityscape; <br>• the AT LARGE stamp covers max HP; <br>• the purple "D 0" badge and the Breaker dossier are unexplained. | 1 of 1: mothball | Not resolved. The tester could not tell node types apart. | mothball §3, §4, §7#7; audits 0008, 0045, 0053, 0085, 0131, 0214, 0217 | Use a distinct shape per node type. Add a pick-and-confirm prompt. Move the stamp off HP. Label the badge. |
| C5 | city | **Recurs PB-010 C6.** There is no visible way to recover crew when all are flatlined: <br>• the CREW tab is dead (B2); <br>• the free recruit is under MARKET; <br>• the panel says recruit or rest at HQ but doesn't show where; <br>• JACK IN looks active anyway. | 1 of 1: mothball | About 0.6 min, resolved by finding MARKET. | mothball §3, confusion log 24.2m; audit 0261 | Put the recruit action on the crew cards and CREW tab. Disable JACK IN, with the reason, when no crew is available. |
| C6 | city | **Recurs PB-010 C9.** Raid wording and setup are unclear: <br>• the report says "Outcome: Failed" beside the CELL HOLDS stamp; <br>• HOME -10 and CORE 50→40 name the same thing; <br>• Collector, Threats, DOWN and TAKEN are never explained; <br>• Setup highlights Crew 0/3 with a cryptic "Armory empty" and no hint of whether to prepare. | 1 of 1: mothball | The outcome wording confused the tester. Setup was usable only as a projection. | mothball §5 Q1, Q3, §7#5, 0264.png; audits 0262, 0263, 0264 | Make the outcome text match the stamp. Use one name for the home server. Say what Crew and Armory do and what can be placed. |
| C7 | city | **Recurs PB-010 C3, C4.** Heat and the City Grid are opaque: <br>• Heat can't be predicted (+11 per flatline, shown only afterwards); <br>• Heat Scrub [H] looks disabled with no reason (10 of 25 schematics); <br>• the map icons, lock, TARGET and objective are unexplained; <br>• a DECRYPTED stamp sits on the jack-in target. | 1 of 1: mothball | Never resolved. | mothball §3; audits 0004, 0273 | Show the Heat delta before acting. Give the reason Heat Scrub is unavailable. State the objective and the icon legend on the map. |
| C8 | combat | **Recurs PB-010 B6.** When undo is blocked after a random event, the message doesn't explain why. The respin message is clear. | 1 of 1: mothball | Not resolved. | mothball §2, 0225.png (respin message) | Match the random-event block message to the respin one. |
| C9 | screens | **Recurs PB-010 C2 (loot), C12, B2/D4.** Loot and result screens have several problems: <br>• Siphon's "does not fit a OVERFLOW slice" appears only after clicking; <br>• a taken card is ghosted with no TAKEN label, and it's unclear whether Continue confirms; <br>• a "SYSTEM 2x NUDGE" card overlaps the HUD; <br>• the LOOT sticker covers PROCEED; <br>• victory dialogue is cut mid-word. | 1 of 1: mothball | Not reported. | mothball §2, 0212.png; audits 0042, 0043 | State the slot condition on the offer. Label taken picks. Move stickers off button labels. |
| C10 | screens | **Recurs PB-010 C13.** Tutorial problems: <br>• pressing TUTORIAL landed on the HQ map, so the tester was unsure the tutorial ran; <br>• the step 2/7 NUDGE popup is a wall of text with the "do it to go on" line buried. | 1 of 1: mothball | Resolved by playing on. | mothball confusion log 0.6m; audit 0009 | Confirm tutorial start on screen. Split step 2 and lead with the action. |
| C11 | screens | **Recurs PB-010 C8.** Locked Ward choice 2 (-60 Cycles, the tester had 21) is greyed with no reason. A key press showed no selection (B3). | 1 of 1: mothball | Resolved by switching to the mouse. | mothball §4; audit 0215 | Mark unaffordable choices with the reason. Show the selection on key press. |
| C12 | screens | **Recurs PB-010 C14, C15.** Title and setup labels are unclear: <br>• the BREACH / SIMULATE / OVERTHROW stickers don't map to the buttons beside them; <br>• the BREACH lock is unexplained; <br>• unlock costs (120/40/60/80) have no currency. | 0 of 1 (audit only) | — | audits 0002, 0003, 0090 | Tie each sticker to its button. Name the unlock currency. |

## 4. Balance and design signals (→ checkpoint items for the designer; never straight into tuning)

| ID | Signal | Testers | Evidence | Question for the designer |
|---|---|---|---|---|
| D1 | **Tester skill-limited.** <br>• 3 deaths, 4 of 7 fights won, average 40.1 HP lost per fight, 0.00 Perfects per turn. <br>• Early on the tester mashed Space without reading and lost about 12 HP a turn. <br>• The elite death came from sending on a -5 skull chip at turn 7. <br>Failed to read or do: <br>• RAM costs and negative RAM (C2, C3); <br>• node types before the elite (C4); <br>• pushing the enemy needle, because the enemy nudges are mouse-only (C1); <br>• the firmware pick, which has no key (C1). | mothball | Combat skill table; mothball §1, §2, 0258/0259 | Observation only, no tuning question. Re-test after C1–C3 land. |
| D2 | **Tester skill-limited (HP attrition). Recurs PB-010 D3.** At 16 HP the only next node was an Elite. The tester felt the death was "forced by the map" (RNG 3). | mothball | mothball §3 | Carried open from PB-010 D3: (A) guarantee a non-Elite alternative, (B) make HP recovery visible on the route, or (C) as designed? |
| D3 | The raid was a tax with nothing to place. With all crew flatlined and an empty armory, setup was a projection the tester could not change. The puzzle with assets is untested. | mothball | mothball §5 Q2–3; audit 0262 | When the player has nothing to place, should setup (A) still offer some decision, (B) skip straight to the playout, or (C) stay as is, with the projection as the information? |
| D4 | **Tester skill-limited. Recurs PB-010 D6.** Flatlines added +11 Heat each. The raid added 34→39. Heat ended at 39. | mothball | mothball §1, §3, §5 Q2 | Carried open from PB-010 D6: is flatline Heat meant to be the main early source? (A) Yes, with a warning (C7). (B) Reduce its share. (C) Undecided until skilled play. |
| D5 | **Recurs PB-010 D4.** Siphon was offered but refused for the OVERFLOW slot. The tester rejects off-plan rewards. | mothball | mothball §2, 0212.png | Carried open from PB-010 D4: (A) offer conditional firmware only when usable, (B) state the condition on the face, or (C) leave as is? |
| D6 | **Recurs PB-010 D7.** Netrun length was "just right" at 5–10 min. The Summary says campaign "too long", but §3 says the campaign was not judged (INCOMPLETE). | mothball | mothball §3, §8 | Hold the length judgement until a tester completes a campaign? (A) Yes. (B) Probe now with a briefed tester. |

## 5. Motion and feel (→ the animation pass queue)

| ID | Moment | Verdict | Sheets | Problem |
|---|---|---|---|---|
| — | — | Not judged | none | There was no motion tester or contact sheet this batch. PB-010 M1–M10 have not been re-checked. mothball noted only that the result stamps are clear (§4). |

## 6. What worked (keep)

- **Combat keyboard coverage:** cards 1–5, Q/E, Space, Z (labelled), R, H and Esc. Winning the Collections Agent fight entirely from the keyboard was the tester's favourite moment (mothball §4, §6, 0208).
- **Raid projection matched the playout exactly.** The raid was called fair and understandable (mothball §5 Q1).
- **Combat readability:** HP, wheels, the result chips and the result stamps were readable. Reading the chips before sending let the tester steer a turn (mothball §2, §4).
- **Clear respin undo-block message** (mothball §2, 0225).

## 7. Proposed actions

1. **Slice items:**
   - Bugs P1: B1. Check for a state dependency: mothball's freeze followed a raid.
   - Clarity, all 1 of 1, in rank order: C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, then C12 (audit only).
   - Bugs P2: B2 and B3, after a human repeat.
   - Most of these duplicate open PB-010 items on the same build. Merge them there rather than opening new tickets.
2. **Checkpoint items for the designer:**
   - D3: raid setup with nothing to place — offer a decision, skip to the playout, or leave as is?
   - D2, D4, D5, D6: carried open from PB-010 D3, D6, D4 and D7, with the same questions.
   - D1 is an observation only.
3. **Next batch:**
   - Collect saltlamp's missing report, or re-run it, to restore the expert and pacing view.
   - Run a full mix again (n=1 is too thin to rank anything).
   - Keep the keyboard-only persona to verify C1 once bindings land.
   - Brief a raids tester to enter a raid with crew and assets placed, to test whether the puzzle exists (D3).
   - Get human repeats of B2 and B3. Reproduce B1 after a raid.