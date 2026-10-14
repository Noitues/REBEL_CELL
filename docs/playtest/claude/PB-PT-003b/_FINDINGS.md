# Playtest findings — PB-PT-003b · build 3eac0f086e6d32f23afd7c95dbb0e7eb35379339 · 2026-10-14

> Synthesised from 4 Claude playtest reports, their screen audits and motion judgements
> (docs/process/05_CLAUDE_PLAYTESTER.md §9). Every finding names the testers who hit it and the
> evidence (report section, shot or contact sheet). Ingest per doc 04 §3: bugs and clarity items
> become slice items; balance and design items go to the checkpoint for the designer's ruling.

## 1. Headline

- **No tester completed a netrun.**
  - Play time was 180 minutes, with 6 operative deaths (saltlamp 3, tinroof 3).
  - All 4 testers ended INCOMPLETE. The highest Site tier was T1, and no Site was claimed.
  - nullpoint got furthest: fight 4 on layer 4, at 2/60 HP.
  - Enjoyment rose from 3.0 to 3.8. RNG fairness held at 3.2.
- **Backing out of a staged card is still the biggest time sink.** This recurs from PB-PT-002 B1 and B2.
  - UNDO refuses after a turn-start random spin (3 testers, B1).
  - No control cancels an aim or a staged card, and Esc opens the pause menu (3 testers, B2).
  - The cost: ferrite lost about 10 minutes, and tinroof lost an operative to a staged Jolt.
  - One improvement: the refusal now states its reason, which it did not in PB-PT-002.
- **Ground truth: every difficulty signal is skill-limited.**
  - A Perfect was reachable on 91–100% of turns. Testers landed one on 15–21%, and doing nothing would have landed 13–25%.
  - Testers acted on only 27–47% of turns.
  - Every tester took as much damage per turn as doing nothing, or more: 3.0–4.0 against 2.5–3.8. The best plan took 0.3–1.0.
  - The testers' own FIGHT-line counts (0.00–0.10 Perfects per turn) undercount.
- **The same clarity gaps recur:**
  - combat chips and tags (4 of 4);
  - nudge and free nudge (3);
  - Heat (3);
  - clipped card text and overlapping hand (3).
  
  New this batch: unexplained unlock currency, and loot picks with no confirmation.
- **HP attrition shaped every run.** Testers carried low HP into single-node layers with no heal, and this is skill-limited (D2).
  - ferrite's raid focus went untested, because Heat stayed at 0.
  - The 2 raids that did happen were driven by flatline Heat, and neither tester had anything to deploy.
- **Status of PB-PT-002 items:**
  - Not reported this batch: B3 (tutorial overlay in fights), B5 and B6.
  - B4 (empty-roster dead end) was not reproduced. tinroof got a free rookie after each death.
  - There was no keyboard-only persona, so PB-PT-002 C8 is unchecked.

| Metric | This batch | Previous (PB-PT-002) |
|---|---|---|
| Testers (novice / intermediate / expert / motion) | 3 / 1 / 0 / 0 | 2 / 2 / 0 / 0 |
| Furthest progress | No netrun completed, T1 max, no Site claimed. nullpoint reached fight 4 on L4 with 0 deaths. saltlamp and tinroof each started 4 netruns, lost 3 operatives and played 1 raid. | No Site cleared, T1 max. saltlamp logged 2 netruns completed. neon_moth survived 2 raids. |
| Avg enjoyment (1–10) | 3.8 (n=4) | 3.0 (n=4) |
| Avg RNG fairness (1 fair – 5 cheated) | 3.2 (n=4) | 3.2 (n=4) |
| Bugs reported (deduplicated) | 27 raw → 8 | 28 raw → 10 |

## 2. Bugs (→ slice items; P1 = fix before the next gate, P2 = next slice)

