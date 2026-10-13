# Playtest feedback — copperjack · PB-010 · build 19ad76a3a10c260a760667a0d6dde27156508740 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** copperjack
- **Persona / focus / quirks:** Casual evening player (intermediate) / Cards, Firmware and Daemons / prefers on-screen keyboard shortcuts; avoids Elite Routers unless forced
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 19ad76a3a10c260a760667a0d6dde27156508740
- **Total playtime:** 97 minutes (890 actions, 1 session; time ran out, I used Quit to save)
- **Campaign setup:** corporation not shown in my notes, ICE not recorded, Standard Home Server (Relay Nest was locked at 50 Schematics), starting roster Breaker, campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (out of time, INCOMPLETE). Still alive on Breaker 6, in a fight on turn 3 vs the Compliance Officer.
  - Netruns: 6 started, 5 completed (all ended in a flatline), 5 operative deaths. Where:
    - Breaker 1: Billing Farm L1, Billing Daemon, turn 16.
    - Breaker 2: Billing Farm L2, elite Recall Unit, turn 11.
    - Breaker 3: Cell-3, second fight vs Dosage Dispenser, turn 12.
    - Breaker 4: Dosage Dispenser, turn 2 (went in at 8 HP).
    - Breaker 5: L3 fight 5 vs Claims Adjuster.
  - Highest Site tier reached: T1 · Exploits held: 0 · Sites claimed at the end: not encountered (never cleared one)
  - Raids: 0 survived as a proper defence. Two raids hit with no crew, Home dropped 50 to 40 and then 40 to 27. Both reports still said Cell Holds or Failed, with no node lost noted.
  - Final Heat: 67 · Home server integrity: 27/50
- **Overall enjoyment (1–10):** 3 — I spent most of the session confused and losing, and the wheel and nudge rules never clicked.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Not really, and that's on me and the game. Aiming clicks on the wheels often did nothing, so I lived on number keys. I only learned late (~96 min) that the Q/E nudge buttons need a nudge card dropped on them. I wasted many free nudges before that.
  - Did SEND IT ever give a different result from the preview chips? Not noticed.
  - Did UNDO / rewind behave as expected? Mostly yes, and it's free within a turn. But on Cell-3 fight 2, turn 4, Undo was blocked once a random pick had come up, so I couldn't rewind Brute Spin.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen. Firewall (cheap block) was the only thing I felt helped.
  - Useless / never worth picking: Ring Tap was unplayable on wheels with no inner ring ("Target has no inner ring"), so taking it was a trap. Siphon and Static Coat firmware were offered but "do not fit an OVERFLOW slice" in my slot. Offering chips that can't be installed feels like a trap.
- **Synergies & archetypes:** No build came together. My deck felt like a random pile of Jolt, Brute Spin, Fine Tune and Overdrive, plus a few pickups. I only tried Breaker, so I can't compare classes.
- **Card text & clarity:** No. Mirror Flip and Overdrive descriptions are cut off by ellipses or overlapping cards. Free Nudge, RAM shown as negative (-1 to -3), the chips beside HP, RESIST, and the Q/E icons are all unexplained.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** Netruns were too long when they went badly. The Billing Daemon grinds ran 16–17 turns, about 7 min each. I can't judge the whole campaign (~97 min, not finished).
- **Netrun map & encounters:** I saw fights, an elite (forced at 23/60 HP, route offered only an elite), and two events (Wellness Kiosk, Patient Records). There were no healing options when I needed them. Mostly fights back to back.
- **City Grid & HQ:** Finding the starter site cost me about 37 minutes the first time and about 13 the second. Every site said it was locked behind another, and the orange-ring hint was easy to miss. I only opened the Map Key at 38 min, and it was empty in one screenshot. The Recruit Breaker option sits under Market, not Crew. Crew tab clicks did nothing when all breakers were flatlined.
- **Heat:** I couldn't predict it. Flatlines jumped it (to 52, then 67), and Heat triggered the raids.
- **Raids:** I started both raids with zero crew because I hadn't recruited first. Nothing on the setup screen warned me. The outcome text was jargon-heavy (Core, Home, HP, Cell Holds vs Failed).
- **RNG & fairness (1–5):** 3 — the Recall Unit elite, forced at 23 HP, felt unfair, but mostly I lost to not understanding the rules.
- **Permadeath & meta-progression:** Deaths felt earned by my confusion. A free replacement Breaker is a good safety net, but I never got anywhere to feel progression.

