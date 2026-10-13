# Playtest feedback — lowtide · PB-012 · build 19ad76a3a10c260a760667a0d6dde27156508740 · date not recorded

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** lowtide
- **Persona / focus / quirks:** Roguelite newcomer / First hour and onboarding / uses UNDO to experiment most turns; picks the rightmost option when two look equal
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 19ad76a3a10c260a760667a0d6dde27156508740
- **Total playtime:** 30 minutes (488 actions, 326 steps; quit once via pause menu to save)
- **Campaign setup:** corporation Solace Biosystems, ICE not shown (defaults kept), home server Standard, starting roster Breaker (two Breakers), campaign code not shown in my notes (the pause menu has a code field, 0203.png)
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time at 30 minutes, INCOMPLETE; quit to desktop from netrun combat T3)
  - Netruns: 2 started, 0 completed, 1 operative death (Breaker 1, flatlined after the Billing Daemon fight, turn 13, L1 of Continuum Billing Farm). The second netrun was still in progress.
  - Highest Site tier reached: T1 · Exploits held: not encountered · Sites claimed at the end: not encountered
  - Raids: not encountered
  - Final Heat: 11 (first threshold at 10) · Home server integrity: 50/50 at the start; later value not seen
- **Overall enjoyment (1–10):** 3 — I spent most of the session confused by unlabelled symbols and never reached anything that felt good.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Not really. I could not read the wheels well enough to plan, so I mostly learned by trying cards. The "1 LANDS HERE" arrow when targeting was the first thing that made a card's effect clear.
  - Did SEND IT ever give a different result from the preview chips? Not clearly. I never lined the result up against the preview. The SEND IT preview did spell out damage (a Shim hit costing the Breaker 4 HP, 47 to 43), which I liked.
  - Did UNDO / rewind behave as expected? Mostly. My first click on the UNDO button in the tutorial seemed to do nothing, and later I clicked the wrong spot for it. In combat it rewound pending plays cleanly. At 28.8m it greyed out with a red "blocked" note after a random pick, and nothing had warned me that would happen.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen.
  - Useless / never worth picking: Overdrive, which I avoided because it turns the slice CORRUPTED and the game never said what that costs. That is a clarity problem, not a balance finding.
- **Synergies & archetypes:** Not encountered. I only saw the starting cards (Jolt, Brute Spin, Fine Tune, Mirror Flip, Overdrive) and built no deck.
- **Card text & clarity:** No.
  - "Tick" is never defined; I guessed it meant a needle step.
  - The "1/0" glyph on the wheel was never labelled in combat.
  - CORRUPTED, "Null", and negative RAM, e.g. "(-1)" next to RAM, were not explained.
  - Mirror Flip's text is cut off ("Blocked while th...").
  - Fine Tune's text says "drag onto a target", while this setup uses click-then-target.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** The first netrun lasted about 14 minutes (13 turns) and ended in defeat. I can't judge whole-campaign length.
- **Netrun map & encounters:** I saw only the L1 route of Continuum Billing Farm and two fights (Billing Daemon, then a Solace General / Collections Agent fight). The map icons are tiny and the legend is hard to match to the nodes. Nothing says to pick a node.
- **City Grid & HQ:** I barely touched it. The site panel says "OPENS 2 SITES" and "CAN BE YOUR NODE", and I never learned what a node is. The locked setup options show "UNLOCKS 120/40/60" with no currency named.
- **Heat:** I couldn't predict it at first. Hovering the Heat bar explained it (0/100, first threshold at 10), but the map itself doesn't. Heat rose by 11 after the failed netrun.
- **Raids:** Not encountered.
- **RNG & fairness (1–5):** 3 — I couldn't tell whether I lost to bad luck or to my own misunderstanding; I think mostly the latter.
- **Permadeath & meta-progression:** Losing Breaker 1 felt unearned because I had never learned the rules. I wasn't sure how the campaign continues with one operative down, but a second Breaker was available. I did not see any unlock progress.

## 4. UI, controls & audio

- **Information in combat:** Poor. HP and RAM are visible, but the hand cards overlap and their text is clipped. The small chips beside the HP bars have no legend, and the rim text on the wheels is unreadable. The "EXECUTE" label sits behind the SEND IT button.
- **Information outside combat:** I couldn't find what the top counters do (the "D 0" badge, Exploits 0/3, Schematics). The map's JACK IN button, the TARGET, and the site panel are spread out across the screen. The campaign setup tooltip says "Buy it with Schematics" while the cards say "UNLOCKS".
- **Controls:** Click-then-target works, but the tutorial text says to drag. Hovering the SEND IT / UNDO / RAM tooltips taught me a lot. In the tutorial, turn 2 stalled for about 1.5 minutes before I clicked SEND IT and it moved on.
- **Visual feedback:** The "1 LANDS HERE" arrow is good. A large pink and cyan wheel graphic covered the map on the JACK IN transition (0094.png). I couldn't tell hits and Perfects apart; I got zero Perfects.

