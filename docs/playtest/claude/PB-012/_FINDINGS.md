# Playtest findings — PB-012 · build 19ad76a3a10c260a760667a0d6dde27156508740 · 2026-10-12

> Synthesised from 3 Claude playtest reports, their screen audits and motion judgements
> (docs/process/05_CLAUDE_PLAYTESTER.md §9). Every finding names the testers who hit it and the
> evidence (report section, shot or contact sheet). Ingest per doc 04 §3: bugs and clarity items
> become slice items; balance and design items go to the checkpoint for the designer's ruling.

## 1. Headline

- **This is the same build as PB-010 (19ad76a3).** Every recurring item below is still open, not a regression. Nothing can be marked fixed.
- **Nobody cleared a Site.**
  - The 3 testers played 66 minutes in total and logged 3 operative deaths. All 3 sessions ended INCOMPLETE.
  - Only nullpoint completed a netrun. He also survived a raid (CELL HOLDS, home 5/50, Heat 86).
  - The highest tier reached was T1.
- **Combat symbols were again the biggest time sink.**
  - lowtide spent about 9 minutes on the "1/0" Null slice (10.0–18.9m) and was stuck on it again at 24.1–25.5m.
  - Negative RAM "(-1)" was never resolved by lowtide or saltlamp.
  - Card text is clipped, and slot jargon (OVFL/SHIM/DFRG) is unexplained, for all 3 testers.
  - The "D 0" badge is unlabelled for all 3 testers.
- **The tutorial still dead-ends on FIGHT WON** with no Next (B1, recurring PB-010 B1). The raid banner still reads "RAID IN PROGRESS" after the raid ends (B4).
- **All difficulty signals are tester skill-limited.** The 7 fights produced 0.00 Perfects per turn. Testers entered fights at 11 HP, or with RAM and resistance rules they could not read.
- **Trend:** enjoyment is 3.7 vs 3.4 and RNG fairness 3.3 vs 2.9. Both comparisons rest on n=3 vs n=8, which is too small to call a change.

| Metric | This batch | Previous (PB-010) |
|---|---|---|
| Testers (novice / intermediate / expert / motion) | 1 / 1 / 1 / 0 | 3 / 3 / 1 / 1 |
| Furthest progress | No Site cleared. nullpoint completed 1 netrun and held 1 raid (CELL HOLDS, home 5/50, Heat 86). Highest tier T1 | No Site cleared. Most netruns: copperjack, 6 started. Campaign lost: halfmoon |
| Avg enjoyment (1–10) | 3.7 (n=3) | 3.4 (n=8) |
| Avg RNG fairness (1 fair – 5 cheated) | 3.3 (n=3) | 2.9 (n=7) |
| Bugs reported (deduplicated) | 18 raw → 10 | 69 raw → 15 |

## 2. Bugs (→ slice items; P1 = fix before the next gate, P2 = next slice)

