<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__corp__meridian; status ok; tokens in 56724 cache-write 0 cache-read 32585 out 2952; cost $0.075. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: corporation meridian

**Verdict:** FIX

## Roster variety

| draft | class | the one question | hook relied on |
|---|---|---|---|
| cargo_hauler | normal | Pay to move it or leave it? | WEIGHT 2, uneven slices |
| conveyor_warden | normal | Where will the needle be next turn? | ORBIT 3, 4-tick Overflow |
| customs_scanner | normal | Which of two needles carries the hazard? | 2 needles 0/11, 3-4 tick slices |
| drone_dispatcher | normal | Kill the guard or steer past it? | satellite + REPLACE |
| route_optimizer | normal | Can you align both needles? | 2 needles 0/15 |
| tariff_collector | normal | What is your RAM worth? | RAM drain, OUTPUT_DOWN |
| last_mile_enforcer | elite | P1 orbit readable; P2 latch/refuse | ORBIT, escort, listener, OUTPUT_DOWN |
| port_authority | elite | P1 steer or skip; P2 keep your Perfects | WEIGHT 2, TIER_DOWN |
| logistics_director | mini-boss | Weight/RAM, then Packages, then respin lock | WEIGHT, parasite ring, respin lock |
| the_manifest | boss | where will the pointer be? | orbit, locks, parasites, uneven needles |

**Too similar:**
- **customs_scanner vs route_optimizer:** both are "two needles, steer to a safe pair". The scanner (0/11, uneven) is the better design. Rework route_optimizer so it is the clean pointer-rule teacher: its payoff is landing your own hits twice, with no intake puzzle. It is a poor L1-2 pick next to Scanner, as its own Q admits.
- **cargo_hauler vs port_authority P1:** both are Weight 2 plus "spin cards beat nudges". Hauler teaches it, so this is fine. But the Director P1 repeats it a third time, so the HQ boss needs a new angle.
- **conveyor_warden vs last_mile_enforcer P1:** both are orbit plus a 4-tick no-Perfect Overflow. Fine as teacher and payoff.
- **tariff_collector** has no distinct wheel hook. Its RAM drain overlaps Priority in six drafts.

## Phase and hook overlap
- **Priority (RAM drain)** appears in Warden, Scanner, Dispatcher, Collector, Port Authority, Director and Manifest. It is the corporation's whole RAM identity and is used too much. It is the only RAM mechanic, and its flat amounts get the same treatment everywhere.
- **The "4-tick no-Perfect Overflow" trick** is in nearly every draft. It reads as a template, which breaks the direct-design rule.
- **Orbit** is used by Warden, Enforcer P1, Manifest P1/P3/P5 and the Director concept. The Director draft drops orbit because the per-turn respin makes it a no-op. That claim contradicts the other drafts, which treat orbit as readable ahead. Settle it: orbit moves the needle after the respin, which is why it is readable.
- **TIER_DOWN or OUTPUT_DOWN stack-and-Cleanse** appears in the Enforcer, Port Authority, Collector and Manifest P3. No Meridian elite should reuse another's status.
- **Parasite Packages** are shared by the Director P2 and Manifest P5. That is acceptable as a payoff, but the Manifest asks Q3 whether they should differ.
- **Respin or nudge lock** is in the Director P3 and Manifest P3. This is a deliberate echo.
- **Missing teaching steps:** no Meridian normal teaches the Parasite ring, the respin lock or satellite replacement, and none teaches Hub Breach against Weight. The mini-boss and boss therefore introduce their core mechanics cold. The Director is never met in L1-6.

## Systems used
- **Shared (build once):** N1, N2, N3, N4, N11, N12 (nearly all), N13 (Dispatcher).
- **Mid-weight shared:** N8/N9 (TIER_DOWN, OUTPUT_DOWN stacks) across 4 drafts, and N7 (Director, Manifest, plus HQ N16).
- **Heavy and concentrated:** N10 (Director, Manifest), N6 (Enforcer, Manifest), N20, N5 (Manifest only).
- **HQ and events:** a NEW HQ clock map, N16 across 4 drafts and N17 (wheel event), N18.
- **Verdict:** Meridian needs roughly the full N list, plus a new HQ clock system that exists for one run type. Every normal and elite has a data-only fallback, which is good. The Manifest has fallbacks only for N10 and N12.

## Difficulty curve
- **Intake:** normals run 2-5 damage per turn at T1, except Route Optimizer at 8-10 and Scanner at about 5. Route Optimizer is a harder L1-2 fight than the others. HP at the band ceiling for a 2-needle normal is also questionable.
- **Elites:** Enforcer (about 7 turns) and Port Authority (about 7) are fair. Enforcer T4 at 82% win is the weakest.
- **Director:** 3 phases, about 11 turns at all tiers, 90% at T3. Good.
- **Manifest:** 5 phases against a roster that never used 3 needles, odd-tick needles or Hold-locks. Its P4 is gated on a "RAM ≥ 8" listener that punishes banking.
- **HQ:** 12 layers and ~36 min against a boss with 4-8% campaign wins. The Direct Lift ±2 RAM swing is minor next to that. HQ fights are all T4, but T1-T3 are never the HQ stage, so the roster's T1 tuning is not exercised.

## Identity
Freight, tariffs, time and position read as Meridian. The Weight and Priority terms are correct. The HQ clock map is strongly Meridian and well tied to the art. Weak spots:
- The Collector and Customs Scanner both read "customs".
- The Manifest buff list and the P3 stamp pile on customs flavor.
- Events: Dock Broadcast and Wrong Address read Meridian. Exclusive Carrier is generic legal-ambush. Favor Slot is generic with only a "sorter" skin.

## Concrete fixes
1. **route_optimizer:** drop to a pure pointer-rule teacher. Make the Overflow pair milder (14 → 10), and move it to L3+. Scanner takes the L1-2 two-needle role.
2. **logistics_director:** keep orbit out. Add a single stronger line in P1: Hub Breach can disable the Weight, so the elites should teach it first.
3. **port_authority P2:** replace TIER_DOWN with a unique effect, or give the Enforcer a non-status P2. Do not have both use the same status.
4. **tariff_collector:** give it a wheel hook beyond the drain, such as a second needle at 0/11 or a satellite, and cut the Surcharge drain so Priority is not the identity of seven drafts.
5. **Add a normal or elite** that teaches parasite or respin-lock at small scale (for example Drone Dispatcher gets a single 4-tick latch), so the Director and Manifest are not cold introductions.
6. **the_manifest:** cut P4's "RAM ≥ 8 resolves again" and cut the P2/P3 Express reuse. Reduce to 4 phases if N5, N6 and N10 slip. Decide on Package reuse (Q3): use the Director's version.
7. **hq/meridian:** reduce to 9-10 layers, or tie the boss-entry swing to HP, not only RAM.
8. **events:** reskin Favor Slot and Exclusive Carrier with Meridian-specific content, and unify the heat and cost scales.
9. **All normals:** vary the "4-tick no-Perfect Overflow", or state it as the Meridian "no Perfect" signature once.

## Q:
- Q: Does orbit apply after the start-of-turn respin, so it is readable? The Director draft assumes it does not.
- Q: Is Priority RAM drain the sole Meridian RAM identity, or should some enemies use a different one?
- Q: Should a 2-needle normal get HP above the 1-needle band (pointer rule)?
- Q: Is a bespoke HQ clock system justified for one corporation, or should Dwell and timetable ideas be cut to a data-only version?
