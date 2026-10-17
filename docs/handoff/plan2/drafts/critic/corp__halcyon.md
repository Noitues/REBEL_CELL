<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__corp__halcyon; status ok; tokens in 62263 cache-write 0 cache-read 32585 out 3051; cost $0.081. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: corporation halcyon

**Verdict:** FIX

## Roster variety

| Draft | Class | The one question | Hook |
|---|---|---|---|
| parking_warden | normal | Which slice takes the Citation? | OUTPUT_DOWN ×1, random vs under-pointer pick |
| permit_office | normal | How many stamps are on you when Processing lands? | OUTPUT_DOWN count, `hits_per_target_status` |
| patrol_unit | normal | Can you steer off the 3-tick Overflow? | Uneven sizes only, no status |
| surveillance_mast | normal | Where will the orbiting needle end? | ORBIT 2, SANDBOX slices, OUTPUT_DOWN ×2 |
| transit_controller | normal | Which of 2 orbiting needles do you steer? | 2 needles at 0/12, orbit 1 |
| utility_meter | normal | Strip the shield before the Surcharge? | SHIELD-reading rider |
| riot_control | elite | Which needle do you steer? / which slice do you protect from stacks? | Barrier, 0/11 needles, OUTPUT_DOWN, listener |
| zoning_board | elite | Which slice gets marked? / Rezone | Orbit, OUTPUT_DOWN, TIER_DOWN, drone |
| city_manager | mini-boss | Where do the fines land? / Curfew lock / which needle? | OUTPUT_DOWN ×3, nudge lock, 0/13 needles |
| civic_core | boss | Five decrees | TIER_DOWN marks, ban listener, 0/13 needles, orbit |

Too similar:
- **Parking Warden and Permit Office** both teach Citation→OUTPUT_DOWN. Keep the Warden as the teacher. Rework the Permit Office so Processing does not require stacking and is a separate lesson.
- **Parking Warden, Permit Office, Surveillance Mast, Riot Control P2, Zoning Board P1 and the City Manager P1** all use Citation→OUTPUT_DOWN. That is six of ten drafts built on the same status.
- **Transit Controller, Riot Control and Zoning Board P2** all use two needles with uneven or even spacing and a "nudge one onto Null" answer.

## Phase and hook overlap

- Citation/OUTPUT_DOWN is overused. Teaching, elite, mini-boss and boss all use it with no relief.
- The boss and the mini-boss share the same shape: stack marks, then a uniform 0/13 two-needle phase, then orbit. The boss P4 is a near copy of City Manager P3.
- The mini-boss does not distinguish itself from Zoning Board, which also goes marks → two needles.
- **No parasite ring and no satellite variety.** Only the drone appears (Zoning Board, Permit Office dropped it). Halcyon identity (GDD: heal and shield each other, Citations) is thin: only Utility Meter heals and shields. The "enemies support each other" theme is absent.
- **Missing teaching steps:** nobody teaches TIER_DOWN before the boss or the Zoning Board P2. There is no Cleanse/Encrypt-specific normal. The only fight that teaches SANDBOX negation is the Mast.
- **Hidden issue:** the City Manager P2 Curfew refuses the free nudge while resistance 2 absorbs paid nudges. The two stack into a very harsh nudge lockout.

## Systems used

| System | Used by | Shared? |
|---|---|---|
| N1, N2, N3, N4 | almost all | foundation |
| N8/N9 | 8 drafts (also 2 as TIER_DOWN) | shared, critical |
| N12 | 9 drafts | shared, critical |
| N11 | transit, riot, zoning, city_manager, civic_core | shared |
| N20 | permit, utility (new rider), civic_core | partly new |
| N6 | riot, civic_core | 2 uses |
| N7 | city_manager only | single-use |
| N14 | mast, civic_core, utility | shared |
| N5 | boss | single-use |
| N13 | HQ Enforcer | single-use |
| N16/N17/N18 | events, HQ | shared |
| NEW: HQ layout, eye rule, node access | HQ | HQ-only, heavy |