| ID | Sev | Area | Bug | Testers | Repro (from the reports) | Evidence | Confidence |
|---|---|---|---|---|---|---|---|
| B1 | P1 | screens | The tutorial FIGHT WON banner has no Next or continue button. The only exit is Esc → pause → Quit to Main Menu. Recurring PB-010 B1. | lowtide (PB-010: copperjack, ferrite, gridlock, halfmoon) | 1. Win the tutorial sim fight. 2. Click the middle of the screen (6 times); no button appears. 3. Esc opens pause. | lowtide §5 Q1, §7#1 0077–0082 | confirmed (clean steps; 5 testers across both batches) |
| B2 | P1 | rules | UNDO greys out with a red "blocked" note after a random pick, with no prior warning. The tester relied on "free, unlimited UNDO". Recurring PB-010 B6. | lowtide (PB-010: copperjack, halfmoon, gridlock) | 1. In combat, trigger a random pick. 2. UNDO greys out and shows "blocked". | lowtide §2, §6, §7#5 0307 | confirmed (same steps as PB-010) |
| B3 | P1 | screens | On JACK IN, a giant pink/cyan ring covers the map and the left HUD. The "DEFENS…" label is clipped. Recurring PB-010 B12. | lowtide (PB-010: ferrite) | JACK IN from the City Grid. | lowtide §4, §7#6 0094; audit 0094 (blocker) | confirmed (2 testers across both batches) |
| B4 | P1 | screens | The raid banner still says "RAID IN PROGRESS" after the feed says "Raid over". Recurring PB-010 B8. | nullpoint (PB-010: gridlock, halfmoon, quietcarrier) | Let a raid play out, then compare the banner with the feed. | nullpoint §5 Q2, §7#4 0062; audit 0062 | confirmed |
| B5 | P2 | screens | The loot sheet shows two blank white cards. The footer already says "x1 FIRMWARE CHIP TAKEN // U" while PICK is still shown. | nullpoint | Win a fight and open the loot sheet (0.6m). | nullpoint §7#1 0004; audit 0004 (blocker: nothing to evaluate) | single |
| B6 | P2 | rules | The recruit card says 15 Schematics, but the recruit was free: the wallet read 7 before and after. Free replacement recruits were praised in PB-010 §6, so the price label may be the error. | nullpoint | After the crew wipe, recruit a Breaker in HQ Market. | nullpoint §3, §7#3 0057 | single |
| B7 | P2 | combat | On tutorial turn 2, Fine Tune is not in the hand (only Mirror Flip is), and clicks on the breaker ring do nothing. The turn advanced only after SEND IT, after about 2.5 minutes stalled. | lowtide | Tutorial, turn 2 (2.6–5.1m). | lowtide §7#2 0031–0060, confusion log | single (hand); ring clicks: unconfirmed-input (cf. PB-010 B4) |
| B8 | P2 | combat | The hand appeared to swap after a card was selected. The tester was unsure whether this was a bug. Possibly PB-010 B15. | lowtide | Combat, 8.9–9.2m. | lowtide §7#4 0098–0101 | single |
| B9 | P2 | combat | Mirror Flip was refused twice on the Billing Daemon's wheel with no message. The truncated text ("Blocked while th…") suggests a rule, not a fault (see C1). | nullpoint | Combat vs Billing Daemon, 7.4m: play Mirror Flip on the Daemon wheel. | nullpoint §2, §7#2 0037 | unconfirmed-input |
| B10 | P2 | screens | The first click on the UNDO button in the tutorial showed no response. The Z key worked. | lowtide | Tutorial, 0.7–0.8m: click UNDO. | lowtide §2, §7#3 0009–0010 | unconfirmed-input |

Every bug was hit by one tester in this batch. Because the build is unchanged, the severity of a recurring item counts the PB-010 testers who reported the same steps. Six raw entries are polish and moved to section 3: the AT LARGE stamp ×2, the LOOT sticker, the loot confirm flow, the Heat badge, and the Heat 75 vs 81 notice. Two more moved as well: the unlabelled prerequisite site went to section 3, and the forced Rack went to section 4.

## 3. Clarity and UX (→ slice items, ranked by how many testers it cost)

