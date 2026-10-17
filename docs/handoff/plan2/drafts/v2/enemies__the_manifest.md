<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__the_manifest; status ok; tokens in 8189 cache-write 0 cache-read 32585 out 18456; cost $0.104. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, HP and phase arithmetic).** Rebuilt the budget with an explicit needle factor: 1 needle ×1.0, 2 needles ×1.2, 3 needles ×1.3 (diminishing, because about half of a hand is not damage). P4 now gets 78 HP instead of 60, and the phases are 45 / 54 / 57 / 78 / 66 = 300. The thresholds are now 0.85 / 0.67 / 0.48 / 0.22. All five tick layouts were re-added and sum to 30. Section 4 shows the per-phase turn estimate: 16.7 turns total.
- **Issue 2 (BLOCKER, sustain).** The Seal is now 1.5 % everywhere (tables, buff and §3), so 4.5 HP/turn against a 5.4 cap. It is the only sustain source.
  - Weigh-in is no longer a BLOCK. It is now an OUTPUT_DOWN stamp on your slice, so it is not a defense slice.
  - Hold's BLOCK and the Inspection block listener are gone; Inspection is now a fee on you.
  - Insured Cargo no longer heals; it adds OUTPUT_DOWN stacks.
- **Issue 3 (BLOCKER, P4 cleanse).** `cleanse_on_enter` is NONE for every transition. Your CORRUPTED slices from P2 and P3 carry into P4, which is the payoff of the RAM-tax design.
- **Issue 4 (MAJOR, stacked RAM tax).** Priority and Priority Lane only apply CORRUPTED, with no extra RAM drain. The P5 Package no longer drains RAM; it cuts your damage and chips HP.
- **Issue 5 (MAJOR, tick maps).** Rewrote the Sealed Crate note: a 4-tick slice cannot read a boss Perfect, so no Perfect-only multiplier fires on it. All Weigh-ins are now 4 ticks, and the Parcel is 6 ticks in P1–P3. The no-double-Perfect claims for P2 and P4 are now checked with real tick centres.
- **Issue 6 (MAJOR, buffs).**
  - Each buff now has a unique counter.
  - Only the three fixed gate types map to named Exploits: Customs Seal ← Breach, Hidden Manifest ← Intel, Fast Lane ← Virus.
  - The other five are marked "(Exploit name TBD)".
  - Cold Chain is dropped; Fast Lane replaces it, so Virus has a coherent job (a rogue routing table).
  - Insured Cargo's heal is removed.
  - Weight is limited to P2 and P4 so it does not overlap with P3's lock.
- **Issue 7 (MAJOR, P5 question).** P5 keeps "no floor" (R3: the last phase has none). Its question is now "route around the Delivery Tags with a deterministic orbit", not "how much damage can you take".
- **Issue 8 (NIT).** Expanded §3 and §7 and added a turns-per-phase estimate to §10.
- **Own re-check.** Tuned Express damage down (OVERFLOW 8 / 10 / 9 FLAT instead of 14 / 16 / 18). At T4's ×2.2 the v1 numbers would have one-shot a 45–60 HP operative on a Perfect read.
- **Critic Q (does the fight reach 14–19 turns).** Yes: 16.7 at the reference player (§4).
- **Critic Q (Weight vs Logistics Director).** Kept, but restricted to P2 and P4.
- **Rulings.** No conflicts. R1–R13 and the DECISIONS rulings are applied unchanged.

---

# the_manifest: direct design

Working name: **Customs Seal / The Master Manifest** (Meridian HQ boss, T4 only).

## 1. Identity & the one question

- **Class:** HQ boss, 5 phases, about 3.3–3.5 turns each, target 14–19 turns (inside the 12–20 band). T4 only; never in L1–2 teaching.
- **Theme:** one package moving through five stations: **Intake → Sorting → Customs Hold → Express → Last Mile**. Meridian's identity is *time and position*: orbit, weight, locks, parasite Packages.
- **Distinct from the Logistics Director.** The Director owns Package latching and the respin lock at mini-boss scale. The Manifest's own question is **"where will the pointer be, and what is already waiting there?"** Each phase teaches one deterministic scheduling skill, and P5 combines them.

