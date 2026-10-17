<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__04_future_orbital; status ok; tokens in 3658 cache-write 0 cache-read 32585 out 1480; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/04_future_orbital

**Verdict:** FIX

## Issues

1. **BLOCKER, template (Choices, new-system fields):** Choice 1 and 2 use `next_combat_overrides` with ad hoc keys (`phase_reveal`, "+1 free nudge", "satellite removed on spawn"). The fields `starts_combat`/`map_edits` read "none" but are not typed. N16 is named only in the fallback note, never tagged on the fields. Dependencies are untagged: free nudge, Frozen start, phase reveal and satellite removal each need an N# or NEW.
2. **MAJOR, determinism / R2:** The +15% damage in Choice 3 is in R2's buff category, which is fine, but "applied once, not stacked" and "Frozen start" lack a stated precedence rule. The Q about Heat stacking is a design gap the draft leaves open. Also "Frozen" is not an existing status. Freeze exists as a wheel action: "target skips its next start-of-turn respin". "Enemy starts Frozen" is therefore a new init flag, not a status.
3. **MAJOR, design quality, dominated choice:** Choice 1 (+2 Heat, two fights with Freeze + reveal) is almost free next to Choice 2 (−8 HP, one fight). Frozen only skips the first respin, so the pointer position is not even chosen. The draft says it applies "to the enemy's first phase", but a normal enemy has 1 phase, so "phase reveal" does nothing on normals. The draft also says reveal is skipped on bosses, and elites are the only ones with phases. Choice 1's value is mostly empty on normals.
4. **MAJOR, fallback:** Choice 3's damage rise has "no fallback", but a data-only version is possible: drop the override and use only Heat +6. The data-only fallback must still keep the choice distinct.
5. **MAJOR, template/spec:** Choice 2's reward, "Calibrated-style chip", duplicates the R11 Firmware, which depends on N12. No N12 tag or fallback (use Patch+ instead).
6. **NIT, Choice 4:** missing the full field list. Choice 2 lists `effects: none` with hp_cost 8, which is fine.
7. **NIT, Q about "Terminal-skipped nodes":** moot, since the override is consumed by combat creation.
8. **NIT, word count:** about 650 words. OK.
9. **NIT, template:** Choice 1's label states "+0 Cycles", which is noise.

## Concrete fixes

- **Fix 1:** Replace the new-system lines with typed, tagged fields:
  - C1: `next_combat_overrides = {combats: 2, enemy_start_freeze: true, reveal_next_layout: true}` (N16; the Freeze flag needs NEW: enemy_start_flags, fallback: none).
  - C2: `next_combat_overrides = {combats: 1, free_nudges_turn1: +1, remove_enemy_satellites: 1}` (N16, N13; fallback: a Firmware reward only).
  - C3: `next_combat_overrides = {combats: 2, enemy_damage_pct: +15}` (N16; fallback: Heat +6, no override).
- **Fix 2 (precedence):** "enemy_damage_pct overrides add with Heat modifiers; the same key never stacks, the highest wins." Then answer Q2 in the text.
- **Fix 3:** Make Choice 1 cost +3 Heat and restrict it to Elite/Mini-Boss fights in the next 3 fights (count only those that match), or drop the reveal on normals: "applies to the next 2 fights; reveal only matters on elites, Freeze on all." This fixes the dominance.
- **Fix 5:** Reward: "Firmware, uncommon: Calibrated (N12); fallback: Patch+."

## Keep
- The no-dominant-option structure, with the greedy Choice 3 and its deferred cost.
- The determinism note (run-state data consumed at combat creation).
- The text voice and the "ON FILE" HUD chip idea.

## Q:
- Should the Freeze flag count as Frozen for the Halcyon P2 Curfew lockout (stacking edge case)?
- Should Choice 2's satellite removal be allowed to carry over, or is a no-op simply wasted?