| ID | Sev | Area | Bug | Testers | Repro (from the reports) | Evidence | Confidence |
|---|---|---|---|---|---|---|---|
| B1 | P1 | rules | UNDO will not revert cards staged after a turn-start random spin. It shows "nothing to undo; this turn began with a random spin", and the queued cards and RAM stay. The rule was never told to testers beforehand (nullpoint 18.1m). The design question is D7. Recurs PB-PT-002 B2. | ferrite, tinroof, nullpoint | 1. Start a turn that begins with a random spin. <br>2. Stage Jolt or Fine Tune. <br>3. Click UNDO, or press Z or ctrl+z. <br>4. The refusal appears and the card stays. <br>tinroof then took an unavoidable 12 HP hit and lost the operative. nullpoint clicked UNDO six times while marked LETHAL. | ferrite §7#2 0191 (4.4m, 28.2m, 38.1m), §2; tinroof §7#1 0138 (21.0–23.0m), §6; nullpoint §7#1 0251 (37.7–39.5m), confusion 18.1m | confirmed (the game shows the refusal; UNDO works elsewhere for ferrite) |
| B2 | P1 | combat | A selected or staged card cannot be cancelled. Esc opens the pause menu. Right-click, Z and RESPIN leave the aim or staged card in place, or clear it only sometimes, and clicks are swallowed while the aim is stuck. Recurs PB-PT-002 B1 and C4. | ferrite, tinroof, nullpoint | 1. Select or stage a card and enter aim. <br>2. Press Esc: the pause menu opens (nullpoint 6.9m, 23.8m, 34.0m, 38.3m; ferrite and tinroof §4). <br>3. Right-click, press Z, or RESPIN: the aim or card stays (ferrite 21–33m; tinroof 23.0–25.4m). | ferrite §7#3 0156, §2, §6 (about 10 min); tinroof §7#2 0156, §6; nullpoint §7#2 0161, §4 | confirmed |
| B3 | P1 | combat | With a card selected, clicks on the enemy wheel often show no response. Then the aim appears late, or Space is needed to commit. Recurs PB-PT-002 B1 (openloop) and B10 (saltlamp). | nullpoint, saltlamp | 1. Select Fine Tune, Jolt or Brute Spin. <br>2. Click the enemy wheel. <br>3. Nothing changes for several clicks, then the aim appears late (nullpoint 22.5–29.7m). Or nothing happens until Space (saltlamp 10.7–10.8m). | nullpoint §7#5 0189, §5 Q3; saltlamp §7#1 0074, §2 | confirmed (wheel clicks register for ferrite at 7.7m, so check latency and state, not only the input) |
| B4 | P2 | combat | The card selection jumps to a neighbouring card. It flipped between Jolt and Overdrive, and a right-click on Fine Tune selected Overdrive. This may be the overlapping hand hit areas (C2). | nullpoint | Click cards and the enemy wheel (8.2–9.7m). Right-click Fine Tune (6.8m). | nullpoint §7#3 0060, §7#4 0046 | single |
| B5 | P2 | combat | Preview readouts changed while the testers report no change of input: <br>• ferrite's Dispenser readout went 14→11, 14→8, 14→2, with the same LETHAL flag. <br>• tinroof's staged Jolt preview went 28→22, 28→16, 28→24. <br>• saltlamp: "previews kept shifting". <br>None was checked against a send. | ferrite, tinroof, saltlamp | Hold a staged card across several screens (ferrite 39–40m; tinroof Fight 2 turn 2; saltlamp 27.3m). | ferrite §7#5 0267, §2; tinroof §2; saltlamp §2 | unconfirmed (needs a replay check before any fix) |
| B6 | P2 | screens | After Quit to Main Menu and then CONTINUE, the restored fight state disagreed with ferrite's notes. It is unclear whether the save or the notes are wrong. | ferrite | Quit mid-fight, then Continue (45.3m). | ferrite §7#9 0303, §4 | single (check the replay) |
| B7 | P2 | combat | SEND IT stalled for several clicks on turn 9 of the third run's fight. This happened during an escalation, so it may relate to PB-PT-002 B8. | tinroof | 31.4–32.1m. | tinroof §7#4 0195, confusion 31.4m | single |
| B8 | P2 | screens | Single-tester ignored inputs: <br>• Tutorial 7/7 FINISH took no clicks; ferrite skipped the tutorial via the menu. <br>• Key 3 did not play Brute Spin; saltlamp suspects RAM. <br>• The HQ recruit click showed nothing until "Not enough Schematics" appeared later. <br>• Right-click on a wheel did nothing (tinroof). <br>• Z sometimes did nothing (ferrite). | ferrite, saltlamp, tinroof | As listed in each report. | ferrite §7#1 0011 (1.6–2.6m), §2; saltlamp §7#2 0133 (19.1m), §7#3 0119 (16.8–17.0m); tinroof §4 | unconfirmed-input (needs a human repeat) |

