# Playtest feedback — tinroof · PB-PT-003b · build 3eac0f086e6d32f23afd7c95dbb0e7eb35379339 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** tinroof
- **Persona / focus / quirks:** Returning after a bad first try (novice) / Economy and difficulty curve / never reads tooltips unless stuck; uses UNDO to experiment most turns
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 3eac0f086e6d32f23afd7c95dbb0e7eb35379339
- **Total playtime:** 40 minutes (334 actions, 1 session; ended with the in-game Quit to save)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, home server Standard Home Server, starting roster Breaker (rookies hired free after each death), campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time; INCOMPLETE, stopped at Dosage Dispenser, L2, turn 1)
  - Netruns: 4 started, 0 completed, 3 operative deaths (all in fights: Billing Daemon L1, Compliance Officer L2, Collections Agent L1). The 4th run was still in progress.
  - Highest Site tier reached: T1 · Exploits held: not encountered · Sites claimed at the end: 0
  - Raids: 1 raid played out (Collections raid, Home 50 to 40); nodes lost: not encountered
  - Final Heat: 38 (NOTICED) · Home server integrity: 40/50
- **Overall enjoyment (1–10):** 3 — I never understood the nudge or wheel rules, so I lost three operatives while guessing.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? No. I never figured out what the free nudge does, and the preview numbers were the only thing I trusted.
  - Did SEND IT ever give a different result from the preview chips? Not clearly verified. In Fight 2 turn 2 the staged Jolt preview kept changing (28 to 22, then 28 to 16, then 28 to 24), which confused me.
  - Did UNDO / rewind behave as expected? No. On Fight 2 turn 2 UNDO ignored many clicks and ctrl+z, then said "the new turn began with a random spin". I also could not cancel a staged card by right-click, Esc or RESPIN. That led to a 12 HP hit I could not avoid.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen. Brute Spin looked like my best damage preview in one fight.
  - Useless / never worth picking: Jolt on my own wheel cost me 6 HP for 3 damage in the preview. Fine Tune was cheap, but I could not tell what it achieved.
