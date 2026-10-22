# Playtest feedback — copperjack · PB-SOL-1 · build 52626bcd24d785a8dd7c75b213a52ea639892935 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** copperjack
- **Persona / focus / quirks:** Explorer / completionist, intermediate / City Grid, HQ and Heat / avoids Elite Routers, sticks with the same operative class (Breaker)
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 52626bcd24d785a8dd7c75b213a52ea639892935
- **Total playtime:** 18 minutes (238 actions, 2 sessions: quit to main menu and continued, twice)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, Standard home server, starting roster Breaker crew, campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: soft-lock. On the third node of the first netrun, a Respin left Undo refused and the Breaker at 5/60 HP with a LETHAL preview. I would not send into it.)
  - Netruns: 1 started, 0 completed, 0 operative deaths
  - Highest Site tier reached: T1 · Exploits held: not encountered · Sites claimed at the end: 0
  - Raids: not encountered
  - Final Heat: 0 · Home server integrity: not shown
- **Overall enjoyment (1–10):** 4 — The tutorial and the preview chips were nice, but I lost most of my time to laggy loot screens, an undo loop and a soft-lock.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Partly. Perfects felt earned, but the wheels re-spun every turn and took my good landings away (a Perfect 6 became a Weak 6 on turn 4 of the Billing Daemon fight). Jolt was poor value: two Jolts cost 10 RAM and moved the needle from a WEAK 12 to a GOOD 6.
  - Did SEND IT ever give a different result from the preview chips? No. The tutorial preview matched exactly.
  - Did UNDO / rewind behave as expected? No. I looped on undo for many minutes on Collections Agent turn 2. After a Respin, Undo was refused with a "random spin can't be undone" toast, so a staged lethal plan could not be cleared.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen.
  - Useless / never worth picking: Jolt (RAM-hungry for little movement) and Mirror Flip (3 RAM, dead in hand when I was low). Stacked Brute Spin drained RAM and left me at 5 HP.
- **Synergies & archetypes:** Breaker was barely tested. I took Nudge Driver, Sanitize and Patch+, but did not see a strategy come together in one fight and a half.
- **Card text & clarity:** Mostly yes. Fine Tune's aim was confusing: it kept defaulting to the enemy wheel, in the tutorial and in the netrun, and I had to click my own wheel to redirect it.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netrun not judged (never finished; the first two fights took ~3 and ~5 min); campaign not judged.
- **Netrun map & encounters:** I saw only Fights (Billing Daemon, Collections Agent, Dosage Dispenser). Nothing on the map offered a heal at 5/60 HP; only a Fight was available next. Other node types: not encountered.
- **City Grid & HQ:** I saw only the T1 site panel, which showed flatline Heat +11 and 2 sites opened. Recruiting, stationing, installing nodes and spending Schematics: not encountered.
- **Heat:** Heat stayed at 0 for the whole session. Predicting it: not encountered beyond the site panel's flatline number.
- **Raids:** not encountered.
- **RNG & fairness (1–5):** 4 — The wheels rerolled good landings, and then I was forced into a lethal fight at 5 HP with no heal.
- **Permadeath & meta-progression:** not encountered.

## 4. UI, controls & audio

- **Information in combat:** The preview chips are clear (LETHAL, skulls, HP changes). The tutorial box covered part of the wheels.
- **Information outside combat:** The route map is hard to read. Only one node shows a number although the help says to press numbers. The legend is hidden by the "Taken" toast. The D badge and FRONT 4.0 are unexplained. The view toggle is called both GRID VIEW and OVERVIEW.
- **Controls:** JACK IN ignored my first clicks. The loot sheet was dim and unresponsive until I pressed PROCEED. The pause menu puts Abandon Run next to Quit to Main Menu, and my first clicks on Quit did nothing. The Rewards confirm dialog ("Leave 1 reward(s) behind?" with BACK / PROCEED) is ambiguous.
- **Visual feedback:** Not much judged. Perfects were readable on the wheel.

## 5. Focus questions (City Grid, HQ and Heat)

1. Could you predict how much Heat an action would add or remove before doing it? Only partly: the site panel showed flatline Heat +11. Heat stayed 0 after my actions, so I never saw it change.
2. Did you ever feel stuck with no good Site to take? Not encountered at the grid. Inside the netrun I was stuck with only a Fight and no heal at 5 HP.
3. What did you spend Schematics on, and did it feel worth it? Not encountered.

## 6. Open feedback

- **Favourite moment or build:** The Perfect 12 on Collections Agent turn 1 and the Perfect 12 that finished it on turn 3.
- **Biggest frustration / moment you wanted to quit:** The Respin soft-lock on the Dosage Dispenser. Undo was dead, the lethal preview stayed, and quit and continue restored the same stuck state.
- **One thing to change or add right now:** Let Undo clear staged cards after a Respin, or refund the Respin. Also offer a way out (heal or retreat) when HP is too low to survive.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | L3 Dosage Dispenser turn 1 | Respin at 13.6m, then Undo/Z (13.9–17.9m) | Staged plan can be cleared | Undo refused after Respin, RAM stuck at 1/12 with debt, LETHAL preview stayed. Quit and continue restored the same state | blocker | 0162.png |
| 2 | Loot sheet after Billing Daemon | 7.7m | Card pick appears | Only CYCLES taken on a dim screen; clicks ignored until PROCEED | wrong | 0080.png |
| 3 | HQ T1 site | 3.9m | JACK IN responds | Several clicks ignored | wrong | 0044.png |
| 4 | Fine Tune aiming | tutorial 1.9m, netrun 5.9m and 15.6m | Aims at my wheel | Defaults to the enemy wheel | wrong | 0063.png |
| 5 | Route map | after firmware pick | Legend readable | Toast covers the legend; node numbers missing | cosmetic | 0128.png |
| 6 | Confirm Rewards dialog | 7.9m | Clear Yes/No | BACK / PROCEED ambiguous, "reward(s)" placeholder | cosmetic | 0082.png |
| 7 | Pause menu | 14.4m | Quit responds | First clicks on Quit ignored; Abandon Run placed right beside it | cosmetic | 0143.png |
| 8 | Collections Agent turn 2 | 9.4–11.5m | Undo clears cleanly | Long undo loop, the 13→5 preview kept returning | wrong | 0115.png |

**Confusion log:**
- 7.7m — loot sheet — dim screen with only Cycles shown — about 1 min, resolved by pressing PROCEED.
- 13.1m — route map at 5 HP — no heal visible, only a Fight — never resolved.
- 14.6m — blank ON AIR screen after Quit — unsure whether the run saved — about 0.2 min, the title then offered CONTINUE.

## 8. Summary

```
SUMMARY
handle: copperjack
persona: PB-SOL-1
focus: City Grid, HQ and Heat
build: 52626bcd24d785a8dd7c75b213a52ea639892935
outcome: ABANDONED
netruns_completed: 0
operative_deaths: 0
raids_survived: 0
playtime_min: 18
enjoyment: 4
rng_fairness: 4
netrun_length: just right
campaign_length: just right
text_clear: no
op_picks: none
weak_picks: Jolt, Mirror Flip
bugs: 8
top_frustration: Respin left Undo dead and a LETHAL preview on 5 HP, and quit/continue did not fix it
top_change: Let Undo clear staged cards after a Respin, and give a way out when HP is too low
```