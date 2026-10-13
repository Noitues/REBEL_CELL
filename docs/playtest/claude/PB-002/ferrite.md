# Playtest feedback — ferrite · PB-002 · build 19ad76a3a10c260a760667a0d6dde27156508740 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** ferrite
- **Persona / focus / quirks:** Roguelite newcomer / Bug hunting and edge cases / sticks with the same operative class (Breaker) all campaign
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 19ad76a3a10c260a760667a0d6dde27156508740
- **Total playtime:** 24 minutes wall-clock (185 steps, 257 actions, 1 session; I used Quit to Desktop at the end and never did Continue)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, home server Standard, starting roster Breaker. Campaign code shown in the pause menu: RC1-solace-0-1-home_standard-breaker.
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time, INCOMPLETE). I quit in fight 3 of the first netrun, turn 20 vs Triage Unit (10/45), at 8/60 HP.
  - Netruns: 1 started, 0 completed, 0 operative deaths
  - Highest Site tier reached: T1 · Exploits held: 0 (the map showed 0/3) · Sites claimed at the end: 0
  - Raids: not encountered
  - Final Heat: 0 (COOL) · Home server integrity: not shown
- **Overall enjoyment (1–10):** 4 — I like the look, but the rules went unexplained and I lost a lot of time to a stuck Jolt aim and a stalemate fight.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Only partly. The chips beside the HP bars helped me predict results, but I couldn't make sense of the "1 LANDS HERE" tag until turn 5 of the sim (0039.png). Even then I only guessed that it shows the slice landing at the pointer.
  - Did SEND IT ever give a different result from the preview chips? Not clearly. On fight 1 turn 2 I took 7 corrupted damage I hadn't understood in advance (0105.png). I can't say whether the preview showed it.
  - Did UNDO / rewind behave as expected? Mostly. Undo cleared a stuck Jolt aim and restored the hand (two Jolts and Mirror Flip) with RAM at 3/12 (0084.png). Turn 1 RAM later read 1/12 after more clicks.
- **Card balance & utility:**
  - Overpowered / automatic picks: Jolt and Brute Spin were my staple plays. Jam seemed to help a little (the enemy took -3 HP on turn 15, 0174.png). I can't call anything overpowered.
  - Useless / never worth picking: Mirror Flip. Its text is cut off and it needs 3 RAM. It is blocked against resistance, and I never got a use out of it. Overdrive scared me off because its tooltip says it corrupts after one trigger.
- **Synergies & archetypes:** I only ran Breaker. The deck felt like a random pile. I added Jam, Sanitize and the Firmware chip Patch+, but none of it came together against Triage Unit.
- **Card text & clarity:** No. Mirror Flip's text reads "Blocked while th..." and only the hover shows the rest (0088.png). Jolt's "spin a wheel" never says which wheel. The words nudge, spin, tick, ring, slice and wheel are never defined. "FREE NUDGE 1" in the header was never explained.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** the netrun was too long, because one fight stalled for 17+ turns (~8 min for fight 3 alone). Whole campaign: not finished, so I can't judge.
- **Netrun map & encounters:** I saw three fights in a row: Billing Daemon, Dosage Dispenser, Triage Unit. No heal option appeared at 26/60 or 17/60, which worried me. I saw no events, shops or racks.
- **City Grid & HQ:** I picked Continuum Billing Farm (T1). Jargon such as "Exploits 0/3" and "Heat COOL" was never explained. Recruiting, stationing and installing nodes: not encountered.
- **Heat:** Heat stayed at 0 (COOL) and I never saw it move.
- **Raids:** not encountered.
- **RNG & fairness (1–5):** 3 — Triage Unit healed +3 to +8 per turn and I sat at 17/60 for about ten turns with no heal available.
- **Permadeath & meta-progression:** not encountered.

## 4. UI, controls & audio

- **Information in combat:** The "LAST TURN: -10 HP" line and the outcome chips are good. HP and the enemy's HP are easy to see. The RAM debt number, e.g. "(-2)" next to 12/12, is never explained. The RAM hover only explains the bar. DECK and DISCARD labels are tiny and cut off.
- **Information outside combat:** On the map, the AT LARGE stamp covers the max HP value (it reads "26 /"). Node types are hard to tell apart. The Continue and Skip buttons on the loot sheet give no hint of what each does. On the victory screen the LOOT sticker covers the word PROCEED.
- **Controls:** Esc opens the pause menu and does not cancel a card aim. Clicks on my own Breaker wheel were never accepted while Jolt was aimed, and the aim kept snapping to the enemy wheel. The SEND IT / EXECUTE / turn_resolve.exe naming is inconsistent.
- **Visual feedback:** The wheel preview arrows and the "LANDS HERE" tag give real feedback, but the yellow aim lines cover the cards and HP. Hovered cards cover their neighbours.

