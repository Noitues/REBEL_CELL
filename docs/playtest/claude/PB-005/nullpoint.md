# Playtest feedback — nullpoint · PB-005 · build 19ad76a3a10c260a760667a0d6dde27156508740 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** nullpoint
- **Persona / focus / quirks:** Genre veteran / Raids and cell defense / prefers on-screen keyboard shortcuts, visits Terminals (events) whenever possible
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 19ad76a3a10c260a760667a0d6dde27156508740
- **Total playtime:** 22 minutes (142 actions, 1 session). The harness crashed at 21.6 min on a UnicodeEncodeError in its own log print; it was fixed.
- **Campaign setup:** corporation Solace Bio on the route map (target T1 Continuum Billing Farm), ICE not shown in my notes, home server Relay Nest-style 50/50 integrity (variant not recorded), starting roster two Breakers (classes not recorded), campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**: home server **BREACHED** after <n> netruns, in a raid triggered by <cause>
  - [ ] Campaign **won**: final server breached after <n> netruns
  - [x] Campaign **abandoned** / could not continue (why: out of session time after the harness crash. Breaker 1 had died on the L4 Server Rack and I was at HQ with Breaker 2 ready. INCOMPLETE.)
  - Netruns: 1 started, 0 completed, 1 operative death (Server Rack, layer 4)
  - Highest Site tier reached: T1 · Exploits held: 0 · Sites claimed at the end: 0
  - Raids: 0 survived (CELL HOLDS), 0 nodes lost (DOWN / TAKEN). Raids counter at HQ was 0.
  - Final Heat: 11 (band not recorded) · Home server integrity: 50/50
- **Overall enjoyment (1–10):** 4 — The wheel combat was interesting, but the forced corridor map ended in a death I couldn't avoid, and I never reached a raid.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Partly. The free Q nudge onto a good slice and the wheel preview of where a Firmware chip lands were satisfying. But I often sent the turn with most of my RAM unspent, because natural landings did the work.
  - Did SEND IT ever give a different result from the preview chips? Yes. Fight 3, T8 (0094/0095): the preview said -18 against Triage Unit's 14 HP, but it ended at 2/45. The preview seems to ignore its heal or block. Also at 0111, Freeze landed (FROZEN tag) but the -3 lethal preview on me didn't change, and the game doesn't say whether the preview ignores it or Freeze doesn't stop that hit.
  - Did UNDO / rewind behave as expected? Not encountered.
- **Card balance & utility:**
  - Overpowered / automatic picks: Patch+ on the 12 slice (made it an 18). Nothing else stood out.
  - Useless / never worth picking: Inner Drift is dead on a wheel with no inner ring (error banner at 0080). Inner Snap and Gear Shift were also inner-ring cards offered to a deck with no inner ring. Bulkhead was dead on an offensive slice.
- **Synergies & archetypes:**
  - Breaker 1: the deck stayed a small, random-feeling pile (10 → 11 cards plus a few picks). Nothing came together. Against a healer (Triage Unit) I had no way to out-scale the heal, and the loot pool didn't help build toward one.
- **Card text & clarity:** No. Mirror Flip's text is clipped ("Blocked while th..."). Cards overlap and hide costs. The dial markers (1/0, +10, +6) are unexplained. The turn-1 RAM is 6/12 with no reason given.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netrun just right until the Rack (~17 min for 3 fights and part of a Rack). Whole campaign not judged.
- **Netrun map & encounters:** It was a corridor. Every next node had exactly one option: Fight L2, Fight L3, then a forced Rack L4. I saw no Terminal, shop, elite or heal. Grid View's "PICK THE NEXT NODE" panel offered a single entry (0104).
- **City Grid & HQ:** The HQ loop after death was fast, which I liked. The Defence tab was only a hint ("Armory empty: runs bank assets from their drops"), so there was no way to prep the cell. The Market offers Warm Cache 10, Overclocked Deck 15, Field Kit 20 and a Breaker recruit for 15. Tooltips didn't clearly line up with the buttons. I bought Field Kit (+2 max RAM next netrun).
- **Heat:** Heat was 11 after the death. I couldn't judge predictability or thresholds.
- **Raids:** Not encountered.
- **RNG & fairness (1–5):** 4 — Forced into a Rack at 11/60 HP with no healing option, and its opening preview was lethal-range (-11 on 11 HP).
- **Permadeath & meta-progression:** The death felt unearned because the map gave me no choice. Schematics (20) carried over. I didn't get far enough to judge the unlocks.

