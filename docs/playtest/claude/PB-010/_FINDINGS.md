# Playtest findings — PB-010 · build 19ad76a3a10c260a760667a0d6dde27156508740 · 2026-10-12

> Synthesised from 8 Claude playtest reports, their screen audits and motion judgements
> (docs/process/05_CLAUDE_PLAYTESTER.md §9). Every finding names the testers who hit it and the
> evidence (report section, shot or contact sheet). Ingest per doc 04 §3: bugs and clarity items
> become slice items; balance and design items go to the checkpoint for the designer's ruling.

## 1. Headline

- **Nobody cleared a Site.** Testers played 661 minutes in total and logged 26 operative deaths. Seven sessions ended INCOMPLETE. One campaign was lost: halfmoon's home server was breached in a raid at Heat 80 with no crew left. Highest Site tier reached was T1 for everyone who got that far.
- **Finding a reachable Site on the City Grid was the biggest time sink.** It cost about 2.5 hours across 5 testers. Locked nodes gave no feedback, the prerequisite site was named but not marked, and the "orange ring" the panel points to was hard to see (C4).
- **Core combat rules never landed for the 6 testers who fought:**
  - the HP/RAM chips and the negative RAM readout;
  - nudge, Free Nudge and the Q/E buttons;
  - card text clipped on the card face.
  
  Testers describe guessing rather than aiming.
- **Several flows dead-end or stall:**
  - the tutorial FIGHT WON screen has no Continue (4 testers);
  - loot Continue is silently blocked by a firmware chip that doesn't fit the selected slot (4 testers);
  - Quit never responded for 2 testers.
- **The expert accessibility tester never reached gameplay.** rustbelt spent 151 minutes on New Campaign setup at 2.0× text and never found START.
- **All difficulty signals are tester skill-limited.** No FIGHT lines were logged this batch, and no report shows a tester aligning for Perfects. There is no previous batch to compare against.

| Metric | This batch | Previous (none) |
|---|---|---|
| Testers (novice / intermediate / expert / motion) | 3 / 3 / 1 / 1 | — |
| Furthest progress | No Site cleared. Most netruns: copperjack, 6 started, 5 ended in flatline. Campaign lost: halfmoon | — |
| Avg enjoyment (1–10) | 3.4 (n=8) | — |
| Avg RNG fairness (1 fair – 5 cheated) | 2.9 (n=7) | — |
| Bugs reported (deduplicated) | 69 raw → 15 | — |

## 2. Bugs (→ slice items; P1 = fix before the next gate, P2 = next slice)