| ID | Area | Problem | Testers (of n) | Time lost / what resolved it | Evidence | Suggested direction |
|---|---|---|---|---|---|---|
| C1 | combat | Card text is clipped or too small to read: <br>• Mirror Flip reads "Blocked while th…" and Overdrive is cut off, with the hand overlapping it. <br>• Loot card text is tiny and thin. <br>• Fine Tune says "drag onto a target", but this setup uses click-then-target. <br>Recurring PB-010 C2. | 3 of 3: lowtide, nullpoint, saltlamp | Never resolved. nullpoint guessed at the Mirror Flip block (B9). | lowtide §2, §4; nullpoint §2, §7#2; saltlamp §2, §6; audits 0096, 0257, 0034, 0003 | Fit the full rules text on the card. Keep neighbouring cards from covering it. Match the wording to the input method. |
| C2 | combat | Slot and wheel jargon is unexplained: OVFL, SHIM, DFRG, SPINNER, NULL, "Slot 1: OVFL 12", "IF STATIONED (RAIDS)". It appears on the firmware drop panel and the dossier. | 3 of 3: nullpoint, saltlamp, lowtide (Firmware and dossier) | Never resolved. | nullpoint §2; saltlamp §2; lowtide §5 Q1; audits 0004, 0003, 0083, 0042, 0254 | Spell out each slot type on first use. Give each a hover definition. |
| C3 | screens | HUD counters and costs have no labels: the "D 0" badge, Exploits 0/3, and the unlock numbers ("UNLOCKS 120/40/60"), which name no currency. The tooltip says "Buy with Schematics" while the cards say "UNLOCKS". Partly recurring PB-010 C14. | 3 of 3: lowtide, nullpoint, saltlamp | "D 0" was never resolved by anyone. lowtide never resolved the unlock number (7.5m). | lowtide §3, §4, confusion log 7.5m; nullpoint §4; saltlamp §4; audits 0085 | Label every counter. Name the currency next to each cost and show the current balance. |
| C4 | combat | Combat readouts are unexplained: <br>• the "1/0" Null slice; <br>• negative RAM "(-1)"; <br>• CORRUPTED; <br>• the chips beside HP (-9, (8), +8, x1); <br>• the red badges. <br>Recurring PB-010 C1. | 2 of 3: lowtide, saltlamp | lowtide spent about 9 minutes on 1/0 and found the answer only in the pause-menu Codex (Slices tab). She stalled on 1/0 again at 24.1–25.5m. Negative RAM and CORRUPTED stayed unresolved for both testers. lowtide lost Breaker 1 to RAM overdraw. | lowtide §2, §5 Q2, confusion log; saltlamp §4, confusion log 8.3m; audits 0054, 0257 | Label the Null slice on the wheel. Explain negative RAM where it is shown. Add a legend for the chips. Put RAM in the first tutorial card (lowtide's ask). |
| C5 | combat | Tick, nudge, Free Nudge and the Q/E arrows are never taught. Recurring PB-010 C5. | 2 of 3: lowtide, saltlamp | lowtide never learned "tick" during the tutorial. saltlamp played "by feel". | lowtide §2, §5 Q1; saltlamp §2; audits 0054, 0096, 0097, 0257 | Define tick and nudge in the tutorial. Label the Q/E controls. |
| C6 | city | The netrun route map has several problems: <br>• no "pick a node" prompt; <br>• node-type icons are tiny and look alike against a busy background; <br>• the TARGET mark is unclear; <br>• the option string "[1] Rack +2 Heat > Elite fight · Event" is cryptic; <br>• the AT LARGE stamp hides max HP. <br>Recurring PB-010 C7. | 2 of 3: lowtide, saltlamp (audit also nullpoint 0005) | Not resolved. saltlamp searched for another node at 14.1m. | lowtide §3, §7#7 0254; saltlamp §3, §4, §7#2 0083; audits 0095, 0254, 0035, 0042, 0083, 0089, 0005 | Add a prompt and a confirm step. Give each node type a distinct shape. Move the stamp off the HP value. |
| C7 | screens | The loot and victory flow is unclear: <br>• it is not clear whether picking a card confirms it or Continue is needed; <br>• the difference between SKIP and CONTINUE is unexplained; <br>• the LOOT sticker covers PROCEED and JACK OUT covers PROCEED; <br>• the DELETED stamps overlap. <br>Recurring PB-010 C12. | 2 of 3: saltlamp, nullpoint | saltlamp clicked and it worked out (4.5m). | saltlamp §4, §7#1 0033, §7#4 0034; nullpoint §4; audits 0033, 0034, 0003, 0052 | Show an explicit confirm state. Move the stickers off the button labels. |
| C8 | city | The City Grid hides prerequisites: <br>• locked Heat-relief sites name a prerequisite that is not labelled on the map (Continuum Billing Farm); <br>• a DECRYPTED stamp sits on an unreachable site; <br>• "node", "OPENS 2 SITES" and "CAN BE YOUR NODE" are undefined. <br>Recurring PB-010 C4. | 2 of 3: nullpoint, lowtide | nullpoint spent about 1 minute checking four sites, none reachable. lowtide never resolved "node". | nullpoint §3, §7#7 0070, confusion log 12.4m; lowtide §3, confusion log 7.7m; audits 0070, 0084, 0064 | Show the gate chain on the node. Label or highlight the prerequisite site. |
| C9 | city | Heat is hard to read: <br>• the badge is clipped on the defeat screen; <br>• the raid notice says "Heat 75" while the HUD says 81 (possibly the trigger threshold, unlabelled); <br>• the /100 ceiling was unclear (nullpoint expected 80 to end the campaign); <br>• HEAT SCRUB looks disabled and its cost is hard to read; <br>• the map does not explain Heat. <br>Recurring PB-010 C3. | 2 of 3: nullpoint, lowtide | nullpoint resolved the ceiling about 2 minutes later (12.1m) when the bar showed /100. lowtide resolved Heat by hovering the bar. | nullpoint §3, §7#5 0055, §7#6 0052; lowtide §3; audits 0052, 0084, 0064 | Label the notice ("threshold 75"). Keep the Heat badge legible. Show the reason HEAT SCRUB is unavailable. |
| C10 | city | Raid Setup hides its levers and uses conflicting terms: <br>• PATCH is found only in the Crew tab; <br>• "Armory empty: runs bank assets from their drops" is cryptic; <br>• Home, Core, HQ and Integrity are used interchangeably; <br>• "HOME -29" conflicts with "Reached home: 4"; <br>• "Outcome: FAILED" sits beside "CELL HOLDS"; <br>• several action buttons compete with no priority. <br>Recurring PB-010 C9. | 1 of 3: nullpoint | Resolved in about 0.2 minutes by finding PATCH in the Crew tab. | nullpoint §4, §5 Q2–3, confusion log 10.7m; audits 0058, 0059, 0062, 0063 | Surface PATCH and other levers inside Raid Setup (nullpoint's ask). Use one term for the home server. |
| C11 | screens | Tutorial and turn controls are unclear: <br>• Next looks disabled while Skip looks active; <br>• the tutorial says to drag, but input is click-then-target; <br>• the EXECUTE label sits behind SEND IT. <br>Recurring PB-010 C13. | 1 of 3: lowtide | Not resolved in the tutorial. | lowtide §4; audit 0004 | Make Next look active. Match the instructions to the input method. Use one end-turn label. |
| C12 | city | When all six Breakers are FLATLINED, there is no visible Recruit or Rest button, yet JACK IN looks active. Recurring PB-010 C6. | 1 of 3: nullpoint (audit) | nullpoint recruited via HQ Market (see B6). | audit 0055 | Put the recover action on the crew cards. Disable JACK IN and show the reason. |
| C13 | screens | Main menu stickers BREACH / SIMULATE / OVERTHROW do not match the buttons beside them, and the lock on BREACH is unexplained. Recurring PB-010 C15. | 0 of 3 (audit only, lowtide) | — | audits 0002, 0003 (lowtide) | Tie each sticker to its button, or state what it is. |
| C14 | screens | A blank isometric grid screen appeared with no title, prompt or button. The tester did not report being stuck, so it is likely a load or transition frame. | 0 of 3 (audit only, nullpoint) | — | audit 0002 (nullpoint, blocker) | Check which screen this is. Add a loading label. |

## 4. Balance and design signals (→ checkpoint items for the designer; never straight into tuning)

| ID | Signal | Testers | Evidence | Question for the designer |
|---|---|---|---|---|
| D1 | **Tester skill-limited.** There were 3 deaths and 0.00 Perfects per turn in all 7 fights. lowtide lost Breaker 1 after a 13-turn Billing Daemon fight. nullpoint entered at 11 HP and died to a lethal slice. saltlamp died on turn 1 of a Rack at 11/60. What testers failed to read or do: <br>• negative RAM, the Null slice and CORRUPTED (C4); <br>• nudge (C5); <br>• the Mirror Flip block rule (C1, B9); <br>• Heat thresholds (C9). | lowtide, nullpoint, saltlamp | Combat skill table; lowtide §1, §6; nullpoint §1, §2; saltlamp §1 | Observation only, no tuning question. Re-test after C4 and C5 land. |
| D2 | **Tester skill-limited (HP attrition).** saltlamp reached layer 4 at 11/60 HP. Only a Rack was offered, also in Grid View, and saltlamp found no heal. saltlamp reports each layer offered one node, while lowtide saw three numbered next nodes (0095). | saltlamp (lowtide for contrast) | saltlamp §3, §7#3 0089; audits 0089, 0095 | Is a single-node layer intended? (A) Guarantee a choice on each layer. (B) Show HP-recovery options ahead on the route. (C) As designed. |
| D3 | Every Heat-relief site is gated behind another site. At Heat 86 none was reachable, and HEAT SCRUB costs 25 Schematics against 0–7 held. The Heat itself came from a flatline (+11) and a raid (+5), so it is partly skill-limited. Recurring PB-010 D5. | nullpoint | nullpoint §3, §6; audit 0084 | (A) Make one Heat-relief site ungated. (B) Keep the gates but make the chain visible (C8). (C) As designed. |
| D4 | The raid felt like "a tax". The armory was empty, nothing could be placed, and all 4 units reached home. PATCH was the only lever. The projection matched the result exactly (34 → 5 HOLDS). | nullpoint | nullpoint §5 Q1–3 | Should an early raid (A) always offer a placeable lever, (B) keep its current levers but surface them in setup (C10), or (C) stay as designed? |
| D5 | Card picks: <br>• called OP: Patch+ ×2 (a safe pick for the OVFL 12 slice), Respin ×1; <br>• called weak: Brute Spin ("a full lap on a 6-slice wheel") and Freeze; <br>• inner-ring cards looked dead on wheels without an inner ring; <br>• the Overdrive and Mirror Flip calls were clarity-driven (C4, C1). <br>Recurring PB-010 D4. | saltlamp, nullpoint, lowtide | saltlamp §2, §5; nullpoint §2; lowtide §2 | Should Brute Spin's lap behaviour on 6-slice wheels be (A) as designed, (B) stated on the card, or (C) reconsidered? Should cards that need an inner ring be (A) offered only when usable or (B) offered with the condition stated on the card? |
| D6 | Netrun was called "too long" by 2 testers and the campaign by 1. lowtide's netrun included clarity stalls (C4). saltlamp's 17-minute netrun included the tutorial fight. | lowtide, saltlamp | Batch statistics; lowtide §3; saltlamp §3 | Re-judge length after C4 and C5 land? (A) Yes. (B) Probe now with a briefed tester. |

## 5. Motion and feel (→ the animation pass queue)

| ID | Moment | Verdict | Sheets | Problem |
|---|---|---|---|---|
| — | No motion tester or contact sheets this batch | Not judged | — | PB-010 M1–M10 remain open on this build. B3 (the JACK IN ring) overlaps with PB-010 M5 (map → combat). |

## 6. What worked (keep)

- **The SEND IT preview and the "1 LANDS HERE" arrow:** lowtide, nullpoint and saltlamp. Testers said it gives exact damage, shows lethal clearly, and "felt trustworthy".
- **Raid projection matching the result exactly,** and a readable dispatch dossier. Flipping BREACHED to HOLDS with PATCH was the high point (nullpoint).
- **Hover tooltips** for SEND IT, UNDO, RAM and Heat taught lowtide the most. The Codex Slices tab explained NULL once she found it.
- **Free UNDO for experimenting** (lowtide), but see B2.
- **Respin onto the 12 slice to beat the Triage Unit's heal.** The healing was readable (saltlamp).

## 7. Proposed actions

1. **Slice items:**
   - Bugs P1: B1, B2, B3, B4.
   - Clarity, by tester count: C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C14.
   - Bugs P2: B5, B6, B7, B8. B9 and B10, and the ring-click part of B7, need a human repeat first.
2. **Checkpoint items for the designer:**
   - D2: single-node layers. (A) guarantee a choice, (B) show recovery ahead, or (C) as designed?
   - D3: Heat-relief gating. (A) one ungated site, (B) visible chain, or (C) as designed?
   - D4: early raid levers. (A) always placeable, (B) surface the existing levers, or (C) as designed?
   - D5: Brute Spin on 6-slice wheels, and offers of inner-ring cards.
   - D6: re-judge length after C4 and C5.
   - D1 is an observation only.
3. **Next batch:**
   - Run it on a build that carries PB-010 and PB-012 fixes. A third run on 19ad76a3 would only re-confirm.
   - Keep FIGHT lines with Perfects logged.
   - Brief one tester to align for Perfects, so difficulty can be read.
   - Add back a motion tester.
   - Give the raid persona a save with armory assets to test D4.
   - Get a human repeat of B7 (ring clicks), B9 and B10.