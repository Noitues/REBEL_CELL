<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__hq__rebel_cell; status ok; tokens in 11904 cache-write 0 cache-read 32585 out 1861; cost $0.024. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: hq/rebel_cell

**Verdict:** FIX

## Issues

1. **BLOCKER, §2.1/§2.2/§3.1 (arithmetic and structure).** "9 steps" is described as 3 + 3 + 2 route steps + 1 switch step. The map table shows steps 1-8 route layers plus step 9, and §2.1 says "3 lanes × 8 route layers + switch layer = 27 nodes". The node count is wrong either way: it is 3 lanes × 9 steps with 2-3 nodes per layer. Also, "one step = three nodes resolved" is wrong for a lane with 2-3 *options* per layer, because each operative picks one.
2. **BLOCKER, §3.1 (determinism and UI).** The shared step makes three fights per step, one at a time, with a lane that "waits". The text conflicts: STALL means "holds in place while the others move", but the step "does not close until all three are done". A stalled lane has no node to resolve, so the clock rules contradict each other. Define one rule.
3. **BLOCKER, §3.3 (preview = result / R7 spirit).** The counter picks the lane by "most-used Firmware play count" and a Shop swap changes it. That is gameable, and the use-count stat does not exist. The same rule also applies the Mirror modifier (1 pointer, ×1.5) to a normal fight, which is an N6/M11 dependency that is not tagged.
4. **BLOCKER, §3.2/§8 (systems).** The relay uses N16 `next_combat_overrides`, but N16 is run-level and not designed for per-lane routing. The relay's "+1 weight" or "−10 % HP" HP edits must also respect R2 (percent amounts read the enemy's own max HP). The draft says "no data-only fallback" yet offers one in the same cell. Pick one.
5. **MAJOR, §3.4 (R3/R1).** The lone-pair penalty "DISPATCH core starts +1 phase advanced... +25 % damage" bypasses R1/R3. Skipping a phase is not designed in the boss draft. The 8 flat "backlash" damage must be ×tier factor (R2), and it is not stated how that damage is dealt.
6. **MAJOR, §3.5.** Absorbing a hit per phase for parked operatives hits preview = result. It also makes parked operatives take HP loss and potentially die, which is not covered in §7. The Botnet passive "+1 drone cap" is a Hub-level change, and the Breaker's "+10 % OVERFLOW" is an unscaled buff with no tag.
7. **MAJOR, §4.1 Virus.** It uses CORRUPTED on enemy wheels, but R9 retired damage and the draft's own Q admits it is unruled. §3.3 also invents "disabled one turn in two". Remove it or tag it as dependent on the Q3 ruling.
8. **MAJOR, §6/§7.** "Winning ends the campaign" conflicts with the retry text ("HQ netrun stays open") and with the entering operative dying permanently on boss defeat. Not stated whether the boss fight itself ends the run on a loss.
9. **NIT.** Hack puzzle seeded "from the netrun seed" needs a named RNG stream. "Site names" are not an issue. Spelling "synchronised" and "Counter-attack" should be US ("synchronized"). Run length of 50-55 min is not budgeted against the ~395-min campaign target.

## Concrete fixes

1. Replace §2.1 count: "9 steps × 3 lanes; each lane offers 2-3 nodes per step and the operative takes one. Total route nodes: 27 chosen, about 66 drawn."
2. Replace the §3.1 clock rule: "A step closes when every lane has resolved its chosen node or spent a STALL token (a STALL is the lane's node for that step: the operative does nothing, heals 0). A detour node takes two step slots in its own lane only." Remove "the lane waits".
3. Replace the §3.3 selector: "The countered lane is `(seed-fixed permutation)[step mod 3]`, previewed from run start. Intel shows the whole schedule early. Mirror modifier: NEW: mirror_fight, with a data-only fallback of an authored REBEL_CELL elite at that node."
4. Replace the §3.2 relay: "writes `combat_overrides` on the specific next-lane node at graph build (data-only) and at fight end via N16; the HP edit is a PERCENT of the enemy's max HP (N1)."
5. §3.4: "Lone pair: the boss starts with the Compliance buff off and enrage start −2 turns (N4). No phase skip. Backlash: 8 × `enemy_damage_by_tier[t]` (N2), pierce-free."
6. §3.5: "Parked passives are data rows. Drop the hit redirect (no new rule)."
7. §7: "A failed showdown ends the run; entering operative follows GDD 4.2; the HQ stays open."

## Keep

- The three-lane synchronization spine is genuinely unique among the HQs.
- The countered room previewed ahead preserves preview = result.
- Exploit payoffs per lane (§4.1) are legible, and the art state table in §9 is complete.

## Q:

Q: What is the minimum crew size if the campaign has fewer than three operatives?
Q: Does the whole run share one save checkpoint per step?
Q: Does a lane death cost Heat once or per death?