## 5. Focus questions (First hour and onboarding)

1. After the tutorial (or skipping it), what did you still not understand? — "Tick", the "1/0" Null slice, what a negative RAM number means, what CORRUPTED does, what Firmware chips are, and what a node is. The tutorial ended on a FIGHT WON banner with no Next button I could find, so I left through the pause menu.
2. Which word, icon or number confused you longest? — The "1/0" slice on the wheels (about 10 minutes of hovering). It shows only a Null tooltip that says "nothing happens unless a Daemon says otherwise". The Codex Slices tab explained NULL, but only after I went looking for it. Close behind were "tick" (the whole tutorial) and the RAM "(-1)" readout (never resolved).
3. When did the game 'click', if it did? — Partly, around 26.5m, when I read the RAM tooltip and the SEND IT preview showed exact damage. The "1 LANDS HERE" arrow helped earlier. I never got the full picture before time ran out.

## 6. Open feedback

- **Favourite moment or build:** The targeting arrow with "1 LANDS HERE", and the free, unlimited UNDO that lets a nervous player experiment.
- **Biggest frustration / moment you wanted to quit:** Turn 1 of the second netrun, where I stalled for about 25 minutes hovering the same cards because I couldn't read RAM costs or the Null slice. Losing Breaker 1 to unexplained RAM overdraw was close behind.
- **One thing to change or add right now:** Label things where the player sees them: define "tick", show what the 1/0 Null slice is on the wheel itself, and say what negative RAM does, with RAM explained in the first tutorial card.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity (crash / blocker / wrong / cosmetic) | Shot |
|---|---|---|---|---|---|---|
| 1 | Tutorial sim, FIGHT WON banner | 6.7–7.2m, clicked the middle of the screen 6 times, then Esc | A Next/continue button | None found; left via pause menu → Quit to Main Menu | blocker | 0077–0082 |
| 2 | Tutorial turn 2 | 2.6–5.1m | Fine Tune in hand and a clear way forward | Fine Tune missing, only Mirror Flip; breaker ring clicks did nothing; turn advanced after SEND IT | wrong | 0031–0060 |
| 3 | UNDO button in tutorial | 0.7–0.8m | UNDO responds to a click | First click showed nothing; I switched to the Z key | cosmetic | 0009–0010 |
| 4 | Combat, hand | 8.9–9.2m | Hand stays stable while a card is pending | Hand appeared to swap after selecting a card | wrong (or unclear) | 0098–0101 |
| 5 | Combat T3, UNDO | 28.8m | UNDO stays available | Greyed out with a "blocked" note after a random pick, with no prior warning | cosmetic | 0307 |
| 6 | JACK IN transition | 8.3m | Readable map | Giant pink/cyan ring covered the screen and left HUD | cosmetic | 0094 |
| 7 | Dossier on route map | 23–24m | Full HP value shown | "AT LARGE" stamp covers the max HP | cosmetic | 0254 |

**Confusion log** (moments you did not know what to do):
- 0.5–6.3m — tutorial sim — what a "tick" is — never resolved; I guessed it means a needle step.
- 1.5–1.6m — tutorial sim — what RAM is — about 6 seconds after hovering the RAM bar.
- 2.6–5.1m — tutorial turn 2 — Fine Tune missing and breaker clicks doing nothing — about 2.5 minutes; resolved by pressing SEND IT.
- 6.7–7.2m — tutorial end — no Next button — about 30 seconds; left via the pause menu.
- 7.5m — campaign setup — what the "UNLOCKS 120" number means — never resolved.
- 7.7–8.0m — campaign map — what Heat and "node" mean — Heat resolved after hovering the bar; node never resolved.
- 10.0–18.9m — netrun combat — the "1/0" slice — about 9 minutes, resolved only by the pause-menu Codex (Slices tab).
- 24.1–25.5m — second netrun T1 — the 1/0 slice and RAM "(-1)" again — about 1.5 minutes, then I just played a card.
- 26.3–30.1m — netrun T3 — what CORRUPTED and negative RAM do — never resolved.

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: lowtide
persona: PB-012
focus: first-hour-onboarding
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 1
raids_survived: 0
playtime_min: 30
enjoyment: 3
rng_fairness: 3
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: none
weak_picks: Overdrive
bugs: 7
top_frustration: Wheel symbols and RAM were unexplained in combat, so I stalled for many minutes and lost an operative without knowing why.
top_change: Label the Null 1/0 slice, define "tick", and explain negative RAM and CORRUPTED where the player sees them.
```