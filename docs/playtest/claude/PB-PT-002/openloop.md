# Playtest feedback — openloop · PB-PT-002 · build 52ba1e942fc6205fa97a705cb4c3171aafbbeae9 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** openloop
- **Persona / focus / quirks:** Impatient skimmer / Menus, navigation and information / Uses UNDO to experiment; right-clicks new cards or icons to inspect them
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
- **Total playtime:** 30 minutes (304 actions, 2 sessions: I quit to the main menu once and continued)
- **Campaign setup:** corporation Solace Biosystems, ICE not shown, home server not shown (HOME 50 max), starting roster Breakers (4), campaign code shown on the pause menu but not recorded
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**: home server **BREACHED** after <n> netruns, in a raid triggered by <cause>
  - [ ] Campaign **won**: final server breached after <n> netruns
  - [x] Campaign **abandoned** / could not continue (why: soft-lock. All 4 Breakers flatlined, 0 Schematics, and I found no way to recruit or rest. The outcome reason was "stuck".)
  - Netruns: 4 started, 0 completed (all four ended in a flatline), 4 operative deaths. Breaker 1 died on fight 4 vs Claims Adjuster at 2 HP. Breaker 2 died vs Recall Unit. Breaker 3 died vs Collections Agent on T1 Continuum Billing Farm. Breaker 4 died vs Billing Daemon, turn 18. Layer numbers for the deaths are not recorded beyond that.
  - Highest Site tier reached: T1 · Exploits held: not encountered · Sites claimed at the end: 0
  - Raids: 1 survived (CELL HOLDS, HOME 50 to 40), 1 failed (Collections: Second Notice, HOME 32/50), 0 nodes lost
  - Final Heat: 57 (FLAGGED) · Home server integrity: 32/50
- **Overall enjoyment (1–10):** 2 — Fights dragged, I got bled out by my own skimming, and then the campaign dead-ended with no way back.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? No. I mostly mashed Jolt then SEND IT. Wheel targeting cost two clicks per card, and Fine Tune never confirmed after about ten clicks on the Daemon wheel (possible bug). Jolt and Brute Spin did target.
  - Did SEND IT ever give a different result from the preview chips? Not noticed; I didn't read the chips.
  - Did UNDO / rewind behave as expected? Yes, UNDO backed out of the stuck Fine Tune targeting. I used it a lot there.
- **Card balance & utility:**
  - Overpowered / automatic picks: Jolt was the only card I trusted, and I used it every fight.
  - Useless / never worth picking: Fine Tune never worked for me. I never really tested Overdrive or Brute Spin.
- **Synergies & archetypes:** No strategy came together. I played Breakers only, and the deck was just Jolt spam.
- **Card text & clarity:** No. The Overdrive tooltip is wordy and hard to parse at a glance. Fine Tune's text confused me and I never worked it out. Right-click inspect did work. Later in the run it seemed to show nothing useful to me.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netrun too long. One fight took 20 turns because Triage Unit kept healing itself, and another took 18 turns. Whole campaign: not finished, ~30 min and it dead-ended.
- **Netrun map & encounters:** I didn't read the map. I took the nearest orange node each time. Seen: fights, one Terminal event (Wellness Kiosk, +10 HP for +2 Heat), and an Elite node I walked past. I don't know why there's both a route map and a grid view button.
- **City Grid & HQ:** The HQ gave no visible way to revive or rest flatlined Breakers. The Core panel offered only Heat Scrub (25 Schematics). The Market Breaker recruit cost 15 Schematics, and I had 5 and then 0. Recruiting looked unreachable once I was broke.
- **Heat:** I couldn't predict it. Heat 11 stayed unexplained for most of the run. It rose from failed netruns (+14, then +11 each time) and from the Wellness Kiosk (+2). It ended at 57.
- **Raids:** The setup screen was a wall of text. One raid ran on its own and I don't know how, since the Start Defense step seemed skipped. The report said FAILED but CELL HOLDS.
- **RNG & fairness (1–5):** 3 — A Perfect landed by luck on turn 13, but most of the damage was my own doing. Enemy HP also felt high: Claims Adjuster had 112 and Recall Unit 106.
- **Permadeath & meta-progression:** Losing operatives was my fault, but the permadeath warning only appeared in the flatline box. With no recovery path, it became a soft-lock rather than a setback. I didn't want to restart.

