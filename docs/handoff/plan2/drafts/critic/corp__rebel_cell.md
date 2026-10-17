<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__corp__rebel_cell; status ok; tokens in 53164 cache-write 0 cache-read 32585 out 3153; cost $0.072. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: corporation rebel_cell

**Verdict:** FIX

## Roster variety

| draft | class | the one question | hook relied on |
|---|---|---|---|
| cell_informant | normal | which slice is it on next turn? | orbit 3/turn, trail, 7 slices, Citation |
| dead_drop | normal | which slice holds the courier, hit or steer around? | Echo Drone bodyguard, N13 |
| echo_process | normal | pay for a Perfect? | N6 ON_PERFECT, Dose |
| handler_proxy | normal | which slice is leashed? | OUTPUT_DOWN on your wheel, resistance 2 |
| loyalty_test | normal | take the Perfect or the safe Good? | N6 ON_PERFECT (Report) |
| mirror_script | normal | which pair do the two needles read? | 2 needles 15 apart, 5-tick slices |
| the_handler | mini-boss | shared nudge, then Perfect echo, then 2 needles | N6 ON_NUDGE, ON_PERFECT, N7, TIER_DOWN |
| dispatch_core | boss | don't repeat, then RAM, then geometry, guards, race | Forecast, five phases, listeners, satellites |

**Echo Process and Loyalty Test are the same enemy.** Both are a flat 4-damage tax on your Perfect. Rework Loyalty Test. Make it punish *repeating a slice* (a ×1.25 buff on a slice you landed last turn) or a NULL landing. Alternatively, cut it from the pool. This also stops the ON_PERFECT overload (Echo Process, Loyalty Test, Handler P2, DISPATCH P3 all use it).

Informant, Proxy and Mirror Script all lean on a Citation or OUTPUT_DOWN tax over a plain damage wheel. Mirror Script is a clean geometry teacher. It is the best L1 enemy and the only one needing no new system.

## Phase and hook overlap

- **The Perfect-punish listener appears four times** (Echo Process, Loyalty Test, Handler P2, DISPATCH P3), at 4 flat, 4 flat, 60 % and 25 %. The Handler's and DISPATCH's versions are not clearly different from the normals' versions. After the rework, only the Handler and one normal should keep it.
- **The 2-needle uneven geometry repeats.** The Handler P3 (0/11) and DISPATCH P3 (0/11) are the same phase with the same offset. Give DISPATCH a different offset, or make it the orbit phase.
- **"Mirror your actions" is the corporation's identity but is under-used.** Only the Handler's P1 (ON_NUDGE) mirrors a player action. The normals mostly don't mirror anything.
- **No normal teaches the mirror loop.** The Handler's P1 and P2 are the first time the player meets listeners reacting to nudges or Perfects at scale. Echo Process is the only listener-teaching normal, and it is rated L3-6.
- **DISPATCH's Forecast needs a new last-landing record** with no N# fit. It also contradicts the mini-boss's no-history reading. Its P4 drones repeat Dead Drop's idea and add nothing new.
- **DISPATCH's phase shares are inconsistent.** The 0.80 / 0.60 / 0.40 / 0.20 grid is replaced by 0.82 / 0.64 / 0.44 / 0.22, yet the text still references both.

## Systems used

- **Shared, build once:** N1, N2, N3, N4, N5, N6, N8, N9, N11, N12, N13, N16, N19, N20. The corporation is dependent on a lot, especially N6 (6 drafts), N12 (7 drafts) and N16 (4 events plus HQ).
- **Single-use:** N7 (Handler P2 only), N17 (witness wheel), N18 (HQ rewards).
- **NEW and heavy:**
  - Triple Run, which reworks `netrun_session` and has no fallback.
  - The lane graph generator, step clock and counter selector.
  - The Hack node.
  - Parked-support redirect.
  - The Forecast last-landing record.
  - Echo-scales-with-output rider.

  That is about eight NEW items for one corporation, which is too many. Make the Triple Run an explicit prerequisite, not an assumption.
- **Data-only normals:** only Mirror Script works without N12 or N6. Any normal needs N12 to match its draft.

