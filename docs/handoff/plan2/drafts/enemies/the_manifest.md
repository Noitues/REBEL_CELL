<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__the_manifest; status ok; tokens in 18442 cache-write 0 cache-read 32007 out 5010; cost $0.047. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# the_manifest: direct design

Working name: **Customs Seal / The Master Manifest** (Meridian HQ boss, T4 only).

## 1. Identity & the one question

- **Class:** HQ boss, 5 phases, about 3.5 turns each, target 14–19 turns. Shown only at T4, never in L1–2 teaching.
- **Theme:** a freight pipeline that never stops. The fight is the same package moving through five stations: **Intake → Sorting → Customs Hold → Express → Last Mile**. Meridian's identity is *time and position*: orbit, weight, the respin lock and parasite "Packages".
- **Distinct from Meridian's other enemies.** Logistics Director owns the Package parasite and the Weight/respin-lock themes at mini-boss scale. The Manifest uses them only as a late payoff. Its own question is **"where will the pointer be, and what is already waiting there?"** Each phase teaches one deterministic scheduling skill, and the last phase combines them.

| Phase | The question | The answer that shortens the fight |
|---|---|---|
| P1 Intake | Which lane is the belt feeding? Its intent is readable two turns ahead (orbit). | Hit when its needle sits on the empty "Sealed Crate" gap, and spend nudges *before* the orbit moves it. |
| P2 Sorting | Which of the two uneven needles carries the hit and which one is the target for your wheel? | Keep both needles off Bulk/Express. Kill the Seal's shield while it is vulnerable. |
| P3 Customs Hold | Can you finish while your wheel is partly sealed? Your wheel is locked (nudges and respin) every other turn. | Plan the locked turn from the unlocked one. Cards still work. |
| P4 Express | Which needle is the lethal one? Pointers are on odd ticks (0 / 11 / 19), so **only one is ever a Perfect-capable read** for the boss. | Put the safe needle on Express. Race the shield clock. |
| P5 Last Mile | How much damage can you take? No defense, orbit 3, a Package ring on you. | A solved plan: orbits are deterministic, so route around the Packages and burst before enrage step 2. |

## 2. Phase plan

**Common to all phases:** the hub is Customs Seal. It gains SHIELD each turn (PERCENT, 2 % of max HP per turn in P1–P3, not scaled again). It is reduced by Hub Breach and by the Customs Seal buff Exploit. The shield cap for the boss is 15 % of max HP. Chosen: no separate cap in the data. Use the existing `shield_cap` and mark Q4.

**HP-by-band reference (T4, ICE ≤ 1.00):** 300 HP. Shares: P1 0 % → 82 %, P2 → 62 %, P3 → 42 %, P4 → 22 %, P5 → 0. Thresholds 0.82 / 0.62 / 0.42 / 0.22.

### P1 Intake (100 → 82 %, ≈ 54 HP at 300)
| Field | Value |
|---|---|
| Needles | 1, tick 0, **Orbit 2 ticks/turn** (trail shows next 2 turns) |
| Layout (sum 30) | Parcel 6 · Gap(Null) 5 · Weigh-in 5 · Parcel 6 · Sealed Crate 4 · Weigh-in 4 |
| Parcel | SHIM 8 damage FLAT (× tier damage 2.2 → 17.6 ≈ 18 at T4) |
| Weigh-in | DEFRAG BLOCK, PERCENT 4 % max HP |
| Sealed Crate (4 ticks, WEAK G G W, no Perfect) | OVERFLOW 12 FLAT, so it is dangerous but cannot be Perfect-read by the player's counter |
| Gap | NULL |
| Hub | Customs Seal: +2 % SHIELD per turn |
| Statuses/listeners | none |

**Intent is the question:** the orbit is deterministic, so the player sees which slice will be read next turn too.

### P2 Sorting (82 → 62 %, ≈ 60 HP)
| Field | Value |
|---|---|
| Needles | 2: ticks 0 and 11 (uneven, 11 apart), orbit off. |
| Layout | Express 3 · Parcel 5 · Weigh-in 5 · Express 3 · Priority 7 · Gap 7 |
| Express (3 ticks, G P G) | OVERFLOW 14 FLAT, **Perfect-read ×2** (`perfect_multiplier`) |
| Priority (7 ticks, WWGPGWW) | INFECT: drain 3 RAM + CORRUPTED on 1 random non-NULL player slice |
| Parcel / Weigh-in | as P1 |
| Hub | Seal +2 % SHIELD |

