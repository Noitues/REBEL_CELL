# Playtest feedback — nullpoint · PB-012 · build 19ad76a3a10c260a760667a0d6dde27156508740 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** nullpoint
- **Persona / focus / quirks:** Campaign strategist / Raids and cell defense / leftmost option when equal; UNDO to experiment (UNDO use is not recorded in the journal)
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 19ad76a3
- **Total playtime:** 14 minutes (85 actions, 1 session; the run started from a saved campaign at Heat 70)
- **Campaign setup:** corporation Solace Bio (seen on the raid notice), ICE not shown, home server variant not shown, starting roster Breaker (the roster showed Breaker 1–6 plus a recruited Breaker), campaign code not shown (save name: end_quietcarrier_181628)
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (out of time; INCOMPLETE, quit via the pause menu at time up)
  - Netruns: 2 started (one fight won before my part of the session, one lost), 1 completed in my part, 1 operative death (Breaker flatlined vs Billing Daemon, Router, layer 2)
  - Highest Site tier reached: T1 · Exploits held: 0 · Sites claimed at the end: not encountered
  - Raids: 1 survived (CELL HOLDS), 0 nodes lost
  - Final Heat: 86 (HUNTED, /100) · Home server integrity: 5/50
- **Overall enjoyment (1–10):** 4 — The raid layer had interesting levers, but the run collapsed fast and Heat relief was locked.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? I went in at 11 HP with Heat's +1 resistance on enemies. Turn 1 showed a lethal -11 preview, so it felt like a damage race I could not win. I tried Fine Tune, Hub Breach and Mirror Flip to dodge the lethal slice.
  - Did SEND IT ever give a different result from the preview chips? Not encountered.
  - Did UNDO / rewind behave as expected? Not encountered in the journal.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen.
  - Useless / never worth picking: Mirror Flip was refused twice on the Daemon's wheel with no message. The card text was truncated ("Blocked while th..."), so I guessed a lockdown hub. Mostly a clarity problem.
- **Synergies & archetypes:** Not enough played. I picked Patch+ over Barbed Wire for raw output.
- **Card text & clarity:** No. Card text is truncated, and OVFL, SPINNER, SHIM and DFRG are unexplained.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netrun not judged (the fight lasted about 5 turns); whole campaign not judged (INCOMPLETE).
- **Netrun map & encounters:** Route L2 offered two T1 fights paying 15–25 Cycles. Not enough seen to judge variety.
- **City Grid & HQ:** Site choices were not meaningful at Heat 86 because every Heat-relief site was locked behind another site. Wipe Biometrics needs Firmware Signing Office. Burn the Ledger needs Compliance Audit Bureau. Scrub Records needs Continuum Billing Farm. Purge Camera Logs needs Insurance Reconciliation Hub. Patch Distribution Node needs Patient Records Vault. After the wipe I recruited a Breaker for free, although the card said 15 Schematics and the wallet stayed at 7.
- **Heat:** I could not manage it. Heat went 70 to 81 on the flatline and 81 to 86 on the raid. I expected 80 to end the campaign, but it did not. The notice said "Heat 75" while the HUD said 81.
- **Raids:** Setup, projection and playout were understandable and matched (see section 5).
- **RNG & fairness (1–5):** 3 — the Daemon's lethal 7 slice at 4 HP was partly luck. I had one breather when its needle landed on its block slice.
- **Permadeath & meta-progression:** The death felt earned by low HP, but the wipe snowballed into a raid. Restart appeal not judged.

## 4. UI, controls & audio

- **Information in combat:** The preview showed lethal damage and "lands here" clearly. The "LANDS HERE" tag is cramped, and the Heat badge is clipped on the defeat screen (0052).
- **Information outside combat:** The raid dispatch dossier was clear and readable. I could not find which node is Continuum Billing Farm, because the map has no labels. HEAT SCRUB looks disabled and its cost is unclear. The ticker is clipped. The unlabeled "D 0" badge is unexplained. Home, Core, HQ and Integrity are used interchangeably.
- **Controls:** The Mirror Flip refusal gave no message. The loot screen shows blank cards in 0004 and a "chip taken" footer before any pick.
- **Visual feedback:** Not judged beyond the above.

## 5. Focus questions (Raids and cell defense)

1. **Did the projected outcome in setup match the result?** Yes. Setup projected CORE 34 → 5 HOLDS, and the result was Home -29 (34 to 5), exactly as projected. The earlier projection of 27 → 0 BREACHED was also consistent with a nearly defenseless cell.
2. **Did you understand why a node went DOWN or TAKEN?** Not encountered, because no node went DOWN or TAKEN. Only the CORE was targeted. The Heat +5 from Collector, Auditor, Enforcer and Lockdown was listed. "HOME -29" and "Reached home: 4" read as contradictory, and the banner still said "RAID IN PROGRESS" after "Raid over".
3. **Did raids feel like a puzzle you could solve, or a tax?** A tax. The armory was empty, so there was nothing to place, and all 4 units reached home. The one real lever was a 5-Schematic PATCH (+5 CORE integrity) that turned BREACHED into HOLDS, but it is only found by leaving setup and checking the Crew tab. Setup should point to it.

## 6. Open feedback

- **Favourite moment or build:** Patching 5 Schematics and watching the projection flip from BREACHED to HOLDS. It was the only moment where my planning mattered.
- **Biggest frustration / moment you wanted to quit:** Finding that all four Heat-relief sites were gated at Heat 86, with no way out.
- **One thing to change or add right now:** Surface levers such as PATCH inside Raid Setup. Also show why Heat-relief sites are locked, and label the prerequisite site on the map.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Loot sheet | 0.6m | Two readable chip cards | Blank white cards, footer says "chip taken // U" | wrong | 0004.png |
| 2 | Combat vs Daemon | 7.4m | Mirror Flip works or explains the refusal | Refused twice, no message, card text truncated | wrong | 0037.png |
| 3 | HQ Market | 10.5m | 15 Schematics deducted | Free recruit, wallet stayed at 7 | wrong | 0057.png |
| 4 | Raid playout | 11.5m | Banner reads raid over | "RAID IN PROGRESS" while the feed says "Raid over" | cosmetic | 0062.png |
| 5 | Raid notice | 10.3m | Heat matches HUD | Notice says Heat 75 while the HUD says 81 | cosmetic | 0055.png |
| 6 | Defeat screen | 10.0m | Legible Heat badge | Heat badge clipped and overlapped | cosmetic | 0052.png |
| 7 | HQ map | 12.8m | Prerequisite site identifiable | Billing Farm unlabeled; "DECRYPTED" stamp on an unreachable site | cosmetic | 0070.png |

**Confusion log:**
- 10.3m — HQ after the wipe — Heat 81 with the campaign still running, when I expected 80 to end it — resolved at 12.1m when the bar read /100.
- 10.7m — Raid Setup — nothing to place and a BREACHED verdict — resolved at 10.9m by finding PATCH in the Crew tab.
- 12.4–13.4m — HQ map — which Heat-relief site is reachable — about 1 minute checking four sites, none reachable.
- 7.4m — Combat — Mirror Flip refusal reason — unresolved.

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: nullpoint
persona: PB-012
focus: raids
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 1
operative_deaths: 1
raids_survived: 1
playtime_min: 14
enjoyment: 4
rng_fairness: 3
netrun_length: just right
campaign_length: just right
text_clear: no
op_picks: Patch+
weak_picks: Mirror Flip
bugs: 7
top_frustration: Every Heat-relief site was gated at Heat 86, and the raid offered nothing to place.
top_change: Surface PATCH and other levers inside Raid Setup, and show what unlocks each locked site.
```