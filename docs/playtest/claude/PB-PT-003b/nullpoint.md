# Playtest feedback — nullpoint · PB-PT-003b · build 3eac0f086e6d32f23afd7c95dbb0e7eb35379339 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** nullpoint
- **Persona / focus / quirks:** Roguelite newcomer / Bug hunting and edge cases / takes every card reward, sticks with the same operative class (Breaker)
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 3eac0f086e6d32f23afd7c95dbb0e7eb35379339
- **Total playtime:** 40 wall-clock minutes (393 actions, 1 session; I quit via the pause menu at the time limit, no Continue tested)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, Standard Home Server, starting roster Breaker, campaign code: a campaign code field was visible in the pause menu, but the value is not recorded in my notes
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time; INCOMPLETE). I was on turn 2 of the fight vs Claims Adjuster (fight 4) at 2/60 HP, marked LETHAL.
  - Netruns: 1 started, 0 completed, 0 operative deaths. I won 3 fights (Billing Daemon, Dosage Dispenser, Triage Unit) and was in the 4th.
  - Highest Site tier reached: T1 (Continuum Billing Farm) · Exploits held: not encountered · Sites claimed at the end: not encountered
  - Raids: not encountered
  - Final Heat: 0 · Home server integrity: not encountered
- **Overall enjoyment (1–10):** 4 — the cyberpunk look is great, but the jargon and the fights that kept eating my clicks wore me down.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Not really. I never worked out what a nudge does. The previews (HP 42->24 and so on) were my only guide. The tutorial fight and the first real fight both showed zero Perfects for me.
  - Did SEND IT ever give a different result from the preview chips? Not confirmed. A few HP and RAM readings differed from my notes (17/60 vs 10/60 on turn 3 vs Dispenser, RAM 9/12 vs 11/12), but I think that was my misreading.
  - Did UNDO / rewind behave as expected? No. On turn 2 vs Claims Adjuster the UNDO button ignored six clicks, and Z and ctrl+z did nothing. Earlier, the UNDO tooltip said it was blocked because the turn began with a random spin, which nobody had told me about.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen.
  - Useless / never worth picking, and why: can't judge. I took everything. Nudge Driver ("nudge cards trigger twice next turn") means nothing to someone who doesn't know what a nudge is.
- **Synergies & archetypes:** Breaker was a random pile for me. I took every reward (Nudge Driver, Sanitize, Inner Snap, Patch+ twice). No strategy came together, though that is partly my lack of understanding.
- **Card text & clarity:** No. Confusing terms: FREE NUDGE, NULL, nudge, Corrupted, "Weak to Good", the PICK 1 OF 3 label. Card descriptions are truncated. Clear ones: Jolt, Mirror Flip, Hub Breaker Core and the LETHAL tooltip.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** a fight runs about 2–10 minutes at my slow pace. The Triage fight took 16 turns. Whole campaign: not finished, so I can't say.
- **Netrun map & encounters:** I only saw Fight nodes on the route map. The only open path was a single node on L3 and L4. Not enough seen to judge variety.
- **City Grid & HQ:** not encountered
- **Heat:** Heat stayed at 0 and I never saw it matter. The tutorial's Heat and banking text was jargon-heavy.
- **Raids:** not encountered
- **RNG & fairness (1–5):** 3 — healing only at run end meant I carried 23/60, then 8/60, then 2/60 into the next fights. That felt harsh for a cautious player.
- **Permadeath & meta-progression:** not encountered. Most targets and crew were locked behind unlock costs at campaign setup.

## 4. UI, controls & audio

- **Information in combat:** Enemy wheels and previews are readable. HP and RAM are findable. The FREE NUDGE banner is never explained, and neither is NULL. Hovering helped for some elements. The "Q/E nudge your wheel, W nudge the target" hint at the top is the first plain help, but I only found it after many turns. The Fine Tune card raised over the stat row covers the deck and discard counters. The tooltip on turn 2 vs Claims Adjuster covers the player wheel.
- **Information outside combat:** I couldn't tell whether the Patch+ and Nudge Driver picks were applied. The loot sheet jumped straight to the route map. The Codex Lexicon has 214 entries and no "nudge" entry.
- **Controls:** Esc during targeting opens the pause menu instead of cancelling the card. Right-click on the Fine Tune card selected Overdrive instead. Card selection appeared to flip between Jolt and Overdrive on turn 2 of fight 1. Clicks on the enemy wheel often gave no visible result, and the aim arrow only showed after a delay. UNDO clicks were dead.
- **Visual feedback:** The wheel preview and skull markers are good. Feedback on committing a click is weak or slow.

