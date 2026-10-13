# Playtest feedback — neon_moth · PB-010 · build 19ad76a3a10c260a760667a0d6dde27156508740 · session date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** neon_moth
- **Persona / focus / quirks:** Story and tone fan (novice) / Economy and difficulty curve / always picks the rightmost option when two choices look equal
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard. Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 19ad76a3
- **Total playtime:** 60 minutes (857 actions, 710 steps, 2 sessions: I quit to the title once and used Continue)
- **Campaign setup:** corporation Solace Biosystems, ICE not shown, home server standard (Home 50/50), starting roster Breaker ×2 (one more recruit slot, CREW x/3), campaign code shown on the pause menu as "RC1-solace-0-1-home_standard-breaker"
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue: out of time (INCOMPLETE). I spent the second half on the HQ map clicking locked nodes, with both Breakers flatlined.
  - Netruns: 3 started, 0 completed, 2 operative deaths (Breaker 1 on layer 2 in a Dosage Dispenser fight; Breaker 2 on layer 1 vs the Collections Agent). The first fight of netrun 1 was won.
  - Highest Site tier reached: T1 · Exploits held: 0/3 · Sites claimed at the end: 0
  - Raids: not encountered
  - Final Heat: 22 (COOL) · Home server integrity: 50/50
- **Overall enjoyment (1–10):** 4 — the writing and the radio ticker are great, but I lost most of the hour to a map I couldn't read and combat rules nobody explained.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? In the tutorial, yes: Q/E tilting felt like a dial. In real fights I was mostly guessing, because nudges showed nothing until SEND IT.
  - Did SEND IT ever give a different result from the preview chips? Not clearly. Against the Collections Agent (turn 3 to 4, 0111–0117) the Agent stayed at 40/40 through three rounds of nudges, then dropped to 31/40 on SEND IT. The damage only showed up at resolve.
  - Did UNDO / rewind behave as expected? Not encountered.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen.
  - Useless / never worth picking: I can't judge. I picked the rightmost reward (Leech Worm) by habit, and I never tested it.
- **Synergies & archetypes:** Not encountered. I only ran the starting Breaker deck of Jolt, Fine Tune, Brute Spin, Overdrive and Mirror Flip, and it felt like a pile.
- **Card text & clarity:** No. Overdrive and Mirror Flip descriptions were clipped ("OVERCLOCK your slid... under th...", "Blocked while th..."), the tooltip bar covered the lower cards, and the RAM readout showed baffling "(-1)" / "(-2)" values.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** Netrun: the first fight took about 2.5 minutes and 13 turns. Campaign length: can't judge, since I never got past the first layer.
- **Netrun map & encounters:** I saw only Fight nodes. No Terminal appeared in reach on layer 1 or 2. The operative kept saying "Patch me at the next Terminal", but I never found one.
- **City Grid & HQ:** Almost every site was locked behind another site, and the locked nodes gave no feedback when clicked. I assumed the map was broken and wasted roughly 30 clicks, then dozens more. The gate text appears only in the side panel. The panel names a gate site that I couldn't match to any marker on the map. The "DECRYPTED" stamp on a "Not reachable yet" card contradicts it. The Market, Heat Scrub and recruit options were readable, and I bought Overclocked Deck.
- **Heat:** I couldn't predict it. The only definition was a Codex Lexicon entry ("How hard the corporation is looking for you. Thresholds fire raids and complications."), and it took many clicks to reach. Thresholds weren't spelled out anywhere I saw. Each flatline added +11 (0 → 11 → 22).
- **Raids:** Not encountered.
- **RNG & fairness (1–5):** 3 — I entered the second fight at 2/60 HP with no way to heal, and the loss felt more like missing information than bad luck.
- **Permadeath & meta-progression:** The deaths were my own doing, but nothing warned me that HP carries between fights. Losing both Breakers left the campaign nearly stuck, with a 15-Schematic recruit I couldn't afford.

## 4. UI, controls & audio

- **Information in combat:** HP and RAM were visible. Nudge effects, the win condition (shown only in a tooltip, and stale after the win) and the end-turn rule weren't clear. I mentioned the unexplained SEND IT in the tutorial, and the tooltip explaining it only appeared on turn 2 of the first real fight.
- **Information outside combat:** I looked for what Heat does and found nothing on the map. I looked for the Codex and it took about 20 clicks through MORE, until I found it in the pause menu.
- **Controls:** The map swallowed clicks on locked nodes with no feedback. The quit buttons seemed to do nothing for a long stretch of the session. The pause-menu Quit to Desktop gave no response, and the Quit confirm dialog later also ignored clicks, Enter and the A key. The "KEEP GOING" sticker may cover the QUIT button.
- **Visual feedback:** The title, stickers and ticker have strong mood. Hits and spins didn't feel impactful, since the results landed only on resolve.

