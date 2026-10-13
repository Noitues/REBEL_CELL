# Playtest feedback — gridlock · PB-010 · build 19ad76a3a10c260a760667a0d6dde27156508740 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** gridlock
- **Persona / focus / quirks:** Returning after a bad first try (novice) / City Grid, HQ and Heat / uses UNDO to experiment most turns; visits Terminals (events)
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 19ad76a3a10c260a760667a0d6dde27156508740
- **Total playtime:** 60 wall-clock minutes (820 actions, 1 session; the quit never completed, so the game was not exited)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, home server Standard, starting roster Breaker (four Breakers), campaign code shown in the pause menu as RC1-solace-0-1-home_standard-breaker
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (out of time). I never got past the first HQ visit, then spent the last ~35 minutes unable to take a second Site.
  - Netruns: 3 started, 0 completed, 3 operative deaths (all at Continuum Billing Farm, or its fight 4: Claims Adjuster at layer 4, Compliance Officer on the Terminal route, Collections Agent on the rebuild run)
  - Highest Site tier reached: T1 · Exploits held: 0 · Sites claimed at the end: 0
  - Raids: 0 survived (CELL HOLDS), 1 raid went through (Home 50→40), 0 nodes lost
  - Final Heat: 38 (NOTICED) · Home server integrity: 40/50
- **Overall enjoyment (1–10):** 3 — I couldn't read Heat, lost three Breakers, and then got lost on the grid.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Not really. The wheel readout was dense and I was mostly guessing at damage before committing.
  - Did SEND IT ever give a different result from the preview chips? Not clearly identified. Some hits were bigger than I expected, e.g. -12 then -18 vs Claims Adjuster, but I never compared them against the chips.
  - Did UNDO / rewind behave as expected? The tutorial said it is free and unlimited. In the later fights I logged several times that UNDO "did nothing visible".
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen.
  - Useless / never worth picking: Sanitize, because I couldn't find a CORRUPTED slice to target.
- **Synergies & archetypes:** Not enough time. The deck felt like a random pile, and I only played Breakers.
- **Card text & clarity:** No. The hand overlaps so badly that I clicked the wrong card, and descriptions are clipped (Overdrive, Mirror Flip, Fine Tune). Tooltips were readable when I hovered.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** Netruns ran about 3–10 minutes each. I didn't get far enough to judge the whole campaign.
- **Netrun map & encounters:** I saw Fight nodes, a Rack (+2 Heat on entry) and a Terminal route. I started towards the Terminal but died in a fight on the way, so I didn't reach any event.
- **City Grid & HQ:** Site choices looked meaningful, because tooltips name the type, difficulty, reward and prerequisite. In practice they were very hard to use. Locked state shows only on hover, nodes have no labels, and tooltips say "clear Continuum Billing Farm" without marking which node it is. I spent over 30 minutes clicking locked or wrong nodes. Recruiting costs 15 Schematics and I had 5, so I couldn't afford it.
- **Heat:** I could not predict it. Heat sat at 0 through my first fights, with nothing explaining why. It jumped +11 on each flatline and +5 in a raid. The Heat tooltip does give the thresholds and what is in force.
- **Raids:** The Raid Setup screen was readable: it showed 10 HP at stake and 1 of 4 crew ready. The playout log repeated "Step 1" lines, and the banner said in progress while the result said over.
- **RNG & fairness (1–5):** 4 — Claims Adjuster took me from 30 to 14 to dead in two turns, and I couldn't read the threat.
- **Permadeath & meta-progression:** Losing operatives felt harsh. At Heat 0 I started a fight at 30/60 HP, then entered a 112 HP enemy fight. That setup was my own doing, but it wasn't flagged. I didn't get to try profile unlocks.

## 4. UI, controls & audio

- **Information in combat:** Wheels, HP and RAM were visible, but the wheel icons and numbers had no legend. No per-card Heat was shown anywhere in combat.
- **Information outside combat:** I went looking for how to rest or revive flatlined Breakers and never found it. The MAP KEY is hidden behind a small top-right button. When I finally opened it, it covered the grid and blocked my clicks for a long time. The ON AIR ticker is cut off.
- **Controls:** Several inputs were ignored: the tutorial win banner had no Continue button (Esc was my way out), the Insurance Hub clicks did nothing, and the Quit confirm and QUIT TO DESKTOP never responded to clicks, A, Enter or Esc.
- **Visual feedback:** Not much to report beyond the wheel preview chips, which were readable once I knew to look.

## 5. Focus questions (City Grid, HQ and Heat)

1. Could you predict how much Heat an action would add or remove before doing it? — No. Only the Rack showed "+2 Heat on entry". Flatline +11 and the raid's +5 appeared only after the fact. Site tooltips say "Heat reduction" but never give a number.
2. Did you ever feel stuck with no good Site to take? — Yes. Heat-reduction Sites (Scrub Records, Purge Camera Logs, Wipe Biometrics, Burn the Ledger) were all locked behind other Sites. I couldn't tell which node was Continuum Billing Farm, so I lost about 35 minutes on the grid.
3. What did you spend Schematics on, and did it feel worth it? — Nothing. I held 5 against costs of 10–25: Heat Scrub 25, Recruit 15, boosts 10–20, Patch 5 (+5 integrity on CORE only). Spending them never felt possible.

## 6. Open feedback

- **Favourite moment or build:** The tutorial's chips-beside-HP preview and the Heat tooltip listing thresholds.
- **Biggest frustration / moment you wanted to quit:** The grid hunt for Continuum Billing Farm, with locked nodes, the stuck Map Key, and not being able to quit.
- **One thing to change or add right now:** Show Heat deltas on actions and Sites, label nodes and lock state on the grid, and fix the Quit buttons.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Tutorial win banner | 2.4–2.7m | Continue button | Clicks ignored; Esc opened pause | wrong | 0028.png |
| 2 | Combat UNDO | 5.2m, 6.6m | UNDO visibly reverts | Nothing visible | wrong | 0056.png |
| 3 | City Grid nodes | 27.7–30.4m | Click selects the node | Clicks ignored (some may have been wrong nodes) | wrong | 0271.png |
| 4 | Map Key | 36.2–38.0m | Closes on click or Esc | Wedged open over the grid, then collapsed by itself | wrong | 0394.png |
| 5 | Quit confirm / Quit to Desktop | 52.3–60.0m | Saves and quits | Ignored clicks, A, Enter and Esc; never exited | blocker | 0587.png |
| 6 | Raid playout | 25.3m | Clear steps | Repeated "Step 1" lines; banner says in progress while over | cosmetic | 0240.png |
| 7 | Grid tooltips | 31m onward | Readable tooltip | Tooltip hides the intel panel | cosmetic | 0266.png |

**Confusion log:**
- 2.4m — tutorial win — no Continue button — ~0.3 min, Esc
- 20.4m — flatline — Heat read 22, my notes said 11 — never resolved
- 21.0m — HQ after deaths — no way to rest or revive found — never resolved
- 27–50m — City Grid — which node unlocks which — ~35 min, only partly resolved by tooltips

## 8. Summary

```
SUMMARY
handle: gridlock
persona: PB-010
focus: City Grid, HQ and Heat
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 3
raids_survived: 0
playtime_min: 60
enjoyment: 3
rng_fairness: 4
netrun_length: just right
campaign_length: too long
text_clear: no
op_picks: none
weak_picks: Sanitize
bugs: 7
top_frustration: Heat and Site locks unreadable on the grid, and the quit flow never worked
top_change: Show Heat deltas on actions and Sites, label grid nodes and locks, fix Quit
```