## 5. Focus questions (Bug hunting and edge cases)

1. **List every bug with its exact steps (actions.log lines).** See the table in section 7. The actions.log lines themselves are not in my notes, so I give journal times instead.
2. **Did Quit then Continue ever restore a different state from the one you left?** Not tested. I used the in-game Quit at the time limit. Pause then Resume mid-fight restored the same state (turn 2 at 7.1m, turn 14 at 29.5m).
3. **Did any input get lost or applied twice?** Yes, lost inputs. Repeated enemy-wheel clicks with a card selected often showed nothing, then registered later (e.g. 25.9m, 29.7m). UNDO clicks were ignored six times (37.7–39.5m). Card selection flipped between Jolt and Overdrive (8.2–9.7m). Nothing was applied twice that I saw.

## 6. Open feedback

- **Favourite moment or build:** Turn 6 vs Billing Daemon, when the preview showed the kill clearly with a skull marker. Surviving the 16-turn Triage fight at 2 HP was also tense.
- **Biggest frustration / moment you wanted to quit:** Clicking the enemy wheel over and over with no feedback (turns 12–14 vs Triage), and an UNDO that did nothing while I was staring at LETHAL.
- **One thing to change or add right now:** Define "nudge" and FREE NUDGE in plain words on the combat screen, and add a glossary tooltip. Make Esc cancel a selected card, and make UNDO work.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Combat T2 vs Claims Adjuster | Stage Fine Tune, click UNDO six times, try Z and ctrl+z (37.7–39.5m) | Staged card rewound | Nothing happened | wrong | 0251.png |
| 2 | Combat, card selected | Select a card, press Esc (6.9m, 23.8m, 34.0m, 38.3m) | Selection cancelled | Pause menu opened | wrong | 0161.png |
| 3 | Combat T2 vs Billing Daemon | Click cards and the enemy wheel (8.2–9.7m) | Clicked card stays armed | Selection flipped between Jolt and Overdrive, commit didn't land | wrong | 0060.png |
| 4 | Combat T2 vs Billing Daemon | Right-click the Fine Tune card (6.8m) | Card info or cancel | Overdrive got selected | wrong | 0046.png |
| 5 | Combat T12–T14 vs Triage | Click the enemy wheel with Jolt or Brute Spin selected (22.5–29.7m) | Immediate aim/commit feedback | No visible change for many clicks, then the aim appeared late | wrong | 0189.png |
| 6 | Loot, Firmware pick | Pick Patch+ (15.6m, 31.1m) | Confirmation | Jumped to the route map with no confirmation | cosmetic | 0107.png |
| 7 | Route L2 and L4 | Press Enter on the node (11.6m, 31.6m) | Not sure | Fight started with no further prompt (I had expected the route map) | cosmetic | 0077.png |
| 8 | Combat screens (screen audit) | Turn 1 vs Claims Adjuster; fight-won screen | Clean layout | Fine Tune card covers the stat row and piles. The tooltip truncates its text. EXECUTE ghost text overlaps SEND IT. CONTINUE overlaps a PROCEED panel. | cosmetic | 0241.png / 0020.png |
| 9 | Combat T2 vs Claims Adjuster | Hover the LETHAL tag (37.1m) | Concise preview | Dense tooltip covering the wheel, header cut at "YOU", garbled ALL RESULTS line | cosmetic | 0246.png |

**Confusion log:**
- 1.1m — Tutorial — jargon (RAM, nudge, slice, needle) — followed it anyway.
- 6.4m — Combat — NULL tag — about 1 min until I found the PRECISION TAG tooltip.
- 7.6m–21.2m — Combat — FREE NUDGE banner — never resolved; the top-banner tooltip only explains Q/E/W.
- 18.1m — Combat — UNDO tooltip cites a random spin — never told about it.
- 31.6m–36.0m — Combat and Codex — what "nudge" does — about 5 minutes; only partly resolved by the Nudge Driver tooltip.
- 37.2m — Combat — "Corrupted" — not resolved.

## 8. Summary

```
SUMMARY
handle: nullpoint
persona: PB-PT-003b
focus: bug hunting and edge cases
build: 3eac0f086e6d32f23afd7c95dbb0e7eb35379339
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 0
raids_survived: 0
playtime_min: 40
enjoyment: 4
rng_fairness: 3
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: Nudge Driver, Sanitize, Patch+, Inner Snap
weak_picks: none
bugs: 9
top_frustration: Never learned what FREE NUDGE or nudge means, and clicks, Esc and UNDO did not respond as expected.
top_change: Define nudge and FREE NUDGE in plain words on the combat screen, make Esc cancel a selected card, and fix UNDO.
```