# Playtest feedback — byte_rat · PB-PT-003 · build 52ba1e942fc6205fa97a705cb4c3171aafbbeae9 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** byte_rat
- **Persona / focus / quirks:** Story and tone fan / First hour and onboarding / Seeks out Elite Routers whenever HP is above half (never found one; no Elite Router showed up on the routes I saw)
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
- **Total playtime:** 40 minutes (363 actions, 1 session; quit to the title menu at the time box and the game saved)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, home server Standard, starting roster Breaker (crew grew to 4 operatives), campaign code: a "Campaign code" line is on the pause menu, but I did not copy the value down.
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time, INCOMPLETE; stuck on the map with CENTRAL SERVER locked and no HQ route I could find)
  - Netruns: 3 started, 0 completed, 2 operative deaths (both in fights at layer 3: Breaker 1 to the Triage Unit, Breaker 2 to the Collections Agent; no Router, Elite Router or Server Rack labels seen)
  - Highest Site tier reached: T3 · Exploits held: 0 (0/3) · Sites claimed at the end: 0
  - Raids: not encountered
  - Final Heat: 22 (COOL) · Home server integrity: 50/50
- **Overall enjoyment (1–10):** 3 — the writing and mood are lovely, but I spent most of the 40 minutes guessing what the wheel words meant and then hunting for an HQ I never found.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Not really. The first fight (won in 5 turns, no HP lost) felt promising. After that I was guessing, because GOOD, NULL, WEAK and PERFECT were never defined on screen. The turn preview (e.g. Daemon HP 9 to 0) was my only teacher.
  - Did SEND IT ever give a different result from the preview chips? Not clearly. I could not confirm any mismatch.
  - Did UNDO / rewind behave as expected? Not encountered in play. I saw it only in the tutorial.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen. Jolt and Fine Tune did the most work for me.
  - Useless / never worth picking: I never worked out Overdrive's effect ("overclock your slice"). I took Nudge Driver, Sanitize and Shunt, and could not judge them.
- **Synergies & archetypes:** Not enough runs to judge. My Breaker deck felt like a random pile because I did not understand the wheel rules.
- **Card text & clarity:** No. Chips, GOOD, NULL, WEAK, PERFECT, "random-slice card" and the card-vs-wheel vocabulary were never explained. Where a card lands is only readable once the card is selected ("1 LANDS HERE").

## 3. Roguelite loop & campaign progression

- **Pacing & length:** Netruns were too long in practice (Fight 2 took 8 turns, Triage took 16, Collections Agent took 13). The whole campaign is not judgeable.
- **Netrun map & encounters:** I only saw Fight nodes and a loot sheet with 3 picks plus a Firmware pick. Routers, Elite Routers, Terminals, Mainframes and Server Racks were not encountered.
- **City Grid & HQ:** The Site chain is explained only in node text ("clear X first"), not on the map. The text said "recruit or rest at the HQ", but I never found where HQ is. The Market recruit costs 15 schematics and I had 5.
- **Heat:** Heat went up 11 after the first death (22 at the end). I never understood how to manage it.
- **Raids:** Not encountered.
- **RNG & fairness (1–5):** 3 — the Triage fight (16 turns, Breaker stuck at 12/60 from the start after the previous fight) felt like ignorance, not dice.
- **Permadeath & meta-progression:** The permadeath screen was clear and I appreciated that. It felt unearned because I had not been taught the rules. Profile unlock tiles were visible but dim and I did not evaluate them.

## 4. UI, controls & audio

- **Information in combat:** HP and the turn preview box are good. The enemy wheel readout is a wall of numbers, and the small stacked numbers beside the enemy wheel are unlabelled.
- **Information outside combat:** I could not find HQ, the Site links or the Map Key's HQ entry. The CENTRAL SERVER target label does not obviously match the selected site card. JACK IN looks active even when no operative can run the site.
- **Controls:** Clicking my own wheel with Jolt or Fine Tune selected seemed to do nothing, and the aim kept going to the enemy ring. This cost me about ten turns in fight 2. Esc opens the pause menu (it was handy, and the code line there was unknown to me).
- **Visual feedback:** The "OURS NOW / DELETED" stamps felt great. The operative's lines ("Nothing. Static. Spin it again.") carry the mood.

## 5. Focus questions (First hour and onboarding)

1. After the tutorial (or skipping it), what did you still not understand? — What chips on cards and wheels are, what GOOD, NULL, WEAK and PERFECT mean, where a card's aim lands, what a Site is, what Heat does, and where HQ is.
2. Which word, icon or number confused you longest? — GOOD/NULL (about 40 minutes, never resolved). "HQ" was second, since the map has no HQ marker.
3. When did the game 'click', if it did? — Partly at fight 1, turn 4-5, when the turn preview showed HP going down (Daemon 21 to 15). The "1 LANDS HERE" arrow helped with aim. It never fully clicked.

## 6. Open feedback

- **Favourite moment or build:** Winning fight 1 without losing HP, and the OURS NOW stamp.
- **Biggest frustration / moment you wanted to quit:** The 16-turn Triage loss, then the long HQ search, when the map told me to "recruit or rest at HQ" and showed no way to get there.
- **One thing to change or add right now:** Define GOOD, NULL, WEAK, PERFECT and chips in the tutorial or with tooltips, and mark HQ and the Site links on the map.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Combat L2, Jolt/Fine Tune aim | 9.5m-15.6m | Click my own wheel to aim | Clicks gave no visible change; aim stayed on enemy ring | wrong | 0057.png |
| 2 | Map after both breakers flatlined | 30.7m-38m | Route to HQ | "Recruit or rest at HQ" with no HQ on map or Map Key | blocker | 0173.png |
| 3 | Map, JACK IN with no operative | 25.7m-30.7m | Disabled JACK IN | Button looks active, only dim | cosmetic | 0174.png |
| 4 | Map, CENTRAL SERVER label | 33.4m | Label matches selected site | Target label and site card differ | cosmetic | 0183.png |

**Confusion log:**
- 1.1m — Tutorial — chips on cards — never resolved
- 9.5m — Combat L2 — Jolt would not take an enemy-wheel target — about 6 minutes, never resolved; it only worked when I let it default
- 10.9m — Fine Tune aim snapping to the enemy ring — about 6 minutes; "1 LANDS HERE" on the arrow at 16.7m partly explained it
- 30.9m — Map — where HQ is — about 9 minutes, never resolved
- 35m — Map — Site chain, which lit node to take — about 5 minutes, resolved only by reading node text

## 8. Summary

```
SUMMARY
handle: byte_rat
persona: PB-PT-003
focus: onboarding
build: 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 2
raids_survived: 0
playtime_min: 40
enjoyment: 3
rng_fairness: 3
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: Jolt, Fine Tune, Nudge Driver
weak_picks: Overdrive
bugs: 4
top_frustration: GOOD/NULL and wheel aiming never explained, and no way found to reach HQ after both operatives died
top_change: Explain GOOD/NULL/WEAK/PERFECT/chips in the tutorial and mark HQ and Site links on the map
```