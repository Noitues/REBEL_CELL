# Playtest findings — PB-PT-002 · build 52ba1e942fc6205fa97a705cb4c3171aafbbeae9 · 2026-10-13

> Synthesised from 4 Claude playtest reports, their screen audits and motion judgements
> (docs/process/05_CLAUDE_PLAYTESTER.md §9). Every finding names the testers who hit it and the
> evidence (report section, shot or contact sheet). Ingest per doc 04 §3: bugs and clarity items
> become slice items; balance and design items go to the checkpoint for the designer's ruling.

## 1. Headline

- **Nobody completed a real campaign step.**
  - 190 minutes of play produced 11 operative deaths.
  - Outcomes: 3 INCOMPLETE, 1 ABANDONED (openloop soft-locked with an empty roster and 0 Schematics).
  - Highest Site tier was T1. No Site was cleared.
  - saltlamp, whose focus was the City Grid, HQ and Heat, never reached the City Grid.
- **A stuck card or nudge aim was the biggest time sink, and it recurs from PB-010 B3.** All 4 testers hit it:
  - parallax: about 30 min;
  - saltlamp: about 11 min;
  - neon_moth: about 8 min;
  - openloop: about 3 min.
  
  UNDO being blocked after a random event, with no reason given, made it worse for 3 testers (recurs PB-010 B6).
- **The ground truth says every difficulty signal is skill-limited.**
  - A Perfect was reachable on 96–100% of turns.
  - Testers landed one on 15–30% of turns. Doing nothing at all would have landed 18–26%.
  - Testers acted on only 22–46% of turns.
  - Damage taken (2.9–3.8 per turn) is barely below doing nothing (2.9–4.8) and far above the best plan (0.0–0.9).
  - The testers' own FIGHT-line counts (0.00–0.11 Perfects per turn) undercount.
- **The same clarity gaps as PB-010 recur:**
  - Heat (all 4 testers);
  - the wheel tags and RAM-debt chips;
  - nudges and aim landing;
  - clipped card text;
  - no cancel key.
- **The two keyboard-only testers (neon_moth, parallax) still need the mouse to aim, and most buttons show no key** (recurs PB-010 C11).
- **Several PB-010 P1s were not reported this batch:** B1 (FIGHT WON with no Continue), B2 (loot OVERFLOW block), B7 (Map Key) and B8 (raid banner). They are not confirmed fixed, because coverage was thin.

| Metric | This batch | Previous (PB-010) |
|---|---|---|
| Testers (novice / intermediate / expert / motion) | 2 / 2 / 0 / 0 | 3 / 3 / 1 / 1 |
| Furthest progress | No Site cleared, T1 max. saltlamp logged 2 netruns completed (report §1: 3 fights started, 2 completed) with 0 deaths. neon_moth started 5 netruns, completed 0, and survived 2 raids | No Site cleared. 1 campaign lost (halfmoon) |
| Avg enjoyment (1–10) | 3.0 (n=4) | 3.4 (n=8) |
| Avg RNG fairness (1 fair – 5 cheated) | 3.2 (n=4) | 2.9 (n=7) |
| Bugs reported (deduplicated) | 28 raw → 10 | 69 raw → 15 |

## 2. Bugs (→ slice items; P1 = fix before the next gate, P2 = next slice)

