<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__triage_unit; status ok; tokens in 4926 cache-write 0 cache-read 32585 out 1795; cost $0.017. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/triage_unit
**Verdict:** FIX

## Issues
1. **BLOCKER, R1/R2 "sustain at most one source" and cap 30 %.** Section 2 adds a Hub heal on top of the two Hotfix slices, so there are two sources. Section 3 calls the Hub heal "conditional" and then admits worst case T3 is 4.5 against a 4.2 cap. Section 2 also says the Hub heal is "the only extra sustain besides the Hotfix slices". It violates the rule either way.
2. **BLOCKER, arithmetic and R2 bands, section 4.** The sustain figures are inconsistent. Section 3 gives T3 sustain 2.3/turn, but section 4 subtracts 8.1 over 3.5 turns (2.3×3.5 = 8.05, fine). T1 4.6 / 3.5 = 1.3, fine. The real fault is the HP: T1 30 is in band, but T2 36 and T4 58 sit low in band while the budget says 52.8 at T4 (58 is above the budget it computed). The T3 budget is 40.9 and the draft uses 46. Three of four HP values exceed their own budget, and the "Block absorbs 15 %" rationale pushes them the wrong way (absorption argues for more HP only if the budget ignores it, but the draft's own formula says otherwise). The draft's T4 prediction of 4.5 turns breaks the 3-4 target too.
3. **MAJOR, hotfix scaling inconsistency.** Hotfix is "FLAT (× tier damage factor)" at 5, giving 11 at T4 (5 × 2.2). Intake uses Shim 6 × 2.2 = 13.2, correct. But the heal-chance table ignores WEAK halving, though the text says a Hotfix never lands Perfect and often lands WEAK. Average heal is overstated, so the sustain cap check is unreliable.
4. **MAJOR, R11 sub-tick map.** A 4-tick slice reads W G G W. Nudging by 1 tick from a Hotfix edge shifts a WEAK landing to the adjacent slice, which is the advertised counterplay and works. But the claim "Only the 5-tick Null has a Perfect centre" is wrong: a 6-tick slice has no Perfect, and the 5-tick Block (slice 1) does read W G P G W. Slice 1 Block therefore can land Perfect. The text and the Null-as-only-Perfect plan are inconsistent.
5. **MAJOR, systems.** `hub_condition` is tagged "NEW", and it is a new rule (damage-taken flag) that is a listener in effect. N6 (ON_HIT_DEALT / enemy listeners) fits better than a new field. The fallback "unconditional 2 % heal" also reintroduces the two-source problem. The N12 fallback of lowering Hotfix to 4 contradicts the changed table.
6. **NIT, template.** Section 7 "better player" says "W edge of a Block or Hotfix", but a 5-tick Block has W at both edges, fine. Section 11 lists 5 Q's (limit 5, OK) but the third and fifth are tuning, not design.

## Concrete fixes
- **Issue 1:** delete the Hub heal. Make Hotfix the single source: `Hub: none`. Section 3: "Sustain: Hotfix slices only, 2.3/turn at T3 vs cap 4.2." Fallback line for `hub_condition` goes away; remove it from section 8.
- **Issue 2:** set `hp_by_tier` = [27, 33, 41, 53], 0.9 × budget each (T1 26.9→27, T2 32.5→33, T3 40.9→41, T4 52.8→53). T1 27 is under the band (28), so use [28, 34, 44, 56] (band floors) and note the budget slightly exceeds. Predicted turns: T1 3.2, T2 3.5, T3 3.8, T4 4.0.
- **Issue 3:** avg heal = 0.27 × Hotfix × 0.8 (mix of G and W: half of the four ticks WEAK = 0.75). Use T3: 0.27 × 8.5 × 0.75 = 1.7; update the table.
- **Issue 4:** replace with "Only the 5-tick Block (slice 1) and the Null have a Perfect centre; the Block Perfect is harmless (BLOCK 6)."
- **Issue 5:** retag: if a conditional is kept later, "N6 (ON_HIT_DEALT listener)". Data-only fallback: none needed once the Hub heal is removed.

## Keep
- Two 4-tick Hotfix slices that never read Perfect: a clean, readable use of R11 and a real steering question.
- Intake of 1.2–2.6 per turn fixes the baseline's near-zero threat.
- The delta list and single-needle layout, with sizes correctly summing to 30.

## Q:
- Should Block slice 1 stay 5 ticks, or become 4 to remove the stray Perfect?
- With the Hub heal gone, is a single Hotfix at ~10 % of ticks enough to keep the "treats the worst-hurt" identity?
- Which T1–T4 HP row should the sim lock first?
