# Playtest feedback — mothball · PB-011 · build 19ad76a3a10c260a760667a0d6dde27156508740 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** mothball
- **Persona / focus / quirks:** Keyboard-first player / Raids and cell defense / spends every Cycle at the first shop seen; rejects card rewards that don't fit the plan
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 19ad76a3a10c260a760667a0d6dde27156508740
- **Total playtime:** 45 minutes (352 actions, 1 session)
- **Campaign setup:** corporation Solace, ICE 0, home server Standard, starting roster Breaker (2 Breakers at start), campaign code RC1-solace-0-1-home_standard-breaker
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue: out of time (INCOMPLETE). Save & Quit confirm stopped responding at the end.
  - Netruns: 3 started, 0 completed, 3 operative deaths (Billing Daemon L1 fight, Collections Agent fight, Elite Claims Adjuster L3). The last two were on the Breaker 3 / new-recruit runs.
  - Highest Site tier reached: T1 · Exploits held: 0 · Sites claimed at the end: not encountered
  - Raids: 1 survived (CELL HOLDS), 0 nodes lost (DOWN / TAKEN)
  - Final Heat: 39 · Home server integrity: 40/50
- **Overall enjoyment (1–10):** 4 — the keyboard coverage in combat is good, but I flatlined three times and the campaign never got going.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Partly. Once I started reading the result chips before sending, I could steer a turn. Early on I mashed Space without reading and lost about 12 HP a turn.
  - Did SEND IT ever give a different result from the preview chips? Possibly once: in the Claims Adjuster elite fight, turn 7 (0258/0259), I sent on a -5 skull chip and flatlined. The journal does not confirm the preview was wrong, so I may have misread it.
  - Did UNDO / rewind behave as expected? Z is labelled on the button and works. It gets blocked after a random event or a respin; the respin message was clear (0225), the random-event one was not.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen.
  - Useless / never worth picking: none firmly identified. Siphon was refused ("does not fit a OVERFLOW slice") only after I clicked it (0212).
- **Synergies & archetypes:** Not enough runs to form an archetype. Cards I used were Jolt, Brute Spin, Fine Tune, Overdrive and Mirror Flip. No strategy came together.
- **Card text & clarity:** No. Card text is tiny and clipped (Mirror Flip "Blocked while th..."). RAM cost shows only as a "Not enough RAM" message, and Brute Spin turned out to need 2 RAM. A negative RAM readout like (-1) or (-2) beside 12/12 was never explained.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netruns ran about 5–10 min each. Whole campaign: not judged (INCOMPLETE).
- **Netrun map & encounters:** Fights, an event (Locked Ward) and an elite appeared. I could not tell node types apart on the map, and at 16 HP the only next node was an Elite.
- **City Grid & HQ:** Market let me buy Warm Cache first (my shop quirk). The CREW tab did not respond to clicks or keys when all Breakers were flatlined. A free Breaker recruit was hidden under MARKET.
- **Heat:** I could not predict it. Heat rose +11 per flatline and ended at 39.
- **Raids:** Understandable and fair; see section 5.
- **RNG & fairness (1–5):** 3 — the elite fight at 16 HP with no alternative route felt forced.
- **Permadeath & meta-progression:** Losing operatives felt earned in the first two fights. The third felt forced by the map. I never got to unlocks.

## 4. UI, controls & audio

