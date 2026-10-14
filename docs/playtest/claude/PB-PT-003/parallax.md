# Playtest feedback — parallax · PB-PT-003 · build 52ba1e942fc6205fa97a705cb4c3171aafbbeae9 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** parallax
- **Persona / focus / quirks:** Explorer / completionist, intermediate / Economy and difficulty curve / prefers the keyboard shortcut whenever one is shown
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
- **Total playtime:** 60 minutes (438 actions, 2 sessions: the game closed and relaunched itself around 54.2m after the Save & Quit attempts)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, Standard Home Server, starting roster Breaker only (2 crew slots), campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time, INCOMPLETE)
  - Netruns: 3 started (the third is a 4th-layer-free, tutorial-overlay fight), 0 completed, 2 operative deaths (Claims Adjuster Server Rack, layer 4; Recall Unit Elite, layer 3 of the second netrun)
  - Highest Site tier reached: T1 · Exploits held: 0 · Sites claimed at the end: 0
  - Raids: 1 survived (First Notice, Home 50→40), 0 nodes lost
  - Final Heat: 30 (Noticed) · Home server integrity: 40/50
- **Overall enjoyment (1–10):** 5 — The wheel preview is great, but HP never recovered on the route and two operatives died to forced fights.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Yes, partly. Chasing the 12 slice with Jolt and free nudges was fun. Fine Tune and Brute Spin targeting kept misfiring, which hurt that feeling.
  - Did SEND IT ever give a different result from the preview chips? No. The preview matched every turn I checked (0032, 0035, 0048). One stale-looking lethal chip on the Rack turn 4 eventually cleared after a setup change.
  - Did UNDO / rewind behave as expected? Mostly. Undo locks after a random pick (Jolt, respin). The banner says so, but I missed it for about 20 steps and wrongly logged it as a bug. That lock also left me no clean line on Rack turn 6, so I sent into mutual lethal and died.
- **Card balance & utility:**
  - Overpowered / automatic picks: Jolt (cheap rotation), Mirror Flip (cut an incoming hit from 16 to 4 on the elite), Patch+ firmware.
  - Useless / never worth picking: inner-ring cards (Gear Shift, Ring Tap, Inner Snap) are dead for the Breaker. Sanitize, Reroll and Inner Drift looked weak.
- **Synergies & archetypes:** Only a few cards were gathered (Jam, Patch+, Firewall). It stayed a small pile with no strategy forming.
- **Card text & clarity:** Mixed. Fine Tune's arc kept landing on the enemy's nudge arrow instead of my wheel, which was confusing. Brute Spin double-queued two spins with no visible wheel turn (0070). Z undo cleared it.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netrun too short in practice (about 10–15 min each, ended by death); whole campaign not judgeable (~60 min, never past HQ).
- **Netrun map & encounters:** Routes were nearly linear: one forced next node, then a forced Rack at 16 HP, then a forced Elite at 16 HP. I saw Fight, Event (Wellness Kiosk), Rack and Elite. I never saw a shop or Mainframe.
- **City Grid & HQ:** Only one site (Continuum Billing Farm) was tried. Market recruit appeared free after the wipe. Schematics stayed at 20 throughout.
- **Heat:** Rose from 0 to 11 (after the first death), then 25, then 30. A Wellness Kiosk scan cost +2 Heat. Thresholds led to the First Notice raid, which seemed fair.
- **Raids:** First Notice was understandable (2 collectors, Home 50>40 HOLDS) but I had almost no crew to defend with.
- **RNG & fairness (1–5):** 3 — The forced Rack and Elite at low HP were the problem, not the dice.
- **Permadeath & meta-progression:** Losing Breaker 1 felt partly earned (I called a Rack at 16 HP a trap) and partly route-forced. Both deaths came from fights I could not avoid. I did not reach any unlocks.

## 4. UI, controls & audio

- **Information in combat:** Good. Preview chips, enemy pointers, RAM and the lethal chip are easy to read.
- **Information outside combat:** The HQ map has many unexplained stats (Exploits 0/3, Raids, Ice) and no clear objective prompt. The ticker and command box text are clipped.
- **Controls:** Space never advanced tutorial steps, only clicking NEXT did. Space did work for SEND IT in fights. Escalation hand-offs went unanswered. Save & Quit was ignored repeatedly, then the game closed and relaunched itself.
- **Visual feedback:** Fine. Brute Spin gave almost no visible feedback.

## 5. Focus questions (Economy and difficulty curve)

1. Where did difficulty spike, and where was it flat? — The first fights were flat to moderate (Daemon cost 29 HP, Dispenser 6, Triage 0). It spiked hard at the Claims Adjuster Rack (112 HP, Perfect 16 pointer vs my 16 HP) and at the Recall Unit Elite (106 HP at 16 HP). The route gave no heals before them. HP never refilled between nodes: I went 60→31→16→16.
2. Were shop prices fair for what you could afford? — Not encountered. I saw no shop. The only price I saw was the Market recruit, which showed 0 Schematics after the wipe.
3. Was any resource always too scarce or always piling up unused? — HP was always scarce, and the one heal was +10 (with +2 Heat). Schematics sat unused at 20. Cycles (62) were lost on death. RAM debt appeared often from Jolt chains.

## 6. Open feedback

- **Favourite moment or build:** A Perfect 12 opening on the Dosage Dispenser (38→14), and the preview matching every send.
- **Biggest frustration / moment you wanted to quit:** The Rack turn-4 lethal-chip loop, about 15 minutes of undos. Then forced fights at 16 HP with no heal.
- **One thing to change or add right now:** Add a heal node, or a rest option, before the Rack and Elite. Make the Undo-lock banner more prominent.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Tutorial | 1.7–2.6m | Space advances steps | Space ignored, NEXT click needed | wrong | 0007.png |
| 2 | Fine Tune targeting | 7.5–8.5m | Arc lands on my wheel | Kept landing on the enemy nudge arrow | wrong | 0043.png |
| 3 | Brute Spin | 13.4m | One spin per play | Two spins queued, no wheel turn | wrong | 0070.png |
| 4 | Rack turn 4 preview | 23–30m | Chip refreshes with wheel changes | Lethal chip seemed stale (cleared at 30.7m) | wrong | 0128.png |
| 5 | Save & Quit | 53.8–54.2m | Clean quit | Clicks ignored, then game closed and relaunched itself | crash | 0294.png |
| 6 | Escalation hand-off | 17.6–40m | A stronger player answers | Escalations never took effect | wrong | 0099.png |
| 7 | HQ map (0217) | – | Full ticker/command text | Clipped text, cryptic ids | cosmetic | 0217.png |

**Confusion log:**
- 15.4m — Rack fight — Undo blocked, reason unknown — about 24 minutes, resolved by reading the banner at 39.1m.
- 7.5m — Fine Tune aiming — unclear which wheel gets targeted — never resolved.
- 53.6m — Pause menu — Abandon Campaign sits right beside Quit to Main Menu, easy to miss-click.

## 8. Summary

```
SUMMARY
handle: parallax
persona: PB-PT-003
focus: economy-difficulty
build: 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 2
raids_survived: 1
playtime_min: 60
enjoyment: 5
rng_fairness: 3
netrun_length: too short
campaign_length: too long
text_clear: no
op_picks: Jolt, Mirror Flip, Patch+
weak_picks: Gear Shift, Ring Tap, Inner Snap, Sanitize, Reroll, Inner Drift
bugs: 7
top_frustration: No healing between forced Rack and Elite fights at 16 HP, plus the Undo lock after a random pick
top_change: Add a heal node before the Rack and Elite, and make the Undo-lock reason more visible
```