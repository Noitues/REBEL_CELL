# Playtest findings — PB-PT-003 · build 52ba1e942fc6205fa97a705cb4c3171aafbbeae9 · 2026-10-14

> Synthesised from 4 Claude playtest reports, their screen audits and motion judgements
> (docs/process/05_CLAUDE_PLAYTESTER.md §9). Every finding names the testers who hit it and the
> evidence (report section, shot or contact sheet). Ingest per doc 04 §3: bugs and clarity items
> become slice items; balance and design items go to the checkpoint for the designer's ruling.

## 1. Headline

- **No tester completed a netrun or cleared a Site.**
  - 180 minutes of play produced 14 operative deaths, and all 4 outcomes were INCOMPLETE.
  - blue_hour's summary says "netruns_completed: 7". Their §1 describes about 14 fights across several campaigns, about 7 of them won, so the 7 counts fights, not netruns.
  - blue_hour's focus was raids, and they never saw one. The only raids this batch were two First Notice raids (nullpoint, parallax). Both ended CELL HOLDS with Home at 50→40.
- **The post-wipe dead-end is the top blocker, and it recurs from PB-PT-002 B4.**
  - After both Breakers died, blue_hour (twice) and byte_rat (about 9 min) were told to "recruit or rest at HQ". They found no HQ route and held 5 Schematics against a 15-Schematic recruit.
  - The recruit price display is also inconsistent: it showed 0 for blue_hour and parallax (B2).
- **Ground truth says every difficulty signal is skill-limited.**
  - A Perfect was reachable on 94–100% of turns. Testers landed one on 16–28%. Doing nothing at all would have landed 12–25%.
  - blue_hour landed 16% against 21% for doing nothing, and took exactly the no-action damage (3.5 per turn).
  - Testers acted on 16–55% of turns. They dealt 3.4–7.0 per turn against 14.5–21.9 for the best plan.
  - No tester aligned for Perfects and still lost.
- **The same clarity gaps recur.** Each cost 3 of 4 testers:
  - the wheel vocabulary (GOOD/NULL/WEAK/PERFECT, chips, RAM -1);
  - nudges and aim landing;
  - Heat;
  - finding HQ.
  
  The Jolt/Fine Tune aim snapping to the enemy ring recurs from PB-PT-002 B1, but at lower cost: byte_rat lost about 6 min, against about 30 min for parallax last batch.
- **Trend.**
  - Enjoyment rose to 3.5 from 3.0, and RNG fairness held at 3.0 against 3.2.
  - The UNDO lock after a random pick now shows a banner, but parallax still missed it for about 24 min.
  - PB-PT-002 B5, B8 and B9 were not reported this batch. They are not confirmed fixed.
  - parallax §1 calls the third netrun a "tutorial-overlay fight", which may mean PB-PT-002 B3 recurs. The report gives no further detail.

| Metric | This batch | Previous (PB-PT-002) |
|---|---|---|
| Testers (novice / intermediate / expert / motion) | 3 / 1 / 0 / 0 | 2 / 2 / 0 / 0 |
| Furthest progress | No Site cleared and 0 netruns completed. byte_rat reached Site tier T3 with 0 Sites claimed. 2 First Notice raids held (nullpoint, parallax) | No Site cleared, T1 max |
| Avg enjoyment (1–10) | 3.5 (n=4) | 3.0 (n=4) |
| Avg RNG fairness (1 fair – 5 cheated) | 3.0 (n=4) | 3.2 (n=4) |
| Bugs reported (deduplicated) | 20 raw → 10. A further 7 cosmetic items moved to C5 and C6, and 1 harness item went to tooling | 28 raw → 10 |

## 2. Bugs (→ slice items; P1 = fix before the next gate, P2 = next slice)