| Phase | The question | The answer that shortens the fight |
|---|---|---|
| P1 Intake | Where will the orbiting needle be in 1 and 2 turns? | Spend the free nudge to put a Gap or Weigh-in under the needle's next position, and burst on the turn it sits on Gap. |
| P2 Sorting | Two uneven needles: which one carries the Express? | Never allow a Perfect Express read (1 tick of nudge); keep Priority off your wheel's best slice. |
| P3 Customs Hold | Your nudges are locked every other turn. Can you plan the locked turn from the unlocked one? | Set up on the open turn; cards still work on the locked turn. |
| P4 Express | Three needles at 0 / 11 / 19. Which one is lethal, and what are you banking RAM for? | Put the needle that reads Express onto SANDBOX turns; finish before enrage step 2. |
| P5 Last Mile | Orbit 3 per turn and Delivery Tags on your wheel: can you route around them? | A solved plan: orbits are deterministic, so land off the Tags and burst. |

## 2. Phase plan

**Common:** hub **Customs Seal** (P1–P3 only): SHIELD PERCENT 1.5 % of max HP per turn (4.5 at 300), capped by the existing `shield_cap` = 15 (Q4). Hub Breach disables it for a turn, and the Breach Exploit turns it off for the whole fight (buff table). It is the **only sustain source**. P4 and P5 have no Seal.

**Statuses used:** OUTPUT_DOWN (Weigh-in), TIER_DOWN (Stamp), CORRUPTED (Priority). All are anti-Firmware (R8). The only parasite is the P5 Delivery Tag.

**Thresholds** (T4, ICE ≤ 1.00, 300 HP): 0.85 / 0.67 / 0.48 / 0.22 → floors 255 / 201 / 144 / 66. P5 has no floor (R3).
Phase HP: 45 / 54 / 57 / 78 / 66 = 300.

**Flat amounts** below are × tier factor 2.2 at T4. The Seal's percent is not rescaled.

### P1 Intake (100 → 85 %, 45 HP)
| Field | Value |
|---|---|
| Needles | 1, tick 0, **Orbit 2 ticks/turn** (trail shows the next 2 turns) |
| Layout (6+6+4+6+4+4 = 30) | Parcel 6 · Gap(Null) 6 · Weigh-in 4 · Parcel 6 · Sealed Crate 4 · Weigh-in 4 |
| Parcel (W W G G W W, no Perfect) | SHIM 4 FLAT (8.8 at T4) |
| Weigh-in (4 ticks) | INFECT: OUTPUT_DOWN ×1 on your slice under the pointer |
| Sealed Crate (4 ticks, W G G W) | OVERFLOW 6 FLAT (13.2). A 4-tick slice cannot read Perfect, so it never gets a Perfect-only multiplier. |
| Gap | NULL |
| Hub | Seal |
| Listeners | none |

### P2 Sorting (85 → 67 %, 54 HP)
| Field | Value |
|---|---|
| Needles | 2: ticks 0 and 11, orbit off (uneven) |
| Layout (3+6+4+3+7+7 = 30) | Express 3 · Parcel 6 · Weigh-in 4 · Express 3 · Priority 7 · Gap 7 |
| Express (3 ticks, G P G; centres at ticks 1 and 14) | OVERFLOW 8 FLAT (17.6), **×2 on Perfect** (`perfect_multiplier`) |
| Priority (7 ticks, W W G P G W W) | INFECT: CORRUPTED on 1 random non-NULL player slice. No RAM drain; the 2× RAM cost is the tax. |
| Parcel / Weigh-in | as P1 |
| Hub | Seal |

- **Uneven-needle check.** Express centres are 13 ticks apart and the needles 11, so the two needles can **never both read a Perfect Express**.
- **Transition P1 → P2:** parks damage, keeps statuses (R6 remap), `wheel_override` + MULTIPLY (0, 11), `cleanse_on_enter` = NONE.