## 4. UI, controls & audio

- **Information in combat:** The preview chips and yellow aim arcs were the best parts and helped me. Deck/discard counters are tiny. The cards overlap each other. "Free Nudge" and the negative RAM number were never explained.
- **Information outside combat:** Map icons (flame, key, lock) and the "D 0" badge are unexplained. The site lock chain is hard to trace, and the route map has no "pick a node" prompt.
- **Controls:** Number keys, Space and Z worked reliably. Wheel clicks often didn't register (tutorial and many real fights). Key 2 on an event choice did nothing. The Continue button on loot sheets ignored clicks several times. The tutorial win screen had no Continue and I had to Esc out.
- **Visual feedback:** The aim arcs are clear. Hits themselves didn't feel impactful because I mostly watched numbers.

## 5. Focus questions (Cards, Firmware and Daemons)

1. **Card reward offers and my pick:**
   - After the first Collections Agent fight: Firewall, Cleanse, Gear Mesh. Took Firewall.
   - Cell-3 fight 1: Ring Tap, Gear Shift, Data Surge. Took Ring Tap (it turned out to be a trap).
   - After the Billing Daemon: Gear Shift, Data Surge, Leech Worm. Took Gear Shift.
   - After the Triage Unit: Snap, Encrypt, Counter-Spin. Took Snap.
   - L3 fight 3: Firewall, Strip, Gear Mesh. Took Strip.
   - Firmware offers: Siphon vs Shunt (Siphon rejected, did not fit); Static Coat vs Hardened (Static Coat rejected, took Hardened). Daemons as pickups: not encountered.
2. **Pickup that changed my play most:** Firewall, as cheap block. Nothing else really changed how I played. The Warm Cache boost bought at HQ had no visible effect.
3. **Class strength:** Not comparable, only Breaker played. It felt weak for me, mostly through my own confusion.

## 6. Open feedback

- **Favourite moment or build:** The Triage Unit fight at 60/60 HP, where I took no damage. Also the yellow aim arcs.
- **Biggest frustration:** The 37 minutes hunting for a jackable site, and the nudge buttons silently doing nothing.
- **One thing to change or add right now:** Say plainly on the Q/E buttons that they need a nudge card. Also mark the starter site clearly on the grid.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Combat aiming | 2.0–2.3m, 43–48m | Click on wheel to target | Clicks ignored, keyboard worked | wrong | 0021, 0355 |
| 2 | Loot firmware | 42.0m, 85.2m | Offered chip installs | "Does not fit OVERFLOW slice" | wrong | 0305, 0634 |
| 3 | Loot sheet | 42.0m, 85.3m | Continue works | Clicks ignored | wrong | 0304, 0635 |
| 4 | Ring Tap | 43.2m | Playable card | "Target has no inner ring" | wrong | 0311 |
| 5 | Undo | 46.5m | Rewind turn | Blocked after random pick | wrong | 0343 |
| 6 | Event keys | 85.9m | Key 2 picks option | Nothing happened | cosmetic | 0639 |
| 7 | Crew tab (all flatlined) | 22.0m, 51.5m | Recruit option | Click did nothing | wrong | 0142, 0382 |
| 8 | Tutorial win | 2.5m | Continue button | None, had to Esc | wrong | 0025 |

**Confusion log:**
- 2.0–2.3m — tutorial — wheel aiming clicks missed — resolved with number keys.
- 5.6–14.0m — combat — negative RAM readout — never explained.
- 22.0–38.3m — HQ grid — which site was jackable — about 16 min the first time (about 37 min in total across the first hunt), resolved via Map Key and the orange ring.
- 63.7–77.0m — HQ grid — same hunt again — about 13 min, resolved by orange rings on the left edge.
- 78.1–82.0m — combat — Free Nudge stuck at 0 and Q/E did nothing — about 4 min, resolved partly by tooltip.
- 96.3m — combat — nudge buttons need nudge cards — resolved by tooltip.

## 8. Summary

```
SUMMARY
handle: copperjack
persona: PB-010
focus: cards-firmware-daemons
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 5
operative_deaths: 5
raids_survived: 0
playtime_min: 97
enjoyment: 3
rng_fairness: 3
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: Firewall
weak_picks: Ring Tap, Static Coat, Siphon
bugs: 8
top_frustration: Hunting for the jackable site on the grid, and nudge buttons silently doing nothing without nudge cards
top_change: Explain nudge buttons on screen and clearly mark the starter site on the City Grid
```