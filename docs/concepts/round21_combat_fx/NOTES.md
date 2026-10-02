# Round 21: combat FX revisions

**Base:** the locked D4 combat screen (no NEXT arrows). The round 20 scripts were copied here; earlier rounds are untouched. All new code is in `scripts/fx_r21.py`.

## GENERAL RULE (round 21 onward)
**Any effect caused by a card stems from the card play.**
1. The sticker card slaps onto the target wheel (drop, squash, shadow snap, gloss).
2. It dissolves with **dissolve A, the bit stream**.
3. The effect's bits leave **from that slap point**, never from the hand or the card's bottom position.

The bits are in the effect's colour (e.g. CORRUPTED pink). They then travel to whatever the effect touches: a slice, the hub, a ring, a drone. Effects that no card causes keep their own sources: slice resolutions, hub passives, turn start, enemy actions.

**Godot:** the card-play controller owns one `CardPlayFx`. It runs the slap tween, then the dissolve-A emitter on the slap position. It emits `dissolve_arrived(target, t)` so the effect's view starts its on-target animation (tear write-on, wall bricks and so on) when the bits arrive, not on a separate timer. The view never changes game state.

## Files
| File | Change |
|---|---|
| `fx_corrupt_apply_v2.gif` | CORRUPT PACKET is dragged onto THE MANIFEST, slaps, then dissolves (A) into pink 0/1 bits. The bits swirl up both sides of the hub into the slice under the needle. On arrival: a flash, the tear bars write on left to right, the badge slaps on and the rule chip shows. The played card leaves the hand and the other four close up. |
| `fx_evade_v3.gif` | The token lifts at 760 ms, while the attack is still only 42 % of the way along its path, high over the centre gap. The token flies **up** and then left (Bézier through (700, −320)). The attack turns away towards it **only once the token is well up**, so it never comes near the player wheel. Both fade at the screen edge, and EVADED stays. |
| `fx_drone_destroyed_v2.gif` | As round 20, without the `DRONE DESTROYED` chip and the `DRONE (BODYGUARD)` sub-label. The `-5` number and the `HP 0` chip stay. |
| `fx_phase_change_v2.gif` | The orange bits that build the second needle now stream from the **crossed phase pip on the HP arc** (66 %), which glows while it feeds them. They run along under the arc to the needle base. The rest is unchanged (hit-stop, banner flip, PHASE 2 vinyl). |
| `fx_ram_gain_origins.gif` + `fx_ram_gain_origins_strip.png` | The same +4 RAM fill from three origins, side by side: **A** the class core, **B** the TURN banner (it ticks over and the bits fall down the centre gap), **C** the deck/terminal. |
| `heat_city_v3.gif` + `heat_city_v3_strip.png` | Heat, dialled down (backdrop only). |

## RAM origin: recommendation **B, the TURN banner**
- The GDD gives +4 RAM at the start of **each turn**, so the refill should come from the thing that marks the new turn. The TURN plate ticks over (a cyan sweep) and the bits fall down the centre gap, never across a wheel, into the meter.
- **A (class core)** suggests RAM depends on the class, but every class gets +4.
- **C (deck)** reads as "drawing cards" and is a 30 px trip, so the eye barely catches it.

## Heat v3 mapping (backdrop only; no siren tint at any band)
| Band | Shows |
|---|---|
| NOTICED 25–49 (new) | Three alarm beacons (a red/amber light that turns slowly, with a short beam) on **side** buildings: left edge, top right, right of the boss. Nothing on the target building. |
| FLAGGED 50–74 | The old NOTICED: 9 police lights and 1 searchlight sweeping the target. |
| HUNTED 75+ | The old FLAGGED: 13 police lights and 2 searchlights. No helicopters, no wash. |

## Open
- The old HUNTED (helicopters, 3 searchlights) is now unused. Should it come back as a PURGE-100 state, or stay cut?
- In evade v3, the attack still travels for about 240 ms before the token lifts. Lifting even earlier would mean the token leaves before the attack is visible.

## Build
Run from `scripts/`:
- `python plates.py warm`
- `python fx_r21.py`

`scratch/` is git-ignored and cleared.