### P3 Customs Hold (67 → 48 %, 57 HP)
| Field | Value |
|---|---|
| Needles | 2: ticks 0 and 11, **Orbit 1 per turn** |
| Layout (6+4+6+6+4+4 = 30) | Hold 6 · Stamp 4 · Parcel 6 · Hold 6 · Stamp 4 · Gap 4 |
| Hold (6 ticks) | SHIM 2 FLAT (4.4) + LOCK_NUDGE on your wheel for your next turn (cards still work; the free nudge is refused with a reason) |
| Stamp (4 ticks, no Perfect) | SHIM 2 FLAT ×3 hits (`hits`; 4.4 each) + TIER_DOWN ×1 on your slice under the pointer |
| Parcel | as P1 |
| Hub | Seal |
| Listener **Inspection** | ON_RAM_SPENT: each RAM you spend on a nudge costs you 2 FLAT damage (4.4). Max 3 per turn. It is a fee on you, not sustain. |

- **Transition P2 → P3:** `wheel_override` + orbit 1, `cleanse_on_enter` = NONE. Your CORRUPTED slices stay.
- The lock shows in the enemy intent a turn ahead, so you can plan around it.

### P4 Express (48 → 22 %, 78 HP)
| Field | Value |
|---|---|
| Needles | 3: ticks 0 / 11 / 19 (gaps 11 / 8 / 11), orbit off |
| Layout (3+6+3+3+3+4+5+3 = 30) | Priority Lane 3 · Gap 6 · Express 3 · Express 3 · Priority Lane 3 · Weigh-in 4 · Gap 5 · Parcel 3 |
| Express (centres at ticks 10 and 13) | OVERFLOW 10 FLAT (22), **×2 on Perfect with pierce** |
| Priority Lane (3 ticks, G P G) | INFECT: CORRUPTED ×1 on 1 random non-NULL player slice |
| Weigh-in | OUTPUT_DOWN ×1 as P1 |
| Parcel (3 ticks) | SHIM 4 FLAT |
| Hub | Seal **off**. **Express rule:** on any turn you *end* with RAM ≥ 8, the boss resolves a second time at ½ (ON_TURN_END listener; the preview shows both resolves). |

- **Perfect check.** Needle offsets are 11 / 8 / 19, while Express centres are 3 apart (or 27), so **two Perfect Express reads never happen at once**. One needle is lethal at worst, and your SANDBOX or steering decides which.
- **Transition P3 → P4:** adds the third needle (MULTIPLY to 0 / 11 / 19) + `hub_override` (Seal off, Express rule). **`cleanse_on_enter` = NONE.** The CORRUPTED slices you stacked in P2–P3 cost you 2× RAM here, which is the pressure of this phase.

### P5 Last Mile (22 → 0 %, 66 HP, no floor)
| Field | Value |
|---|---|
| Needles | 2: ticks 0 and 13, **Orbit 3 ticks/turn** |
| Layout (4+5+4+4+5+8 = 30) | Express 4 · Package-Drop 5 · Gap 4 · Express 4 · Package-Drop 5 · Delivery 8 |
| Express (4 ticks, no Perfect) | OVERFLOW 9 FLAT (19.8), pierce |
| Package-Drop (5 ticks) | LATCH_PARASITE: a 4-tick **Delivery Tag** on your wheel (max 2). When read: −50 % to your damage on the boss and 3 FLAT damage to you (6.6). No RAM drain. |
| Delivery (8 ticks, W W G G G G W W) | SHIM 3 FLAT ×4 hits (6.6 each) |
| Defense / hub | none |

- **Transition P4 → P5:** `wheel_override` + orbit 3, `cleanse_on_enter` = NONE. Statuses remap by centre tick, then the Tags are added.
- The orbit is deterministic, so you can route around the Tags.

## 3. Sustain and intake