## 5. Focus questions (Bug hunting and edge cases)

1. **List every bug with its exact steps (actions.log lines).** I only have my journal's time stamps, not the actions.log line numbers; see section 7 for the bugs with their times.
2. **Did Quit then Continue ever restore a different state from the one you left?** Not tested. I resumed from the pause menu twice (5.5m and 9.1m) and both times landed back in the same fight with the same aim. I used Quit to Main Menu once at 6.5m and Quit to Desktop at the end, and never pressed Continue.
3. **Did any input get lost or applied twice?** Lost: about a dozen clicks on my Breaker wheel in the sim (5.0–6.4m) and about 25 more in fight 1 (8.2–11.2m) did nothing. In fight 1 turn 1 RAM also dropped from 3/12 to 2/12 to 1/12 as I tried Jolt and Mirror Flip, with no visible wheel change. Applied twice: not seen.

## 6. Open feedback

- **Favourite moment or build:** Seeing the preview chips beside the HP bars before committing. The late turns where Triage Unit finally dropped to 7/45 (0178.png) were a close second.
- **Biggest frustration / moment you wanted to quit:** The Jolt aim that would not move to my own wheel, followed by a 17-turn stalemate against a healing enemy.
- **One thing to change or add right now:** Explain RAM debt and FREE NUDGE on screen. Also say on Jolt and Brute Spin which wheels they can target.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity (crash / blocker / wrong / cosmetic) | Shot |
|---|---|---|---|---|---|---|
| 1 | Training sim turn 6 | Select Jolt, click own Breaker wheel repeatedly (5.0–6.4m) | Jolt aims at my wheel | Aim stuck on the Collections Agent wheel; I left via the pause menu | wrong | 0053.png |
| 2 | Fight 1 turn 1 | Select Jolt, then Brute Spin, then Mirror Flip; click Breaker centre, segment and rim (8.2–11.2m) | Own wheel accepts the click | About 25 clicks produced no change; I used Undo and Send It instead | wrong | 0094.png |
| 3 | Fight 1 turn 1 | Mirror Flip selected, click Breaker wheel (10.8–10.9m) | No RAM spent without an effect | RAM read 1/12 and the wheels did not change | wrong | 0091.png |
| 4 | Training sim turn 5 | Esc after aiming Fine Tune (4.0–4.4m) | Esc clears the aim | The aim stayed until I reselected a card from the hand | wrong | 0037.png |
| 5 | Pause menu | Esc during a card aim (5.5m, 9.1m) | Esc cancels the aim | The pause menu opened | cosmetic | 0046.png |
| 6 | Hand cards | Hover Mirror Flip (10.3–10.5m) | Full text visible | "Blocked while th..." is cut off; the full text is only shown on hover | cosmetic | 0088.png |
| 7 | Victory screen | Fight 1 won (13.6m) | Readable PROCEED button | The LOOT sticker covers PROCEED; two DELETED stamps overlap | cosmetic | 0113.png |
| 8 | Route map | Dossier card (13.9m onward) | Max HP readable | The AT LARGE stamp hides the max HP ("26 /") | cosmetic | 0115.png |
| 9 | Fight 3 | Turns 4–20 vs Triage Unit | A way to make progress | Enemy healed +3 to +8 per turn; a long stalemate | wrong | 0160.png |

**Confusion log** (moments you did not know what to do):
- 0.5–1.0m — Tutorial 2/7 to 7/7 — dense jargon (wheel, nudge, hook, resistance) — the whole tutorial; nothing resolved it.
- 1.4–4.6m — Training sim — "1 LANDS HERE" tag — about 3 min; the dashed chevron path and the "8" tag on turn 5 made me guess it shows the landing slice.
- 5.0–6.4m — Training sim turn 6 — Jolt would not aim at my own wheel — about 1.5 min; gave up and left via the pause menu.
- 11.6–17.4m — Fights 1–3 — RAM "(-N)" debt and "FREE NUDGE 1" header — never resolved; the RAM hover at 17.4m only explained the bar.
- 13.8m — Loot sheet — whether Continue works before a pick — resolved by clicking.

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: ferrite
persona: PB-002
focus: bug-hunting-edge-cases
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 0
raids_survived: 0
playtime_min: 24
enjoyment: 4
rng_fairness: 3
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: Jolt, Brute Spin
weak_picks: Mirror Flip, Overdrive
bugs: 9
top_frustration: Jolt would not aim at my own wheel, and RAM debt and FREE NUDGE were never explained.
top_change: Explain RAM debt and FREE NUDGE on screen, and say which wheels each card can target.
```