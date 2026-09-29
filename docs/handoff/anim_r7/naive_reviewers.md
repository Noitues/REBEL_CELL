# ANIM-R7 naive reviewers (main 7b5c0f8)

Reviewer A: beginner, never played a deckbuilder. Reviewer B: reads English slowly, relies on
icons, colour and motion. Report only. Captures: storyboard at 1.0, 1.6 `--pad`, `--scramble`;
Movie Maker: netrun `--demo-combat --demo-end=win|lose`, `--demo-tutorial`, `--demo-run`,
`--demo-end=died|completed`, `--demo-shop --demo-buy`, `--demo-loot --demo-pick`,
`--demo-event --demo-choose`; hq `--demo-playout`, `--demo-campaign-end=won|lost`; lab
jack_in, heat_banner, heat_number_pop, raid_result_banner.

## Understanding (R6 → R7)
| | Combat | Campaign |
|---|---|---|
| A (beginner) | ~80% → ~75% | ~65-70% → ~70% |
| B (plain text) | ~70% → ~70% | ~60% → ~60% |
| B (scrambled) | ~60% | ~50% |

R6 helped: combat chips with ✓ ticks, WAS row, NEXT / LAST TURN; clear VICTORY/DEFEAT
stamps and LOOT / JACK OUT; run-end pages name the Heat cause; raid playout (moving token,
floats, HOME -5 · HOLDS, RAID RESULT circle); WON (star) / LOST (house). A's combat score
dropped because of P1-1 and P2-1. B still blocked by the English raid feed, the event body,
"same road as choice 1".

## Combat
- **P1-1 Tutorial never shows step 1/7 "THE WHEEL".** `--demo-tutorial`, storyboard 06_fight
  and `--demo-combat` with fresh settings open on "2/7 NUDGE (1/2)". Step 1 has `until: ""`;
  R6 A16 advances such steps on `turn_start` (`tutorial_overlay.gd:242-249`); the fight's
  opening turn_start reaches `on_events` (`combat_scene.gd:1224`) right after
  `start_tutorial` (`:152-157`). Step 1 is the only text explaining needles, tags, dots, NEXT
  and LAST TURN. Fix: ignore the fight's first turn_start (events from before the tutorial
  began); test that step 1 shows on the first drawn frame.
- **P2-1 "HITS BILLING DAEMON 6 → 1 LEFT" next to VICTORY** (win demo frames 40-49): R6 A4 meant
  "only 1 HP was left to take"; both read "enemy has 1 HP left", contradicting VICTORY. "1 LEFT"
  also means Armory copies on raid asset cards. Code: `combat_scene.gd:2775-2778`,
  `clamp_item` `:3867`, `wheel_view.gd:2578`. Fix: "→ 0 HP" / "TAKES THE LAST 1 HP", skull when
  it kills.
- **P2-2 "collections drone" named in chips but not findable** (storyboard 06, 07, 11): only an
  unlabelled hex badge (sword/shield icon, "5") on the enemy wheel's rim; the wheel says
  COLLECTIONS AGENT. Fix: badge icon inside its chip, name the badge (or leader line on
  hover/aim), pulse the badge when its chip ticks.
- **P2-3 Tutorial pages cut sentences; the step advances before the instruction page.** 1.0:
  NUDGE 1/2 ends "…the right one clockwise,", CARDS 1/2 ends "Nudge cards go"; key/drag
  instructions on page 2, never read because the step advances on the action. 1.6: NUDGE 1/5,
  CARDS 1/4, CARDS page overflows (scroll bar, "choose a" half cut) against A16 "never cut".
  Next pulses alpha down to 0.45 (`tutorial_next_pulse`), reads as disabled. Fix: split at
  sentence ends; the action instruction ({nudge_how}/{card_how}) on page 1; pages fit the
  note at 1.6; pulse border/colour, alpha never below ~0.8.
- **P3-1** Tutorial note stays up on VICTORY/DEFEAT still teaching "4/7 CARDS": hide or fold it
  during the end stamp and hold.
- **P3-2** On DEFEAT, "0/60" HP stays green; Heat jumps 0→11 on poster and HUD with no cause
  (cause only on the next page). Fix: HP at 0 red/grey; "+11" float by the poster or hold the
  HUD change until the run-end page.
- **P3-3** The enemy still hits you in the SEND IT that kills it ("HITS YOU 7 ✓" then DOWN).
  Fix: caption "wheels resolve together", or tick DOWN first.

## Netrun screens
- **P2-4 Modem SLICES "BUY 100" stay yellow when unaffordable** (67 and 94 Cycles; chips, cards,
  daemons turn pink). `netrun_scene.gd:2738-2759` never sets `tile.disabled` from cycles vs
  price (compare shred `:2775`). Fix: disabled/pink when `run.cycles < low`.
- **P3-4** Event choice has almost no acknowledgement: `FlightFx.stamp_on(row, "")` stamps a
  snapshot of the row on itself with no word (`flight_fx.gd:173-193`); "no change" shows
  nothing for ~0.6 s then the page leaves. Fix: stamp "TAKEN ✓" or flash the chosen border.
- **P3-5** Route "[2] Fight (same road as choice 1)" and "then: Shop" confuse both. Fix: draw
  the shared road once, highlight both choices on hover; Shop icon on the options it follows.
- **P3-6** At 1.6 the event body can show truncated ("…still warm, still logg"), probably
  event_type still typing at storyboard settle; check typing finishes within settle.

## City, raid, HQ, bake
- **P2-5 (known item, as described)** Raid playout feed and result are English rules text
  ("Step 2: Turret on … hits Collector for 4", "Raid over after 2 step(s)…", "Heat +5: Collector
  reached CORE: 0 → 5"). For B the map carries most, but why Heat rose is text only. Fix: Heat
  icon float at CORE when the collector arrives; icons in feed lines.
- **P3-7** Threat token (white circle, red diamond) not in the MAP LEGEND; "IF THE RAID RUNS NOW"
  circle fades half under the RAID FEED panel during steps. Fix: legend entry; fade fully.
- **P3-8** heat_banner stamp reads "HEAT 30 NOTICED (25-)" and overlaps the "NOTICED" caption
  beneath; B reads "25-" as minus 25. Fix: "25+" or a threshold tick; offset the stamp.
- **P3-9** Campaign-end Profile "Something opens at ICE 10 everywhere (0/4)" and "Best ICE: … −"
  are jargon. ("0 won" after WON is a demo artifact: DemoSetup.end_campaign doesn't record to
  the profile.)

## Motion rules, kit, tests, docs
- **P2-6** Missing tests behind P1-1 and P2-3: step 1 on screen when a real fight starts
  (tutorial_done false, `step == 0` after the first drawn frame); each step at 1.0/1.3/1.6 fits
  its note with no scroll bar.
- **P3-10** Every `--quit-after` Movie Maker run logs "2 ObjectDB instances were leaked at exit"
  (netrun, hq, lab; 10/10 logs). R6 fixed the suite's exit leaks, not this path.
- Known item 1 unchanged: AWAITING_FIX (`test_motion_lab_demos.gd:59-71`) still the same 11.

## R6 confirmed on screen
A4 tags show applied numbers, LAST TURN one number ("-1 HP") (but P2-1 wording). A16 paged
steps with Next pulse (but P1-1, P2-3). B3/B9 combat end in context. B12 event page waits for
its stamp (stamp nearly invisible, P3-4). Run-end Heat cause. Raid speed buttons, HOLDS banner,
RAID RESULT. Modem SOLD stamp and Cycles roll.

**Verdict: NOT CLEAN** (P1-1; P2-1 to P2-6).
