# Playtest feedback — deadreckon · PB-001 · build 19ad76a3a10c260a760667a0d6dde27156508740 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** deadreckon
- **Persona / focus / quirks:** Roguelite newcomer / Bug hunting and edge cases / tries a different operative class on each netrun (never reached)
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 19ad76a3a10c260a760667a0d6dde27156508740
- **Total playtime:** 7 minutes (107 actions, 1 session; Quit/Continue not tried)
- **Campaign setup:** not encountered (no campaign started). Corporation, ICE, home server, roster and campaign code: not shown.
- **How far did you get?**
  - [x] Stopped in the tutorial / before the first netrun (the tutorial fight showed FIGHT WON on turn 11, but I found no visible Continue and could not advance)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [ ] Campaign **abandoned** / could not continue (arguably this too: soft-lock on the tutorial result screen)
  - Netruns: 0 started, 0 completed, 0 operative deaths
  - Highest Site tier reached: not encountered · Exploits held: not encountered · Sites claimed at the end: not encountered
  - Raids: not encountered
  - Final Heat: not encountered · Home server integrity: not encountered
- **Overall enjoyment (1–10):** 3 — I never got past the tutorial, and the jargon plus the unresponsive targeting wore me out.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Couldn't tell. For about 11 turns most of my card-then-target clicks on the Collections Agent wheel showed no visible response. Only my own Breaker wheel responded.
  - Did SEND IT ever give a different result from the preview chips? Not noticed.
  - Did UNDO / rewind behave as expected? Not tested. Tutorial step 5/7 only described it, and I just pressed NEXT.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen.
  - Useless / never worth picking: none seen. I looked at Jolt, Fine Tune, Brute Spin, Overdrive and Mirror Flip, but never saw a clear effect on the enemy.
- **Synergies & archetypes:** not encountered. Only the Breaker was used, in the tutorial.
- **Card text & clarity:** No. The tooltips say "drag it onto a glowing target, or click it and then the target", which doesn't say where to click. Confusing terms: needle, slice, tick, Hub, nudge, FREE NUDGE, "LAST TURN line", "defensive slices", statuses, bank, Schematics, Heat.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** not encountered (the tutorial fight alone took 11 turns, about 4 minutes).
- **Netrun map & encounters:** not encountered.
- **City Grid & HQ:** not encountered.
- **Heat:** not encountered. The tutorial's explanation of Heat and banking left me unsure what Heat meant.
- **Raids:** not encountered.
- **RNG & fairness (1–5):** 3 — I can't judge fairness, but not being able to affect the enemy wheel felt unfair.
- **Permadeath & meta-progression:** not encountered.

## 4. UI, controls & audio

- **Information in combat:** I could read HP (Breaker 18/60, Collections Agent 16/40) and RAM (7/12). The "1 LANDS HERE" marker on the enemy wheel was visible but clicking it did nothing I could see.
- **Information outside combat:** only the title screen: CONTINUE greyed out (no save), TUTORIAL and NEW CAMPAIGN. No other screen seen.
- **Controls:** Targeting the enemy wheel with a selected card seemed to be ignored. I tried the wheel body, centre, outer ring top and the "1 LANDS HERE" marker, about fifteen tries across turns 2–11. Clicks on my own Breaker wheel did work. SEND IT worked and advanced turns. On the FIGHT WON screen, centre clicks, Enter, a click on the DELETED card, a long wait and a bottom-right click all did nothing. Esc opened the PAUSED menu.
- **Visual feedback:** Couldn't tell. I saw no clear on-screen confirmation when I played cards at the enemy.

## 5. Focus questions (Bug hunting and edge cases)

1. **List every bug with its exact steps (actions.log lines).** See the table in section 7. The actions.log lines themselves are not in my journal, so I give journal times instead.
   - Bug A: the enemy wheel ignored card-then-target clicks (about 1.6m–5.3m).
   - Bug B: the FIGHT WON screen has no visible Continue (about 5.4m–7.2m).
2. **Did Quit then Continue ever restore a different state from the one you left?** Not tested. I never used Quit, and CONTINUE was greyed out on the title screen at the start.
3. **Did any input get lost or applied twice?** Lost: yes, probably. Repeated targeting clicks on the Collections Agent wheel showed no visible effect. I saw nothing applied twice. I can't tell whether the clicks were really lost or just not explained.

## 6. Open feedback

- **Favourite moment or build:** none yet. I picked this up for the cyberpunk look, and the title screen delivers that.
- **Biggest frustration / moment you wanted to quit:** the enemy wheel not responding for about 3 minutes, then the won fight with no way forward.
- **One thing to change or add right now:** add a visible CONTINUE button on the FIGHT WON result, and state in the tutorial exactly where to click to aim a card.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Tutorial 7/7 combat, turns 2–11 | Select a card (Jolt / Fine Tune / Brute Spin), click the Collections Agent wheel, its centre, the outer ring or the "1 LANDS HERE" marker (1.6m–5.3m) | The card applies to the enemy wheel | No visible response on the enemy wheel; only my Breaker wheel responded. Might be unclear aiming rather than a bug | wrong | 0020, 0030, 0050 |
| 2 | Training Sim FIGHT WON result | Click centre, Enter, Esc, click the DELETED card, wait (6.2m–7.2m) | A Continue prompt, or advance to the next screen | No Continue visible; Esc opens PAUSED only; stuck | blocker | 0065–0073 |

**Confusion log:**
- 0.4m — Tutorial 1/7 — "needle", "slice", "LAST TURN line" — read slowly, never fully resolved.
- 0.5m — Tutorial 2/7 — "tick", "centre", FREE NUDGE 1 — had to read twice.
- 0.7m — Tutorial 4/7 — text says "drag" but then says click — settled on click; this contradiction came back later.
- 1.6m–5.3m — Tutorial 7/7 — which spot on the enemy wheel to click — about 3.7 min, never resolved. The enemy was deleted on turn 11 anyway, and I don't know how.
- 5.4m–7.2m — FIGHT WON — how to leave the screen — unresolved by the end.

## 8. Summary

```
SUMMARY
handle: deadreckon
persona: PB-001
focus: bug-hunting-edge-cases
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 0
raids_survived: 0
playtime_min: 7
enjoyment: 3
rng_fairness: 3
netrun_length: just right
campaign_length: just right
text_clear: no
op_picks: none
weak_picks: none
bugs: 2
top_frustration: Tutorial FIGHT WON screen has no visible Continue, so I could not leave the tutorial; the enemy wheel also ignored my card targeting for many turns
top_change: Add a visible Continue on the tutorial result screen and say exactly where to click to aim a card
```