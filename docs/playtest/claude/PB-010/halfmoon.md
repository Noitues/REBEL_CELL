# Playtest feedback — halfmoon · PB-010 · build 19ad76a3a10c260a760667a0d6dde27156508740 · session date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** halfmoon
- **Persona / focus / quirks:** Keyboard-first player (intermediate) / First hour and onboarding / prefers shown keyboard shortcuts; quits to title and uses Continue once per session (I did it several times, and the save held each time).
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 19ad76a3a10c260a760667a0d6dde27156508740
- **Total playtime:** 78 minutes (766 actions, 564 steps; quit to title and continued several times)
- **Campaign setup:** corporation Solace Biosystems, ICE not shown, home server variant not shown, starting roster 2 Breakers, campaign code not shown (a pause menu showed a campaign code, but I did not note the value).
- **How far did you get?**
  - [x] Campaign **lost**: home server **BREACHED** after 6 netruns, in a raid triggered by Heat crossing 75 (Collections Final Notice) with no crew left to defend.
  - Netruns: 6 started, 0 completed, 6 operative deaths (Breaker 1 at L3 vs Triage Unit; Breaker 2 at L2 vs Recall Unit; Breaker 3 at L1 vs Collections Agent; Breaker 4 at fight 3 vs Compliance Officer; Breaker 5 at L6 Elite Claims Adjuster; Breaker 6 at fight 2 vs Billing Daemon). The journal does not say which node types those were, only the layer numbers.
  - Highest Site tier reached: T1 · Exploits held: 0 (Exploits 0/3 seen) · Sites claimed at the end: 0
  - Raids: 2 survived (CELL HOLDS), the final raid breached the Core (shown as "Campaign lost"). The journal says nothing about nodes lost (DOWN / TAKEN).
  - Final Heat: 80 (Hunted) · Home server integrity: 0/50
- **Overall enjoyment (1–10):** 3 — I died six times without ever understanding the wheel, and the fights I won felt accidental.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Not really. I never got a clear read on what the red/green chips beside HP and RAM meant, so I couldn't plan. Some fights were stalls (Triage Unit regenerating, my wheel stuck on the 1/0 slice for 20 turns).
  - Did SEND IT ever give a different result from the preview chips? Not reliably judged. The preview chips were unlabelled, so I couldn't compare them with the outcome.
  - Did UNDO / rewind behave as expected? Partly. Z worked and refunded RAM, but it was often blocked ("a random event came since the last respin"). The tutorial's undo step didn't warn about that limit, and I couldn't complete it as written.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen.
  - Useless / never worth picking: not judged with confidence. Static Coat could not be slotted on an OVERFLOW slice, which made that firmware pick feel wasted.
