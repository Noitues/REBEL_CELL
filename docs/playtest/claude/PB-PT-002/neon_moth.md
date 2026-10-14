# Playtest feedback — neon_moth · PB-PT-002 · build 52ba1e942fc6205fa97a705cb4c3171aafbbeae9 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** neon_moth
- **Persona / focus / quirks:** Keyboard-first player / Economy and difficulty curve / Quit to title and Continue once per session (done at 35.5m, 49.0m and 55.4m; the save held each time)
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
- **Total playtime:** 60 wall-clock minutes (449 actions; the game was quit to title and continued three times)
- **Campaign setup:** corporation Solace Biosystems, ICE not shown, home server standard (from the campaign code), starting roster not shown (code reads "RC1-solace-0-1-home_standard-breaker"), campaign code RC1-solace-0-1-home_standard-breaker
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time, INCOMPLETE at the 60-minute box, not the 4 hours in the brief)
  - Netruns: 5 started, 0 completed, 4 operative deaths (Breaker 1 at layer 3 Triage Unit fight; Breaker 2 at layer 3 Elite Recall Unit; Breaker 3 at layer 3 Elite Claims Adjuster; Breaker 4 at layer 2 Dosage Dispenser). The fifth netrun (Breaker 5) was still going at the end, at the layer 3 route map.
  - Highest Site tier reached: T1 (Continuum Billing Farm only) · Exploits held: 0 · Sites claimed at the end: not encountered
  - Raids: 2 survived (CELL HOLDS), 0 nodes lost (DOWN / TAKEN); Home fell 50 to 40 to 27
  - Final Heat: 58 (Flagged band) · Home server integrity: 27/50
- **Overall enjoyment (1–10):** 4 — The wheel combat was readable at times, but the HP drain, forced elites and mouse-only aiming made it a grind for a keyboard player.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Partly. E nudge and Space send worked well. Landing a Perfect was rare: I logged perfects=0 in almost every fight, and it was hard to tell where Jolt and Fine Tune would land without the dashed arc.
  - Did SEND IT ever give a different result from the preview chips? Possibly once. At 47.1m the Dosage Dispenser showed 0/38 DELETED, yet the fight was counted as a defeat (Breaker 4 at 7/60 flatlined). Both sides hit zero, so the preview and the verdict disagreed. Otherwise the previews matched what I saw.
  - Did UNDO / rewind behave as expected? Mixed. Z cleared stuck aims and stacked cards. Undo was often blocked after a respin, a Jolt, or a "random event" (27.4m, 40.3m, 42.0m), and RAM debt then stayed on screen.
- **Card balance & utility:**
  - Overpowered / automatic picks: Firewall (6 block) was the safe pick at low HP. Space-only plain sends with no cards often won fights by themselves.
  - Useless / never worth picking: Jolt and Fine Tune, which cost RAM and often did not land on the 12. Gear Shift and Ring Tap looked dead without an inner ring. Mirror Flip showed up at 3 HP with no real defence.
- **Synergies & archetypes:** No strategy came together. I picked defence and draw cards (Jam, Reroll, Firewall, Data Surge, Snap) and the deck felt like a random pile. Nothing built toward a plan.
- **Card text & clarity:** No. The Mirror Flip text was truncated ("Blocked while th..."). Cards overlapped in the hand. The tutorial paragraph was very long. The slice icons and "1/0" values went unexplained. Heat read 58 on the top bar but 0 in the payout panel, which was confusing.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netrun too long for what it gave back (~6–12 min per fight at this pace; the first netruns were over in 10–20 min because of deaths); whole campaign not finished. In 60 minutes I got through 5 netruns and 4 deaths.
- **Netrun map & encounters:** Layer 3 repeatedly offered only a single node: a Fight at 3 HP, then Elites at 13 HP and at 19 HP. Layer 2 sometimes had a heal Event (Wellness Kiosk) but also a Locked Ward trap. Nothing felt like a real choice.
- **City Grid & HQ:** Most Sites were locked behind other Sites. Only Continuum Billing Farm (T1) was open, and finding it on the map took a long time. Schematics went 20 to 5 on a recruit and stayed there.
- **Heat:** I could not predict it. Each flatline added roughly +11 Heat (11, 25, 42, 53). Raids added +5. Heat 30 crossed a threshold that cuts Mainframe items. The numbers climbed fast and were not explained.
- **Raids:** The setup and projection were understandable (Home 50 to 40 to 27, "HOLDS"). With no crew or armory they played out with nothing I could do. Fair only in the sense that I had nothing to defend with.
- **RNG & fairness (1–5):** 3 — The single-node forced Elites at 13 and 19 HP set the score. Some of that was my own entry at 3 HP.
- **Permadeath & meta-progression:** Losing an operative was earned at 3 HP (Breaker 1) and at the forced Elites. Four dead Breakers and a wiped wallet each time made me dread jacking in. No profile unlocks seen, so I had no pull to restart.

## 4. UI, controls & audio