## 4. UI, controls & audio

- **Information in combat:** The enemy needle preview and damage chips are clear and readable. But the preview misleads against healers and block, and Freeze's effect isn't reflected. Small captions ("LAST TURN: ...") are hard to read.
- **Information outside combat:** I couldn't find what the route options meant beyond the tooltip. The HP max is hidden behind the AT LARGE stamp on the dossier. Node types are hard to tell apart without hovering. The TARGET label is unexplained.
- **Controls:** Space on the loot sheet only highlights card 1, and Continue takes the lit one. The highlight looks too much like a done pick. Clicking Fine Tune and then the wheel body did nothing three times, with no hint on the wheel. The Q nudge worked as the target. Tutorial popups appeared in the first fight even though I skipped the tutorial.
- **Visual feedback:** The wheel preview and FROZEN tag were clear. The PROCEED button is hidden under the LOOT sticker on the fight-won screen (0028).

## 5. Focus questions (Raids and cell defense)

1. Did the projected outcome in setup match the result? — Not encountered. I never reached a raid. The only preview/result mismatch I saw was in combat (the Triage Unit lethal preview).
2. Did you understand why a node went DOWN or TAKEN? — Not encountered.
3. Did raids feel like a puzzle you could solve, or a tax? — Not encountered. The Defence tab at HQ was empty with just a hint, so there was nothing to set up yet.

## 6. Open feedback

- **Favourite moment or build:** Patch+ on the 12 slice, with the wheel preview showing the chip's landing spot, and a clean lethal on the Dosage Dispenser in 4 turns.
- **Biggest frustration / moment you wanted to quit:** The forced L4 Rack at 11/60 HP after three fights with no healing, which killed Breaker 1 (0113).
- **One thing to change or add right now:** Give the route map real choices (at minimum a heal, shop or event before a Rack), and don't force a Rack at low HP.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity (crash / blocker / wrong / cosmetic) | Shot |
|---|---|---|---|---|---|---|
| 1 | Combat L3 | T8 send, 15.2m | Lethal preview -18 vs 14 HP kills | Enemy ended at 2/45 | wrong | 0094/0095 |
| 2 | Combat L4 Rack | Freeze, 19.2m | Preview reflects Freeze | -3 lethal preview unchanged | wrong | 0111 |
| 3 | Combat L3 | Fine Tune then wheel click, 13.9m | Wheel click works or gives a hint | Three clicks did nothing | wrong | 0086 |
| 4 | Fight-won screen | 5.5m | Readable PROCEED | LOOT sticker covers PROCEED | cosmetic | 0028 |
| 5 | Loot sheet | 5.7m | Clear lit/picked state | Lit card looks already taken | cosmetic | 0029/0030 |
| 6 | Firmware drop | 16.6m | Slot choice | Both offers target Slot 1, making one useless | wrong | 0102 |
| 7 | Harness | 21.6m | n/a | UnicodeEncodeError in its log print (harness, fixed) | crash | not shown |

**Confusion log:**
- 2.6m — Combat T1 — tutorial popups after skipping the tutorial — brief, Skip button resolved it.
- 6.6m — Combat L2 T1 — only 6/12 RAM, no explanation — never resolved.
- 13.3m — Combat T6 — Inner Drift error on a wheel with no inner ring — resolved by the error banner, but the pick was wasted.
- 17.2m — Grid View — "PICK THE NEXT NODE" with a single option — checked Grid View, no alternative existed.
- 21.4m — HQ Market — hover tooltips didn't line up with the buttons — resolved by hovering back and forth.

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: nullpoint
persona: PB-005
focus: raids
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 1
raids_survived: 0
playtime_min: 22
enjoyment: 4
rng_fairness: 4
netrun_length: just right
campaign_length: just right
text_clear: no
op_picks: Patch+
weak_picks: Inner Drift, Bulkhead, Inner Snap, Gear Shift
bugs: 7
top_frustration: Forced L4 Rack at 11/60 HP with no heal or alternative node killed the operative
top_change: Offer real route choices (heal/shop/event) and don't force a Rack at low HP
```