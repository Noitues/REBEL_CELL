# Playtest feedback — kilo_echo · PB-000 · build main @ 19ad76a3 · 2026-10-12

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard. Pilot run, shortened: about 22 minutes of play (not the full 30).

## 1. General & session info

- **Playtester handle:** kilo_echo
- **Persona / focus / quirks:** Roguelite newcomer / Bug hunting and edge cases / opens pause menu once per netrun
- **Platform & hardware:** PC, Windows 10, 1280x720, mouse + keyboard, audio off.
- **Build:** main @ 19ad76a3
- **Total playtime:** ~22 min (~257 screenshots/actions, 1 session; Quit+Continue done via main menu twice)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, home server Standard, starting roster 2x Breaker, code RC1-solace-0-1-home_standard-breaker
- **How far did you get?**
  - [x] Campaign **abandoned / could not continue** (out of time: pilot time box; outcome INCOMPLETE)
  - Netruns: 2 started, 0 completed, 1 operative death (Breaker 1, Continuum Billing Farm, fight 4 of 7, turn 1, Claims Adjuster)
  - Highest Site tier reached: T1 · Exploits held: 0 · Sites claimed: 0
  - Raids: 0 survived, 0 nodes lost
  - Final Heat: 11 (Cool band) · Home server integrity 50/50
- **Overall enjoyment (1-10):** 6 - great look and clear skull "lethal" chips, but jargon and a broken quit dialog hurt.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Needle/nudge felt like some skill, but Q/E and nudge direction were not what I expected (shot 0062, 0065).
  - SEND IT vs preview chips: matched in the fights I checked (e.g. 0084->0086, skull chip 0172->0174). One oddity: Overflow 12 slice under the needle on my wheel produced only a -3 enemy chip and 3 damage (shots 0238, 0240); I did not understand why.
  - UNDO (Z) worked and refunded RAM/cards as expected (0125-0126).
- **Card balance & utility:** Overdrive felt strong when the 12 slice lined up; Brute Spin useful. Useless: nothing judged in 22 minutes.
- **Synergies & archetypes:** too little time. Deck was a small pile of Jolt/Fine Tune/Brute Spin; no strategy formed.
- **Card text & clarity:** No. Cards text is truncated ("Nudge an enemy whee..."), and words like Shim, Dfrg, OVFL, Overclock, CORRUPTED, Guard, Free Nudge are not explained at a glance.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** early fights 3 to 13 turns; ~5 min per fight. Whole campaign not judged.
- **Netrun map & encounters:** only Fight nodes seen. The fight 4 Claims Adjuster (112 HP, 16 dmg wheel) killed a 15 HP operative on turn 1 with no chance to react; as a cautious player I wanted a warning/heal before it (no heal node seen on this route).
- **City Grid & HQ:** recruiting Breaker for 15 Schematics was clear. Market boosts have lock icons after recruiting that I did not understand.
- **Heat:** went 0 to 11 only from the flatline ("Heat +11: flatlined on a run") - explained, but felt harsh.
- **Raids:** not encountered.
- **RNG & fairness (1-5):** 3 - the Claims Adjuster kill on turn 1 with 15 HP.
- **Permadeath & meta-progression:** loss was clear and well explained (shot 0189). Not enough to judge unlocks.

## 4. UI, controls & audio

- **Information in combat:** HP, RAM, deck/discard counts and enemy pointer visible. Enemy wheel intent is readable once learned. Chips next to HP (red box, skull, "?") need explaining.
- **Information outside combat:** HQ clear. Map key hidden behind MAP KEY button; opening it covers the site info panel.
- **Controls:** keyboard shortcuts Q/E/Z/X/Space shown and worked. Quit confirm dialog broken (below).
- **Visual feedback:** stylish; hits readable via the last-turn text. Nice title, fight-won and flatline screens.

## 5. Focus questions (Bug hunting and edge cases)

1. Bugs (details in section 7): (a) Quit confirm dialog buttons unresponsive; (b) first NEW CAMPAIGN click ignored after Quit to main menu; (c) tutorial Next button briefly greyed.
2. Quit then Continue: no difference seen. Mid-fight (turn 3, RAM 11, same hand, same chips; shots 0070 vs 0074) and at HQ (0191 vs 0197) restored identical state.
3. Lost/doubled inputs: yes, one lost click (NEW CAMPAIGN, 0040) and the Quit dialog buttons ignored every click and key A/B/Enter-to-confirm. No doubled input seen.

## 6. Open feedback

- **Favourite moment or build:** lining up a 12 slice and Overdrive for a skull-chip kill (shot 0172).
- **Biggest frustration:** the Quit dialog not responding, and being one-shot by Claims Adjuster.
- **One thing to change or add right now:** fix the Quit/Save&Quit confirm buttons, and add short explanations for Shim/Dfrg/OVFL.
- TOOLING: the shot after an action sometimes seems stale (confirm dialog still shown after a click), the hook forbids even `cat`/`ls` so I could not check files; reading the template needed the Read tool; blackbox `start` returns before the title finishes loading.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Pause > Quit to desktop confirm | HQ: Esc, click Quit to Desktop, click KEEP GOING (505,400); also keys b, a, and click SAVE & QUIT (740,414) in netrun | Buttons act | No click or A/B key did anything; only Esc/Enter closes the dialog. Could not use in-game Quit | wrong | shots/0200.png, 0205.png, 0257.png |
| 2 | Title after Quit to main menu | click NEW CAMPAIGN (500,408) | Opens setup | First click ignored, second worked | cosmetic | shots/0041.png |
| 3 | Tutorial step 1 | click Next at once | Advances | Greyed for ~1 s | cosmetic | shots/0004.png |

**Confusion log:** 0033 - tutorial - "?" at my HP chip - a minute, ignored; 0238-0240 - fight - Overflow 12 slice damaged only 3 - never resolved; 0213 - HQ - lock icons on boosts after recruit - not resolved.

## 8. Summary

```
SUMMARY
handle: kilo_echo
persona: roguelite_newcomer
focus: bug_hunting
build: 19ad76a3
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 1
raids_survived: 0
playtime_min: 22
enjoyment: 6
rng_fairness: 3
netrun_length: just right
campaign_length: just right
text_clear: no
op_picks: Overdrive
weak_picks: none
bugs: 3
top_frustration: Quit confirm dialog buttons do not respond; one-shot by Claims Adjuster
top_change: Fix Quit confirm buttons and explain jargon (Shim, Dfrg, OVFL)
```
