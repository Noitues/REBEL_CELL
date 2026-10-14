# Playtest feedback — ferrite · PB-PT-003b · build 3eac0f086e6d32f23afd7c95dbb0e7eb35379339 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** ferrite
- **Persona / focus / quirks:** Explorer / completionist, intermediate / Raids and cell defense / uses UNDO to experiment on most turns
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard. Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 3eac0f08
- **Total playtime:** 60 minutes (648 actions, 2 sessions: I quit to the title and continued once, then quit again at the time limit)
- **Campaign setup:** corporation Solace Biosystems, ICE not noted, home server standard (home_standard), starting roster Breaker plus one other crew member (2 Breakers ready), campaign code RC1-solace-0-1-home_standard-breaker
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun
  - [ ] Campaign lost
  - [ ] Campaign won
  - [x] Campaign **abandoned** / could not continue (out of time). INCOMPLETE: stopped mid-fight on layer 3 (Triage Unit, turn 3), Breaker at 1/60 HP. The Quit to Main Menu save shows CONTINUE.
  - Netruns: 1 started, 0 completed. Two fights won (Billing Daemon, Dosage Dispenser), third fight unfinished. 0 operative deaths.
  - Highest Site tier reached: T1 · Exploits held: not encountered · Sites claimed at the end: 0
  - Raids: not encountered (Heat stayed at 0), so 0 survived and 0 nodes lost
  - Final Heat: 0 (COOL) · Home server integrity: 50/50 at the start; never changed afterwards
- **Overall enjoyment (1–10):** 4 — the wheel puzzle is interesting, but the Undo lockout, the unexplained RAM debt and a run stuck at 1 HP ate most of the hour.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Lining up the needle felt like skill when it worked. On the Billing Daemon, Brute Spin onto a Perfect 12 finished the fight (turn 16). Turn 6 preview (Fine Tune): Daemon 33→21, me 41→34.
  - SEND IT vs the preview: I did not log a mismatch I could prove. One oddity: at 1 HP on Dispenser turn 2, the Dispenser readout kept changing between screens (14→11, 14→8, 14→2) while the lethal flag stayed. I never checked it against a send.
  - UNDO did not behave as expected. On turns that begin with a random spin it refuses ("nothing to undo; this turn began with a random spin"). That is bad for someone who experiments every turn. Elsewhere it worked, but I burned a huge number of steps on undo loops. Z sometimes did nothing, and a stuck aim state needed right-click, Z and Esc, sometimes with no visible effect.
- **Card balance & utility:**
  - Overpowered / automatic picks: none confirmed. Brute Spin got my Perfect 12 on the kill, and a Fine Tune turn dealt 12 to the Daemon.
  - Useless: Jolt felt like a trap because its aim defaults to the enemy wheel. Mirror Flip is greyed out on a resisting enemy wheel and its text is truncated.
- **Synergies & archetypes:** I only ran the Breaker, with a small pile of Jolt, Fine Tune, Brute Spin and Mirror Flip, and added Jam and Patch+. No archetype came together in this short run.
- **Card text & clarity:** No. Mirror Flip text is cut off, Fine Tune text is garbled/clipped, and the RAM debt chips (-1, -2, -10) were never explained on screen. Hand cards overlap each other.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** The first fight took 16 turns (~21 min), which is too long. The whole campaign is not judged because I did not finish it.
- **Netrun map & encounters:** Only 3 fight nodes seen across layers 1-3, with no Terminals, shops or Racks. Layer 2 and 3 offered a single fight node each and no heal; the panel says only the run's end heals fully.
- **City Grid & HQ:** Only saw the HQ screen at campaign start (Schematics 20, Home 50/50, Crew 2). The rest is not encountered.
- **Heat:** Stayed at 0 (COOL). Not tested.
- **Raids:** Not encountered.
- **RNG & fairness (1–5):** 3 — the Dispenser's Perfect 6 on turn 1 took me from 7 HP to 1, and the random spin locked my Undo before I could react.
- **Permadeath & meta-progression:** Not encountered. The locked cards on the setup screen show "UNLOCKS · 60/120" with no currency explained.

## 4. UI, controls & audio

