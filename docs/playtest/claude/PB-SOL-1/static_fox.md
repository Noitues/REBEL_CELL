# Playtest feedback — static_fox · PB-SOL-1 · build 52626bcd24d785a8dd7c75b213a52ea639892935 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** static_fox
- **Persona / focus / quirks:** Min-maxer / Pacing and session length / right-click new cards and icons before using them
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 52626bcd24d785a8dd7c75b213a52ea639892935
- **Total playtime:** 104 wall-clock minutes (780 actions, 1407 steps; the game was quit once at the time limit)
- **Campaign setup:** corporation Solace, ICE 0, home server Standard, starting roster Breaker, campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time, INCOMPLETE; I was in netrun 4, in an elite fight at turn 3 at 4/60 HP)
  - Netruns: 4 started, 0 completed, 3 operative deaths (Breaker 1 in a layer-2 fight vs Collections Agent; Breaker 2 in a layer-2 fight vs Recall Unit; Breaker 3 in a layer-3 fight vs Claims Adjuster). Breaker 4 was still alive when I quit.
  - Highest Site tier reached: T1 · Exploits held: not encountered (the map showed 0/3) · Sites claimed at the end: not encountered
  - Raids: 1 survived (CELL HOLDS; Home 50>40, Heat 25>30), 0 nodes lost
  - Final Heat: 43 (Noticed) · Home server integrity: 40/50
- **Overall enjoyment (1–10):** 3 — the fights are long, drawn-out slogs and the route forces fights at near-zero HP, so I never got to run a build.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Partly. Staging Brute Spin and Jolt to dodge a lethal slice was a real puzzle (turn 2 vs Claims Adjuster: two Brute Spins moved the enemy needle off Perfect 16 onto its 8 block slice). But at low HP it turned into repeated re-rolling of the same lethal preview.
  - Did SEND IT ever give a different result from the preview chips? Not seen. Raid 1 also matched its projection (Home 50>40).
  - Did UNDO / rewind behave as expected? Yes, I used it a lot with no problems.
- **Card balance & utility:**
  - Overpowered / automatic picks: Jolt, Brute Spin and the free nudges (Flick, Calibrate) were the useful tools. Mirror Flip fixed a Perfect 16 on the elite (it became WEAK 16, damage 16 → 8).
  - Useless / never worth picking: Mirror Flip is blocked while the target has resistance (Recall Unit, resist 3). Ring Tap and Gear Shift were likely dead because they are inner-ring cards. Overdrive is risky at low HP (1.5x once, then CORRUPTED).
- **Synergies & archetypes:** The deck stayed a pile of nudges. I had no time to build toward a plan, because every loot choice was driven by surviving at low HP.
- **Card text & clarity:** Mostly yes. Tooltips gave exact numbers (Brute Spin 6 ticks clockwise, 2 RAM; Jolt 3 ticks, 1 RAM). The enemy elite's two pointers confused me, though: the lower pointer was on NULL but the preview was still LETHAL.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netruns were too long and short-lived. Netrun 1 lasted ~6 min, netrun 2 ~50 min, netrun 3 ~18 min and netrun 4 ~24 min (still going). Whole campaign too long (104 min and nowhere near the end).
- **Netrun map & encounters:** It repeated. Layers were mostly plain Fights, with a lone Wellness Kiosk event and one rest node at layer 4 of netrun 4. Routes forced single nodes at very low HP (15/60, 7/60, 22/60) with no recovery option.
- **City Grid & HQ:** HQ visits were quick (~1 min), and the free rookie hire was welcome. Site choices were not meaningful for me, because I only ever took the T1 site.
- **Heat:** Predictable. The site panel showed the flatline cost up front (+11), and Heat went 0 → 11 → 25 → 30 → 42 → 43. It was clear, but flatlining pushed me toward the Heat 50 raid threshold.
- **Raids:** Understandable. Setup showed a projection (Home 50>40 HOLDS) and the playout was one step, so a good length.
- **RNG & fairness (1–5):** 4 — forced fights at 7/60 and 15/60 HP after losing 45 HP in a T1 fight felt unfair.
- **Permadeath & meta-progression:** Losing Breakers 1 and 3 felt like a result of the route, not of my play. I was not drawn to restart.

## 4. UI, controls & audio