## Difficulty curve

- Normal drafts all predict 3.3–3.5 turns and win rates of ~85–98 %. T4 ones fall below the 90 % bar: Dead Drop 85, Echo Process 85, Proxy 88.
- The Handler totals about 9 turns. Its T2 and T3 win rates (91 % and 84 %) miss the criteria, and its own text admits a bot would finish under the 6-turn floor. Its P3 bands are deliberately breached.
- DISPATCH at about 17 turns fits, but its intake (2-14 per turn) is lower than the Genome Core's. Its first phase is easy. The player is only prepared for single-pair listeners, not for Forecast or ×N stacks.
- **No elites were provided** (rc_template_elite and rc_template_elite_b). The curve normal → elite → mini-boss is incomplete.
- **The HQ run is the weakest link.** It runs 9 steps and about 50 minutes, three lanes with about 15 fights, and every fight is a T4 normal. The set contains no elite design and no L1-2 enemy that prepares for the HQ's relay, counter and sync ideas.

## Identity

- **Strong:** mirror and handler themes, tone, DISPATCH as a forecaster (matches GDD 8.2), the Sync Strike as the three-operative HQ.
- **Weak:** Dead Drop and Mirror Script read as generic. The GDD says REBEL_CELL elites use the player's classes' wheels, Hub Cores and Daemons (M11). Only the HQ Counter honors it. Most normals use nothing from the player's profile.
- **Off-identity:** DISPATCH P2 and P3 reuse Citation, Priority and Flare from other corporations (a deliberate "corporate mix"), but then a REBEL_CELL boss no longer feels like the Cell's own.
- **The events are clean but thin.** Holding Cell Tip and the Man in the Van show the Cell as owner. Standing Contract has the right tone. The ambush event writes the fight as `handler_proxy` at +1 tier, which for a normal is 3-4 turns, and that is fine.

## Concrete fixes

1. **loyalty_test:** replace the ON_PERFECT Report with a "repeat tax": a slice landed twice in a row takes a flat 5 on the second landing. Needs a record, so prefer the simpler "NULL landing costs you 4". Rate it L3-4.
2. **echo_process:** keep. Add the Calibrated Firmware interaction as its explicit answer. Resolve the double-resolve question: one fire per turn.
3. **dispatch_core:** P3 needles at 0 / 9 (not 11), or replace P3 with an ORBIT phase, so it differs from the Handler P3.
4. **dispatch_core:** drop the Forecast last-landing record. Use the staged landing at preview time (a pure function of the board) as the draft's own Q suggests.
5. **dispatch_core:** drop the P2 Priority/Citation corporate mix, or limit it to Dose and OUTPUT_DOWN. Fix the threshold grid to 0.82 / 0.64 / 0.44 / 0.22 everywhere.
6. **the_handler:** keep Echo at 60 %, but make DISPATCH's Echo a different thing (no echo). Keep the mini-boss P3 hub clean.
7. **cell_informant:** move to L1. Make Citation target the slice under the pointer (the draft's own Q), not a random one.
8. **dead_drop:** add an L2 note. Its Cache slice is a Perfect-able defensive slice with no payoff, so change it to a full 5 BLOCK with no Perfect map.
9. **hq/rebel_cell:** cut to 2 lanes or a single-operative stub first. Add a Sync Strike prerequisite and move the Triple Run out of the corporation's critical path. Fix the Counter basis (a seed, not "most-used Firmware"), which lets the player game the preview.
10. **Add elite drafts** (rc_template_elite and _b), each with one Mirror hook the player's class implies.
11. **events:** raid-win event 28 offers a map edit that also opens a raid route. Mark it as an N16 `map_edits` dependency, with a fallback.

## Q:
- Q: Should the REBEL_CELL elites use the player's actual class wheels (GDD 8.5), which ties all fights to profile state?
- Q: Is the HQ run a three-lane Triple Run or a single-lane run in the first build?
- Q: Does a SANDBOX negate a listener hit (Echo, Report), or only resolved attacks?
- Q: Which one normal keeps the Perfect-punish listener?
