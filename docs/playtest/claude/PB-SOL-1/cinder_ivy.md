# Playtest feedback — cinder_ivy · PB-SOL-1 · build 52626bcd24d785a8dd7c75b213a52ea639892935 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** cinder_ivy
- **Persona / focus / quirks:** Casual evening player / Bug hunting and edge cases / opens the pause menu at least once per netrun; tries a different class per netrun when possible (only Breaker was unlocked, so not possible)
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 52626bcd24d785a8dd7c75b213a52ea639892935
- **Total playtime:** 37 minutes (549 actions, 3 sessions: the game was quit to the main menu and continued twice)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, home server Standard, starting roster Breaker (the only unlocked class), campaign code RC1-solace-0-1-home_standard-breaker
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: suspected soft-lock on netrun T1, turn 1 vs Dosage Dispenser at 4/60 HP, RAM 0/12 with debt, LETHAL preview, UNDO refused)
  - Netruns: 1 started, 0 completed, 0 operative deaths
  - Highest Site tier reached: T1 · Exploits held: not encountered · Sites claimed at the end: 0
  - Raids: not encountered
  - Final Heat: 0 · Home server integrity: 50/50 (HQ screen)
- **Overall enjoyment (1–10):** 3 — the wheel idea is fun, but fighting the aim and the preview made it a slog, and I ended up stuck.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Sometimes. A clean Perfect 12 felt great (tutorial turn 6). Mostly I was fighting the targeting, not thinking.
  - Did SEND IT ever give a different result from the preview chips? Not clearly. The preview itself kept changing on the same setup (LETHAL 9→0 vs 9→7), so I couldn't tell which one to trust.
  - Did UNDO / rewind behave as expected? No. It often said "Nothing to undo" while cards were clearly staged. After a Respin it said "Nothing to undo since your RESPIN".
- **Card balance & utility:**
  - Overpowered / automatic picks: Patch+ firmware on the OVFL 12 slot felt good. Little else tested.
  - Useless / never worth picking: Inner Drift looked dead without an inner ring. Respin turned out to be a trap for me.
- **Synergies & archetypes:** Only Breaker was available. I took Nudge Driver and Reroll, but the deck never really came together before I got stuck.
- **Card text & clarity:** No. Cards overlap in the hand and the text is cut off. Overdrive left a "RAM -1" debt that nobody explained. The tutorial boxes were wordy.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** the one netrun I played was too long, with fights dragging to 10 turns (~30 min). Whole campaign: not encountered.
- **Netrun map & encounters:** I saw only Fights on the route map. The rest: not encountered.
- **City Grid & HQ:** HQ map and Jack In seen. Recruiting, stationing and spending Schematics: not encountered.
- **Heat:** stayed at 0 the whole time. Not tested.
- **Raids:** not encountered.
- **RNG & fairness (1–5):** 4 — I went into the third fight at 4/60 HP with a LETHAL preview on turn 1, so the run felt dead from the previous fight.
- **Permadeath & meta-progression:** not encountered.

## 4. UI, controls & audio

- **Information in combat:** wheels and pointers are readable once you get used to them. Outcome chips on SEND IT are nice. The hand overlaps, the EXECUTE/SEND IT label is covered, and the RESIST tag covers the enemy HP.
- **Information outside combat:** the route map and city map nodes are dim and unlabeled. "FRONT" and the purple "D 0" badge are unexplained.
- **Controls:** Esc did nothing on the HQ map but worked in a netrun. Clicks were often lost or slow: JACK IN took 3 clicks, LOOT took 2–3, loot CONTINUE took 3, and Quit to Main Menu needed a second try. Jolt and Fine Tune always default to the enemy wheel, and clicking my own wheel often did nothing.
- **Visual feedback:** a Perfect landing felt good. Otherwise the previews flicker too much to feel impactful.

## 5. Focus questions (Bug hunting and edge cases)