- **Information in combat:** HP, wheels and result chips are readable. RAM, including the negative figure, is not explained, and the draw and discard piles were not examined.
- **Information outside combat:** The dossier HP is hidden by the AT LARGE stamp. The unlabeled purple "D 0" badge has no explanation. Node types on the map are hard to tell apart.
- **Controls:**
  - Keys that work: cards 1-5, Q/E nudges, Space for SEND IT, Z for undo, R for raid setup, H for Heat Scrub, Esc for the pause menu, and A/B in the quit dialog (hints shown).
  - Actions with no key, or a key not shown:
    - JACK IN, NEW CAMPAIGN, TUTORIAL, START and CONTINUE
    - route node selection
    - tutorial NEXT, FINISH and Skip
    - loot Continue and Skip
    - the firmware pick
    - the enemy-wheel nudge buttons (mouse-only)
    - HQ CREW, MARKET and DEFENCE tabs
    - START DEFENSE
    - raid playout Continue
    - raid report BACK TO THE GRID (ignored Enter and Esc)
    - pause-menu Abandon, Quit to Main Menu and Quit to Desktop
  - The SEND IT [Space] hint appeared inconsistently.
  - Event key 3 did not select Ghost past, so I used the mouse.
  - The Save & Quit confirm ignored A, Enter, B and the mouse for the last several minutes.
- **Visual feedback:** Not strongly judged. The result stamps are clear.

## 5. Focus questions (Raids and cell defense)

1. Did the projected outcome in setup match the result? Yes. Setup showed Core 50>40 HOLDS, and the playout ended Core 50>45>40 with HOLDS. The only surprise was the report's "Outcome: Failed" next to the "CELL HOLDS" stamp.
2. Did you understand why a node went DOWN or TAKEN? Not encountered. Only the Core took damage, and I had no assets or crew to place. Home went 50 to 40 and Heat went 34 to 39.
3. Did raids feel like a puzzle you could solve, or a tax? A tax in this session. With all Breakers flatlined and an empty armory there was nothing to place, so setup was only a projection I could not change. I never saw whether the puzzle exists with assets.

## 6. Open feedback

- **Favourite moment or build:** Winning the second Collections Agent fight entirely from the keyboard (0208).
- **Biggest frustration / moment you wanted to quit:** The raid report's BACK TO THE GRID ignoring Enter and Esc, and then the unresponsive Save & Quit.
- **One thing to change or add right now:** Add key hints and keyboard activation for every confirm, continue and back button, starting with the raid report, loot and route screens.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Quit confirm | 42.7–45m, pressed A, Enter, B, mouse | Save and quit | No response for many steps | blocker | 0310.png |
| 2 | HQ CREW tab | 24.3–24.7m, click, Enter, Tab | Open recruit panel | Nothing happened | wrong | 0180.png |
| 3 | Raid report | 37.5–39.5m | Enter or Esc leaves the report | Ignored both; mouse only | wrong | 0272.png |
| 4 | Combat RAM readout | 3.5m onward | Explained | (-1) / (-2) shown with no explanation | wrong | 0108.png |
| 5 | Raid report | 37.5m | Consistent outcome | "Outcome: Failed" beside the "CELL HOLDS" stamp | cosmetic | 0264.png |
| 6 | Event Locked Ward | 29.2m | Key 3 selects | No visible selection | wrong | 0216.png |
| 7 | Route and dossier | 0085/0217 | Max HP readable | AT LARGE stamp covers it | cosmetic | 0085.png |

**Confusion log:**
- 0.6m — title/HQ — pressing TUTORIAL landed on the HQ map, so I wasn't sure the tutorial ran — resolved by playing on.
- 12.9m onward — combat — what negative RAM costs — never resolved on screen.
- 24.2m — HQ — how to revive flatlined Breakers — about 0.6 min, resolved by finding the free recruit under MARKET.
- 38.2m — raid report — how to leave it by keyboard — about 1.3 min, resolved by clicking.

## 8. Summary

```
SUMMARY
handle: mothball
persona: PB-011
focus: raids
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 3
raids_survived: 1
playtime_min: 45
enjoyment: 4
rng_fairness: 3
netrun_length: just right
campaign_length: too long
text_clear: no
op_picks: none
weak_picks: none
bugs: 7
top_frustration: Many key actions have no key hint or ignore the keyboard (raid report, loot, route); Save & Quit froze at the end.
top_change: Add key hints and keyboard activation for every confirm, continue and back button.
```