| ID | Sev | Area | Bug | Testers | Repro (from the reports) | Evidence | Confidence |
|---|---|---|---|---|---|---|---|
| B1 | P1 | screens | The tutorial FIGHT WON screen has no Continue/Next. The only ways out are Esc→pause or Quit to Main Menu, and the tutorial never completes. | copperjack, ferrite, gridlock, halfmoon (audit also: quietcarrier 0036; neon_moth 0024, the sim loss screen has no prompt) | 1. Win the training sim fight. 2. Clicks, Enter, Space and the gear icon reveal no button. 3. Esc opens pause. | copperjack §7#8 0025; ferrite §7#1 0219; gridlock §7#1 0028; halfmoon §4; audits 0023, 0024, 0036 | confirmed |
| B2 | P1 | screens | Loot sheet Continue is blocked with no lasting explanation. A taken firmware chip that "does not fit an OVERFLOW slice" stops Continue. The error toast disappears in about 0.25 s. | copperjack, halfmoon, quietcarrier, byte_rat | 1. Win a fight. 2. Take an offered firmware chip (Siphon, Static Coat). 3. The OVERFLOW toast appears. 4. Continue does nothing until a different slot or firmware is chosen. | copperjack §7#2–3 0304/0305/0634/0635; halfmoon §7#4–5 0092/0452; quietcarrier §7#2 0665; byte_rat motion 0040 | confirmed |
| B3 | P1 | combat | Aim state sticks. A wheel-card aim is not cleared by Esc, Z or undo, and the RAM readout keeps a "(-1)"/"-2" reservation for several turns. | byte_rat, halfmoon, quietcarrier | 1. Select Fine Tune or Brute Spin and start an aim. 2. Press Esc or Z, or undo. 3. The aim line and RAM (-N) remain. byte_rat took about 15 steps to clear it. | halfmoon §7#3 0156, §6; quietcarrier §7#1 0050, §2; byte_rat §5, 0004/0021 | confirmed |
| B4 | P1 | combat | Clicking a wheel to target a selected card often does nothing. Number keys work. Once the aim jumped to the enemy ring and could not be retargeted. | copperjack, halfmoon, ferrite, byte_rat | 1. Select a wheel card. 2. Click a wheel. 3. The click is often ignored. Seen in the tutorial and in real fights. | copperjack §7#1 0021/0355; halfmoon §4, §7#3 0156; ferrite §4; byte_rat §5 | unconfirmed-input (needs a human repeat) |
| B5 | P1 | screens | Quit to Desktop and the Quit confirm ignore clicks, Enter, A and Esc. The game never exits. | gridlock, neon_moth | 1. Pause. 2. Quit to Desktop gets no response. 3. When the confirm dialog appears, QUIT ignores mouse and keys. Note: ferrite, copperjack and quietcarrier quit successfully, so look for a state dependency. | gridlock §7#5 0587; neon_moth §7#6–7 0657 | confirmed |
| B6 | P1 | rules | Undo is blocked after a random event ("a random event came since the last respin"), but the tutorial teaches undo as free and unlimited. Tutorial step 5/7 cannot be done as written. | copperjack, halfmoon, gridlock | 1. In a turn, trigger a random pick (e.g. Brute Spin). 2. Press Z. 3. Undo is blocked, or nothing visible happens. | copperjack §7#5 0343; halfmoon §7#2 0017; gridlock §2, §7#2 0056 | confirmed |
| B7 | P1 | city | The Map Key opens empty and needs a header click. Once it stayed wedged open over the grid, blocking clicks, then collapsed by itself. | quietcarrier, copperjack, gridlock | Open MAP KEY on the City Grid. The body is empty. | quietcarrier §7#9 0319; copperjack §3, audit 0277; gridlock §7#4 0394, audit 0413 | confirmed |
| B8 | P1 | screens | The raid result banner still says "RAID IN PROGRESS" after the feed says "Raid over". The playout log repeats "Step 1" lines. | gridlock, halfmoon, quietcarrier | Let a raid play out, then read the banner against the feed. | gridlock §7#6 0240; halfmoon §7#8 0218; quietcarrier §7#8 0220 | confirmed |
| B9 | P1 | screens | At 2.0× text, START on New Campaign setup cannot be reached. Scroll-wheel jumps overshoot it repeatedly. This blocked the whole session. | rustbelt | 1. Set text scale to 2.0. 2. Open New Campaign. 3. Scroll to find START. | rustbelt §7#1 0026/2528; audits 0568, 1003, 0023, 0010, 0601 | single |
| B10 | P2 | rules | A Patient Records event option presented as free ("Copy the index") leads straight into a fight. | quietcarrier | Patient Records Terminal → pick Copy the index. | quietcarrier §7#7 0697 | single |
| B11 | P2 | screens | Number keys pressed in combat carry into the loot sheet and auto-take a card or firmware. | halfmoon | Finish a fight while pressing number keys. A loot pick is taken. | halfmoon §7#4 0092 | single |
| B12 | P2 | screens | After JACK IN, a huge unlabelled segmented ring covers the map, the top HUD and the crew cards. | ferrite | JACK IN from the City Grid. | ferrite §7#7 0246 (audit: blocker) | single |
| B13 | P2 | screens | Tutorial Next has two problems. On a tutorial retry it is greyed and only Skip is live. On step 1 only Space advances; Enter and Tab+Enter do nothing. | neon_moth, halfmoon | Retry the tutorial (neon_moth), or press Enter on step 1/7 (halfmoon). | neon_moth §7#1 0030; halfmoon §7#1 0008 | single (Enter: unconfirmed-input) |
| B14 | P2 | screens | Single-tester ignored inputs: Esc in the training sim; right-click inspect on Jolt, Mirror Flip and the Q icon; Abandon-campaign CANCEL ignores the mouse (keyboard works); Crew-tab Breaker 5 card ignores 6–7 clicks. | ferrite, quietcarrier | As listed in each report. | ferrite §7#3–4 0131/0329; quietcarrier §7#4–5 0452/0459 | unconfirmed-input |
| B15 | P2 | combat | The hand and its number-key mapping changed between turns with no notice. | halfmoon | Combat, turns around 26.5–27.6 min. | halfmoon §7#10 0201 | single |

