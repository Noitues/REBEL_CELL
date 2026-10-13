# Playtest feedback — rustbelt · PB-010 · build 19ad76a3a10c260a760667a0d6dde27156508740 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** rustbelt
- **Persona / focus / quirks:** Campaign strategist / Readability and accessibility / Hoards Cycles and Schematics; seeks Elite Routers when HP is above half (neither came into play)
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 19ad76a3a10c260a760667a0d6dde27156508740
- **Total playtime:** 151 minutes (2534 actions, 1 session)
- **Campaign setup:** corporation Solace Biosystems appeared selected, ICE 0, home server not confirmed, starting roster Breaker (the only unlocked crew), campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time). I never got past New Campaign setup because I could not find the START control. Scrolling at 2.0x text kept overshooting it.
  - Netruns: 0 started, 0 completed, 0 operative deaths
  - Highest Site tier reached: not encountered · Exploits held: not encountered · Sites claimed at the end: not encountered
  - Raids: not encountered
  - Final Heat: not encountered · Home server integrity: not encountered
- **Overall enjoyment (1–10):** 2 — I never reached gameplay, because the setup screen at the largest text scale fought me for 150 minutes.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Not encountered
  - Did SEND IT ever give a different result from the preview chips? Not encountered
  - Did UNDO / rewind behave as expected? Not encountered
- **Card balance & utility:**
  - Overpowered / automatic picks: not encountered
  - Useless / never worth picking: not encountered
- **Synergies & archetypes:** Not encountered
- **Card text & clarity:** Not encountered

## 3. Roguelite loop & campaign progression

- **Pacing & length:** not encountered
- **Netrun map & encounters:** not encountered
- **City Grid & HQ:** not encountered
- **Heat:** not encountered
- **Raids:** not encountered
- **RNG & fairness:** 1 — nothing to judge
- **Permadeath & meta-progression:** Not played. The locked crew, locked home servers and locked corporations show "UNLOCKS · 40/60/80" with no unit. The Profile panel teases "Something opens at ICE 10 everywhere (0/4)". As a campaign planner, I could not tell what currency I would be saving.

## 4. UI, controls & audio

- **Information in combat:** Not encountered
- **Information outside combat:** I looked for a START button on the setup screen and could not find it. I could not see where it was in the scrolled views. The setup page is long. Today's Run and Share Codes sit below the crew list. The city seed shows 1 while Today's Run shows seed 20261012, and nothing explains how the two relate.
- **Controls:** Scroll-wheel jumps were inconsistent at 2.0x and overshot repeatedly. The scrollbar is very thin. The only scroll cue is a "MORE BELOW" bar, which also covers content.
- **Visual feedback:** Not encountered

## 5. Focus questions (Readability and accessibility)

1. Which screens clipped or overlapped at the large text scale? — The Options Accessibility tab clipped. The REDUCE row label was cut off by the MORE BELOW bar, and the Subtitles description and the Heat glitch preview were sliced. On New Campaign setup, a tooltip about the locked Classified target overlapped the ICE row and a second tooltip, and the text underneath was garbled. The SELECTED tag sat over the top of the BREAKER and SOLACE names. The scrolled setup and menu pages cut text mid-line at the top and bottom: crew cards, Today's Run rows, the Share Codes text and the Profile // Records text. The pause menu had a peel-corner graphic over the "E" of RESUME.
2. Was anything hard to read against its background? — Yes. The footer text and controller hints on the main menu sit under the ticker bar. The [C] [X] [S] [O] [ESC] hints are small, dim grey. Locked crew portraits are dark on dark. Small hint text on the Options screen, such as the slider ticks and "saved to profile", is faint, and the tiny ON/OFF labels are too. The seed spinner arrows are tiny and dim. The SIMULATE sticker is hard to read.
3. Did any information rely on colour alone? — Mostly not, though some cases lean on it. Toggle states in Options are mainly fill colour plus knob position, with tiny labels. The pause menu's focused item is shown by yellow fill. The panel border colours (cyan versus pink) separate sections, but the headers carry text labels. The red outline and red dot on the Classified card are not explained beyond the lock icon and text. Locked versus selected cards use lock icons and a SELECTED tag, so those are fine.

## 6. Open feedback

- **Favourite moment or build:** Not encountered. The Accessibility options themselves are generous: a text scale slider from 1.0 to 2.0, colour-blind modes, high contrast and reduce effects.
- **Biggest frustration / moment you wanted to quit:** Spending the whole session scrolling the New Campaign setup page for START at 2.0x text, and overshooting it over and over.
- **One thing to change or add right now:** Pin START as a fixed footer on the setup screen, or put it near the top. Make scrolling land predictably at large text sizes.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | New Campaign setup | scroll at 2.0x (2.0m–151m) | Reach START predictably | Scroll overshoots, START not found | blocker | 0026.png, 2528.png |
| 2 | Options Accessibility | open at 2.0x (0.5m) | Rows fully visible | REDUCE row label clipped by MORE BELOW bar | cosmetic | 0004.png |
| 3 | New Campaign setup | hover Classified (0.7m) | One clear tooltip | Two overlapping tooltips over the ICE row | wrong | 0007.png |
| 4 | New Campaign setup | view ICE row and Classified card | Consistent ICE range | Label says ICE 0-3, card says "Opens at ICE 10" | wrong | 0007.png |
| 5 | Setup crew card | view Breaker | Name fully visible | SELECTED tag clips the name | cosmetic | 0568.png |
| 6 | Setup | view seed fields | Clear seed relationship | City seed 1 vs daily seed 20261012 unexplained | cosmetic | 0011.png |
| 7 | Pause menu | open at time up | Clean RESUME button | Peel-corner graphic covers the "E" | cosmetic | 2529.png |

**Confusion log:**
- 0.7m–151m — New Campaign setup — could not find START — the whole session; never resolved.
- 0.8m — setup lower — what Today's Run and Share Codes were for — not resolved.
- 0.9m — crew list — "UNLOCKS · 60/80" with no unit — not resolved.

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: rustbelt
persona: PB-010
focus: readability-accessibility
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 0
raids_survived: 0
playtime_min: 151
enjoyment: 2
rng_fairness: 1
netrun_length: just right
campaign_length: just right
text_clear: no
op_picks: none
weak_picks: none
bugs: 7
top_frustration: Could not find START on the New Campaign setup at 2.0x text; scrolling kept overshooting
top_change: Pin START as a fixed control and make scrolling predictable at large text scales
```