## 4. UI, controls & audio

- **Information in combat:** HP and the enemy's HP were readable. The wheels and arrows were a blur at a glance. Deck, draw and discard piles: not mentioned in my notes.
- **Information outside combat:** I never found how to revive or rest the crew. The hint "recruit or rest at HQ" pointed at nothing I could find. I also didn't find what Heat does. The Schematics drop (20 to 5 to 0) was never explained.
- **Controls:** Esc and the gear icon did nothing on the HQ Core panel for about 20 minutes. The pause menu only opened after I clicked the bottom-left spot and then pressed Esc. The CREW tab click showed no visible change. Wheel clicks gave no feedback during the Fine Tune bug.
- **Visual feedback:** Weak for me. Fight results were clear enough, but the wheels gave no sense of impact.

## 5. Focus questions (Menus, navigation and information)

1. Which piece of information did you look for and fail to find? — How to revive flatlined Breakers or rest at HQ. I also never found what Heat does.
2. Which screen took the most clicks to do something simple? — The HQ Core panel, about 20 minutes of clicking just to open the pause menu. The Fine Tune wheel targeting was second, with roughly ten clicks and no confirmation.
3. Did hover and right-click inspect behave consistently? — Not really. Right-click on cards worked early, but later it "shows nothing useful". Right-clicking a flatlined Breaker card said nothing about healing.

## 6. Open feedback

- **Favourite moment or build:** The 3-turn Dosage Dispenser win at 0 HP lost. Jolt spam worked there.
- **Biggest frustration / moment you wanted to quit:** The HQ with a wiped roster. After 20+ minutes of clicking I found no revive, no rest, and a menu that wouldn't open.
- **One thing to change or add right now:** Put an obvious Rest/Recruit action on the HQ screen. Warn about permadeath and an empty roster before jacking in.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity (crash / blocker / wrong / cosmetic) | Shot |
|---|---|---|---|---|---|---|
| 1 | Combat T2, Fine Tune targeting | 3.0–5.9m | Clicking the Daemon wheel confirms the card | About ten clicks, no feedback; UNDO to escape | wrong | 0010–0027 |
| 2 | HQ, Core panel | 20.5–21.2m | Esc or the gear opens the pause menu | Neither worked until I clicked the bottom-left spot first | wrong | 0131–0136 |
| 3 | HQ, roster 0/4 | 27.9–30.3m | A rest or recruit path | None found; Heat Scrub and the Market recruit both unaffordable | blocker | 0191–0199 |
| 4 | Raid | 19.0m | A Start Defense step | The raid ran on its own | wrong | 0118 |
| 5 | Codex, Home Servers tab (reviewer audit) | after session | Consistent wording | "3 asset slots", "5 asset slots", then "2 slots"; low-contrast small text | cosmetic | 0199 |

**Confusion log:**
- 2.0m — Netrun route map — why a route map AND a grid view button — not resolved.
- 3.0–5.9m — Fine Tune targeting — no feedback on wheel click — resolved by switching to Jolt.
- 14.0m — HQ/route map — what Heat does — unresolved to the end.
- 17.6–21.2m — HQ — how to revive flatlined Breakers and open the pause menu — about 4 min on revive and about 20 min total, unresolved.
- 18.5m — HQ top bar — why Schematics dropped from 20 to 5 — not resolved.

## 8. Summary

```
SUMMARY
handle: openloop
persona: PB-PT-002
focus: menus_navigation_information
build: 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
outcome: ABANDONED
netruns_completed: 0
operative_deaths: 4
raids_survived: 1
playtime_min: 30
enjoyment: 2
rng_fairness: 3
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: Jolt, Patch+, Nudge Driver
weak_picks: Fine Tune, Freeze
bugs: 5
top_frustration: Wiped roster and no visible way to recruit or rest at HQ; a dead end.
top_change: Add an obvious Rest/Recruit action to HQ and warn about permadeath and an empty roster.
```