- **Information in combat:** HP, RAM, the enemy wheel and the incoming preview were readable. The aim preview was weak, and I could not read where Jolt and Fine Tune would land without the arc. RAM debt tooltips were confusing. Draw and discard piles were not noted.
- **Information outside combat:** The HQ map did not make the orange-ringed starting Site obvious. It took about 5 minutes of clicks (30.3m to 35.9m) to select Continuum Billing Farm. Locked Sites give a gate message, which helped.
- **Controls:** Keyboard-only gaps, as listed:
  - Number keys select cards, but every aim needs a mouse click on a wheel.
  - Space (send), E (nudge) and Z (undo) work; Esc is shown on the pause menu.
  - No key shown, or none worked, for: route map node picks, loot picks and Continue, Firmware choice, JACK IN, START DEFENSE, BACK TO THE GRID, raid Continue, Market recruit, Save & quit, Continue and the other title buttons, and Quit to Desktop.
  - Event option 1 (Wellness Kiosk) and option 3 (Locked Ward) did not register by key.
  - There is no key to cancel a stuck aim; right-click and Esc did not clear it, and Z, a pause-menu open, or a wheel click did.
  - Abandon Run sits right beside Quit to Main Menu, which is risky.
- **Visual feedback:** Hits and block reads were fine. Perfects barely registered. The tutorial nudge box repeated every turn.

## 5. Focus questions (Economy and difficulty curve)

1. Where did difficulty spike, and where was it flat? — It spiked at layer 3 in every netrun: the Triage Unit fight at 3 HP, the Recall Unit Elite at 13/60 (106 HP, I lost with it at 85) and the Claims Adjuster Elite at 19/60. The first fight of the tutorial already took 42 HP. Layer 1 and 2 fights were milder (6 to 27 HP lost), with the Dosage Dispenser as an exception (60 HP lost). It was flat at the start of each run, where fights cost little before the HP bank ran dry.
2. Were shop prices fair for what you could afford? — Barely tested. The only Market item I used was a Breaker recruit at 15 Schematics, with 20 in hand. That left 5 and nothing else was affordable. At 5 Schematics I could not afford another. The Mainframe shops were not seen.
3. Was any resource always too scarce or always piling up unused? — HP and Schematics were always too scarce. HP rarely recovered; the only heals were +10 at a Wellness Kiosk and the Siphon Firmware. Schematics sat at 5 to 20. Cycles never piled up (18 to 42 per run), and a flatline wiped them. Heat only went up, from 0 to 58.

## 6. Open feedback

- **Favourite moment or build:** Winning the layer 2 Dosage Dispenser fight with Breaker 5 using plain Space sends, losing only 6 HP (57.7m).
- **Biggest frustration / moment you wanted to quit:** The stuck aim arc on the Recall Unit Elite (about 20.4m to 28.8m), when nothing but the pause menu or Z cleared it. Finding the starting Site on the HQ map was a close second.
- **One thing to change or add right now:** Give a key for aiming and cancelling a card, and show key hints on the route map, loot sheet, JACK IN and the HQ buttons.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity (crash / blocker / wrong / cosmetic) | Shot |
|---|---|---|---|---|---|---|
| 1 | Elite Recall Unit fight, turn 2 | 16.5m–17.9m: after escalation, keys, wheel clicks and Space did nothing | Input accepted | Screen unresponsive until the pause menu was opened and resumed | blocker | 0095.png |
| 2 | Card aim, Elite turn 8 | 20.4m–23.6m: Fine Tune arc stayed after right-click, Esc and Z | Aim cancels | Aim stuck; cleared only after the pause menu and a wheel click | wrong | 0136.png |
| 3 | Wellness Kiosk | 15.4m: key 1 | Option 1 chosen | No response; click worked | wrong | 0078.png |
| 4 | Locked Ward | 38.8m–38.9m: key 3, twice | Option 3 chosen | No response; click worked | wrong | 0249.png |
| 5 | Undo after Jolt, respin or random event | 27.4m, 40.3m, 42.0m | Undo works | Undo blocked, RAM debt stayed | wrong | 0257.png |
| 6 | Dosage Dispenser fight, turn 11 | 47.1m | Win, enemy 0/38 DELETED | Counted as a defeat | wrong | 0294.png |
| 7 | Loot payout panel | 38.2m, 54.0m | Heat matches the top bar | Panel read 0, bar read 30 and 58 | cosmetic | 0334.png |
| 8 | HQ map, Billing Farm | 30.3m–35.9m: clicks on several nodes | Starting Site easy to find | Took about 5 minutes of clicking | wrong | 0230.png |
| 9 | Escalation | 7.5m–28.4m: escalated about 10 times on lethal turns | A reply or hand-off | Never returned | wrong | 0049.png |

**Confusion log:**
- 5.3m — netrun fight screens — I thought the tutorial was replaying (the Dosage Dispenser and Triage Unit fights) — until 7.4m, when I realised they were real netrun fights.
- 8.5m — Triage Unit fight, turn 5 — I thought the game was stuck, but I had never pressed Send It — until 8.8m.
- 30.3m — Market recruit — I expected 0 Schematics after the wipe, but it cost 15 — resolved after the click (Schematics 20 to 5).
- 48.6m — Market recruit card — I expected it to be free or 0, but it read 15 Schematics — resolved by 49.2m, when Breaker 5 turned up ready.
- 58.4m–60.1m — Pause menu — about 40 attempts to finish the time box — resolved only with the in-game Save & Quit confirm at 60.2m.

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: neon_moth
persona: PB-PT-002
focus: economy_difficulty_curve
build: 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 4
raids_survived: 2
playtime_min: 60
enjoyment: 4
rng_fairness: 3
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: Firewall
weak_picks: Jolt, Fine Tune, Mirror Flip, Gear Shift
bugs: 9
top_frustration: Aiming needs a mouse and the arc gets stuck; forced low-HP elites after each flatline.
top_change: Add keys for aim and cancel, and show key hints on every button.
```