**Transition P1 → P2:** parks damage, keeps statuses (R6), `wheel_override` + MULTIPLY (0, 11). `cleanse_on_enter` = NONE.

### P3 Customs Hold (62 → 42 %, ≈ 60 HP)
| Field | Value |
|---|---|
| Needles | 2: ticks 0 and 11, Orbit 1 per turn. |
| Layout | Hold 6 · Stamp 4 · Parcel 5 · Hold 6 · Stamp 4 · Gap 5 |
| Hold (6 ticks, W W G G W W) | LOCK_NUDGE on your wheel for 1 turn **and** BLOCK 8 % PERCENT |
| Stamp (4 ticks, no Perfect) | SHIM 6 FLAT ×3 hits (`hits`) + TIER_DOWN ×1 on your slice under the pointer |
| Parcel | as P1 |
| Hub | Seal +2 % SHIELD |
| Listener | **Inspection:** whenever you spend RAM on a nudge, +1 BLOCK PERCENT 1 % on the boss (ON_RAM_SPENT, N6). Max +4 %. |

Lock: when a Hold resolves, the player's wheel is `nudge_locked` for the next player turn (cards still work, the free nudge is refused). Visible in the intent.

### P4 Express (42 → 22 %, ≈ 60 HP)
| Field | Value |
|---|---|
| Needles | 3: ticks 0 / 11 / 19, orbit off. |
| Layout | Priority Lane 3 · Gap 6 · Express 3 · Express 3 · Priority Lane 3 · Weigh-in 4 · Gap 5 · Parcel 3 |
| Express | OVERFLOW 16 FLAT, ×3 on Perfect, pierce on Perfect |
| Priority Lane (3 ticks) | INFECT: CORRUPTED ×1 + drain 2 RAM |
| Hub | Seal off (breached by default in P4: the "no-stop" lane). **Hub rule:** the boss resolves again at ½ on any turn you end with RAM ≥ 8 (ON_TURN_END listener). |
| Transition | wheel_override + MULTIPLY (0, 11, 19); cleanse_on_enter = PLAYER (the Express lane clears your statuses to be fair about the corruption you stacked) |

### P5 Last Mile (22 → 0 %, ≈ 66 HP, no floor)
| Field | Value |
|---|---|
| Needles | 2: ticks 0 and 13, **Orbit 3 ticks/turn**. |
| Layout | Express 4 · Package-Drop 5 · Gap 4 · Express 4 · Package-Drop 5 · Delivery 8 |
| Express | OVERFLOW 18 FLAT, pierce |
| Package-Drop | LATCH_PARASITE: 4-tick Package on your wheel (max 2): when read, drain 2 RAM and −50 % to your damage |
| Delivery (8 ticks) | SHIM 6 FLAT ×4 hits |
| Defense | none |
| Transition | wheel_override + orbit, `cleanse_on_enter` = NONE (statuses stay, then the Packages add) |

## 3. Sustain and intake

- **Sustain (one source): the Seal.** SHIELD 2 % max HP per turn = 6 HP/turn at 300 HP, plus Weigh-in BLOCK in P1–P4.
- **Cap check:** 30 % of reference 18 dpt = 5.4 HP/turn. Seal is 6 → over by ~10 %. **Fix:** the Seal gains 1.5 % (4.5 HP/turn); Weigh-ins are temporary BLOCK (expires, so not counted). **Stay under 5.4.** P4 has no Seal.
- **Intake per turn at the reference player (T4 reference, one needle on average):**
  - P1: ~6 (orbit makes some turns 0)
  - P2: ~11
  - P3: ~9 (locks cost you, not HP)
  - P4: ~14 before enrage
  - P5: ~16
- All above 0.

## 4. HP by tier

Boss band (R2, hp_bands, T4 only): ICE ≤ 1.00 → 300, ≤ 1.15 → 330, ≤ 1.30 → 360, > 1.30 → 400.

Phase budget at 300 HP, 18 dpt × 3.5 turns = 63 per phase, minus sustain 4.5 × 3.5 = 16 in P1–P3:

| Phase | Raw 63 − sustain | Needle factor | Assigned HP |
|---|---|---|---|
| P1 (1 needle) | 47 | 1.0 | 54 (18 % of 300) |
| P2 (2 needles) | 47 | 1.2 | 60 |
| P3 (2 needles) | 47 | 1.2 | 60 |
| P4 (3 needles, no Seal) | 63 | 1.0 | 60 |
| P5 (2 needles, no defense) | 63 | 1.0 | 66 |
Total ≈ 300. ✔.

T1–T3: n/a (boss is T4 only).

## 5. Enrage

**Default** (start 10, every 5, +25 % additive). Expected path puts P3 on turn ~10 and P5 near turns 14–17, so step 1 (×1.25) arrives in P3–P4 and step 2 (×1.5) at turn 15 in P5. Authored addition: **"Express Lane Opens":** the Seal never regenerates after turn 10.

## 6. Buffs and counter Exploits

A route draws 5 of 8 Exploits. The three existing types (Intel, Breach, Virus) remain fixed gate types and are mapped to the buffs they already counter.

| Buff (strong) | Effect | Counter Exploit |
|---|---|---|
| **Customs Seal** *(signature)* | +2 % SHIELD per turn and a 15 % cap | Hub Breach exploit (today's Breach turns it off) |
| Second Head | The 2nd/3rd needles in P2–P5 | Breach (needle count −1) |
| Weight | Resistance 3 each turn, absorbs nudges, blocks Flip/Respin | Resistance Waiver |
| Lockout | Hold locks nudge and respin (not only nudge) | Manual Override |
| Insured Cargo | Weigh-ins heal 3 % (PERCENT) | Claims Audit |
| Surge Pricing | Perfect landings cost 1 RAM more (ON_PERFECT listener) | Price Cap |
| Hidden Manifest | Phases and next layouts hidden | Intel |
| Cold Chain | Cleanses own statuses on phase change, plus Virus effects | Virus |

Signature: **Customs Seal** and **Lockout**.

## 7. Counterplay

- **P1:** read the orbit. Aim the Gap at the needle's *next* two positions, not the current one. Burst on turn 3. Weak players nudge to the current slice and are hit by the orbit.
- **P2:** deny the Express Perfect with a 1-tick nudge. Weak players take 2×.
- **P3:** use the free nudge on the unlocked turn to set up the locked turn. Weak players spend RAM on nudges that feed Inspection.
- **P4:** put the 0-needle (safe Gap) first, and let the 19-needle read a Weigh-in. SHIELD/SANDBOX the Express turn.
- **P5:** latch spots are predictable, so route around them. Weak players walk into 2 Packages and lose half their damage.

## 8. Systems needed

N1 (modes), N2 (hp_bands), N3 (phases/park), N4 (enrage), N5 (buffs/Exploits), N6 (listeners: ON_RAM_SPENT, ON_TURN_END), N7 (nudge lock), N8/N9 (TIER_DOWN, corruption RAM), N10 (Parasite ring), N11 (odd ticks), N12 (variable sizes), N20 (hits, perfect_multiplier, pierce). Fallback: without N10, drop P5's Package-Drop for Shim ×4 and a 2 RAM drain; without N12, use 5-tick slices (cheaper, loses the Perfect-denial window).

## 9. Delta vs today

Kept: id, hub concept (Seal shield), Multiply to Orbit progression, the courier drone idea (retired as a satellite). Changed: 400 HP → 300 band; 2 phases → 5; shared template replaced; shield is now PERCENT. `heat_effects`: none on bosses, so no change.

## 10. Predicted sim check

No baseline row; estimated from the wheel. Expected 15–18 turns at the reference player, 12–14 at skill 1.0. Win ≈ 20–30 % fresh (today's boss 25 %), since P4–P5 intake is high but deterministic. No T1–T3 value exists.

## 11. Open questions

Q: Do Hold locks count against "Every phase asks a new question" if a Weight buff makes them overlap with resistance?
Q: Is P4's "RAM ≥ 8 resolves again" too punishing for banking RAM?
Q: Should the P5 Packages use the Logistics Director's exact Package, or a distinct anti-slice?
Q: Is 15 % shield cap acceptable without a boss-specific cap?
Q: Does Cold Chain's Virus counter fit, since Virus today only corrupts slices?