| ID | Sev | Area | Bug | Testers | Repro (from the reports) | Evidence | Confidence |
|---|---|---|---|---|---|---|---|
| B1 | P1 | city | After a wipe the campaign dead-ends. The map says "recruit or rest at HQ", but neither the map nor the Map Key shows an HQ route. The Market recruit costs 15 Schematics and both testers held 5. nullpoint did reach the MARKET tab and later fielded Breaker 4, so a recovery path may exist but be hidden (see C2). Recurs PB-PT-002 B4. | blue_hour, byte_rat | 1. Lose both Breakers. 2. Return to the map with 5 Schematics. 3. The hint points to HQ, but no HQ route or affordable recruit is shown. blue_hour hit this at 9.0–11.0m and again at 27.1–29.5m, then quit and restarted. byte_rat hit it at 30.7–38m. | blue_hour §7#1 0055, §3; byte_rat §7#2 0173, §3 | confirmed (2 testers, matching steps). blue_hour's "CREW click did nothing" is unconfirmed-input. |
| B2 | P1 | rules | The Market recruit card shows a cost of 0 Schematics after a wipe. blue_hour was charged 15. parallax's Schematics stayed at 20 throughout, and the recruit "appeared free". | blue_hour, parallax | 1. Lose the crew. 2. Open MARKET. 3. The recruit card reads 0 Schematics. | blue_hour §7#5 0058; parallax §3, §5 Q2 | confirmed for the displayed 0. The actual charge conflicts between testers and needs checking. |
| B3 | P1 | combat | With Jolt or Fine Tune selected, the aim lands on the enemy ring (or the enemy nudge arrow) instead of the tester's own wheel. byte_rat lost about ten turns in fight 2 to this. Jolt worked only when byte_rat let it default. Recurs PB-PT-002 B1. | byte_rat, parallax | 1. Select Fine Tune or Jolt. 2. Click your own wheel. 3. The arc stays on, or snaps to, the enemy ring. Times: byte_rat 9.5–15.6m, parallax 7.5–8.5m. | byte_rat §7#1 0057, confusion 9.5m/10.9m; parallax §7#2 0043, §2 | confirmed (2 testers saw the aim land on the enemy ring). Whether own-wheel clicks register at all needs a human repeat. |
| B4 | P1 | city | JACK IN looks active when no operative can run the Site. It is only dimmed. | blue_hour, byte_rat | 1. Have no available operative. 2. Select a Site card. 3. JACK IN appears enabled. | blue_hour §7#4 0058; byte_rat §7#3 0174 | confirmed |
| B5 | P2 | screens | Save & Quit clicks were ignored, and then the game closed and relaunched itself. Other testers quit cleanly from the pause menu or to the title. Recurs PB-PT-002 B10 (parallax). | parallax | 53.8–54.2m: click Save & Quit repeatedly. | parallax §1, §7#5 0294 | single |
| B6 | P2 | combat | The lethal preview chip seemed stale on Rack turn 4. It did not refresh with wheel changes and cleared only after a setup change at 30.7m. This cost about 15 min of undos. | parallax | Rack fight, turn 4, 23–30m. | parallax §7#4 0128, §6 | single |
| B7 | P2 | combat | Brute Spin queued two spins with no visible wheel turn. Z undo cleared it. This may be related to PB-PT-002 B7 (a respin spent RAM but did not happen). | parallax | Play Brute Spin at 13.4m. | parallax §7#3 0070, §2 | single |
| B8 | P2 | combat | In the tutorial, undoing on turn 2 made Jolt seem to vanish from the hand, and the queue looked muddled. | nullpoint | Tutorial turn 2: queue Jolt (3.2m), then undo four times. | nullpoint §7#1 0018, §2 | single |
| B9 | P2 | screens | The first click on the title loaded the wrong screen. This is possibly the tail of PB-PT-002 B3, where the title started a tutorial fight. | blue_hour | 1.2m, first click on the title. | blue_hour confusion 1.2m, §4 | single |
| B10 | P2 | screens | Space did not advance tutorial steps, so NEXT had to be clicked. Space did work for SEND IT. Last batch, parallax reported that Space did work in the tutorial (PB-PT-002 C9). | parallax | Tutorial, 1.7–2.6m. | parallax §7#1 0007, §4 | unconfirmed-input (needs a human repeat) |