1. **List every bug with its exact steps** — see section 7 (times are from the journal).
2. **Did Quit then Continue ever restore a different state from the one you left?** Mostly the same state. On turn 9 the staged Brute Spin and Jolt came back, but the LETHAL preview was gone (HP 7→4). On turn 1 vs Dosage Dispenser the stuck state was restored with the debt intact. A few steps later RAM read 2/12 with FREE NUDGE 1, then dropped to 0/12 again after one nudge.
3. **Did any input get lost or applied twice?** Lost: JACK IN, LOOT, loot CONTINUE and Quit clicks needed repeats. Redirecting the aim to my own wheel was often ignored. The loot sheet auto-took Nudge Driver on an earlier click I didn't intend. Doubled: not clearly seen.

## 6. Open feedback

- **Favourite moment or build:** landing the Perfect 12 to finish the tutorial fight.
- **Biggest frustration / moment you wanted to quit:** turn 9 vs Collections Agent, about 20 clicks with a stuck aim and LETHAL flicker. The final turn-1 lock was worse.
- **One thing to change or add right now:** make aiming default to my own wheel and fix UNDO, so it always clears staged cards and never gets blocked by a Respin.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Netrun T1 turn 1 vs Dosage Dispenser | Respin at 4 HP (31.5–31.7m), then waited, nudged, Z and Quit/Continue (to 36.5m) | Way out of the turn | RAM debt, UNDO refused, LETHAL on 4 HP, only 0–1 RAM; soft-lock that survived Quit/Continue | blocker | 0304, 0345 |
| 2 | Combat, Undo | Tutorial turn 2 (2.6m), netrun turn 6, turn 7, turn 9 (15.6–26m) | Undo clears staged cards | "Nothing to undo" while cards were staged | wrong | 0028, 0244 |
| 3 | Combat preview | Turn 7 (18.4–22.6m), turn 9 | Stable preview | LETHAL 9→0 flipped with 9→7 on the same setup | wrong | 0183, 0240 |
| 4 | Aim targeting | Throughout, e.g. 8.1–11.0m | Click my own wheel to aim | Aim defaults to the enemy wheel and clicks are often ignored; turn 9 stuck ~20 tries, cleared only after Quit/Continue and the next turn | wrong | 0086, 0261 |
| 5 | Tutorial turn 3 | 2.7–4.8m | Explained self-hit | -11 self-hit preview with no visible cause | wrong | 0044 |
| 6 | Overdrive | Turn 3 (11.5m) | Clear cost | RAM -1 debt appeared unexplained and stayed | cosmetic | 0113 |
| 7 | Loot sheet | 12.3–12.7m | Pick on my click | Card auto-taken; slots faded; Continue needed multiple clicks | wrong | 0124 |
| 8 | Buttons | JACK IN (7.1m), LOOT (28.6m), loot CONTINUE (29.4m), Quit (35.4m) | Respond to the first click | Needed 2–3 clicks | wrong | 0074, 0274 |
| 9 | HQ map | 6.3m | Esc opens pause | Esc did nothing; MENU button works | cosmetic | 0066 |
| 10 | Layout | Combat, victory, other screens | Readable | EXECUTE/SEND IT and LOOT/PROCEED labels overlap; hand cards overlap | cosmetic | 0078, 0118 |

**Confusion log:**
- 2.2m — tutorial turn 2 — which card caused the -11 self-hit — unresolved.
- 8.1m — netrun fights — why Jolt and Fine Tune aim at the enemy wheel — I learned to click my own wheel, which often failed.
- 11.5m — turn 3 — the RAM -1 chip from Overdrive — unresolved.
- 31.5m — turn 1 vs Dispenser — what Respin does to Undo and debt — unresolved, I got stuck.

## 8. Summary

```
SUMMARY
handle: cinder_ivy
persona: PB-SOL-1
focus: bug hunting and edge cases
build: 52626bcd24d785a8dd7c75b213a52ea639892935
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 0
raids_survived: 0
playtime_min: 37
enjoyment: 3
rng_fairness: 4
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: Patch+
weak_picks: Inner Drift, Respin
bugs: 10
top_frustration: Aim kept snapping to the enemy wheel, Undo said "nothing to undo", and a Respin left me soft-locked at 4 HP.
top_change: Default aim to my own wheel and make Undo reliable, including after a Respin.
```