| ID | Sev | Area | Bug | Testers | Repro (from the reports) | Evidence | Confidence |
|---|---|---|---|---|---|---|---|
| B1 | P1 | combat | A card or nudge aim sticks and cannot be cancelled. The RAM debt stays on screen. What clears it varies: sometimes Z or UNDO, sometimes the pause menu plus a wheel click, sometimes it clears by itself. Quit → Continue restores the same stuck aim. Recurs PB-010 B3. | parallax, saltlamp, neon_moth, openloop | 1. Select Fine Tune, Jolt or Brute Spin, or the free nudge, and start an aim. 2. Press Esc, right-click, press Z or click UNDO. 3. The arc or arrow stays. saltlamp's arrow stayed on the Triage ring, and clicks on her own wheel did nothing. openloop's Fine Tune never confirmed after about 10 wheel clicks. | parallax §7#1 0204/0320, §7#3 0222; saltlamp §7#4 0243; neon_moth §7#2 0136; openloop §7#1 0010–0027 | confirmed (other testers aim by wheel click, so this is not just simulated input) |
| B2 | P1 | rules | UNDO is blocked after a Jolt, a respin or a "random event". The reason is missing, or it names no event. UNDO flickers between live and blocked, Z is ignored, and RAM debt stays. Recurs PB-010 B6. | neon_moth, parallax, saltlamp | 1. In a turn, play Jolt or respin, or stage Fine Tune after a random pick. 2. Press Z or UNDO. 3. It is blocked. saltlamp saw "a random event came since (a respin, a random pick)" and then UNDO 0, greyed. parallax saw the reason only at 34m. | neon_moth §7#5 0257, §2; parallax §7#2 0097/0226, §2; saltlamp §7#3 0209, §2 | confirmed |
| B3 | P1 | combat | The tutorial overlay persists into real netrun fights. parallax: the 4/7 box covered turns 4–10 on a Billing Farm fight, only Space moved it, and it stayed after the Breaker flatlined. neon_moth: the tutorial nudge box repeated every turn. After a reload, the title started a tutorial fight. | parallax, neon_moth | 1. Finish the tutorial and jack in. 2. Tutorial boxes keep appearing in netrun fights. parallax lost a Breaker under the box. | parallax §7#6 0403, §7#9 0397, confusion 56.2m; neon_moth §4, confusion 5.3m | confirmed |
| B4 | P1 | city | With an empty roster and 0 Schematics, the campaign dead-ends. HQ offers only Heat Scrub (25) and the Market recruit (15), and no rest action. The hint "recruit or rest at HQ" points at nothing. The CREW tab shows no change, and permadeath is warned about only in the flatline box. Note: neon_moth had a ready Breaker 5 at 49.2m while holding 5 Schematics, so a recovery path may exist but be hidden. Related to PB-010 C6. | openloop (blocked); neon_moth, parallax (reached the same state and were not blocked, or the session ended) | 1. Lose all Breakers. 2. Spend Schematics to 0 (Market recruit 15). 3. HQ has nothing affordable and no rest. | openloop §7#3 0191–0199, §3, §6; neon_moth §7 confusion 30.3m, 48.6m; parallax §1 | single (dead-end) |
| B5 | P2 | rules | The Dosage Dispenser fight showed 0/38 DELETED but was counted as a defeat. Breaker 4 flatlined. | neon_moth | Turn 11, both sides reached zero. | neon_moth §2, §7#6 0294 | single |
| B6 | P2 | combat | Q/E never visibly moved the needle during the whole tutorial. Clicking the arrow worked. neon_moth's E nudge did work, so check the state (free nudge or nudge card), not the input. | parallax | Tutorial turn 7: the needle is on NULL, and Q/E do nothing. | parallax §7#4 0025, confusion 3.3m | single |
| B7 | P2 | combat | Respin spent RAM (down to 2/12) but no respin appeared. | parallax | Respin at 31.8m. | parallax §7#8 0207 | single |
| B8 | P2 | combat | The whole fight screen ignored keys, wheel clicks and Space after an escalation on Elite turn 2. Opening and resuming the pause menu fixed it. | neon_moth | 16.5–17.9m, Recall Unit Elite. | neon_moth §7#1 0095 | single |
| B9 | P2 | city | A raid ran on its own with no Start Defense step. | openloop | Raid at 19.0m. | openloop §7#4 0118, §3 | single |
| B10 | P2 | screens | Single-tester ignored inputs: <br>• Event option keys 1 and 3 (the click worked) — neon_moth. <br>• Quit confirm [A] did nothing (recurs PB-010 B5); the game later restarted to the Godot splash — parallax. <br>• Esc and the gear icon did not open pause on the HQ Core panel for about 20 min — openloop. <br>• The UNDO button click did nothing until Z — saltlamp. <br>• Fine Tune card-area clicks did nothing — saltlamp. | neon_moth, parallax, openloop, saltlamp | As listed in each report. | neon_moth §7#3–4 0078/0249; parallax §7#5 0383; openloop §7#2 0131–0136; saltlamp §7#1–2 0135/0062 | unconfirmed-input (needs a human repeat) |

Excluded from this table:
- neon_moth §7#9 (escalation never answered) is a playtest-harness issue. It goes to tooling.
- openloop §7#5 (Codex slot wording) is a cosmetic reviewer-audit item that no tester tripped on.

## 3. Clarity and UX (→ slice items, ranked by how many testers it cost)

