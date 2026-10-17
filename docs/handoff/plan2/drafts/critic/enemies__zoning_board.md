<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__zoning_board; status ok; tokens in 6946 cache-write 0 cache-read 32585 out 1927; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/zoning_board

**Verdict:** FIX

## Issues

1. **BLOCKER, R2 HP bands / §4.** The P2 budget is multiplied by 1.5 to get 47/58/73/95. The R2 phase budget is the reference DPT × turns × the needles the player's hits land on, and 2 needles means ×2. The draft's own table then sums to 77/94/120/156, which does not match the HP column. Every tier is pinned at the band cap by choice rather than by derivation: the T1 cap is 72 and T4 is 144. The 1.5× factor is invented and the table is internally inconsistent.
2. **BLOCKER, R11 / §2 P1 layout.** The slice sizes are written as "Shim 12 → 6 ticks", a leftover edit. The sum 5+5+6+4+4+6 = 30 is correct, but a 6-tick Shim reads W W G G W W, so it has no Perfect. The draft also says "WEAK nudge for 0.5×" while calling the window narrow. P2 sizes 5+4+6+5+4+6 = 30 are fine, but the "Overflow occupies 11-16" sentence contradicts the tick check (9-14). Delete it.
3. **BLOCKER, R8/R9, §2 P2.** The Hub is "Compliance Lock: resistance 1", but §1 says the Board's hits mark your slices and the Hub is named as a "mild tax". The P2 needles at 0 and 12 read ticks 0 and 12, which are Shim (0-4) and Overflow (9-14), so at rotation 0 both needles sit on damaging slices. "Exactly one dangerous" is false at the default rotation. The tick-check line concedes it.
4. **MAJOR, R6 / §2 transition.** "The Civic Drone is removed by the override" contradicts the Keep section ("drone P1 only") only if satellites are cleared, and R12 says satellites are fixed and replaced only by docking. State it explicitly as data, or keep the drone.
5. **MAJOR, §3 sustain.** The "21 % of 14 dpt" figure uses 2.9 HP against 14, which is correct arithmetic. But the HEAL is PERCENT of max HP, which is fine under R5, and the Hotfix is a 4-tick slice with one landing per turn, so the "1 in 6" odds are wrong (4/30 ≈ 0.13). Minor, but the "0.5 %" number is not derived.
6. **MAJOR, intake §3.** Intake multiplies base values by 1.69 *and* the 1.69 factor is applied again to Shim 8 and Overflow 16. The P2 estimate "≈ 10-11" is hand-waved ("simplified"). Show it: 2 needles × (Shim 11/30·13.5 + Overflow 6/30·27) ≈ 2 × 10.4 ≈ 21, which exceeds the 8-12 target by 2×.
7. **MAJOR, §10.** The win estimate T4 82 % is below the criterion, with no fix offered. Also "Rezone" and "Variance Denied" are tagged as TIER_DOWN-new; N9 is cited, fine, but the "Variance rule" paragraph in §1 claims no listener while saying "only comes through when marked", and no such rule exists in the slices. Remove it.
8. **NIT, heat_effects.** "The file has none" is unverifiable from the draft. Say "decision: retire" without the claim.
9. **NIT, §1.** "Elites don't spawn in L1-2" is not established in the rulings.

## Concrete fixes

- **HP:** with P2 at ×2 and a P1 budget of 30/36/47/61, P2 = 63/77/98/126, giving totals 93/113/145/187. That is far above the band, so lower the P2 pressure instead: have P2 keep needle 2 mostly on Null, so the player's effective count is ×1. Set `hp_by_tier` = [64, 80, 100, 128] (floor 50 %: 32/40/50/64), with P1 ≈ 30/36/47/61 and P2 ≈ the remainder.
- **P2 layout:** Shim 5 (0-4) · Rezone 4 (5-8) · Null 5 (9-13) · Overflow 6 (14-19) · Rezone 4 (20-23) · Shim 6 (24-29). Needles at 0 and 12: Shim and Null at rotation 0, so one dangerous needle.
- **Intake:** lower the Overflow to 12 and the Shim to 6 (T3: 10 / 20 per hit). Expected ≈ 2 × (11/30·10 + 6/30·20) /… ≈ 8-10, inside target.
- **P1 Shim:** "Shim 6 ticks, 9 FLAT, no Perfect (window GG)". Drop the "narrow Good window" talk for WEAK nudging.
- **Drone:** "Civic Drone stays docked on P1 slot 1; P2 `wheel_override` clears satellites by data."

## Keep
- The territory concept (marking slices, Citation stacks carrying into P2 via R6) is a new question per phase.
- Needle asymmetry, 0/12, and the no-sustain P2 as a racing phase.
- The fallback list per system is honest.

## Q:
1. Should an enemy Hub resistance sit in P2 at all, given that P2 already taxes through TIER_DOWN?
2. Is TIER_DOWN on a 4-tick Rezone a dominated trap, given that Perfect is unavailable there anyway?
3. Does the drone's removal count as destroyed (V2 Q7)?