## 3. Clarity and UX (→ slice items, ranked by how many testers it cost)

| ID | Area | Problem | Testers (of n) | Time lost / what resolved it | Evidence | Suggested direction |
|---|---|---|---|---|---|---|
| C1 | combat | The chips beside HP/RAM, the "(-N)" RAM readout, the red HP tags, the slice icons and pointer numbers, and RESIST have no labels or legend. | 6 of 8: copperjack, ferrite, gridlock, halfmoon, neon_moth, quietcarrier | ferrite about 20 min. halfmoon never resolved it (about 70 min). The RAM-bar tooltip covers only positive use. | ferrite §4, §7#6 0355; halfmoon §5 Q2; neon_moth §7#5 0124; audits 0031, 0076, 0118, 0127, 0046 | Label each chip in place. Explain reserved/negative RAM where it is shown. Add a wheel-icon legend. |
| C2 | combat | Card rules text is clipped and the hand overlaps: Mirror Flip reads "Blocked while th…", Overdrive and Fine Tune are cut off, and the tooltip bar covers cards. This led to misclicks. Fine Tune also has a typo ("on on ring"). | 6 of 8: copperjack, ferrite, gridlock, halfmoon, neon_moth, quietcarrier | Never resolved. Hover tooltips helped some testers. | ferrite §7#5 0250; neon_moth §7#9 0061; gridlock §2; quietcarrier §2; audits 0030, 0014, 0034, 0106; loot text audits 0047, 0084 | Fit the full rules text on the card. Keep neighbouring cards from covering it. |
| C3 | city | Heat can't be predicted. No delta is shown before acting. Flatlines add +11/+12 and raids +5, shown only afterwards. No warning comes before the threshold-75 raid. Heat Scrub looks disabled with no reason given. | 6 of 8: copperjack, ferrite, gridlock, halfmoon, neon_moth, quietcarrier | Never resolved. The Heat tooltip thresholds helped gridlock. The Codex definition took neon_moth about 20 clicks to find. | gridlock §5 Q1; halfmoon §3; neon_moth §3; audits 0144, 0277, 0308, 0222 | Show the Heat delta on Sites, Racks and flatline. Warn before a threshold. Give the reason Heat Scrub is unavailable. |
| C4 | city | The City Grid hides which Site is reachable. Specific problems: <br>• Clicking a locked node gives no feedback. <br>• The prerequisite Site is named but not marked on the map. <br>• The "orange ring" and JACK IN are mentioned but not visible. <br>• Nodes have no labels. <br>• A DECRYPTED stamp appears on "Not reachable yet". | 5 of 8: copperjack, gridlock, neon_moth, quietcarrier, halfmoon | About 2.5 h in total: copperjack about 37 + 13 min, gridlock about 35, neon_moth about 43, quietcarrier 25+, halfmoon about 3 + 3. Resolved by the Map Key, orange rings on the edge, or panning the minimap. | neon_moth §7#3–4 0348/0349; gridlock §5 Q2, §7#3 0271; copperjack §7 confusion log; quietcarrier §3; audits 0404, 0414, 0172, 0161, 0207, 0257, 0154 | Show the lock reason on the node. Highlight or pan to the prerequisite. Draw gate links. Label nodes. Add a "next site" control. |
| C5 | combat | Nudge, Free Nudge, the Q/E buttons, ticks, SEND IT and CORRUPTED are never taught. Q/E take nudge cards, but players clicked them, or the wheels, and saw nothing happen. | 5 of 8: copperjack, ferrite, halfmoon, neon_moth, quietcarrier | copperjack learned it at about 96 min. quietcarrier about 10 min. ferrite about 13 min (Q-arrow tooltip). neon_moth lost the sim on turn 11. | copperjack §6; ferrite §5 Q1, §7#2 0067; quietcarrier §7#6 0334; neon_moth §7#2 0024; audits 0030, 0249 | Put the nudge rules in the tutorial. Give the Q/E buttons a visible state ("needs a nudge card / free nudge"). |
| C6 | city | No visible way to recover crew when all are flatlined. Recruit lives under Market and the Crew tab shows nothing. The panel says "rest at HQ" with no HQ or button. JACK IN looks active anyway. | 5 of 8: copperjack, gridlock, halfmoon, neon_moth, quietcarrier | quietcarrier about 0.5 min, found it in Market. gridlock never found it. neon_moth partly found it via the CORE panel. | copperjack §3, §7#7 0142/0382; gridlock confusion log 21.0m; audits 0140, 0377, 0136, 0437, 0209, 0631 | Add a recruit/recover action where the crew cards are. Disable JACK IN with the reason when no crew is available. |
| C7 | city | The netrun route map gives no "pick a node" prompt. The node numbers and the TARGET marker are unexplained. Node types differ by colour only. Links to RACK/SHOP are not drawn ("Fight > Fight"). The AT LARGE stamp hides max HP. A click shows info only and Enter travels. | 4 of 8: copperjack, ferrite, halfmoon, quietcarrier | ferrite never found the RACK. | ferrite §7#9 0548; halfmoon §7#7 0184; quietcarrier §4; audits 0107, 0075, 0029, 0303, 0281, 0637 | Add a prompt and confirm. Use distinct shapes per node type. Draw all links. Move the stamp off the HP value. |
| C8 | screens | Event choices need a second input that is never prompted. The first click or key only highlights, and the click and key behave inconsistently. | 4 of 8: copperjack, halfmoon, quietcarrier, byte_rat | Resolved by switching input (mouse ↔ key 1). | copperjack §7#6 0639; halfmoon §7#6 0178; quietcarrier §7#3 0152; byte_rat motion 0033 | Commit on the first input, or show an explicit Confirm. |
| C9 | city | Raid Setup allows START DEFENSE with 0 crew and gives no warning. Raid terms conflict: Core / Home / HP, CELL HOLDS beside "Outcome: Failed", INTERCEPTED beside "Stopped 0/3". The intercept message is truncated ("An Auditor has been …"). | 3 of 8: copperjack, halfmoon, quietcarrier | Raids were started undefended. Outcome text was unreadable. | copperjack §3; halfmoon §3; quietcarrier §3; audits 0378, 0445, 0141, 0138, 0139, 0241, 0377 | Warn on 0 crew. Use one term for the home server. Make the outcome wording match the stamp. |
| C10 | screens | The Codex has no search and lacks NUDGE, tick and RAM. It is reached only through MORE or pause. Cycles are never explained. | 2 of 8: ferrite, neon_moth | ferrite: 30+ steps per lookup, never found the terms. neon_moth: about 20 clicks to reach the Codex. | ferrite §5 Q1–2; neon_moth §4 | Add Codex search and a how-to-play page reachable from combat (ferrite's ask). |
| C11 | screens | The keyboard path has gaps. Many buttons show no key (JACK IN, loot Continue, BACK TO HQ, START DEFENSE, recruit, title menu). Wheel targeting has no keyboard step. The pause menu shows only [Esc], and ABANDON sits next to QUIT. | 2 of 8: halfmoon, copperjack | halfmoon fell back to the mouse repeatedly. | halfmoon §4, §6; copperjack §4 | Show key hints on every button. Add keyboard wheel targeting. |
| C12 | screens | Result screens have overlapping labels. The LOOT sticker covers PROCEED and JACK OUT covers PROCEED. End-turn has three names: SEND IT, EXECUTE and turn_resolve.exe. | 2 of 8: quietcarrier, halfmoon (audits in all 6 combat testers) | Space hint used instead. | quietcarrier §4; halfmoon §4; audits 0046, 0089, 0540, 0058, 0083, 0053, 0557, 0365 | Move the stickers off the button labels. Use one name for end-turn. |
| C13 | screens | Tutorial presentation problems. Step 1 is a dense wall of text that refers to a LAST TURN line not on screen. Next looks disabled. The win rule ("Bring its HP to 0") appears only after the win. Nothing says HP carries between fights. | 2 of 8: neon_moth, halfmoon (audit 0004 in 5 audits) | Not resolved within the tutorial. | neon_moth §3, §7#8 0083; halfmoon §5; audits 0004 | Break up step 1. Make Next look active. State the win rule and HP carry-over up front. |
| C14 | screens | Setup and menus have readability problems at 2.0× text: <br>• rows clipped by the MORE BELOW bar; <br>• overlapping tooltips; <br>• the SELECTED tag clips names; <br>• dim hints; <br>• unlock costs have no unit; <br>• "ICE 0-3" contradicts "Opens at ICE 10"; <br>• city seed 1 vs daily seed 20261012 is unexplained. | 1 of 8: rustbelt (unlock-unit also in audits 0238, 0032, 0054) | Never resolved. | rustbelt §5, §7#2–7 0004/0007/0568/0011/2529 | Pin START. Name the unlock currency. Reconcile the ICE range. Explain the seeds. |
| C15 | screens | The main menu BREACH / SIMULATE / OVERTHROW stickers sit beside buttons with different names. The lock on BREACH is unexplained. | 0 of 8 (audit only, all 8 audits) | — | audits 0002, 0003, 0005 | Tie each sticker to its button, or state what it is. |

## 4. Balance and design signals (→ checkpoint items for the designer; never straight into tuning)

| ID | Signal | Testers | Evidence | Question for the designer |
|---|---|---|---|---|
| D1 | **Tester skill-limited.** 26 deaths and 1 campaign loss (halfmoon, Heat 80 raid breach). No FIGHT lines, and no report shows aligning for Perfects. Testers failed to read or do: the chips and negative RAM (C1); nudge and Q/E (C5); HP carry-over and healing (C13); Heat thresholds (C3); crew before raids (C9). | byte_rat, copperjack, ferrite, gridlock, halfmoon, neon_moth, quietcarrier | Summary blocks; halfmoon §1 | Observation only, no tuning question. Re-test after C1/C5 land, with FIGHT lines logged. |
| D2 | **Tester skill-limited.** Long fights against resistance enemies: 10–30 turns. Examples: Recall Unit 30 turns; Triage Unit 15 turns, regenerating; a 1/0-slice stall; Billing Daemon 13–17 turns. Testers didn't know why Mirror Flip is "Blocked", or that nudge cards go on Q/E. | quietcarrier, copperjack, halfmoon, neon_moth | quietcarrier §2, §5 Q1; copperjack §3; halfmoon §2 | How should resistance counterplay be surfaced? (A) Explain it in the "Blocked" tooltip. (B) Show it on the enemy dossier. (C) Leave as is until a skilled tester confirms. |
| D3 | **Tester skill-limited (HP attrition).** Routes forced Elites at 14–23 HP with no heal. Testers never found a Terminal or healing, and arrived at the next fight at 2/60 HP. | copperjack, quietcarrier, halfmoon, neon_moth, ferrite | copperjack §3; quietcarrier §3; neon_moth §3 | (A) Guarantee a non-Elite alternative on each route. (B) Make HP-recovery nodes and HP carry-over visible. (C) As designed. |
| D4 | Weak-pick calls are mostly clarity-driven: <br>• Static Coat ×2 and Siphon: didn't fit OVERFLOW. <br>• Ring Tap: no inner ring. <br>• Sanitize: no CORRUPTED target. <br>• Mirror Flip ×2: resisted, or unaffordable at RAM 3. <br>• Overdrive: CORRUPTED scared the tester. <br>• Fine Tune: ±1 rarely mattered. <br>Called OP: Firewall ×1, Patch+ ×1. | copperjack, halfmoon, gridlock, ferrite, quietcarrier | copperjack §2, §5; gridlock §2; ferrite §2; quietcarrier §2 | Should conditional cards and firmware be (A) offered only when usable, (B) offered freely with the condition stated on the face, or (C) left as is? |
| D5 | Economy. Schematics were always scarce: testers held 5–20 against costs of 10–25. Heat only rose, and Heat Scrub was the only fix. Cycles were lost on death unspent. No tester cleared a Site, so Site income is untested. | gridlock, neon_moth, quietcarrier | gridlock §5 Q3; neon_moth §5 Q2–3; quietcarrier §3 | (A) Hold until a tester clears Sites. (B) Offer earlier or cheaper Heat relief. (C) Make the income route visible. Which? |
| D6 | **Tester skill-limited.** Flatline Heat drove the raids and the one campaign loss: +11/+12 per death, raid at 75. | halfmoon, copperjack, quietcarrier, gridlock | halfmoon §1, §3; copperjack §3 | Is flatline Heat intended as the main Heat source early on? (A) Yes, add a warning (C3). (B) Reduce its share. (C) Undecided until skilled play. |
| D7 | Campaign "too long" from 6 of 8, netrun "too long" from 3. The time went mostly to the Site hunt (C4) and long fights (D2). | 6 testers via Summary blocks | Batch statistics | Re-judge length after C4 is fixed? (A) Yes. (B) Probe now with a briefed tester. |

## 5. Motion and feel (→ the animation pass queue)

| ID | Moment | Verdict | Sheets | Problem |
|---|---|---|---|---|
| M1 | Card played / nudge | Hard to follow | 0003, 0004, 0007, 0008, 0021 | The card never visibly leaves or lands, and no numbers change. Fine Tune spends RAM with no visible effect until resolve. neon_moth also saw nudges show nothing until SEND IT (§2). |
| M2 | SEND IT resolution | Hard to follow | 0018, 0019, 0020 | Beams and particles overlap and damage numbers are tiny. The wheels change with no transition. It lasts 2.2–2.4 s. |
| M3 | Perfect hit | Clear but flat | 0018, 0019 | The PERFECT tag lingers and vanishes with no payoff. |
| M4 | Turn rollover | Glitch | 0006 | The header flips Turn 1 → 2 → 1 within 1.3 s. |
| M5 | Map → combat | Janky | 0017, 0030, 0024 | Hard cut to a dark frame with the UI but no background, then the background pops in. The click gets no acknowledgement for about 0.4 s. |
| M6 | Reward pick | Hard to follow | 0023, 0032, 0039, 0040 | Unchosen cards vanish and leave blank slots for about 0.5 s, then a hard cut. The error toast lasts about 0.25 s (ties to B2). |
| M7 | Enemy return strike | Hard to follow | 0019 | It arrives after a lull and feels disconnected from the player's hit. |
| M8 | Raid playout | Hard to follow | 0036, 0037 | Tiny low-contrast dots, a flickering icon and a pop-in CONTINUE. The stamp lands with no punch. |
| M9 | HQ arrival | Too slow | 0034 | About 0.7 s of dead "Connecting to HQ" hold, then the layout snaps into place. |
| M10 | Menu clicks, loot sheet, defeat | No animation seen | 0001, 0014, 0016, 0022, 0026, 0031 | No press feedback or entrance motion. The cause of each change can't be read. |

Testers wanted to skip these after seeing them twice:
- SEND IT resolve;
- the 4.8 s win finale;
- the HQ hold;
- the 5 s raid playout (byte_rat §3);
- the per-turn nudge and resolve phase over long fights (quietcarrier §5 Q2).

## 6. What worked (keep)

- **Preview arcs, chips and "1 LANDS HERE":** copperjack, ferrite, halfmoon, quietcarrier, gridlock, byte_rat.
- **Clear locked-site tooltips and the Heat-threshold tooltip:** halfmoon, gridlock.
- **Writing, tone, ticker and the Lexicon:** neon_moth. ferrite praised the look.
- **Terminal events with costs shown as chips:** quietcarrier.
- **The fight-won finale and the summary glitch-out:** byte_rat.
- **Free replacement recruits as a safety net:** copperjack, quietcarrier.
- **Saves:** they held across quit and continue (halfmoon), and "Your campaign is saved" reassured ferrite.
- **Plain on-screen permadeath explanation:** ferrite, halfmoon.
- **Readable Raid Setup:** gridlock, halfmoon.
- **Accessibility options:** text scale 1.0–2.0, colour-blind modes, high contrast and reduce effects (rustbelt).

## 7. Proposed actions

1. **Slice items:**
   - Bugs P1: B1, B2, B3, B4 (human repeat first), B5, B6, B7, B8, B9.
   - Clarity, by tester count: C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C14, C15.
   - Bugs P2: B10–B15 (B13 Enter and B14 need a human repeat first).
2. **Checkpoint items for the designer:**
   - D2: how to surface resistance counterplay.
   - D3: route guarantee vs visibility vs as designed.
   - D4: filter conditional offers vs state the condition vs as is.
   - D5: hold vs earlier Heat relief vs a visible income route.
   - D6: flatline Heat share.
   - D7: re-judge length after C4.
   - D1 is an observation only.
3. **Next batch:**
   - Re-run the same personas after B1–B9 and C1/C4/C5 land, with FIGHT lines logged so difficulty can be read.
   - Re-run rustbelt at 2.0× once B9 is fixed, and add an expert who reaches combat.
   - Brief one tester to clear Sites past T1, to probe the economy (D5).
   - Keep the keyboard-only persona to verify C11.
   - Get a human repeat of every unconfirmed-input item (B4, B13, B14).