- **Information in combat:** Good. Chip previews showed the exact HP delta and a LETHAL flag, and I could read RAM, HP and needle slices. I did not record anything about the draw and discard piles.
- **Information outside combat:** Several elements were hard to read or clipped: top HUD counters, the TARGET label, and the Crew/Market/Defense tab names cut off at the left edge. The panel said to jack in but no clear JACK IN button was visible. The rest node tooltip read "Rest: placeholder text". The legend icons are tiny. The route panel says "click a numbered room" but few nodes show numbers.
- **Controls:** Loot CONTINUE ignored mouse clicks repeatedly and needed Enter or Space, and the key that worked varied (see bugs). ROUTE VIEW and the rest LEAVE button also ignored clicks. The Wellness Kiosk option needed several tries.
- **Visual feedback:** I did not note anything on impact of plays, spins or Perfects beyond the previews.

## 5. Focus questions (Pacing and session length)

1. Which part of the loop felt too long? Too short? — Combat was far too long. Recall Unit took 23 turns (~48 min wall-clock, with turn 23 stuck lethal for 30+ min of attempts). Netrun 4 fights ran 7–11 turns. Combats of 5–7 turns were fine. HQ (~1 min), the raid playout (1 step) and the flatline return (~30 s) were the right length.
2. Which animation or transition did you most want to skip? — The netrun intro cutscene (~8 min mark), though Space: SKIP was offered. The loot CONTINUE and screen transitions were worse, because they stalled.
3. Would you start another netrun right now? Why or why not? — No. I would be entering at low HP with forced fights, and each run costs 20+ min for little progress.

## 6. Open feedback

- **Favourite moment or build:** Winning the Dosage Dispenser fight at 1 HP, and getting a Perfect 12 for the kill on Collections Agent.
- **Biggest frustration / moment you wanted to quit:** Turn 23 vs Recall Unit at 2/60 HP, lethal for 30+ min, until I sent into death at 0 RAM.
- **One thing to change or add right now:** Add rest or heal choices on the route after big HP losses, and fix the loot CONTINUE button.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Loot sheet | After taking a card (5.6m, 11.8m, 65.5m, 87.3m, 99.4m) | CONTINUE works on click | Button greyed and ignored clicks; Enter or Space worked, varying by case | blocker (workaround exists) | 0054.png, 0115.png, 0954.png, 1194.png, 1357.png |
| 2 | Loot sheet | 84.3m: SKIP then CONTINUE | Leaves sheet | Stayed on sheet; only picking a card then Continue worked | wrong | 1162.png |
| 3 | Grid map | 65.9m | ROUTE VIEW opens on click | Ignored two clicks; Enter worked | wrong | 0957.png |
| 4 | Rest node | 100.2m, after PATCH | LEAVE works on click | Ignored clicks; Space left | wrong | 1363.png |
| 5 | Kiosk event | 12.3m | Option confirms | Clicks and key 1 had no effect several times | wrong | 0119.png |
| 6 | Route map | 99.7m | Real rest description | Tooltip "Rest: placeholder text" | cosmetic | 1359.png |
| 7 | Rest screen | 99.9m | Clear post-PATCH state | HP 22/60 with "spent" and a PATCH row previewing 43/60 | cosmetic | 1361.png |
| 8 | Combat, Recall Unit | 17.9m–59.2m | A non-lethal line to exist | Turn 15 lethal for ~3 min of attempts; turn 23 lethal 30+ min wall-clock | wrong | 0180.png, 0897.png |
| 9 | HQ screens | 0903.png, 1120.png | Readable text | Clipped text and tab labels, no clear JACK IN button | cosmetic | 0903.png |

**Confusion log:**
- 12.3m — Wellness Kiosk — option highlighted but not confirming — several tries until it went through.
- 78.1m — Claims Adjuster turn 3 — two enemy pointers, lower on NULL but preview still LETHAL — unresolved; I lost the fight.
- 99.9m — Rest node — screen said "spent" while PATCH previewed 43/60 — resolved by leaving with Space.

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: static_fox
persona: min-maxer
focus: pacing
build: 52626bcd24d785a8dd7c75b213a52ea639892935
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 3
raids_survived: 1
playtime_min: 104
enjoyment: 3
rng_fairness: 4
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: Jolt, Brute Spin, Flick, Calibrate, Mirror Flip
weak_picks: Ring Tap, Gear Shift, Overdrive
bugs: 9
top_frustration: Marathon combats (23 turns vs Recall Unit) and forced fights at near-zero HP
top_change: Add heal/rest options after big HP losses and fix the stuck loot CONTINUE button
```