| ID | Area | Problem | Testers (of n) | Time lost / what resolved it | Evidence | Suggested direction |
|---|---|---|---|---|---|---|
| C1 | city | Heat can't be predicted or understood. Specific problems: <br>• No delta is shown before acting. <br>• Flatlines add about 11 and raids add 5, shown only afterwards. <br>• Heat 30 cuts Mainframe items with no explanation. <br>• The payout panel read 0 while the top bar read 30 and 58. <br>• No Heat number appears on the plan preview. <br>• The tutorial's banking rule was misread. <br>Recurs PB-010 C3. | 4 of 4: neon_moth, openloop, parallax, saltlamp | Never resolved. openloop asked "what Heat does" from 14.0m to the end. parallax understood only at the raid warning. | neon_moth §3, §7#7 0334; openloop §3, §5 Q1; parallax §3; saltlamp §3, §5 Q1 | Show the Heat delta before each action. Fix the payout value. State what each threshold does. |
| C2 | combat | These are never explained: <br>• the WEAK/GOOD/NULL/PERFECT tags; <br>• the RAM debt chip (-2/-6); <br>• Resistance and Null; <br>• the slice icons and "1/0" values; <br>• the COOL meter; <br>• the Jolt "-1" chip. <br>Recurs PB-010 C1. | 3 of 4: parallax, saltlamp, neon_moth (openloop: "wheels and arrows a blur") | parallax never resolved it (about 40 min). saltlamp needed 2.5 min, until she found the PRECISION TAG tooltip at 14.5m. | parallax §2, §5 Q1–2; saltlamp §2, confusion 12.1m; neon_moth §2, §4; openloop §4 | Add an in-place legend for the tags and chips. Surface the PRECISION TAG tooltip in the first fight. |
| C3 | combat | Nudges and aim landing are unclear: <br>• what a free nudge gains; <br>• the nudge RAM cost, shown only on the ledger; <br>• where Jolt and Fine Tune land without the dashed arc; <br>• the meaning of "LANDS HERE"; <br>• the FREE NUDGE 1 banner, which did not drop after use. <br>Recurs PB-010 C5. | 3 of 4: saltlamp, parallax, neon_moth | saltlamp: 2 min, then 3 min on the aim arrow. parallax: 2 min in the tutorial. | saltlamp §2, confusion 3.0m and 25.5m; parallax §5 Q1, §7#7 0365; neon_moth §2, §4 | Show the nudge cost on the control. Keep the free-nudge counter live. Show the landing arc for every aimed card. |
| C4 | combat | No visible cancel for a card aim. Esc opens pause, right-click works only sometimes, and nothing on screen names a cancel key. Ties to B1. | 3 of 4: neon_moth, parallax, saltlamp | saltlamp: about 6 min (5.4–11.5m), resolved by UNDO and trial. | neon_moth §4; parallax §4; saltlamp §4, §7#5 0041 | Use one cancel key, and show it while an aim is active. |
| C5 | screens | Abandon Run sits beside Resume and Quit on the pause menu. | 3 of 4: neon_moth, parallax, saltlamp | saltlamp avoided the pause menu entirely. | neon_moth §4; parallax §4; saltlamp §4 | Separate Abandon Run from the other buttons and put it behind a confirm. |
| C6 | combat | Card text is clipped and the hand overlaps. Mirror Flip reads "Blocked while th…" and Overdrive is cut off. Fine Tune got selected by accident. The Overdrive and Fine Tune text is hard to parse. Recurs PB-010 C2. | 3 of 4: neon_moth, saltlamp, openloop | Never resolved. | neon_moth §2; saltlamp §2, §4; openloop §2 | Fit the full rules text on the card face. Stop neighbouring cards covering it. |
| C7 | city | The route map hides options: <br>• At 13/60 HP only Fight L3 showed, and the Rack was only in the route panel. <br>• The map showed 25/68 HP against an expected 25/60. <br>• Route map vs Grid View is unexplained. <br>• Nodes are small and the map is busy. <br>Recurs PB-010 C7. | 3 of 4: saltlamp, openloop, parallax | saltlamp found the Rack in the route panel. openloop never resolved it. Hovering a node helped parallax. | saltlamp §4, §5 Q2; openloop §3, confusion 2.0m; parallax §4 | Draw every reachable node, including Racks, on the map. Make the max HP consistent. Label the two views. |
| C8 | screens | The keyboard path has gaps. No key is shown, or the shown key doesn't work, for: <br>• route nodes, loot and firmware picks; <br>• JACK IN, START DEFENSE, BACK TO GRID/HQ; <br>• raid Continue and Market recruit; <br>• tutorial NEXT/FINISH; <br>• the title buttons and Quit. <br>Card aiming needs a mouse. Recurs PB-010 C11 (not fixed). | 2 of 4: neon_moth, parallax (both keyboard-only personas) | Both fell back to the mouse throughout. | neon_moth §4, §6; parallax §4, §6 | Show key hints on every button. Add keyboard wheel targeting. |
| C9 | screens | The tutorial is hard to follow. The step text is a long paragraph, NEXT looks greyed out, and the nudge isn't taught (see C3). Recurs PB-010 C13. | 2 of 4: neon_moth, parallax | parallax: about 10 s, then found that Space works. | neon_moth §2; parallax confusion 2.0m | Break up the text. Make NEXT look active and show its key. |
| C10 | city | The HQ map doesn't make the starting Site obvious. The gate message on locked Sites helped. Recurs PB-010 C4, but cost about 5 min this batch against about 2.5 h last batch. | 1 of 4: neon_moth | About 5 min (30.3–35.9m). | neon_moth §4, §7#8 0230 | Highlight or pan to the first open Site. |
| C11 | city | The raid setup is a wall of text, and the result reads "FAILED" beside "CELL HOLDS". Recurs PB-010 C9. | 1 of 4: openloop | Never resolved. | openloop §3 | Make the outcome wording match the stamp. Shorten the setup text. |