Excluded from this table:
- parallax §7#6 (escalation hand-offs never answered) is a playtest-harness issue. It goes to tooling.
- Seven cosmetic items moved to C5 and C6: blue_hour §7#2–3, byte_rat §7#4, nullpoint §7#2–4 and parallax §7#7.

## 3. Clarity and UX (→ slice items, ranked by how many testers it cost)

| ID | Area | Problem | Testers (of n) | Time lost / what resolved it | Evidence | Suggested direction |
|---|---|---|---|---|---|---|
| C1 | combat | The wheel vocabulary is never explained: <br>• GOOD, NULL, WEAK and PERFECT; <br>• "GOOD → WEAK" tags; <br>• chips on cards and wheels; <br>• RAM -1; <br>• the unlabelled stacked numbers beside the enemy wheel, and the enemy readout's "wall of numbers"; <br>• which slot or card deals the damage. <br>The tutorial text is a wall that blue_hour skipped. Recurs PB-PT-002 C2. | 3 of 4: blue_hour, byte_rat, nullpoint (parallax found combat info readable) | Never resolved by any of the three. byte_rat spent about 40 min on GOOD/NULL. | blue_hour §2, §4, confusion 2.1m; byte_rat §2, §4, §5 Q1–2; nullpoint §2, §4, confusion "throughout" | Add an in-place legend for the tags, chips and enemy numbers. Break the tutorial text into steps that cannot be skipped by accident. |
| C2 | city | HQ and recruiting are hard to find: <br>• The map has no HQ marker, and the Map Key has no HQ entry. <br>• Recruiting sits in the MARKET tab. <br>• Recruit costs are not shown until MARKET is opened. <br>Ties to B1. | 3 of 4: blue_hour, byte_rat, nullpoint | blue_hour: never resolved (9.0–11.0m and 27.1–29.5m). byte_rat: about 9 min, never resolved. nullpoint: about 0.5 min plus 1.5 min, resolved by finding the MARKET tab. | blue_hour §3, §4; byte_rat §3, §4, confusion 30.9m; nullpoint §3, §4, confusion 14.1m/23.1m | Put an HQ marker and route on the map. When the roster is empty, point the hint at the recruit action and show its cost. |
| C3 | city | Heat can't be predicted or managed. Each flatline adds 11, which testers saw only afterwards. Recurs PB-PT-002 C1. | 3 of 4: blue_hour, byte_rat, nullpoint (parallax read the thresholds as fair) | Never resolved. | blue_hour §3; byte_rat §3, §5 Q1; nullpoint §3 | Show the Heat delta before risky actions. State what each threshold triggers. |
| C4 | combat | Nudges and aim landing are unclear: <br>• The free nudge arrows above the wheels are never taught. <br>• Where a card lands is readable only once it is selected ("1 LANDS HERE"). <br>• It is unclear which wheel Fine Tune targets. <br>Ties to B3. Recurs PB-PT-002 C3. | 3 of 4: nullpoint, byte_rat, parallax | nullpoint: about 1.5 min and four undos, then found the arrows. byte_rat: about 6 min, partly resolved by "1 LANDS HERE" at 16.7m. parallax: never resolved. | nullpoint §2, confusion 3.2m; byte_rat §2, confusion 10.9m; parallax §2, confusion 7.5m | Teach the free nudge in the tutorial. Show the landing arc as soon as an aimed card is selected. |
| C5 | screens | Text is clipped and panels overlap: <br>• Card text: Overdrive and Mirror Flip are cut off (recurs PB-PT-002 C6). <br>• The "needles resolving" tooltip covers the cards. <br>• The defeat screen clips its message, and CONTINUE overlaps PROCEED. <br>• The START DEFENSE label is clipped. <br>• The Map Key covers the top of the site card. <br>• The dossier hides max HP behind its stamp. <br>• The HQ ticker and command box are clipped. | 3 of 4: nullpoint, blue_hour, parallax | Never resolved, though none of these blocked play. | nullpoint §2, §4, §7#2 0044, §7#3 0012, §7#4 0221; blue_hour §7#2 0055, §7#3 0130; parallax §4, §7#7 0217 | Fit the full rules text on each card face. Run a layout pass on the defeat, raid briefing, map and HQ screens. |
| C6 | city | The HQ map and Site chain are hard to read: <br>• The Site chain is explained only in node text ("clear X first"). <br>• The CENTRAL SERVER target label doesn't match the selected site card. <br>• Map stats (Exploits 0/3, Raids, Ice) are unexplained, and there is no objective prompt. <br>• "Home" and "Core HP" read as inconsistent terms. <br>Recurs PB-PT-002 C10. | 2 of 4: byte_rat, parallax (nullpoint raised the terms) | byte_rat: about 5 min, resolved by reading node text. parallax: never resolved. | byte_rat §3, §4, §7#4 0183, confusion 35m; parallax §4; nullpoint §4 | Draw the Site links on the map. Add a one-line objective. Settle on one term for home integrity. |
| C7 | combat | The UNDO lock after a random pick (Jolt, a respin) is now explained by a banner, but the banner is easy to miss. The lock also left parallax with no clean line on Rack turn 6. Recurs PB-PT-002 B2; the reason is now shown. | 1 of 4: parallax | About 24 min (15.4→39.1m), resolved by reading the banner. | parallax §2, §6, confusion 15.4m | Show the lock reason on the UNDO control itself. Warn before a play that will lock UNDO. |
| C8 | screens | Permadeath is signposted only by the LETHAL tag before a fight. byte_rat found the permadeath screen itself clear. | 1 of 4: blue_hour | Never resolved before the first deaths. | blue_hour §3, §6 | Warn before jacking in or committing a lethal turn that the operative's death is permanent. |
| C9 | screens | Abandon Campaign sits right beside Quit to Main Menu, so it is easy to miss-click. Recurs PB-PT-002 C5. | 1 of 4: parallax | Avoided. | parallax confusion 53.6m | Separate Abandon Campaign from the other buttons and put it behind a confirm. |