- **Information in combat:** HP previews and the enemy needle are easy to see. The RAM debt, the lethal chip and the -24 chip are hard to read: I misread the -24 as lethal to me when it was damage to the enemy. Deck/discard counters are tiny.
- **Information outside combat:** I could not find an explanation of the RAM debt or of the unlock currency.
- **Controls:** Aim mode swallowed clicks, and Z/right-click/Esc did not reliably cancel it. Esc opens the pause menu, where Abandon Run sits right next to Resume and Quit to Main Menu. Several of my notes disagreed with the screen after the quit and continue.
- **Visual feedback:** The preview overlays are informative. The SEND IT button is partly covered by a faded EXECUTE label.

## 5. Focus questions (Raids and cell defense)

1. Did the projected outcome in setup match the result? — Not encountered. No raid happened (Heat 0). For fights, the previews I sent matched in the cases I tracked.
2. Did you understand why a node went DOWN or TAKEN? — Not encountered.
3. Did raids feel like a puzzle you could solve, or a tax? — Not encountered. The only tax-like thing I saw was fight-side: the RAM debt and carry-over HP, which left me at 1/60 through layers 2 and 3.

## 6. Open feedback

- **Favourite moment or build:** Landing Brute Spin on a Perfect 12 to finish the Billing Daemon, and the Perfect 6 that finished the Dispenser at 1 HP.
- **Biggest frustration / moment you wanted to quit:** Turn 1 vs the Dispenser, where Undo was locked, the aim kept eating clicks, and I spent about 10 minutes unable to cancel queued cards. A second long stall followed at 1 HP.
- **One thing to change or add right now:** Make cancel reliable (right-click or Esc clears aim, Undo works for queued cards even after a random spin), and explain the RAM debt on screen.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Tutorial 7/7 | Clicked Finish repeatedly (1.6–2.6m) | Tutorial completes | Finish took no clicks; had to skip via the menu | blocker (for the tutorial) | 0011.png |
| 2 | Combat, random-spin turns | Undo (4.4m, 28.2m, 38.1m) | Undo reverts queued cards | "nothing to undo; this turn began with a random spin", queued cards stay | wrong | 0191.png |
| 3 | Aim mode | Right-click, Z, Esc (21–33m) | Aim cancels | Aim stuck, clicks swallowed | wrong | 0156.png |
| 4 | RAM debt chips | 5.4–24m | Explained cost | Debt chips (-1 to -10) never explained | wrong (clarity) | 0048.png |
| 5 | Dispenser turn 2 preview | 39–40m | Stable preview | Dispenser readout changed between screens (14→11, 14→8, 14→2) with the same lethal flag | wrong (unverified) | 0267.png |
| 6 | Card text | 0176.png | Full text | Mirror Flip "Blockev while th…" truncated, Fine Tune garbled | cosmetic | 0176.png |
| 7 | Pause menu | 42.2m | Safe layout | Abandon Run next to Resume and Quit | cosmetic | 0281.png |
| 8 | Setup screen | 0021.png | Unlock cost explained | "UNLOCKS · 120" with no currency or balance | cosmetic | 0021.png |
| 9 | After Quit and Continue | 45.3m | Notes and screen agree | Frame still showed turn 2 fight state | wrong (unclear) | 0303.png |

**Confusion log:**
- 4.4m — Combat turn 1 — Undo refused after the random spin — roughly 5 min, never resolved
- 5.4m — Turn 2 — RAM -1 chips and debt line — never resolved
- 7.7m — Jolt aim defaults to the enemy wheel — resolved by clicking my wheel
- 26.5m — Dispenser turn 1 — Mirror Flip greyed out — resolved after about 5 min (resistance)
- 30.8m — The -24 chip — I took it for lethal to me; corrected at 34.4m (it is enemy damage)
- 36–56m — Dispenser turn 2 at 1 HP — escalating and re-escalating without visible change — resolved when the enemy needle moved to a Weak 6

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: ferrite
persona: explorer-completionist
focus: raids-cell-defense
build: 3eac0f086e6d32f23afd7c95dbb0e7eb35379339
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 0
raids_survived: 0
playtime_min: 60
enjoyment: 4
rng_fairness: 3
netrun_length: too long
campaign_length: just right
text_clear: no
op_picks: Brute Spin, Fine Tune
weak_picks: Jolt, Mirror Flip
bugs: 9
top_frustration: Undo locked after random spins and aim mode that would not cancel
top_change: Make cancel and undo reliable and explain the RAM debt on screen
```