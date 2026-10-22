# Playtest feedback — tinroof · PB-SOL-1 · build 52626bcd24d785a8dd7c75b213a52ea639892935 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** tinroof
- **Persona / focus / quirks:** Roguelite newcomer / Economy and difficulty curve / never reads tooltips unless stuck more than three actions; always picks the leftmost option
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 52626bcd24d785a8dd7c75b213a52ea639892935
- **Total playtime:** 30 minutes (495 actions, 1 session)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, home server Standard, starting roster Breaker crew, campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**: home server **BREACHED** after <n> netruns, in a raid triggered by <cause>
  - [ ] Campaign **won**: final server breached after <n> netruns
  - [x] Campaign **abandoned** / could not continue (why: soft-lock. At the first Solace raid I could not station Breaker 3 in Raid Setup (Stationed 0). Roughly 20 minutes of clicking changed nothing. Marked stuck.)
  - Netruns: 3 started (2 completed fights, 1 aborted by flatline on turn 1), 2 operative deaths (Breaker 1 on the Dosage Dispenser fight turn 1, Breaker 2 vs Recall Unit turn 7; both in the Site's netrun route, not a Rack)
  - Highest Site tier reached: T1 · Exploits held: 0 · Sites claimed at the end: 0
  - Raids: 0 survived (CELL HOLDS), 0 nodes lost (the first raid was never resolved)
  - Final Heat: 25 (NOTICED) · Home server integrity: 50/50
- **Overall enjoyment (1–10):** 3 — The cyberpunk look is great, but the wheel rules were never clear to me and I hit a wall at the first raid.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Not to me. I played the leftmost card and read the numbers. I never landed a PERFECT (perfects=0 in every fight). GOOD/WEAK tags never made sense to me.
  - Did SEND IT ever give a different result from the preview chips? Not noticed. I only compared a few previews, and they seemed to match.
  - Did UNDO / rewind behave as expected? Yes. I undid Brute Spin about six times on turn 1 vs the Recall Unit because I could not tell what it would gain. The tooltip says "spin 6 ticks" and not what that pays out.
- **Card balance & utility:**
  - Overpowered / automatic picks: Firewall ("gain 6 block") was the only card I fully understood, so I leaned on it. Jolt was my default damage card.
  - Useless / never worth picking: I can't judge. I picked leftmost every time (Nudge Driver, Sanitize, Patch+, Firewall) without understanding the alternatives.
- **Synergies & archetypes:** Not a strategy at all for me. The deck was a pile and I clicked leftmost cards.
- **Card text & clarity:** No. Confusing words: wheel, nudge, RAM, RESPIN, Resist, Guard, hack, Firmware, "Shunt ... neighbors and Perfect", Overdrive, GOOD/WEAK tags, "glowing target". The tutorial buried me in jargon, and its Next button went dead for several clicks.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netrun fights ran 6–8 turns each (~3–5 min). Whole campaign: too short, because I never got past the first raid (~30 min).
- **Netrun map & encounters:** I saw Fight rooms, one Event (Wellness Kiosk: +10 HP for +2 Heat), and an Elite Fight I avoided. I never found a REST or shop room on my path. The panels kept saying healing only happens at the run's end.
- **City Grid & HQ:** I bought Warm Cache for 10 Schematics, since it was the leftmost. That left me short of the 15 needed for Breaker 2, so I could not recruit. Stationing was a dead end (see Raids).
- **Heat:** Flatline Heat +11 was shown up front, which helped. But Heat reached 25 and triggered a raid before I understood the basics.
- **Raids:** Raid Setup said "NO CREW STATIONED" and Breaker 3 stayed at Stationed 0 after many clicks on the crew list, the readout, the map node and the tabs. Possible bug, or a step the game never explains. The "hire a rookie when nobody is alive" site text confused me, since Breaker 3 was READY.
- **RNG & fairness (1–5):** 4 — I ended the first fight at 1/60 HP, then went straight into a fight with no way to heal, and died on turn 1.
- **Permadeath & meta-progression:** Losing Breaker 1 on turn 1 felt unearned. I arrived at 1/60 with no heal option. It did not make me want another campaign right away.

## 4. UI, controls & audio

- **Information in combat:** HP and RAM were visible. The RAM cost line, "NEXT TURN" and the wheel pointers were not understandable. The Fine Tune "click a glowing target" prompt was hard to satisfy, and clicking wheels did nothing visible. The Jolt card gave no clear "queued" sign. Only the small THIS TURN box showed it.
- **Information outside combat:** I looked for a REST room, an explanation of the route icons, and how to station crew. I couldn't find any of them. The loot sheet blanks the unpicked cards, so I couldn't tell whether the pick was locked in.
- **Controls:** Several clicks were ignored: tutorial Next, JACK IN (4 clicks), DEFENSE (several clicks, then it suddenly acted), and BACK TO HQ. The CONTINUE and SKIP buttons look alike on the loot sheet.
- **Visual feedback:** Not clear enough for me to feel impact. I couldn't tell what landed.

## 5. Focus questions (Economy and difficulty curve)

1. Where did difficulty spike, and where was it flat? — The spike was the second consecutive fight. The first Collections Agent fight left me at 1/60 HP (hp_lost=59), then the Dosage Dispenser killed me on turn 1. The Recall Unit (106 HP, a 15-damage wedge) also killed Breaker 2. The first T1 fight (hp_lost=31) was gentler. Healing was too scarce to recover between fights.
2. Were shop prices fair for what you could afford? — Not fair for me. Breaker recruit was 15 Schematics, and the boosts cost 10/15/20. I started with 20, spent 10 on Warm Cache, and could not afford the recruit. I couldn't tell which boost mattered.
3. Was any resource always too scarce or always piling up unused? — HP was always scarce, with one +10 heal seen in the whole run. Schematics were pinched (10 at the end, nothing affordable). Cycles piled up and were wasted: 42 were lost when Breaker 1 flatlined, and I never found a shop to spend them in. Cycles were 58 at the end.

## 6. Open feedback

- **Favourite moment or build:** The Wellness Kiosk event, the one place I could heal. The Firewall block card was the only thing I fully got.
- **Biggest frustration / moment you wanted to quit:** The raid stationing dead end. About 20 minutes of clicks and nothing happened.
- **One thing to change or add right now:** Explain wheels, RAM and RESPIN in plain words early, and make station-crew in Raid Setup obvious and responsive. Also offer a heal between fights.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity (crash / blocker / wrong / cosmetic) | Shot |
|---|---|---|---|---|---|---|
| 1 | Raid Setup, Solace raid 1 | Clicked crew list, readout, node A, tabs (24.7m–30.5m) | Breaker 3 gets stationed | Stationed 0, NO CREW STATIONED, no response | blocker | 0308.png |
| 2 | Tutorial 12/12 | Clicked Next repeatedly (1.4m–2.0m) | Text advances | Dead clicks for a long while | wrong | 0022.png |
| 3 | Campaign map JACK IN | 4 clicks at lower-right (5.3m) | Jack in | Ignored until I used centre/Enter | wrong | 0064.png |
| 4 | HQ DEFENSE button | 3+ clicks (14.0m–14.2m) | Panel opens | Nothing, then a sudden dispatch transition | wrong | 0156.png |
| 5 | Netrun summary BACK TO HQ | Repeat clicks (23.9m) | Return to HQ | Clicks seemed to do nothing at first | wrong | 0248.png |
| 6 | Fine Tune targeting | Clicked wheels (16.8m–17.0m) | Card plays | No visible effect | wrong | 0184.png |
| 7 | Loot sheet | After picking a card (8.1m, 18.9m) | Cards stay visible | Other cards blank, so the choice looks locked or unclear | cosmetic | 0202.png |
| 8 | HQ map, crew card | 24.1m | Clear hire wording | Card stamped FIRE with FREE label, site text says hire a rookie | cosmetic | 0250.png |
| 9 | HQ map overlaps | Screen audit | Readable stamps | DESIGNATED/DECRYPTED stamps under the SAVED button, ticker text clipped | cosmetic | 0141.png |

**Confusion log:**
- 1.4m — Tutorial 12/12 — Next did nothing — about 0.6m, resolved on its own
- 4.1m — Tutorial turn 6 — what RESPIN does — about 1.5m, resolved by reading its tooltip
- 5.3m — Campaign map — JACK IN ignored clicks — about 0.3m, resolved by clicking centre/Enter
- 8.1m — Loot sheet — whether the card pick was locked — about 0.3m, resolved with CONTINUE
- 16.4m — Fine Tune targeting — what the glowing target wanted — about 0.8m, never resolved, cancelled and sent the turn
- 21.3m — Turn 1 vs Recall Unit — what Brute Spin gains — about 1.3m of undos, never resolved
- 24.1m — HQ — rookie-hire line vs Breaker 3 READY — never resolved
- 24.7m — Raid Setup — how to station crew — about 6m of attempts, never resolved

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: tinroof
persona: PB-SOL-1
focus: economy-difficulty
build: 52626bcd24d785a8dd7c75b213a52ea639892935
outcome: INCOMPLETE
netruns_completed: 2
operative_deaths: 2
raids_survived: 0
playtime_min: 30
enjoyment: 3
rng_fairness: 4
netrun_length: just right
campaign_length: too short
text_clear: no
op_picks: Firewall, Jolt
weak_picks: none
bugs: 9
top_frustration: Could not station Breaker 3 for the first Solace raid; Raid Setup stayed at Stationed 0 and nothing responded.
top_change: Explain wheels, RAM and RESPIN in plain words early, make stationing crew in Raid Setup obvious and responsive, and add a heal between fights.
```