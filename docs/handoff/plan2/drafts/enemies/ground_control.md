<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__ground_control; status ok; tokens in 15580 cache-write 0 cache-read 32007 out 3421; cost $0.036. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ground_control: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, 3–4 turns, no enrage. Orbital Commons.
- **Layers:** L1–2 teaching (T1–T2 Routers) and L5–6 as a common pressure fight (T3–T4). The design is the same at every tier; only base numbers change (R2).
- **Concept:** a ground station that tracks a satellite. Its reader **drifts 2 ticks per turn** (today's `pointer_orbit_per_turn = 2`), so where it lands next turn is readable ahead. Its big hit (Overflow) and its shield (Sandbox) are always on the same wheel.
- **The one question:** *"Where will its needle be after the drift, and can you land the Overflow on Null or the Sandbox before you commit?"* The preview shows the next turn's drift.
- **What shortens the fight:** nudging or spinning so its needle sits on the Null or the Sandbox at the moment you need it, and striking on the turn the Sandbox is not under the needle. The shield only matters if the needle reads it.
- **Distinct from siblings:** Weather Satellite and Orbital Debris lean on flares and orbit speed. This enemy teaches **orbit prediction with one needle and one dangerous slice**, with no status, no parasite and no listener.

## 2. Phase plan
Single phase, no threshold, no HP floor (R3: last phase has no floor). **No phase entries** on the `.tres` (`EnemyData.validate`: normals have none).

| Field | Value |
|---|---|
| Needles | 1 at tick 0, `ORBIT` 2 ticks per turn. The preview trail shows the next 2 positions. |
| Hub rule | none |
| Statuses, parasites, listeners | none |

**Wheel layout (R11, sizes sum to 30).** Uneven sizes make the Overflow a narrow target and the Null a wide one, so the drift matters more.

| # | Slice | Size (ticks) | Effect | Mode |
|---|---|---|---|---|
| 1 | Shim 10 | 5 | Damage 10 | FLAT (× tier damage factor) |
| 2 | Defrag 8 → BLOCK | 5 | Block 8 | FLAT |
| 3 | Overflow 16 | 3 (G P G) | Damage 16 | FLAT |
| 4 | Shim 10 | 5 | Damage 10 | FLAT |
| 5 | Sandbox 5 → SHIELD | 4 (W G G W) | Shield 5 | FLAT |
| 6 | Null | 8 (W W G G G G W W) | nothing | n/a |

5 + 5 + 3 + 5 + 4 + 8 = **30**.

Changes from today: the current layout has two Shim 10 slices adjacent. Here the Shims are separated by the Overflow and the Defrag, and the Overflow shrinks to 3 ticks, so it has **no WEAK landing**. Every read of it is Good or Perfect at full output, so it is a real spike you steer around. The 4-tick Sandbox has no Perfect, so its shield rarely matters. The wide Null is the safe harbour to steer onto.

**Orbit and tick order** (slices start at tick 0 in listed order; boundaries at 0, 5, 10, 13, 18, 22, 30 with each slice centred on its span, an N12 detail). A drift of 2 per turn means the needle crosses the Overflow (3 ticks) roughly once per 15-turn lap, so the plan is a read-ahead rather than a rotation.

**Transition:** none (single phase).

## 3. Sustain and intake
- **Sustain:** none. The Sandbox 5 SHIELD is defense, not heal. Heal turns per fight: 0 (≤ 1 allowed). This fixes the "at most 30 % of reference damage" rule trivially: 0 %.
- **Defense per turn:** the needle reads Defrag (5/30 of the wheel) or Sandbox (4/30) on about 30 % of random starts, which gives about 8 block or 5 shield. That is ≈ 2.4 / turn average, well under the 30 % cap of 2.7 at T1 (30 % × 9).
- **Intake per turn at the reference player (T3 factor 1.69):**
  Random start, one needle, so per-slice probability is its tick share, with Perfect and Good both full output.
  - Shim ×2: 10/30 × 10 × 1.69 = 5.6 (the Shims read WEAK on 2/5 of their ticks at 0.5×: 10 × 1.69 × (3 + 2×0.5)/5 per read, i.e. ×0.8, so ≈ 4.5)
  - Overflow: 3/30 × 16 × 1.69 = 2.7
  - Total ≈ **7.2 / turn at T3** before block, T1 ≈ 4.3, T2 ≈ 5.6, T4 ≈ 9.4.
  Intake is > 0 at every tier. Over a 3.5-turn fight at T3 that is about 25 HP lost, steerable down to near 0 by nudging onto Null.

## 4. HP by tier
Budget (R2): `reference_dpt_by_tier` × 3.5 turns × 1 needle, minus sustain (0). The reference player's hits land on the one needle.

| Tier | Ref dpt | Budget | Band (R2 normal) | **hp_by_tier** |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 28–36 | **32** |
| T2 | 11 | 38.5 | 34–44 | **38** |
| T3 | 14 | 49 | 44–56 | **48** |
| T4 | 18 | 63 | 56–70 | **60** |

Today's 52 sits at T3 (band 44–56 inside), but is flat across tiers; `hp_by_tier` replaces it.

## 5. Enrage
**Off** (normal class default, R4). A 3–4 turn fight stalls only if the player refuses to hit; the drift keeps the Overflow coming.

## 6. Buffs and counter Exploits
Not applicable (normals have none).

## 7. Counterplay
- **Good player:** reads the drift trail, spends the free nudge (and one cheap RAM nudge) to park the needle on the 8-tick Null on the turn the Overflow would arrive, and strikes the turns the needle sits on Defrag-free slices. Kills in 3 turns taking ~0–10 damage.
- **Strong burst:** lands a big hit before the Sandbox gets read; the 5-shield is small enough that it never gates a kill.
- **Weak player:** ignores the trail, leaves the needle on the Overflow's 3-tick window and takes 16 × factor (27 at T3) with no WEAK discount. Also wastes a big hit into Defrag 8 when a 1-tick nudge would have missed it.
- **Flip / Freeze:** Freeze stops the respin but the orbit still moves, which is a nice teaching beat ("freeze isn't a pause on drift").

## 8. Systems needed
| N# | Use | Fallback |
|---|---|---|
| N1 | Flat amounts × tier damage factor (hub-free, so only slice scaling) | Today's `output_scale` works for slices; no loss |
| N2 | `hp_by_tier` | Single `hp = 48` (T3 midpoint) with `enemy_scale` |
| N12 | `size_ticks` for the 3 / 4 / 8 slices | **Data-only fallback:** all 5-tick slices with 6 slices (today's wheel). Loses the "Overflow has no WEAK" and the wide Null. Acceptable at T1–T2. |
| N11 | Not needed (needle starts on tick 0) | n/a |
| N14 | BLOCK / SHIELD names only | display strings |

Orbit already exists (`pointer_orbit_per_turn`).

## 9. Delta vs today
- **Kept:** id, description spirit, corporation, `pointer_orbit_per_turn = 2`, the five slice types and amounts, `cycle_reward = 15`, one needle at tick 0.
- **Changed:** `hp` 52 → `hp_by_tier` [32, 38, 48, 60]; slice order separated (Shim / Defrag / Overflow / Shim / Sandbox / Null); `size_ticks` 5/5/3/5/4/8 (needs N12); second Shim gets its own slot so the Overflow no longer has a Shim neighbour that Mirror-style Firmware can chain.
- **Heat effects:** none authored today, none added.

## 10. Predicted sim check
No baseline row (Solace-only baseline), so this is an estimate from the wheel.
- **Turns:** 3.4 mean at the step-0 skill, p90 ≈ 5; skill 1.0 about 2.8–3.0.
- **Win %:** T1 ≥ 98, T2 ≥ 97, T3 ≈ 93, T4 ≈ 88 (likely just under the 90 target at T4; T4 intake of ~9.4 per turn against 60 HP is the pressure).
- **Why:** one needle and no sustain means the fight length is just HP ÷ damage, and the expected ~7 intake at T3 costs about 25 HP, so a fresh operative wins comfortably but a depleted L5–6 operative feels it.

## 11. Q:
- Q: Is a 3-tick Overflow with no WEAK landing too punishing for T1 teaching? If so, widen it to 4 and drop the Null to 7.
- Q: Should the orbit trail show the full next 2 turns or only the next 1 (N11 HUD)?
- Q: Does Freeze on the enemy wheel stop the orbit too? Proposed: no, only the respin.
- Q: Should Shield be allowed to stack across turns here (cap 15), or is a 5-shield on a normal worth a PERCENT variant later?