- **Synergies & archetypes:** I only ran Breakers and the deck felt like a random pile. The hand also changed between turns with no notice, so I could not build a plan.
- **Card text & clarity:** No. Card descriptions were cut off (e.g. Mirror Flip's "Blocked while th..."), and "Free Nudge", the RAM (-1) chip, the HP chips and the 1/0 slice were never explained.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netrun too short in practice, because I died early (about 4–15 min each, with one 20-turn fight); whole campaign just right in length for a loss (~78 min).
- **Netrun map & encounters:** I saw fights, an event (Wellness Kiosk, Patient Records), a shop (Mainframe Shop) and an Elite. Often only one next node was offered. At low HP the choices felt forced.
- **City Grid & HQ:** Hunting for the first open site cost me roughly 3 minutes each time (twice). The locked-site tooltips are clear, but nothing points to the starting site until you open the Map KEY. Recruiting is via Market, not the Crew tab, and the Crew tab shows no recruit option.
- **Heat:** I could not predict it. It jumped to 80 after flatlines (+11 or +12 each time), and I'd have liked a warning before the 75 raid threshold.
- **Raids:** Setup and playout were readable via the live feed. However, the banner still said "RAID IN PROGRESS" after "Raid over", and with zero crew START DEFENSE gave no warning.
- **RNG & fairness (1–5):** 3 — the undo block from random events and the hand reshuffles felt arbitrary, but most deaths were my own misunderstanding.
- **Permadeath & meta-progression:** Permadeath was clear on screen. Several deaths felt unearned because wheel aiming failed (clicks not registering). I did not get far enough to judge profile unlocks.

## 4. UI, controls & audio

- **Information in combat:** HP, RAM and the enemy wheel are visible. The red/green chips and the RAM (-1) readout are unlabelled, the card hand overlaps, and there are three names for ending a turn (SEND IT / EXECUTE / turn_resolve.exe).
- **Information outside combat:** I couldn't find a hint for the starting site, and the TARGET arrow doesn't match the selected site. Several panels were clipped, e.g. the Core text and the news ticker.
- **Controls:** Card number keys, Q/E nudge, Z undo, Space send and Esc pause all work and are shown. Gaps (the keyboard path stops at many of these):
  - Tutorial Next answers only to Space, with no hint shown (Enter and Tab+Enter did nothing).
  - Title menu, JACK IN, node picking on the map, Continue on the loot sheet, BACK TO HQ, START DEFENSE, raid CONTINUE, recruit buttons, and the audit-screen MAIN MENU / NEW CAMPAIGN show no key.
  - Slot selection: Enter did nothing on the first try.
  - Wheel targeting after selecting a card has no keyboard step. Clicks on the wheel often did nothing, and aims lingered through Esc and Z.
  - Number keys pressed in combat leaked into the loot picks and auto-took cards or firmware.
  - Event keys 1/2/3 only highlighted a choice, and I needed the mouse.
  - Pause menu: only RESUME [Esc] shows a key, and ABANDON sits right next to QUIT.
- **Visual feedback:** The aim arcs and "1 LANDS HERE" previews are clear. The DELETED / FIGHT WON stickers read well. The victory screen offered no visible Continue prompt in the tutorial.

## 5. Focus questions (First hour and onboarding)

1. After the tutorial (or skipping it), what did you still not understand? — What the red/green chips and RAM (-1) meant, what Free Nudge was, what the 1/0 slice does, how to aim a wheel card by keyboard, and why undo is sometimes blocked.
2. Which word, icon or number confused you longest? — The RAM (-1) readout and the red HP chips. I noted them from the second fight and they were never explained, through the last fight (about 70 min).
3. When did the game 'click', if it did? — Only partly. Number keys plus Space was clear by about minute 4. The wheel itself never clicked for me.

## 6. Open feedback

- **Favourite moment or build:** The Fine Tune "1 LANDS HERE" arc preview, and the clear tooltips on locked sites.
- **Biggest frustration / moment you wanted to quit:** Turns 8–9 of the Collections Agent fight, where a wheel aim wouldn't commit and I cycled Esc, Z and the pause menu for several minutes before dying.
- **One thing to change or add right now:** Show a key hint on every button (Next, JACK IN, CONTINUE, BACK TO HQ), add a keyboard step for wheel targets, and label the chips next to HP and RAM.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity (crash / blocker / wrong / cosmetic) | Shot |
|---|---|---|---|---|---|---|
| 1 | Tutorial 1/7 | 0.6–1.1m | Enter advances Next | Only Space works; no hint | wrong | 0008.png |
| 2 | Tutorial 5/7 undo | 1.9–2.2m | Z undoes as taught | Blocked by a random event, not warned | wrong | 0017.png |
| 3 | Combat wheel aim | 16–19m, 35–42m | Click on the wheel commits the aim | Clicks ignored, aim lingered through Esc/Z | blocker | 0156.png |
| 4 | Loot sheet | 8.3m, 10.8m, 11.7m | Combat number keys don't pick loot | Card or firmware auto-taken; CONTINUE unresponsive until a firmware pick | wrong | 0092.png |
| 5 | Loot, firmware | 59.4m | Taken chip can be slotted | Static Coat doesn't fit an OVERFLOW slice | wrong | 0452.png |
| 6 | Event node | 22.4–22.6m | Key 1 selects | Only highlighted; mouse needed | wrong | 0178.png |
| 7 | Route map L2 | 24.4–25.1m | Click travels to the node | Click showed info only; Enter traveled | wrong | 0184.png |
| 8 | Raid result | 29.7m | Banner says the raid is over | "RAID IN PROGRESS" still shown | cosmetic | 0218.png |
| 9 | Combat dialog | 48.3m | Full operative text | Cut off at "The wheel o" | cosmetic | 0377.png |
| 10 | Combat hand | 26.5–27.6m | Stable hand and key mapping | Hand changed between turns, no notice | wrong | 0201.png |

**Confusion log** (moments you did not know what to do):
- 0.6–1.1m — Tutorial 1/7 — Next wouldn't advance — about 30s, resolved by Space.
- 1.9–2.4m — Tutorial 5/7 — undo blocked — never explained, the step moved on.
- 4.7–8.2m — Combat — RAM (-1) and HP chips — never resolved.
- 11.3–11.7m — Loot sheet 2 — CONTINUE dead — about 25s, a firmware pick was pending.
- 16–21m — Combat L1 — wheel aim — about 5 min, never fully resolved.
- 31–33m — HQ map — finding the open site — about 2 min, resolved by the Map KEY.
- 54.3m — HQ map — finding the starting site again — about 3 min, resolved by the Map KEY.
- 56.7–59m — Triage Unit — 1/0 slice stall — never resolved.

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: halfmoon
persona: PB-010
focus: first-hour-onboarding
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: LOST
netruns_completed: 0
operative_deaths: 6
raids_survived: 2
playtime_min: 78
enjoyment: 3
rng_fairness: 3
netrun_length: too short
campaign_length: just right
text_clear: no
op_picks: none
weak_picks: Static Coat
bugs: 10
top_frustration: Wheel aim ignored clicks and had no keyboard step, so I died in fights I could have won.
top_change: Show key hints on every button, add keyboard wheel targeting, and label the HP/RAM chips.
```