# Playtest feedback — nullpoint · PB-PT-003 · build 52ba1e942fc6205fa97a705cb4c3171aafbbeae9 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** nullpoint
- **Persona / focus / quirks:** Returning after a bad first try (novice) / Pacing and session length / tries a different operative class on each netrun when possible
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
- **Total playtime:** 40 min (324 actions, 1 session; ended by time box and in-game Quit)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, home server Standard, starting roster Breakers only (I could not afford other classes), campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time. INCOMPLETE at the 40-minute box, Breaker 4 alone on a turn-1 L1 fight)
  - Netruns: 3 started, 0 completed, 3 operative deaths (L2 Dosage Dispenser fight; Claims Adjuster fight at L4; L1 Collections Agent fight after about 16 turns)
  - Highest Site tier reached: T1 · Exploits held: not encountered · Sites claimed at the end: 0
  - Raids: 0 survived (CELL HOLDS). One Collections "First Notice" raid ran with no assets, Home 50 to 40. Nodes lost: not encountered.
  - Final Heat: 38 · Home server integrity: 40/50
- **Overall enjoyment (1–10):** 3 — the fights were long and the wheels were hard to read, and I lost three operatives in 40 minutes.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did it feel like skill? Not for me. I kept saying I was guessing and spamming spins. The targeting arrow on Jolt helped later (0141), but I never worked out which slot or card did the damage.
  - Did SEND IT ever differ from the preview chips? Not noticed.
  - Did UNDO / rewind behave as expected? In the tutorial I undid four times on turn 2. Jolt seemed to vanish from my hand and the queue looked muddled. In the end the small arrow icons above the wheels turned out to be the free nudge, and the tutorial never said so.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen. Patch Up was my pick for healing.
  - Useless / never worth picking: not enough data. Nudge Driver seemed to double nudges. Jolt and Fine Tune on the enemy wheel did not obviously blunt the 14 spike.
- **Synergies & archetypes:** Only Breaker was played. No strategy came together, the deck felt like a pile and I just played what was in hand.
- **Card text & clarity:** No. The cards are crowded and some descriptions are cut off (Overdrive, Mirror Flip). The wheel icons and tags such as "GOOD → WEAK" are unexplained. The "needles resolving" tooltip covered the cards.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netrun too long (the first fights ran ~3 min, ~11 min and ~20 min); whole campaign too long (40 min, with no netrun completed).
- **Netrun map & encounters:** Not enough to judge repetition. I saw a Fight, an Event, a Shop, a Rack and an Elite. The Shop had nothing affordable (40 cycles, cheapest card 50). The jump to a 112 HP Claims Adjuster after Rack L4 had no warning.
- **City Grid & HQ:** Recruiting was hard to find. I had to hunt in the MARKET. A Recruit Breaker costs 15 Schematics and I had 5 after losing runs. Other classes (Hivemind, Bunker, Ghost, Fortress, Botnet) were locked at 40–80 Schematics, so I could not try a different class. The Defense armory was empty (0/6).
- **Heat:** Flatlines added +11 each. I did not see how to manage it. The Collections raid at 25 hit me at 33.
- **Raids:** The briefing was readable, but with no assets to deploy there was nothing I could do. Home went 50 to 40 and Heat rose to 38.
- **RNG & fairness (1–5):** 3 — the Dosage Dispenser loss came after I walked in at 18/68, so that one was partly on me. Fights that lasted many turns with little damage dealt felt like attrition.
- **Permadeath & meta-progression:** Losses 1 and 2 felt half earned, because I entered fights hurt. The third felt like a grind loss. With the other classes locked behind Schematics, I had no pull to restart.

## 4. UI, controls & audio

- **Information in combat:** HP, RAM and the enemy spike (14) were visible. The previews said "lethal" and gave the damage I would take. The wheel numbers are small, and I could not tell which slot was best.
- **Information outside combat:** Recruit costs were not shown before I opened the MARKET. The "Home" and "Core HP" terms looked inconsistent. The defeat screen had overlapping CONTINUE and PROCEED buttons, and the dialogue text was clipped ("Tell the Cell it was wort...").
- **Controls:** Mostly responsive. Click-then-target worked. Queueing and undoing was fiddly in the tutorial.
- **Visual feedback:** The iris transition into a netrun was slow. Hits and Perfects did not stand out to me. I noticed Perfects only in the result readouts.

## 5. Focus questions (Pacing and session length)

1. Which part felt too long? Too short? — Fights were far too long. The tutorial sim ran 13 turns and lost, the Billing Daemon took 13 turns (~11 min), and the Collections Agent took 16 turns (~20 min). HQ and market browsing was short but confusing. Netrun 2 took about 7 min before it ended.
2. Which animation or transition did you most want to skip? — The dark iris wipe when jacking into a netrun. The turn-by-turn resolve was also repetitive.
3. Would you start another netrun right now? Why or why not? — Not eagerly. I have one Breaker left, Heat is 38 and I can't afford other classes. I would do it only if fights were shorter and the wheels were explained.

## 6. Open feedback

- **Favourite moment or build:** The Compliance Officer fight, where the 12 slot paid off (5 turns, a Perfect).
- **Biggest frustration / moment you wanted to quit:** The 16-turn Collections Agent grind around the 14 spike, ending in a flatline.
- **One thing to change or add right now:** Explain the free nudge arrows and the damage readout in the tutorial, and shorten fights (or show clearly what deals damage).

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Tutorial turn 2 | Queue Jolt (3.2m) | Jolt stays in hand until played | Jolt seemed to vanish and the queue looked muddled | wrong | 0018 |
| 2 | Defeat screen | Tutorial loss (7.0m) | Full text and one button | Message clipped, CONTINUE overlaps PROCEED | cosmetic | 0044 |
| 3 | Card text | Tutorial hand (2.5m) | Full descriptions | Overdrive and Mirror Flip text cut off | cosmetic | 0012 |
| 4 | Raid briefing | 38.7m | Clear START DEFENSE button | Label cramped and clipped | cosmetic | 0221 |

**Confusion log:**
- 3.2m — tutorial turn 2 — how to use the free nudge — about 1.5 min and four undos; found the arrow icons above the wheels myself.
- 14.1m — HQ market — how to rebuild the crew and which classes were available — about 1.5 min; only Recruit Breaker was affordable.
- 23.1m — HQ — where to recruit — about 0.5 min; found the MARKET tab.
- Throughout the fights — which card or slot does the damage — never resolved.

## 8. Summary

```
SUMMARY
handle: nullpoint
persona: PB-PT-003
focus: pacing
build: 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 3
raids_survived: 0
playtime_min: 40
enjoyment: 3
rng_fairness: 3
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: Patch Up, Nudge Driver
weak_picks: none
bugs: 4
top_frustration: 16-turn fights where the wheels were unreadable and damage barely moved
top_change: Explain free nudges and damage in the tutorial and shorten fights
```