N8/N9 plus N12 gate nearly everything, and data-only fallbacks are weak. The HQ adds three NEW systems on top. Halcyon is expensive but the load is concentrated in shared systems.

## Difficulty curve

- Normals all aim at 3.5 turns with 28–32 HP at T1 and intake of 2.5–4.5. Parking Warden is the first fight and fine. Surveillance Mast, labelled "L3-4 teaching", is the hardest read in the normals and needs orbit planning and SANDBOX.
- Elites are both estimated at roughly 82% at T4, under the 90% T3 pass line for Riot Control and Zoning Board. Zoning Board takes the top of the band at every tier, contradicting the pass criteria.
- The City Manager at 3 phases (~10.5 turns) is close to the boss's phase length, but a ×3 stack is a bigger lock than the boss's TIER_DOWN cap of 2.
- **HQ:** 13 layers and ~40 minutes. The Spotted rider adds a blade, an Enforcer and an early enrage to every fight at once. This is a much harsher stack of changes than anything the roster taught, and its Blade (TIER_DOWN on one slot per turn) hits the same ground as the boss P1 marks.
- The boss win-rate estimate is 35% fresh, above the 25% baseline, so it is not clearly harder.

## Identity

The wheel names (Citation, Curfew, Warrant, Ban) read as bureaucratic and fit the GDD "policing-as-a-service". The HQ's eye and blade fit the art. Missing: "heal and shield each other" and civic services (water, power, transit) beyond the Meter and Controller. Events fit the Corpo voice well. The tunnel event uses a Patrol Unit as the warden, which is fine.

## Concrete fixes

1. **permit_office:** replace OUTPUT_DOWN stamping with a different counter, such as a visible queue of its own (it gains BLOCK each turn it is not hit), or make Processing scale with your cards played, so the lesson is distinct from the Warden.
2. **surveillance_mast:** relabel it L5-6 only, since its orbit plus SANDBOX plus Citation ×2 is not a teacher. Citation becomes OUTPUT_DOWN ×1.
3. **riot_control P2:** drop Citation and use a different pressure (for example the Riot Response listener plus pierce Batons). That frees OUTPUT_DOWN for the Warden and the City Manager.
4. **zoning_board:** remove the Civic Drone, since it adds a system for one use, and reserve TIER_DOWN for the Board's P2 as its first appearance. Add a Halcyon normal that applies TIER_DOWN first (rework the Utility Meter's Peak Rate into a Rezone-style slice).
5. **Support theme:** add a bodyguard or heal-sharing pair in Halcyon (a fixed N13 satellite on Patrol Unit or Transit Controller) to make "enemies support each other" real.
6. **city_manager:** P3 should not reuse the 0/13 pair that the boss P4 uses. Give the boss P4 0/10 or a three-needle layout, and keep the mini-boss at 0/13.
7. **city_manager P2:** drop resistance 2 in Curfew or let the lock refuse only paid nudges; as written the nudge is dead on two axes.
8. **hq/halcyon:** apply the Blade only to Elites and Racks, and keep normals to the Enforcer. Cap the HQ at ~10 layers or state that the Annex nodes replace others. Pick one of the Alert/boss-enrage ties and the Climb rules.
9. **Elites:** pull Zoning Board HP down from the top of the band to mid-band, and give Riot Control's T4 Shove 12 not 14.
10. **Heat:** the HQ uses +1 Heat per Spotted fight while the Normal fights have `heat_effects` nowhere. Add one line stating that.

## Q:

- Q: Is OUTPUT_DOWN meant to be the Halcyon signature across the roster, or is TIER_DOWN the signature with OUTPUT_DOWN a teaching step only?
- Q: Should Halcyon introduce a fixed-satellite support pair (N13) to deliver the "heal and shield each other" identity?
- Q: Should the HQ Blade riders apply to Spotted normals at all?
- Q: Should the mini-boss and boss share any needle geometry, or is overlap fine for corporation identity?