## 4. Balance and design signals (→ checkpoint items for the designer; never straight into tuning)

| ID | Signal | Testers | Evidence | Question for the designer |
|---|---|---|---|---|
| D1 | **Tester skill-limited.** 11 deaths, and all 4 testers called something too hard. Ground truth: <br>• Perfect reachable on 96–100% of turns; landed on 15–30%; doing nothing gives 18–26% (saltlamp landed 15% against 23% for doing nothing). <br>• Acted on 22–46% of turns. <br>• Dealt 3.8–6.2 per turn against 17.6–20.3 for the best plan. <br>• Took 2.9–3.8 against 0.0–0.9 for the best plan and 2.9–4.8 for doing nothing. <br>No tester aligned for Perfects and still lost. Testers failed to read or do: <br>• the wheel tags and RAM debt (C2); <br>• the nudge and aim landing (C3); <br>• cancelling an aim (C4, B1); <br>• why UNDO was blocked (B2); <br>• the heal routes on the map (C7). | neon_moth, openloop, parallax, saltlamp | Ground-truth table; Batch statistics | Observation only, no tuning question. Re-test after B1, B2, C2 and C3 land. |
| D2 | **Tester skill-limited (HP attrition).** Forced single-node routes led into fights and Elites at low HP: <br>• neon_moth, layer 3: at 3, 13 and 19 HP. <br>• parallax: a Rack vs a 112 HP Claims Adjuster at 9/60 and 6/60. <br>• saltlamp: a Rack existed but was visible only in the route panel. <br>Recurs PB-010 D3. | neon_moth, parallax, saltlamp | neon_moth §3, §5 Q1; parallax §3; saltlamp §4 | (A) Guarantee a non-Elite or heal alternative on each layer. (B) Make the existing heal routes visible (see C7). (C) As designed. |
| D3 | **Tester skill-limited.** Long fights and high enemy HP: <br>• Triage Unit healed itself over 20 turns; another fight ran 18 turns. <br>• Claims Adjuster 112 HP and Recall Unit 106 HP. <br>• 6–12 min per fight. <br>Testers dealt about a quarter of the best-plan damage. Recurs PB-010 D2. | openloop, neon_moth, saltlamp | openloop §3; neon_moth §3; saltlamp §3 | How should regen and resistance counterplay be surfaced? (A) On the enemy wheel. (B) In a dossier. (C) Leave as is until a tester who aligns for Perfects confirms. |
| D4 | Card picks are mostly clarity-driven: <br>• Fine Tune called weak ×3 (landing unreadable, B1, C3). <br>• Overdrive ×2 (RAM debt; Corrupted at 13 HP). <br>• Mirror Flip (NEED 3 with 2 RAM). <br>• Gear Shift and Ring Tap (no inner ring). <br>Called OP: Firewall ×2. The summary op_picks also list cards the reports only describe as picked (saltlamp: "none seen"). neon_moth notes plain Space sends often won fights by themselves, consistent with the 18–26% no-action Perfect rate. Recurs PB-010 D4. | neon_moth, openloop, parallax, saltlamp | neon_moth §2; openloop §2; parallax §2; saltlamp §2 | Conditional cards: (A) offer them only when usable, (B) state the condition on the card face, or (C) as is? Separately: is plain SEND winning early fights intended? (A) yes, or (B) review after a skilled pass. |
| D5 | Economy: <br>• Schematics were scarce: 20 → 5 after one 15-cost recruit; openloop reached 0; parallax left 20 unspent. <br>• Cycles stayed at 18–42 and were wiped on flatline. <br>• HP recovery: only Wellness Kiosk +10 and Siphon. <br>Mainframe shops barely seen. Recurs PB-010 D5. | neon_moth, openloop, parallax | neon_moth §5 Q2–3; openloop §3; parallax §3 | (A) Hold until a tester clears Sites. (B) Make the income and recovery routes visible. (C) Revisit the recruit cost relative to the starting Schematics. Which? |
| D6 | **Tester skill-limited.** Flatline Heat drove the raids: <br>• neon_moth: 11/25/42/53, then 58. <br>• openloop: +14, then +11, ending at 57. <br>• parallax: 11/22/33, crossing the raid threshold at 25. <br>Recurs PB-010 D6. | neon_moth, openloop, parallax | neon_moth §3; openloop §3; parallax §3 | Is flatline Heat meant to be the main early Heat source? (A) Yes, and add a warning (C1). (B) Reduce its share. (C) Undecided until skilled play. |
| D7 | Length: <br>• Netrun called too long ×3 and just right ×1. <br>• Campaign called too long ×3 and not encountered ×1. <br>Most of the time went to stuck aims (B1) and long fights (D3). Recurs PB-010 D7. | neon_moth, openloop, saltlamp, parallax | Batch statistics | Re-judge length after B1 lands? (A) Yes. (B) Probe now with a briefed tester. |

