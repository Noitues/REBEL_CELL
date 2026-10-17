<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__corp__orbital; status ok; tokens in 59048 cache-write 0 cache-read 32585 out 2745; cost $0.076. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: corporation orbital

**Verdict:** FIX

## Roster variety

| draft | class | the one question | hook relied on |
|---|---|---|---|
| ground_control | normal | where will the drifting needle be; park Overflow on Null | orbit 2, N12 sizes |
| launch_pad | normal | kill the drone or steer around it | fixed satellite + REPLACE (N13) |
| orbital_debris | normal | pay to move a heavy wheel or plan around it | resistance 2, N12 |
| tracking_station | normal | which of two uneven needles hurts | needles 0/11 (N11), OUTPUT_DOWN |
| uplink_relay | normal | cash in or cleanse the overclock | Flare, orbit 1 |
| weather_satellite | normal | read the orbit, steer to Null | orbit 4, Flare, Hotfix |
| geostationary_guard | elite | pay to steer vs race the overclock | resistance 3 then orbit 3, Flare, drone |
| station_commander | elite | which needle do I feed, then spend overclocks | needles 0/11, Flare, Detonate |
| mission_director | mini | route around gates, steer around guards, feed the safe needle | rim gates, fixed satellites, 0/11, Hotfix |
| commons_array | boss | read the schedule, then race | orbit, satellites, Flare, 0/11, Debris ring |

**Too similar, rework:**
- ground_control, weather_satellite and uplink_relay all ask "read a drifting needle, steer to Null", and two of them add Flare. Rework ground_control: drop the orbit, make it the teaching case for a visible "intent in two turns" (a slow orbit of 1 plus a Sandbox you must avoid). Move Flare out of weather_satellite and give it the pure orbit-read; uplink_relay stays the sole Flare teacher.
- tracking_station and station_commander P1 are the same 0/11 puzzle with a Flare slice. Give tracking_station a different question: keep two needles but make it the gentle L3 teacher (no Flare, no status), and leave Flare to the commander.
- Geostationary Guard's P2 (orbit 3 plus two Flares) and Commander's P2 (Flare Feed, Detonate) both make the question "cash in overclocks". Differentiate the guard: remove Flare entirely from it and make its P2 about the resistance switching off and the Overflow, or the Commander keeps the overclock-cash-in identity alone.

## Phase and hook overlap

- **Solar Flare/OVERCLOCK** appears in 8 of 10 drafts (everything except launch_pad's neighbours and debris). It is the corporation's identity, but it is the answer to every question, so it stops being a question. Restrict it: Flare in uplink_relay (teach), commander (cash in), boss P3 (RAM tax), and nowhere else.
- **Needles 0/11** are used by tracking_station, commander P1, director P3 and boss P4/P5: five times. Fine for the identity, but the L3 teacher must come first and the commander and boss need different follow-ups.
- **Fixed satellites** show up in launch_pad, guard, director and boss P2. The director and boss P2 are near-identical ("steer around guards, don't kill them"). Change the boss P2 to something else, such as a rotating bodyguard.
- **Orbit** is on 5 normals/elites plus the boss. The orbit speeds 1/2/3/4 are hard to tell apart, and orbit is never the sole question except in weather.
- **Hotfix/PERCENT heal** is on weather, director P3 and boss P1-P4; the boss P2-P4 heals break the 30% cap.
- The "no Perfect on 4-tick slice" trick is repeated in nearly every layout.
- The HQ's Pressure (+10%/turn) duplicates enrage.

## Systems used

- **Shared (build once):** N1, N2, N3, N4, N11, N12, N13, N19.
- **Mid-use:** N9 (Flare/CORRUPTED), N20, N15 (gates, director only), N6 (boss Burnout), N10 (boss P5 only), N5 (boss, HQ).
- **Events:** N16, N17, N18.
- **HQ NEW:** run state, Doors modifier, Dish Link, cyclic route graph, campaign strike tally. This is too many for one corporation, and the HQ is the heaviest in the game.
- N12 sizes are mandatory throughout, with fallbacks that mostly erase the designs.
- Single-use but justified: N15, N10, N6, hence the hard fixed-point risk for the Director and boss.

## Difficulty curve

- Normals are well banded (about 3.5 turns, HP 28-70), and the intakes are sensible.
- The boss's HP is inconsistent: the phase budgets sum to about 445 against a 330 band. The thresholds 0.88/0.74/0.46/0.22 yield a 12% P1 and 26% to 28% P2/P3, which is not a coherent plan. Fix it with five equal-budget phases or fewer phases.
- Boss heal: 2 % × 330 ≈ 6.6, over the 5.4 cap; the draft's own "fix" to 1.5% contradicts the table.
- Mission_director matches the mini-boss band.
- The boss predicts 35-45% fresh, which is high next to the 25% baseline; it is plausible, but the draft is unmeasured.
- Commander reaches only 80% at T4, below the target.
- The HQ run is about 28 min and 12-15 layers, which stretches a campaign already at 605 min against a 395 target. The HQ's lap structure is not prepared by the roster: no normal teaches gates or Links.
- The Fallout (2 corrupted slices) plus a skipped boss phase contradicts the boss's P3 RAM-tax design.

## Identity

Strong: the sky/schedule/orbit theme and the cyclic HQ suit Orbital Commons and the art (rocket, dishes, gantry). Weak: the fights read as "Flare plus orbit" more than as privatised orbit with a pay-per-use feel, and the events are generic Cycles/Heat trades. Solar Flare appears as an overclock gift/trap, which does fit the GDD.

## Concrete fixes

1. commons_array: re-derive the thresholds from budgets (e.g. 0.84/0.68/0.42/0.20 with HP 330), set the heal to 1.5% in every phase, and state the hp_bands for T4 only.
2. commons_array P2: replace the Relay guards with a rotating bodyguard, so it doesn't copy the Director.
3. geostationary_guard: remove Flare, make P2 about the resistance dropping plus the Overflow.
4. ground_control: remove the orbit-to-Null framing; make it a gentle orbit-1 teacher.
5. weather_satellite: remove Flare, keep orbit 4 as the sole question.
6. tracking_station: remove the Flare, make it the plain 0/11 teacher.
7. station_commander: lock the Detonate to N20; give Flare to it alone among elites.
8. orbital_debris: add a Hub Breach tell, since the resistance lesson needs a counter.
9. hq/orbital: cut the Doors Pressure, since enrage already exists; drop the Dish Link and the campaign strike tally (defer); cap the run at 12 layers and drop the fork's extra circuit.
10. Events: swap ev_orb_stuck_thruster's HP nudge cost for Cycles; add an Orbital-flavoured consequence to ev_orb_rumor_flare.

## Q:
- Q: Is Flare allowed as a mandatory identity everywhere, or reserved for three fights?
- Q: Should the HQ stay cyclic, given its five NEW systems?
- Q: Should the boss keep five phases at 330 HP, or reduce to four?
- Q: Do orbit speeds need a distinct, readable ladder (1/2/3/4) before N11 ships?
