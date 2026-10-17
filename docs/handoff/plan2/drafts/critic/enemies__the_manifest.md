<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__the_manifest; status ok; tokens in 6493 cache-write 0 cache-read 32585 out 1746; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/the_manifest

**Verdict:** FIX

## Issues

1. **BLOCKER, R1/R3 and the section 2 layouts (arithmetic).** Re-adding the tick sizes:
   - P1: 6+5+5+6+4+4 = 30 ✔
   - P2: 3+5+5+3+7+7 = 30 ✔
   - P3: 6+4+5+6+4+5 = 30 ✔
   - P4: 3+6+3+3+3+4+5+3 = 30 ✔
   - P5: 4+5+4+4+5+8 = 30 ✔

   The wheels add up, but the HP shares don't match the thresholds. The shares are 18 / 20 / 20 / 20 / 22 %. The stated assigned HP of 54+60+60+60+66 = 300 ✔, but 82/62/42/22 gives phase shares of 18/20/20/20/22, so 54/60/60/60/66 is consistent. The real arithmetic failure is the budget table: P4 has 3 needles, yet its needle factor is 1.0 and its 63 budget gives only 60 HP. Three needles should raise the HP budget (R2), not leave it flat.
2. **BLOCKER, R2 sustain cap.** The draft first states 6 HP/turn (2 % of 300), concedes it breaks the 5.4 cap, then "fixes" it to 1.5 % in prose only. Every table still says 2 %, and the Customs Seal buff says "+2 %". The "Weigh-in BLOCK not counted" claim is also shaky: a PERCENT block of 4 % (12 HP) every turn is effectively sustain. Weigh-in is also a second sustain source, which violates "at most one".
3. **BLOCKER, R6/R9, P4 transition.** `cleanse_on_enter = PLAYER` removes the player's corruption, which cuts against the "corruption is a RAM tax" design and invalidates the P2/P3 INFECT payoff. P4 Priority Lane then re-applies it. The justification ("to be fair") is not a question the phase asks.
4. **MAJOR, R9/R8.** The Priority INFECT is "drain 3 RAM + CORRUPTED". The RAM drain is a Parasite-ring/anti-slice effect, which is legal, but it stacks a second RAM tax on top of the 2× cost. Priority Lane in P4 does the same.
5. **MAJOR, R11/R12.** Sealed Crate (4 ticks) is described as "WEAK G G W, no Perfect" and "cannot be Perfect-read by the player's counter", which is confused. The map applies to the boss's slice, so a Perfect is impossible for the *boss's* output, and that is irrelevant to the player's counter. Also P1's Weigh-in sizes (5 and 4) differ for no reason.
6. **MAJOR, R7.** The buff table lists 8, but Second Head's counter is "Breach" and "Hub Breach exploit (today's Breach)" is used twice, so two buffs share a counter. The Lockout/Weight/Insured Cargo entries invent Exploit names ("Resistance Waiver", "Claims Audit", "Price Cap", "Manual Override"). Also, Insured Cargo heals 3 % per Weigh-in, which is a second heal source.
7. **MAJOR, R3/N3.** P1 is only 18 % while the "Intake" phase has a 2-turn-ahead orbit. Fine. But P5 has "no floor" and 22 %, which is inconsistent with the Intake question of "how much damage can you take".
8. **NIT, spelling/structure.** Sections 3 and 7 are thin, and the sim check has no turns-per-phase estimate.

## Concrete fixes

- **Sustain (issues 1–2):** Seal = SHIELD PERCENT 1.5 % max HP per turn (4.5 HP) in P1–P3 only. Change the Weigh-in to FLAT BLOCK 6 × tier factor, and state that it counts as non-sustain only because it expires. Remove Insured Cargo's heal, replacing it with "Weigh-ins block +50 %".
- **P4 HP:** 3 needles, budget 63 × 1.3 = 82, so the thresholds become 100/82/62/42/20/0 and the phases 54/60/60/60/66 are replaced by 50/55/55/70/70. Check: 50+55+55+70+70 = 300.
- **P4 transition:** set `cleanse_on_enter = NONE`.
- **Counters:** reassign Second Head → Breach, Seal → Hub Breach, and mark the other six names as "(Exploit name TBD)".

## Keep

The orbit-based "where will the pointer be" question is clear and distinct. The phase progression Intake → Last Mile gives each phase a new skill. The deterministic uneven-needle P4 plan is good.

## Q:

Q: Does the 5-phase fight reach 14–19 turns with 3.5 turns per phase at T4 only?
Q: Should Weight stay a buff if the Logistics Director already owns it?