- **Sustain (one source): the Seal.** 1.5 % × 300 = **4.5 HP/turn** in P1–P3 only, limited by `shield_cap` 15. The reference damage is 18 per turn, so the cap is 0.30 × 18 = **5.4**, and 4.5 < 5.4 ✔. No BLOCK, heal or defense slice exists on the boss.
- **Intake per turn** (T4, ×2.2 flat; "raw" = unsteered random landing, "ref" = after the reference player's free nudge, one SANDBOX and steering):

| Phase | Raw | Ref | How it is computed (one needle) |
|---|---|---|---|
| P1 | ~5 | ~3 | Parcel 12/30 × 8.8 = 3.5; Crate 4/30 × 13.2 = 1.8 |
| P2 | ~8 | ~5 | Parcel 6/30 × 8.8 = 1.8; Express 6/30 × 17.6 plus the Perfect ×2 = 2.3; ×2 needles ≈ 8.2 |
| P3 | ~14 | ~9 | per needle ≈ Hold 1.8 + Stamp 3.5 + Parcel 1.8 = 7.1 |
| P4 | ~20 | ~12 | per needle ≈ Express 4.4 + Perfect 1.5 + Parcel 0.9 ≈ 6.8 |
| P5 | ~25 | ~14 | per needle ≈ Express 5.3 + Delivery 7.0 = 12.3 |

All are above 0 ✔. P4–P5 sit at the ≥ 12 target before enrage.

## 4. HP by tier

**Band (R2 `hp_bands`, T4 only):** ICE ≤ 1.00 → **300**; ≤ 1.15 → 330; ≤ 1.30 → 360; > 1.30 → 400. T1–T3: n/a.

**Phase budget** at 300 HP: 18 dpt × 3.5 turns = 63 per needle-unit. Needle factor: 1 → 1.0, 2 → 1.2, 3 → 1.3 (diminishing, because many cards aren't damage). Sustain: 4.5 × 3.5 = 15.75 ≈ 16 in P1–P3.

| Phase | Raw | − Sustain | × Needle factor | Budget | Assigned |
|---|---|---|---|---|---|
| P1 (1) | 63 | 47 | 1.0 | 47 | 45 |
| P2 (2) | 63 | 47 | 1.2 | 56 | 54 |
| P3 (2) | 63 | 47 | 1.2 | 56 | 57 |
| P4 (3, no Seal) | 63 | 63 | 1.3 | 82 | 78 (pierce threat) |
| P5 (2, Tags) | 63 | 63 | 1.2 | 76 | 66 (the Tags cost about 13 % of your output) |

45 + 54 + 57 + 78 + 66 = **300** ✔. The thresholds follow from the cumulative HP left: 255 / 201 / 144 / 66 → 0.85 / 0.67 / 0.48 / 0.22.

**Turns per phase** at the reference player (effective dpt: P1 13.5, P2–P3 13.5 × 1.2 = 16.2, P4 18 × 1.3 = 23.4, P5 18 × 1.2 × 0.87 ≈ 18.8):

- P1 3.3
- P2 3.3
- P3 3.5
- P4 3.3
- P5 3.5

That totals **~16.9 turns**, inside the 14–19 target.

## 5. Enrage

**Default** for a boss: start turn 10, every 5, +25 % damage, additive (×1.25, ×1.5). Cumulative turns at the reference player are P1 3.3, P2 6.6, P3 10.1, P4 13.4. Step 1 therefore hits at the P3 → P4 handoff, and step 2 (turn 15) lands in P5. Why default: the fight already has a built-in time pressure (the orbit and the RAM rule), so the stall guard needs no authored trigger.

## 6. Buffs and counter Exploits

A route draws 5 of the boss's Exploit pool (`exploits_per_grid` = 5). Every buff is strong; no buff adds a second sustain source.

| Buff | Effect | Counter Exploit |
|---|---|---|
| **Customs Seal** *(signature)* | The P1–P3 shield of 1.5 % per turn | Breach (fixed gate type; GDD 8.4b) |
| Hidden Manifest | Phases and next layouts hidden (reveal on entry) | Intel |
| Fast Lane | Orbit +1 tick per turn in P1, P3 and P5 | Virus (a rogue routing table) |
| Second Head | The 2nd and 3rd needles (P2–P5) | (Exploit name TBD) |
| Weight | Resistance 3 each turn in P2 and P4 (absorbs nudges; blocks Flip and Respin) | (Exploit name TBD) |
| **Lockout** *(signature)* | Hold also locks respin (not just nudge) | (Exploit name TBD) |
| Insured Cargo | Weigh-in applies OUTPUT_DOWN ×2 | (Exploit name TBD) |
| Surge Pricing | Each of your Perfects costs you 1 RAM at resolve (ON_PERFECT, DRAIN_RAM) | (Exploit name TBD) |

- **Signatures:** Customs Seal and Lockout.
- Seal and Lockout are the two buffs a player most wants to counter, so a route that draws neither is the harder route.
- Weight is kept only in P2 and P4, so it never overlaps with P3's lock.

## 7. Counterplay

- **P1:** read the orbit trail. Nudge a Gap or Weigh-in onto the needle's position two turns out, then spend the burst when the needle sits on Gap. A weak player nudges to the *current* slice, and the orbit carries it away.
- **P2:** use a 1-tick nudge to deny a Perfect Express (×2). Keep Priority off your best slice. A weak player lets both needles read Express and takes 17–35.
- **P3:** use the free nudge on the open turn to set up the locked turn. Don't spend RAM on extra nudges (Inspection costs 4.4 HP each). Cards still work on the locked turn. A weak player nudges every turn and pays the fee.
- **P4:** your CORRUPTED slices cost double RAM, so Cleanse or Encrypt before P4. Put the pierce Express turn on a SANDBOX (pierce ignores BLOCK and SHIELD but not SANDBOX). Spend RAM down below 8 before End Turn. A weak player banks RAM and eats the second resolve.
- **P5:** the Tags land on predictable slices (the orbit is deterministic), so route around them and burst before enrage step 2. A weak player walks into two Tags and loses half their damage.

## 8. Systems needed

- **N1** (amount modes, FLAT enemy amounts × tier factor; the Seal's PERCENT shield), **N2** (`hp_bands`, `enemy_damage_by_tier`), **N3** (phases, parking, status remap, `cleanse_on_enter`), **N4** (enrage).
- **N5** (buffs and Exploits).
- **N6** (listeners: ON_RAM_SPENT, ON_TURN_END, ON_PERFECT).
- **N7** (nudge lock and respin lock).
- **N8 / N9** (OUTPUT_DOWN, TIER_DOWN, corruption as RAM cost).
- **N10** (Parasite ring: the Delivery Tag).
- **N11** (odd-tick needles), **N12** (variable slice sizes and sub-tick maps).
- **N20** (`hits`, `perfect_multiplier`, `pierce`).
- **Data-only fallbacks:**
  - Without N10, P5's Package-Drop becomes APPLY_STATUS PARASITE (today's status halves the slice's output) plus a 3 FLAT hit.
  - Without N8 / N9, use today's PARASITE status for Weigh-in and Stamp.
  - Without N12, use 5-tick slices (P2 and P4 lose the Perfect-denial window and the no-double-Perfect checks).
  - Without N6, drop Inspection and the Express rule (P3 and P4 become plain).

## 9. Delta vs today

- **Kept:** the id `the_manifest`, the Customs Seal hub concept (a shield every turn unless breached), the Multiply → Orbit progression.
- **Changed:**
  - 400 HP → the 300 band (`hp_bands`).
  - 2 phases → 5.
  - The shared boss template is replaced by this direct design.
  - The shield is now PERCENT; flat amounts follow `enemy_damage_by_tier`.
  - The courier-drone satellite idea is retired.
- **`heat_effects`:** the boss has none today, so nothing changes.

## 10. Predicted sim check

- **Turns:** ~16.9 at the reference player (3.3–3.5 per phase); 12–14 at skill 1.0 (the bot lands more hits per needle).
- **Win rate, fresh fight:** 20–30 %, compared with the 25 % baseline fresh boss; **in a campaign**, 5–10 % (baseline 4–8 %). The reason is that P4–P5 intake is high but fully deterministic, and the lever is steering plus SANDBOX.
- **Versus baseline:** a fresh boss takes 38 turns today and a campaign boss 41–50, so the 14–19 target roughly halves it.
- **T1–T3:** no value (T4 only).

## 11. Open questions

Q: Is the 1.0 / 1.2 / 1.3 needle factor right, or should pointer-rule scaling be the full ×2 / ×3 (as in the Genome Core)? It would raise P4 to ~150 HP and break the 300 band.
Q: Is P4's "RAM ≥ 8 at end of turn resolves again at ½" too punishing for banking RAM?
Q: Should the P5 Delivery Tag stay distinct from the Logistics Director's Package, or share it?
Q: Is the existing flat `shield_cap` of 15 acceptable for the Seal, or does an enemy percent shield need its own cap (V2 Q9)?
Q: Do the five TBD Exploit names come from the Meridian pool, or do new Exploits need designing?