Excluded from this table:
- These go to playtest tooling:
  - ferrite's 36–56m escalation loop;
  - tinroof's escalation stall;
  - saltlamp §7#4, where the journal NOW block disagreed with the Crew tab.
- nullpoint §7#7 (Enter on a node starts the fight with no prompt) has no stated expected behaviour.
- These screen-audit items are cosmetic, and no tester tripped on them:
  - EXECUTE ghost text over SEND IT (ferrite §4, nullpoint §7#8);
  - CONTINUE over the PROCEED panel (nullpoint §7#8 0020).

## 3. Clarity and UX (→ slice items, ranked by how many testers it cost)

| ID | Area | Problem | Testers (of n) | Time lost / what resolved it | Evidence | Suggested direction |
|---|---|---|---|---|---|---|
| C1 | combat | Combat chips and tags are never explained: <br>• the RAM debt chips (-1, -2, -10) and the debt line; <br>• NULL, Corrupted and "Weak to Good"; <br>• Blocked/Guard and the enemy Resist number, which grey out Mirror Flip with no visible reason; <br>• damage chips, where ferrite read -24 as lethal to himself; <br>• what the enemy's Perfect marker does. <br>Recurs PB-PT-002 C2. | 4 of 4: ferrite, nullpoint, tinroof, saltlamp | ferrite: RAM debt never resolved (5.4–24m), Mirror Flip about 5 min, the -24 chip about 4 min (30.8–34.4m). <br>nullpoint: NULL about 1 min, via the PRECISION TAG tooltip; Corrupted never resolved. <br>tinroof: Guard and Resist never resolved. | ferrite §7#4 0048, §4, confusion 26.5m and 30.8m; nullpoint §2, confusion 6.4m and 37.2m; tinroof §2, confusion 20.0m; saltlamp §2, §4 | Add an in-place legend for chips and tags. Show why a card is greyed out on the card itself. Mark which side each damage chip hits. |
| C2 | combat | Card text is clipped and the hand overlaps: <br>• Mirror Flip reads "Blockev while th…" and Fine Tune is garbled. <br>• Neighbouring cards hide text. <br>• The raised Fine Tune covers the deck and discard counters, which are tiny anyway. <br>• The LETHAL tooltip covers the player wheel. <br>Ties to B4. Recurs PB-PT-002 C6. | 3 of 4: ferrite, nullpoint, saltlamp | Never resolved. | ferrite §2, §4, §7#6 0176; nullpoint §2, §4, §7#8 0241, §7#9 0246; saltlamp §2, §4 | Fit the full rules text on the card face. Keep the raised card clear of the stat row and piles. |
| C3 | combat | Nudge and FREE NUDGE are never defined: <br>• The arrows give no visible feedback. <br>• The Q/E/W hint was found only after many turns. <br>• The Codex has 214 entries and none for "nudge", so Nudge Driver means nothing. <br>• Jolt aims at the enemy wheel by default. <br>Recurs PB-PT-002 C3. | 3 of 4: nullpoint, tinroof, ferrite | nullpoint never resolved it (7.6–21.2m), plus about 5 min in the Codex (31.6–36.0m). tinroof never resolved it and blames it for the first death. ferrite resolved the Jolt default at 7.7m. | nullpoint §2, §4, confusion 7.6m and 31.6m; tinroof §2, §4, §6, confusion 2.2m and 6.5m; ferrite confusion 7.7m | Put a one-line definition on the FREE NUDGE banner and in the tutorial. Add a Codex entry. Make the needle move visibly, and show the default aim target. |
| C4 | city | Heat can't be predicted: <br>• The +11 on arrival, +11 per flatline and +5 per raid show only after the fact. <br>• The thresholds are vague. <br>• The tutorial's Heat and banking text is jargon. <br>Recurs PB-PT-002 C1 (not fixed). | 3 of 4: tinroof, saltlamp, nullpoint | Never resolved. | tinroof §3; saltlamp §3; nullpoint §3 | Show the Heat change before each action, and state what each threshold does. |
| C5 | city | The route map and campaign map are hard to read: <br>• CONFIRM stays greyed until the node itself is clicked. <br>• Labels sit far from their nodes, and tooltips stack over the site panel. <br>• Nodes are tiny and the legend icons look alike. <br>• The "L2" label does not match the sticker. <br>• The dossier jargon and the RACK tooltip are unclear. <br>Recurs PB-PT-002 C7. | 2 of 4: tinroof, saltlamp | saltlamp: about 2 min on RACK, resolved by committing. tinroof: CONFIRM resolved by clicking the node. | tinroof §3, §4, §7#3 0122; saltlamp §3, §4, §7#5 0154, confusion 33.0m | Make the route-panel selection enable CONFIRM. Anchor labels to their nodes. Use distinct legend icons. |
| C6 | screens | Abandon Run sits next to Resume and Quit, and Esc during combat opens this menu (B2). Recurs PB-PT-002 C5 (not fixed). | 2 of 4: ferrite, saltlamp | Avoided by both testers. | ferrite §4, §7#7 0281; saltlamp §4 | Separate Abandon Run from the other buttons and put it behind a confirm. |
| C7 | screens | Setup shows unlock costs ("UNLOCKS · 60/120") with no currency name and no balance. | 2 of 4: ferrite, nullpoint | Never resolved. | ferrite §3, §7#8 0021; nullpoint §3 | Name the currency, show the balance, and say how it is earned. |
| C8 | screens | Loot and Firmware picks give no confirmation and jump straight to the route map. One option was hidden behind the loot sheet. | 2 of 4: nullpoint, saltlamp | saltlamp: hidden from 12.7m to 32.0m. nullpoint never knew whether Patch+ and Nudge Driver applied. | nullpoint §4, §7#6 0107; saltlamp confusion 12.7m | Confirm the pick on screen, and keep all options visible. |

## 4. Balance and design signals (→ checkpoint items for the designer; never straight into tuning)

| ID | Signal | Testers | Evidence | Question for the designer |
|---|---|---|---|---|
| D1 | **Tester skill-limited.** There were 6 deaths, and saltlamp and tinroof called fights harsh. Ground truth: <br>• Perfect reachable on 91–100% of turns; landed on 15–21%, or 16–23% of reachable turns; doing nothing gives 13–25%. ferrite landed 20% against 25% for doing nothing. <br>• Testers acted on 27–47% of turns. <br>• They dealt 3.2–5.0 per turn against 14.7–20.1 for the best plan. <br>• They took 3.0–4.0 against 0.3–1.0 for the best plan and 2.5–3.8 for doing nothing. <br>No tester aligned for Perfects and still lost. Testers failed to read or do: <br>• the chips and tags (C1); <br>• the nudge and its default aim (C3); <br>• cancelling or undoing a staged card (B1, B2); <br>• committing an aim (B3). | ferrite, nullpoint, saltlamp, tinroof | Ground-truth table; Batch statistics | Observation only, no tuning question. Re-test after B1–B3, C1 and C3 land. |
| D2 | **Tester skill-limited (HP attrition).** HP carries over with no heal until run end, often into single-node layers: <br>• ferrite: at 1/60 through L2–L3, one fight node each. <br>• nullpoint: 23, then 8, then 2/60, single nodes on L3 and L4. <br>• saltlamp: entered L3 at 9/60, and had a Rack choice at 2/60. <br>• tinroof: entered fight 2 at 28/60. <br>Recurs PB-PT-002 D2. | ferrite, nullpoint, saltlamp, tinroof | ferrite §3; nullpoint §3; saltlamp §3, §6; tinroof §3, §5 Q1 | (A) Guarantee a heal or non-fight alternative on each layer. (B) Make the existing heal sources (Rack) readable. (C) As designed. |
| D3 | **Tester skill-limited (length).** <br>• Netruns were called too long ×4; the campaign too long ×3 and just right ×1, though nobody finished it. <br>• Fights ran 9–16 turns. ferrite's first fight took 16 turns (about 21 min). <br>• The tutorial ran 10–11 turns. <br>• saltlamp wants to skip the wheel resolve. <br>Testers dealt roughly a fifth to a third of best-plan damage. Recurs PB-PT-002 D3 and D7. | ferrite, nullpoint, saltlamp, tinroof | Batch statistics; saltlamp §3, §5 Q1–2; tinroof §3; ferrite §3; nullpoint §3 | (A) Re-judge length after B1–B3, with a tester who aligns. (B) Add a skip or speed option for the wheel resolve now, as a feel change. (C) Review the tutorial's repeated free-nudge turns. Which? |
| D4 | Card picks are mostly clarity-driven: <br>• Called OP: Brute Spin ×3, Fine Tune ×2, others ×1. But ferrite reported "none confirmed", tinroof and nullpoint "none seen", and nullpoint's op_picks just list what he took. <br>• Called weak: Jolt ×2 (default aim, and self-damage in the preview), Mirror Flip ×2 (greyed by resistance or Guard), Overdrive (corrupts the slice), Fine Tune (effect unreadable). <br>Recurs PB-PT-002 D4. | ferrite, nullpoint, saltlamp, tinroof | ferrite §2; nullpoint §2; saltlamp §2; tinroof §2 | For conditional cards: (A) offer them only when usable, (B) state the condition on the card face, or (C) as is? |
| D5 | **Tester skill-limited (Heat and raids).** Raids came only from flatline Heat: <br>• saltlamp and tinroof both reached 38. <br>• ferrite and nullpoint had 0 deaths and Heat stayed at 0, so no raid happened. <br>Both raids hit testers with nothing to deploy: <br>• saltlamp had an empty Armory; tinroof had no assets. <br>• Home went 50→38 and 50→40. <br>The testers recorded the result differently: saltlamp wrote 0 survived beside "CELL HOLDS", tinroof wrote 1 survived. This touches PB-PT-002 C11. Recurs PB-PT-002 D6. | saltlamp, tinroof | saltlamp §1, §3; tinroof §1, §3 | (A) Keep flatline Heat as the main early source, and prompt the player on what to deploy before a raid. (B) Ensure a deployable asset exists before the first raid can trigger. (C) As designed. |
| D6 | Economy: <br>• Schematics went unspent: tinroof held 20, later 10; Market items cost 10–20 and felt too tight to spend. <br>• A 15-cost recruit was refused with 5 Schematics (saltlamp). <br>• Cycles were wiped on loss (58), and tinroof ended at 21. <br>• A free rookie arrived after each death, so the PB-PT-002 B4 dead end was not reached. <br>Recurs PB-PT-002 D5. | tinroof, saltlamp | tinroof §1, §3, §5 Q2–3; saltlamp §3 | (A) Hold until a tester clears Sites. (B) Make the value of Market items readable. (C) Revisit how the free rookie and the paid recruit are presented. Which? |
| D7 | The UNDO random-spin rule (B1). 3 testers expected UNDO to revert cards staged after the spin, and tinroof lost an operative to it. | ferrite, tinroof, nullpoint | B1 evidence | (A) Allow UNDO back to the post-spin state. (B) Keep the block, and warn when a card is staged. (C) As is. |

## 5. Motion and feel (→ the animation pass queue)

No contact sheets or motion judgements came with this batch. The rows below come from the testers' own report remarks.

| ID | Moment | Verdict | Sheets | Problem |
|---|---|---|---|---|
| M1 | Per-turn wheel resolve | Too slow, wants a skip | none (report only) | saltlamp §4, §5 Q2. Ties to D3. |
| M2 | Hits on SEND IT | No sense of impact | none (report only) | saltlamp §4 and tinroof §4. Recurs PB-PT-002 M2. |
| M3 | Nudge and click commit | No or slow feedback | none (report only) | tinroof §4: the nudge arrows show nothing. nullpoint §4: commit feedback is weak or slow. Ties to B3 and C3. Recurs PB-PT-002 M3. |
| M4 | Iris wipe on a black screen | Wants a skip | none (report only) | saltlamp §5 Q2 (37.1m). |

## 6. What worked (keep)

- **Preview chips and HP previews:** all 4 testers (ferrite §4, nullpoint §2 and §6, saltlamp §4, tinroof §2 and §6).
  - nullpoint's favourite moment was the skull marker on a kill.
  - tinroof won the Billing Daemon fight by reading the previews.
- **Writing, death lines and look:** saltlamp liked the dying lines; nullpoint said the cyberpunk look is great.
- **Perfect finishes:**
  - ferrite: Brute Spin Perfect 12 on the Daemon, and a Perfect 6 on the Dispenser at 1 HP.
  - saltlamp: a 4-turn Dispenser kill.
- **Controls that worked:**
  - Space and Enter in combat (saltlamp).
  - Z in the tutorial (saltlamp).
  - Pause, then Resume, restored the fight state (nullpoint §5 Q2).
- **Raid setup was readable:** saltlamp and tinroof.
- **Clear wheel cues:** the Perfect and Good wheel labels, and the enemy intent display (tinroof).
- **Clear card text:** Jolt, Mirror Flip and the LETHAL tooltip (nullpoint).

## 7. Proposed actions

1. **Slice items:**
   - Bugs P1: B1, B2, B3.
   - Clarity, by tester count: C1, C2, C3, C4, C5, C6, C7, C8.
   - Bugs P2: B4, B7. B5 and B6 need a replay check first.
   - B8 needs a human repeat.
2. **Checkpoint items for the designer:**
   - D7: allow UNDO after the spin, warn on staging, or keep as is?
   - D2: guarantee a heal or alternative route, make the Rack readable, or keep as designed?
   - D3: re-judge length later, add a resolve skip now, or trim the tutorial?
   - D4: filter conditional cards, state the condition, or keep as is?
   - D5: prompt deployment before raids, guarantee an asset, or keep as designed?
   - D6: hold, make Market value readable, or rework how recruits are presented?
   - D1 is an observation only.
3. **Next batch:**
   - Re-run after B1–B3, C1 and C3 land, keeping the ground-truth replay table.
   - Give the raids focus a reachable raid. Use a tooling start from a save past the raid threshold, because ferrite's Heat stayed at 0.
   - Bring back a keyboard-only persona to check PB-PT-002 C8.
   - Watch for PB-PT-002 B3, B5 and B6, which were not reported this batch.
   - Route the escalation stalls and the journal NOW mismatch to playtest tooling.