## 5. Focus questions (Economy and difficulty curve)

1. **Where did difficulty spike, and where was it flat?** It spiked in the Billing Daemon fight, where I ended at 2/60. That fight dragged on for 13 turns. It spiked hard again at the next node, because I arrived with no HP and no heal, and it spiked on the Collections Agent fight, where I died at turn 12. The map and HQ showed no ramp at all, only a lock wall.
2. **Were shop prices fair for what you could afford?** Mostly unclear. With 20 Schematics: Warm Cache 10, Overclocked Deck 15, recruit Breaker 15, Heat Scrub 25, and Class: Wrecker 60. I bought the Deck, which dropped me to 5, and I couldn't afford anything else. Heat Scrub at 25 was out of reach at 20 and 5, and it was the only Heat fix. The Deck charged on queue with no delivery timing shown.
3. **Was any resource always too scarce or always piling up unused?** Schematics were always scarce: 20 banked after netrun 1, then 5. Heat only rose (11 → 22) and I had no means to lower it. Cycles (21 earned) were lost on death, so I never spent them. HP never recovered in any fight.

## 6. Open feedback

- **Favourite moment or build:** The Lexicon (LEASH, SUBBIE, BRICKED, ICE, DISPATCH). The ticker line about Solace patient data and "Solace will bill the family" after the flatline also landed.
- **Biggest frustration / moment you wanted to quit:** The locked-node loop on the HQ map, which ate the second half of the session. The tutorial never defined SEND IT, and I lost the sim on turn 11.
- **One thing to change or add right now:** Show the reason on the node itself when a locked site is clicked, and draw the links between gated sites on the map.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Tutorial 1/7 retry | ~3.0m | Next button usable | Greyed; only Skip live | wrong | 0030.png |
| 2 | Tutorial sim | 1.4–2.5m | SEND IT explained | Never said it needs a card; sim lost on turn 11 | wrong | 0024.png |
| 3 | HQ map locked nodes | 17–60m | Feedback on click | No response, only the side panel text | wrong | 0348.png |
| 4 | Site card | various | Status matches text | "DECRYPTED" stamp on "Not reachable yet" | cosmetic | 0349.png |
| 5 | Combat RAM readout | 12.2–12.9m | Plain RAM number | "(-1)" / "(-2)" beside RAM, unexplained | wrong | 0124.png |
| 6 | Pause menu / Quit | 52–56m | Quit to Desktop or confirm | Clicks ignored many times; no confirm appeared | blocker | 0657.png |
| 7 | Quit confirm dialog | 56–60m | QUIT works | Ignored clicks, Enter and A key | blocker | 0657.png |
| 8 | Fight-won screen | 7.8m | Win rule shown early | "Bring its HP to 0" text appeared only after the win | cosmetic | 0083.png |
| 9 | Combat hand | various | Readable card text | Overdrive, Mirror Flip clipped; tooltip covers cards | cosmetic | 0061.png |

**Confusion log:**
- 1.4m — tutorial sim — SEND IT does nothing without a committed card — about 1 minute, never resolved by the tutorial.
- 11.0m — Collections Agent fight — nudges showed no effect — 0.5 min, resolved only when I pressed SEND IT.
- 13.5m — campaign map — both Breakers flatlined, "rest at HQ" — about 1.5 min, partly resolved by opening the CORE panel.
- 17–60m — HQ map — which locked node to click and why — never resolved; the Heat definition took about 20 clicks to find.

## 8. Summary

```
SUMMARY
handle: neon_moth
persona: PB-010
focus: economy_difficulty_curve
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 2
raids_survived: 0
playtime_min: 60
enjoyment: 4
rng_fairness: 3
netrun_length: just right
campaign_length: too long
text_clear: no
op_picks: none
weak_picks: none
bugs: 9
top_frustration: Locked map nodes gave no feedback, so I lost most of the hour clicking them, and the tutorial never explained SEND IT.
top_change: Show the lock reason on the node itself and draw the gate links on the map.
```