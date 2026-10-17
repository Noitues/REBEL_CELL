<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__echo_process; status ok; tokens in 4505 cache-write 0 cache-read 32585 out 1643; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/echo_process

**Verdict:** FIX

## Issues

1. **BLOCKER, R9 / rulings (corruption).** §2 Dose: "3 damage + CORRUPTED on 1 random non-NULL slice". It also says "With the old rule it still works (self-damage)". CORRUPTED is now a RAM x2 debuff and the self-damage rules are retired. The N9 fallback line is invalid.
2. **BLOCKER, Rule 3 / N-tagging, §8 fallback.** "delete Echo and use an existing slice effect... not viable." The text trails off, then says "with Priority kept". Priority was dropped in §2, which contradicts it. No usable data-only fallback is given.
3. **MAJOR, arithmetic, §3 intake.** Average slice damage is (8+3+14+8)/6 = 33/6 = 5.5, which is correct. But the draft lists the slices as Shim 8, Dose 3, Defrag, Overflow 14, Null, Shim 8 = 33 damage, and the 5.5 x 1.69 = 9.3 figure is correct. Adding Echo gives 9.3 + 2.3 = 11.6, not "9-11". The T3 "about 35 HP over 3.5 turns" uses 10, which is fine, but the T1 figure of 6.5 omits the Echo term (4/3 = 1.3, so 5.5 + 1.3 = 6.8).
4. **MAJOR, design quality / dominated choice, §1-2.** Only 2 of the 6 slices (10 of the 30 ticks) can ever be Perfect, and Perfect has no output bonus. A player at GOOD loses nothing. Echo is therefore almost never paid except by Breaker. Weak and strong players see the same fight, and the question "will you pay?" has a trivial answer for non-Breaker classes.
5. **MAJOR, R4/N6 determinism, §2 listener.** "Cap: 1 trigger per turn" conflicts with the Q: lines, which ask whether it is once per Perfect or once per turn. That is an open rule stated as settled. The listener also needs a stated preview (the Echo hit must show in the result chip, undo-clean).
6. **MAJOR, R2 sustain/win, §10.** The draft predicts T4 win at about 85 %, below its own proposed T3/T4 criteria. It "fixes" this with a number change but leaves the T4 result failing. T3 at 92 % passes.
7. **NIT, §2 Dose.** "1 random non-NULL slice" needs a named RNG stream or a deterministic pick. Note the existing SlicePick.RANDOM_NON_NULL.
8. **NIT, §4.** hp_by_tier 32/38/50/62 are all inside the bands. Good.

## Concrete fixes

- **Fix 1:** replace §2 Dose with "3 damage x tier factor + CORRUPTED on 1 non-NULL slice (SlicePick.RANDOM_NON_NULL)". In §8 write: "N9: CORRUPTED = RAM x2. Fallback: none needed for Dose; with the old rule the slice is only a worse version."
- **Fix 2:** §8 fallback: "No Echo without N6. Data-only fallback: replace Echo with a plain Overflow, Shim and Defrag normal. Priority stays dropped."
- **Fix 3:** §3 T3: "9.3 + 2.3 = 11.6 per turn (about 28 HP if Perfects are avoided, about 40 if ignored)". T1: "5.5 + 1.3 = 6.8".
- **Fix 4 (make Perfect matter):** Echo price = 4 x factor, but give Shim 8 a Perfect-only rider: "on a Perfect, Shim 8 also applies OUTPUT_DOWN x1 to your slice under the pointer". Or widen Perfects: make Defrag 5 ticks and add a Perfect BLOCK bonus. The player's Perfect then buys something against Echo.
- **Fix 5:** state it: "Echo fires once per resolved Perfect slice; a Breaker double-resolve counts as one. Preview shows 'ECHO -N' on the HP chip."

## Keep

- The single-question identity (taxing precision itself) is distinct from the Handler and Mirror Script.
- The layout sums to 30 and uses uneven slice sizes with a meaningful no-Perfect map.
- The HP-per-tier arithmetic is clean and in band.

## Q:

Q: Should Echo trigger on Perfects from satellites or drones as well?
Q: Should Echo's price scale with the landed damage (PERCENT) to keep it relevant at T4?
Q: Should the Calibrated Firmware's raised sub-ticks count as Perfect for Echo?
