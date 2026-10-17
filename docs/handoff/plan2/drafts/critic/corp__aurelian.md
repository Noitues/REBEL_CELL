<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__corp__aurelian; status ok; tokens in 35599 cache-write 0 cache-read 32585 out 2629; cost $0.052. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: corporation aurelian

**Verdict:** FIX

## Roster variety

| draft | class | the one question it asks | hook relied on |
|---|---|---|---|
| Crier | normal | what does a mark want from me? | VERDICT MARK, land GOOD |
| Dole Cart | normal | free turn now, debt later? | MARK plus a gift to the player (NEW-C) |
| Legionary Drone | normal | which landing is safe under a net? | TIER_DOWN |
| Tax Farmer | normal | how long can I carry this mark? | MARK plus Interest (ALL_MARKED) |
| Lictor | normal | kill the rod or steer away? | fixed satellite plus a MARK slice |
| Vestal Firewall | normal | stay off the Pyre, or land safe? | CALL plus percent shield |
| Praetorian | elite | starve the wall / deny the Perfect | perfect_multiplier, N20 |
| Censor | elite | carry marks or clear them / inverted map | MARK, Interest, INVERTED |
| Games Master | mini-boss | where is my safe offset now? | MARK, net, CALL |
| Rostrum | boss | one rule re-read each act | all of the above |

- **Crier vs Dole Cart:** both are "a mark on the pointer slice, cap 1". Dole Cart is the only one with a distinct decision (the gift). Rework Crier into the pure CALL-free teach and move the gift-for-debt trade into the Dole Cart alone.
- **Tax Farmer vs Censor P1:** both are "Interest on marks, cap 2–3". Rework the Censor's P1 so it is not Interest again. Use a different lever, such as a Thumbs slice that places a mark on the neighbouring slice, so the elite builds on the Tax Farmer instead of repeating it.
- **Praetorian** is the only roster enemy that is not VERDICT-based. That is fine for variety, but it is the one place Murmillo ×3 is taught before the boss.

## Phase and hook overlap

- Every enemy, the mini-boss, the boss and the HQ run all rest on VERDICT. The identity is strong, but the set has no fallback: if the VERDICT preview or UX fails, everything fails together.
- All enemy needles are single and fixed at tick 0. The first uneven or double needle appears in boss P3. The player never practises "which needle gets to be Perfect" beforehand, and the boss then asks it twice (P3 and P5). Add a double-needle elite or normal.
- The Net (TIER_DOWN) appears in the Legionary, the mini-boss P2, and boss P3–P5. It is taught well.
- Boss P4 INVERTED has only a preview in the Censor P2, which is a good setup.
- The Lictor satellite is used only once before the boss buff. That is acceptable.
- The Games Master P2 ("Net + mark") is nearly the boss's P3 net puzzle. The escalation between them is only more needles.

## Systems used

- **Shared (build once):** NEW-A (all 10 drafts), N8/N9, N12 (every layout), N3, N4, N1.
- **Single-use:** NEW-C (the Dole only), NEW-B, N13 (Lictor), N14, N11 and N5 (boss only).
- **HQ and events:** the Circus clock (NEW), the Favor meter (NEW), N16 (all three event drafts), N17 (Wheel), N18.
- That is 3 NEW systems plus the Circus clock and Favor, on top of N1–N20 dependencies. NEW-A is a hard single point of failure with no data-only fallback. NEW-B and NEW-C are small and should be absorbed into NEW-A's spec.

## Difficulty curve

- **Teaching order** is the best-structured of the corporation drafts. It runs Crier, Dole, Legionary, Tax Farmer, Lictor, Vestal, then the elites.
- The Games Master is a 3-phase mini-boss at 86 / 106 / 132 HP. The band floor is used and the sustain math is shown, which is good.
- The boss at 380 HP over 17.6 turns uses all five phases. Two needles at P3 and P5 are the only double-needle content, so the boss's difficulty spike (P5 intake 19 at T4) arrives without preparation.
- The HQ run is 19 nodes at 30–36 minutes. Roughly 10 fights deal 110–140 HP of damage against a 60 HP operative, so it depends on healing the draft has not secured. That total is also well above the other corporations' HQ length.
- The Circus clock adds a timing puzzle that is unrelated to VERDICT. The "opening mark on every fight" rule means every HQ fight starts from a mark that is not in the normal roster.
- The Favor meter rewards Perfect landings on marked slices. The Rostrum's P4 inversion punishes Perfect landings. These two rules directly contradict each other.

## Identity

The set reads clearly as Aurelian: consent, grading, "terms apply", the Dole, the Games. The Service Lift and Verdict Broadcast events borrow the tone well. Two weaker points:
- The Verdict Broadcast uses `geostationary_guard`, an Orbital enemy.
- The Lanista's Contract uses `station_commander`, also an Orbital enemy.
- Both events pull in enemies that carry another corporation's mechanics, so these Aurelian events would deliver non-Aurelian fights.

## Concrete fixes

1. **Crier:** drop the gift; make it the plain "land GOOD" teacher and keep the Dole's debt trade in the Dole Cart only.
2. **Censor P1:** replace Interest with a mark-spreading slice (a mark placed on the neighbouring slice), so it does not duplicate the Tax Farmer.
3. **Roster:** add one elite or normal with two uneven needles (gap 11 or 13, single-phase), so the boss's P3 is not the first time.
4. **HQ §3.3 Favor:** invert the incentive. Award Favor for GOOD landings on marked slices, not Perfect. This also makes the Favor meter compatible with the Rostrum's P4.
5. **HQ length:** cut to 3 rings plus the arena (about 14 nodes, 22–26 minutes), or add guaranteed Rests. The 110–140 HP intake against 60 HP is unsupported.
6. **Events:** replace `geostationary_guard` and `station_commander` with Praetorian and Censor (the Aurelian elites are drafted).
7. **Service Lift:** the "Frozen start" plus "reveal phases" plus −30 % HP in choice 1 is too much of a discount. Drop `reveal_phases`.
8. **NEW-A spec:** fold NEW-B and NEW-C into it, and state the immediate-only reduced version (a CALL as an N6 listener) as the explicit fallback.
9. **Rostrum P5 finish:** add a note that the SANDBOX (N14) answer must be available to every class, since a pierce boss with no defences otherwise hard-counters classes with no SANDBOX slice.

## Q:

Q: Should Favor reward GOOD, so that Perfect-hook classes are not pushed toward the boss's P4 trap?
Q: Is a 3-NEW-system corporation (plus the Circus clock) acceptable, given that Aurelian is described as the "cheapest" to build?
Q: May the Aurelian elites carry two uneven needles at the cost of band overrun, or should the extra needle be a normal-class exception?
Q: Should the HQ's opening-mark rule be limited to Elite Routers only, so that ordinary Routers still teach plain wheels?
