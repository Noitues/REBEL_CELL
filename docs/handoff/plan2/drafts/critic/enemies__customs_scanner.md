<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__customs_scanner; status ok; tokens in 4801 cache-write 0 cache-read 32585 out 1918; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/customs_scanner

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 layout arithmetic:** the table lists 7 slices: 5+3+4+4+6+5+3 = 30, which is correct. But the "centred on ticks 2 / 7 / 11 / 15 / 20 / 26 / 29" claim is wrong. The cumulative-boundary centres are about 2.5, 6.5, 10, 14, 19, 24.5, 28.5, and no centre list is stated in boundaries. Needle 0 therefore does not read "Scan ticks −2…2" with a Perfect at 0. Fix by listing start ticks. Also "needle 2 onto Seizure" contradicts needles 0/11, and "ticks 9-12 = Null, 13-16 = Seizure" does not fit the layout.
2. **BLOCKER, §4 HP arithmetic:** the draft says it multiplies by ×1.0 for needles, but R2 requires the budget to count the needles the player's hits land on. Here a Pointer attack hits both needles, so the budget is dpt × 3.5 × 2 minus sustain. The "Sustain" column also multiplies block by the damage factor *and* by 3.5 with an unexplained 2.4. The result (34 at T1) is only coincidentally in band. Show the real arithmetic: the player's hit lands on the 2 needles only when both read live slices. Pick a stated needle factor of about 1.0–1.1 and say why.
3. **MAJOR, §3 sustain:** BLOCK 6 against the player's 9 dpt is 67 % per read. The 27 % average is inflated by an expectation trick: the cap applies to sustain per turn, 2.4/9 = 27 %, but the draft also says block "reduces the player's effective damage". Block on an enemy absorbs the player's damage, so this is fine. The real problem is that the table later scales it by the tier factor (R2 flat × tier damage factor), so T4 is 2.4 × 2.2 = 5.3 against 18 dpt = 29 %, barely OK. State this explicitly instead of the muddled column.
4. **MAJOR, §2 two-needle claim:** "Seizure lands once, not twice... not possible with 4-tick slices 11 apart." With needles 11 apart, Seizure (4) cannot be read by both, so the "which needle carries the tariff" question is mostly luck, not a choice. Both needles also have Scan (two copies, ticks about 0 and 22) as a dominated hazard. The one question is weak.
5. **MAJOR, §2 listeners/statuses:** "INFECT: drain 2 RAM" is not an INFECT effect; INFECT applies statuses. Use a DRAIN_RAM extra_effect on a slice and say so. Priority corrupts nothing, so fine, but label it.
6. **MAJOR, §10:** intake is stated as about 5 per turn (about 17 per fight) against a 45–60 HP player. This is roughly a third of the player's HP for a normal, which is high for L1–2 teaching. The "99 % win" is unsupported. Say that the Seizure expectation is 1.6 per needle, and reduce Seizure to 10 or Scan to 5.
7. **NIT, §1/§7:** "Kill in 3 turns" depends on Perfect landings, which the text then says are mostly unavailable. Also "pierce" appears nowhere, which is fine. §2 says "Needle count applies only to the player's attack", which is garbled.

## Concrete fixes

- **Layout (issue 1):** start ticks 0 Scan(5, −2..2 → start 28) is awkward. Use this order: Scan 5 (ticks 0–4), Priority 3 (5–7), Null 4 (8–11), Seizure 4 (12–15), Bulwark 6 (16–21), Scan 5 (22–26), Null 3 (27–29). Needle 0 reads Scan (tick 0 is its W edge), needle 11 reads Null's last tick (G edge). Rotation by 1 puts needle 11 on Seizure's W edge, which is a real "nudge across" hazard. Drop the "ticks centred on…" sentence.
- **HP (issue 2):** budget = dpt × 3.5 × 1.1 (needle factor, since both needles are live on about 70 % of landings) − block 2.4 × dmg factor × 3.5. T1: 34.7 − 8.4 = 26 (below band), so use the band floor: **hp_by_tier = [30, 38, 48, 60]**, and state it is band-clamped.
- **Sustain (issue 3):** "Block is 2.4 × tier factor per turn: T1 27 % of 9, T4 29 % of 18."
- **Intake (issue 6):** Seizure OVERFLOW 10 FLAT; the intake expectation becomes about 4.4 per turn at T1.
- **Priority (issue 5):** "Priority: 0 damage, DRAIN_RAM 2 via extra_effects."

## Keep
- The Priority RAM-drain identity and the Null/Seizure no-Perfect idea are a clean teach of the R11 sub-tick map.
- The fallbacks (0/10 needles, 5-tick slices) are correct and data-only.
- The data-only systems list (N1, N2, N11, N12) is honest and complete.

## Q:
- Q: Is a two-needle normal appropriate for L1–2 teaching, or should the second needle wait for L5–6?
- Q: Should the needle factor in the R2 budget be a published constant (e.g. 1.1) for two-needle normals?