- **Synergies & archetypes:** Nothing came together. I played the Breaker with a pile of Jolt, Brute Spin, Fine Tune and Mirror Flip. I saw a loot choice (Gear Shift, Data Surge, Leech Worm) but could not judge it.
- **Card text & clarity:** No. The Fine Tune text ("two plus-or-minus one nudges") was clear once I read it, but the free nudge, Blocked/Guard, the enemy Resist number and staging rules were not explained.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netrun too long (fights took 9–14 turns, ~5–8 min each); the tutorial also ran 11 turns, far too long. I can't judge the whole campaign because I only got through about 3 fights' worth of a run.
- **Netrun map & encounters:** I only saw T1 fights (Billing Daemon, Collections Agent, Compliance Officer, Dosage Dispenser). Other node types: not encountered. The map had only one lit site at first, so the route felt forced. CONFIRM stayed greyed ("pick a node first") until I clicked the orange node itself.
- **City Grid & HQ:** The Market offered Warm Cache (10 Schematics, 40 Cycles at the next run's start), Overclocked Deck (15) and Field Kit (20). I never bought anything. Recruiting was a free rookie after each death. Stationing and installing: not encountered.
- **Heat:** I could not predict it. It jumped +11 on arrival and +11 on each flatline, 11 → 22 → 33, and a raid then added 5 (38). The raid thresholds were only vaguely explained.
- **Raids:** I played one Collections raid. The setup was readable (Home 50 to 40, no assets deployed), but I had no way to affect it.
- **RNG & fairness (1–5):** 4 — Fight 2 started at 28/60 HP with no heal until run end, and then I lost to a staged card I could not cancel.
- **Permadeath & meta-progression:** Losing the first Breaker felt harsh, since I had never been told what a free nudge does. The second loss was partly my fault, but the staging and UNDO rules cost me. The third felt close: the enemy was at 4/40 when I flatlined. I did not feel like starting another campaign.

## 4. UI, controls & audio

- **Information in combat:** HP, RAM and the preview panel were readable. The Perfect/Good labels on the wheels helped. Enemy intent (Mirror Flip threatening 12) was shown. The outer nudge arrows gave no visible feedback.
- **Information outside combat:** The map nodes are tiny against a busy skyline, and the legend icons look alike. The dossier jargon (AT LARGE, IF STATIONED (RAIDS), WHEEL), the TARGET scrawl and the heat ticks are unexplained. The node label "L2" did not match the number on the sticker.
- **Controls:** The UNDO button ignored clicks, and so did SEND IT during escalation on turn 9 of the third run's fight. Right-click on a wheel did nothing. Esc opened the pause menu.
- **Visual feedback:** Hits were readable through the numbers, but I found no impact feedback. The nudge gave nothing visible.

## 5. Focus questions (Economy and difficulty curve)

1. Where did difficulty spike, and where was it flat? — The first real fight (Billing Daemon) was a 14-turn slog that drained 60 HP. The second fight spiked because I carried 28/60 HP in with no heal. The Collections Agent fight on a fresh Breaker 3 also drained all 60 HP. There was no flat stretch, only the Billing Daemon win on the fourth operative (26 HP lost), after I had learned to read the previews.
2. Were shop prices fair for what you could afford? — I could not tell. With 20 Schematics and Heat 11, 10–20 felt too tight to spend on a cushion. Schematics went to 10 later, and I never bought anything.
3. Was any resource always too scarce or always piling up unused? — HP was always scarce, because there is no heal until run end and every fight cost 25–60 HP. Schematics went unspent. Cycles were low: 58 before a loss wiped them (58 lost), then 21 at the end.

## 6. Open feedback

- **Favourite moment or build:** Finally winning the Billing Daemon fight with Breaker 4, reading the previews turn by turn.
- **Biggest frustration / moment you wanted to quit:** Fight 2, turn 2: staged Jolt stuck on my own wheel, UNDO refusing, and then the 12 HP hit that led to the death.
- **One thing to change or add right now:** Explain the free nudge in the tutorial and show a visible effect. Also make staged cards cancellable and UNDO clearly stateful.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Combat Fight 2 turn 2 | Clicked UNDO and pressed ctrl+z many times (21.0–23.0m) | Jolt removed | UNDO blocked: "the new turn began with a random spin" | wrong | 0138.png |
| 2 | Combat Fight 2 turn 2 | Tried right-click, Esc and RESPIN (23.0–25.4m) | Staged card cancelled | Staged card could not be cancelled | wrong | 0156.png |
| 3 | Route map L2 | Clicked CONFIRM with FIGHT L2 selected (19.0–19.8m) | CONFIRM live | Greyed "pick a node first" until the orange node was clicked | cosmetic | 0122.png |
| 4 | Combat L1 fight 1 turn 9 | Clicked SEND IT repeatedly (31.4–32.1m) | Turn sent | SEND IT stalled for several tries | wrong | 0195.png |

**Confusion log:**
- 2.2m — Tutorial turn 2 — what the free nudge does — never resolved, tutorial ran 11 turns
- 6.5m — Real fight turn 1 — same free nudge confusion — never resolved
- 20.0m — Fight 2 turn 1 — Blocked/Guard and Resist numbers unclear — never resolved
- 21.0m — Fight 2 turn 2 — how to cancel a staged card — never resolved, cost the operative
- 31.4m — Fight 1 turn 9 on the third run — SEND IT stalling and escalation — never resolved

## 8. Summary

```
SUMMARY
handle: tinroof
persona: PB-PT-003b
focus: economy and difficulty curve
build: 3eac0f086e6d32f23afd7c95dbb0e7eb35379339
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 3
raids_survived: 1
playtime_min: 40
enjoyment: 3
rng_fairness: 4
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: Brute Spin
weak_picks: Jolt, Fine Tune
bugs: 4
top_frustration: Free nudge and staged-card rules never explained, and UNDO would not cancel a bad staged Jolt
top_change: Explain the free nudge in the tutorial and make staged cards and UNDO clear and cancellable
```