## 5. Motion and feel (→ the animation pass queue)

No contact sheets or motion judgements came with this batch. The rows below come from the testers' own report remarks.

| ID | Moment | Verdict | Sheets | Problem |
|---|---|---|---|---|
| M1 | Perfect hit | Barely registers | none (report only) | neon_moth §4 says Perfects barely registered. Recurs PB-010 M3. |
| M2 | SEND IT resolution and hits | No sense of impact | none (report only) | openloop §4 and saltlamp §4 say the impact was not visible. neon_moth §4 found the hit and block reads fine. |
| M3 | Aiming state | No feedback | none (report only) | Wheel clicks and a stuck aim gave no feedback (openloop §4, parallax §4). Ties to B1. Recurs PB-010 M1. |

## 6. What worked (keep)

- **Preview chips and the incoming preview:** parallax (38→14), saltlamp (Daemon 30→18, Breaker 60→48) and neon_moth.
- **Quick Dosage Dispenser wins:** these were the favourite moment for all 4 testers (neon_moth, openloop, parallax, saltlamp).
- **UNDO when it works:** saltlamp liked taking plays back and found it restored RAM. openloop used it to back out of an aim.
- **Space, E and Z in combat:** neon_moth and parallax.
- **Raid Setup:** parallax liked the [R] hint and the raid warning at 25. neon_moth found the setup and projection understandable.
- **Saves held across quit and continue:** neon_moth, three times.
- **Helpful single-tester items:**
  - locked Site gate messages (neon_moth);
  - node hover explaining type and rewards (parallax);
  - right-click inspect, early in the run (openloop).

## 7. Proposed actions

1. **Slice items:**
   - Bugs P1: B1, B2, B3, B4.
   - Clarity, by tester count: C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11.
   - Bugs P2: B5, B6, B7, B8, B9.
   - B10 needs a human repeat before any fix.
2. **Checkpoint items for the designer:**
   - D2: guarantee a route alternative, make heal routes visible, or keep as designed?
   - D3: how to surface regen and resistance counterplay?
   - D4: filter conditional offers, state the condition, or keep as is? And is a plain SEND winning early fights intended?
   - D5: hold, make the income route visible, or revisit the recruit cost?
   - D6: what share of early Heat should flatlines provide?
   - D7: re-judge length after B1?
   - D1 is an observation only.
3. **Next batch:**
   - Re-run after B1, B2, C2 and C3 land, keeping the ground-truth replay table.
   - Keep both keyboard-only personas to verify C8.
   - Check whether a free crew recovery exists (B4, neon_moth's Breaker 5).
   - Get a human repeat of B10 and of parallax's Q/E (B6).
   - Brief one tester to reach the City Grid and clear a Site past T1. saltlamp's campaign-layer focus went untested, and D5 needs data.
   - Route neon_moth §7#9 (unanswered escalations) to playtest tooling.