## 4. Balance and design signals (→ checkpoint items for the designer; never straight into tuning)

| ID | Signal | Testers | Evidence | Question for the designer |
|---|---|---|---|---|
| D1 | **Tester skill-limited.** There were 14 deaths, and testers called fights long and hard. Ground truth: <br>• A Perfect was reachable on 94–100% of turns. Testers landed one on 16–28%; doing nothing gives 12–25%. blue_hour landed 16% against 21% for doing nothing. <br>• Testers acted on 16–55% of turns. blue_hour acted on 16% and said "I mashed SEND IT". <br>• They dealt 3.4–7.0 per turn against 14.5–21.9 for the best plan. <br>• They took 2.9–3.9 per turn against 0.7–1.0 for the best plan and 3.2–4.3 for doing nothing. <br>No tester aligned for Perfects and still lost. parallax (intermediate, 25% when reachable) sent into mutual lethal on Rack turn 6 rather than push the enemy's Perfect 16 pointer off. Testers failed to read or do: <br>• the wheel tags and chips (C1); <br>• the nudge and aim landing (C4, B3); <br>• the UNDO lock reason (C7); <br>• the HQ recovery path (C2). | blue_hour, byte_rat, nullpoint, parallax | Ground-truth table; parallax §2, §5 Q1 | Observation only, no tuning question. Re-test after B3, C1, C4 and C7 land. |
| D2 | **Tester skill-limited (HP attrition).** Testers went into fights hurt, along forced routes with no heal shown: <br>• parallax: 60→31→16→16, then a forced Rack (112 HP Claims Adjuster) and a forced Elite (106 HP Recall Unit) at 16 HP. <br>• nullpoint: walked in at 18/68, and the 112 HP Adjuster after Rack L4 came with no warning. <br>• byte_rat: started Triage at 12/60. <br>• blue_hour: started a fight at 7/60. <br>The only heal seen was Wellness Kiosk (+10 HP, +2 Heat). Recurs PB-PT-002 D2. | parallax, nullpoint, byte_rat, blue_hour | parallax §3, §5 Q1, Q3; nullpoint §3; byte_rat §3; blue_hour §3 | (A) Guarantee a heal or non-Elite alternative on each layer. (B) Make existing heal routes and upcoming enemy strength visible. (C) Keep as designed. |
| D3 | **Tester skill-limited.** Fights ran long: <br>• blue_hour: 5–18 turns, about 2–4 min each. <br>• byte_rat: 8, 16 and 13 turns. <br>• nullpoint: 13 turns (about 11 min) and 16 turns (about 20 min). <br>Testers dealt roughly a fifth to a third of the best-plan damage. Recurs PB-PT-002 D3. | blue_hour, byte_rat, nullpoint | blue_hour §3; byte_rat §3; nullpoint §3, §5 Q1 | (A) Re-judge fight length once a tester aligns for Perfects. (B) Surface which slot deals damage first (C1), then re-judge. (C) Probe now with a briefed tester. |
| D4 | **Card picks are mostly clarity-driven.** <br>• Called OP in the reports: only parallax (Jolt, Mirror Flip cutting a hit from 16 to 4, Patch+). <br>• The summaries' op_picks for byte_rat and nullpoint (Jolt, Fine Tune, Nudge Driver, Patch Up) contradict their reports, which say "none seen". <br>• Called weak: inner-ring cards (Gear Shift, Ring Tap, Inner Snap) as dead for the Breaker; Sanitize, Reroll and Inner Drift (parallax). <br>• byte_rat never worked out Overdrive. <br>Recurs PB-PT-002 D4. | parallax, byte_rat, nullpoint | parallax §2; byte_rat §2; nullpoint §2 | Should cards that need an inner ring be (A) offered only to classes that have one, (B) labelled with the requirement on the card face, or (C) kept as is? |
| D5 | **Economy.** <br>• Schematics: three testers ended at 5 against a recruit cost of 15. parallax sat on 20, unused. Other classes are locked at 40–80 (nullpoint), and Hivemind shows "UNLOCKS 60" (blue_hour). <br>• Shop: nullpoint had 40 Cycles; the cheapest card cost 50. <br>• Cycles were lost on death (parallax, 62). <br>• The Defense armory was empty (0/6). <br>Recurs PB-PT-002 D5. | blue_hour, byte_rat, nullpoint, parallax | blue_hour §3, §2; byte_rat §3; nullpoint §2, §3; parallax §3, §5 Q3 | (A) Hold until a tester clears Sites. (B) Make income and recovery routes visible. (C) Revisit the recruit cost relative to the post-wipe Schematics. Which? |
| D6 | **Tester skill-limited.** Flatline Heat (+11 per death) drove the raids: <br>• blue_hour: 11, then 22. <br>• byte_rat: 22. <br>• nullpoint: raid threshold 25, hit at 33, final 38. <br>• parallax: 11, 25, 30. <br>Raids arrived with no assets to deploy (nullpoint) or almost no crew (parallax). Recurs PB-PT-002 D6. | blue_hour, byte_rat, nullpoint, parallax | blue_hour §3; byte_rat §3; nullpoint §3; parallax §3 | Is flatline Heat meant to be the main early Heat source? (A) Yes, and warn about it (C3). (B) Reduce its share. (C) Undecided until skilled play. Separately: should a raid with no deployable assets (A) still run, or (B) offer a minimum defense? |
| D7 | **Length.** <br>• Netruns: called too long ×3, too short ×1 (parallax's netruns ended early in deaths). <br>• Campaign: called too long ×4. <br>Most time went to long fights (D3), the HQ dead-end (B1) and the aim and UNDO issues (B3, C7). Recurs PB-PT-002 D7. | all 4 | Batch statistics | Re-judge length after B1 and B3 land? (A) Yes. (B) Probe now with a briefed tester. |

## 5. Motion and feel (→ the animation pass queue)

No contact sheets or motion judgements came with this batch. The rows below come from the testers' own report remarks.

| ID | Moment | Verdict | Sheets | Problem |
|---|---|---|---|---|
| M1 | Hits and Perfects | Barely register | none (report only) | nullpoint noticed Perfects only in the result readouts. blue_hour said little impact registered. Recurs PB-PT-002 M1/M2. |
| M2 | Jack-in iris wipe and turn resolve | Too slow, repetitive | none (report only) | nullpoint most wanted to skip the dark iris wipe, and found the turn-by-turn resolve repetitive. |
| M3 | Aiming state and Brute Spin | No feedback | none (report only) | Own-wheel aim clicks showed no visible change (byte_rat). Brute Spin gave almost no visible wheel turn (parallax). Ties to B3 and B7. Recurs PB-PT-002 M3. |

## 6. What worked (keep)

- **Turn preview and preview chips:** these matched every send parallax checked (0032, 0035, 0048). They were byte_rat's "only teacher". nullpoint's previews called out lethal turns and the damage he would take.
- **Landing a Perfect on the 12 slice:** this was the favourite moment for both parallax (Dosage Dispenser 38→14) and nullpoint (Compliance Officer, 5 turns).
- **Targeting arrows:** "1 LANDS HERE" (byte_rat) and Jolt's targeting arrow (nullpoint) helped once they were seen.
- **Stamps, writing and mood:** byte_rat liked the OURS NOW / DELETED stamps and the operative lines.
- **Clear end-of-fight screens:** byte_rat found the permadeath screen clear. blue_hour's loot-pick win screen was the first thing that felt like progress.
- **First Notice raid:** the briefing was readable and the raid understandable (nullpoint, parallax).
- **Clean quits:** byte_rat's and nullpoint's quits and saves held.
- **Controls:** click-then-target worked (nullpoint), and Space for SEND IT worked (parallax).

## 7. Proposed actions

1. **Slice items:**
   - Bugs P1: B1, B2, B3, B4.
   - Clarity, by tester count: C1, C2, C3, C4, C5, C6, C7, C8, C9.
   - Bugs P2: B5, B6, B7, B8, B9.
   - B10 needs a human repeat before any fix.
2. **Checkpoint items for the designer:**
   - D2: guarantee a heal or alternative route, make heals and enemy strength visible, or keep as designed?
   - D3: re-judge fight length after skilled play, after C1, or probe now?
   - D4: filter inner-ring cards by class, label the requirement, or keep as is?
   - D5: hold, make income routes visible, or revisit the recruit cost?
   - D6: what share of early Heat should flatlines provide, and should an asset-less raid still run?
   - D7: re-judge length after B1 and B3?
   - D1 is an observation only.
3. **Next batch:**
   - Re-run after B1–B4, C1, C2 and C4 land, keeping the ground-truth replay table.
   - Brief the raids-focus tester to reach a raid. blue_hour never saw one.
   - Add one tester briefed to align for Perfects, so difficulty, fight length and D2 can be judged.
   - Check whether a recruit is actually free or costs 15 after a wipe (B2), and how nullpoint fielded Breaker 4.
   - Check parallax §1's "tutorial-overlay fight" against PB-PT-002 B3.
   - Get a human repeat of B10 and of the own-wheel clicks in B1 and B3.
   - Restore a keyboard-preferring persona to re-check PB-PT-002 C8.
   - Route parallax §7#6 (unanswered escalations) to playtest tooling.