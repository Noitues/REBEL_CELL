<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__nodes__black_market; status ok; tokens in 5953 cache-write 0 cache-read 32585 out 2101; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: nodes/black_market

**Verdict:** FIX

## Issues

1. **BLOCKER, DECISIONS D4 / "Terminal" naming.** The node is a "Terminal-slot node" with an "UNKNOWN icon", but the ruling says Black Market is "maybe as an unknown event", and Site names are being removed. The draft invents a node kind and page ("NEW: node kind") where the ruling only allows an unknown *event*. It should be an event type reusing the Terminal slot, not a new node.
2. **BLOCKER, §2 "Heat price is rounded down to the nearest MINOR threshold".** This contradicts "FLAT 3–8" and Example A (+4, 12→16 crosses no threshold, so the rounding rule has no defined result). Example B's "+8" also contradicts the rounding. The rule is unimplementable and the preview text "no threshold crossed" is inconsistent with it.
3. **MAJOR, arithmetic and examples.**
   - Example A card HP "15 % of 60 = 9" is correct, but Example C "25 % = 15 of 60" exceeds the stated 10–25 % band only at its edge. At a 45 HP Botnet, 25 % is 11. This is fine, but the "can't go below 1 HP" floor must be shown.
   - Example B's "HEALTH pack ≈ 90 Cycles" is an invented price with no Mainframe base cited.
   - Example C offers "Zero Day" as a Daemon from the existing GDD list, but the "Leaky Signal (Kernel Sync variant)" and "Burner variant" in A and C are invented content ids.
4. **MAJOR, rule: Hot curse vs Heat cap.** Hot adds +1 Heat per combat for 3 combats, outside `bm_heat_cap` = 10. Example C stacks Hot at HUNTED 80 with a 75–100 gap, so a free good can trigger a PURGE-adjacent state unpreviewed. Hot must count against the cap and be previewed as total Heat.
5. **MAJOR, §2 Brittle.** "ENCRYPTED-immune and loses its effect after 3 combats" is two unrelated riders. ENCRYPTED does not interact with Firmware socketing, so "immune" is meaningless.
6. **MAJOR, §2 Fence conflicts with its own text.** The Fence is described as "the only way to convert surplus into Heat relief on a netrun", but Scrubber, Proxy Relay and Heat-objective Sites exist, and Proxy Relay applies to netruns. Fence also pays "Schematics banked now" mid-run, which GDD 4.2 only allows at Rack capture or completion (unbanked Cycles convert at 10:1). It is a new economy path with no cost note.
7. **MAJOR, §3 Exclusion at Heat ≥ 90 conflicts with weights ×1.5 at FLAGGED+.** The 90 cutoff and the "no Heat ≥ 75 wheel" in Example C mean the market is most unavailable where the draft says the cell is most desperate. State the HUNTED behavior once.
8. **MAJOR, §2 wheel.** "One nudge from a budget of 1; extra nudges cost 5 % max HP" is a new currency for nudges (RAM elsewhere), and `events` RNG at a checkpoint applies to the initial spin only if the wheel's stock is not fixed at generation. Stock is "fixed at map generation" while the crate is rolled, so the two statements overlap.
9. **NIT, §3.** A new RNG stream `black_market` is created, but N16/N17 already provide the `events` stream. Use it.
10. **NIT, §3 Halcyon ×0.5 and REBEL_CELL 0.** Fine, but Aurelian and Tethys (D1, 7 corporations) are not covered.

## Concrete fixes

- **1:** Replace "Terminal-slot node with UNKNOWN icon" with "an unknown event outcome of the Terminal slot, shown as the normal event glyph; no separate node kind." Delete the "NEW: node kind" row. The fallback becomes the primary implementation.
- **2:** Replace the rounding sentence with: "Heat price is FLAT 3–8 and is previewed as 'Heat 18 → 23; crosses 25? no'. A crossing is shown in red and still allowed."
- **3:** Replace invented ids with "(existing Daemon Kernel Sync, curse Leaky)" and "(existing Firmware Burner)". Show Mainframe base: "HEAL pack Mainframe price 60 × 1.5 = 90 (config `mainframe_heal_price`)".
- **4:** Add "Hot's total Heat (+1 × remaining combats) counts against `bm_heat_cap` at purchase and shows in the result chip."
- **5:** Brittle: "a Firmware that loses its effect after 3 combats (`duration_combats` = 3)."
- **6:** Fence payout becomes "−2 Heat per item" and "Cycles at 10:1 equivalent: card 20, Firmware 40, Daemon 60", or a Schematics credit that banks on completion only.
- **7:** State: "Heat ≥ 90 removes the market; HUNTED (75–89) keeps it with no wheel."
- **8:** "Extra nudge costs 1 RAM-equivalent: 4 % max HP" or drop extra nudges. Make the crate wheel's initial spin use `events` at a checkpoint.
- **9:** "Stock roll uses the `events` stream."

## Keep

- The non-Cycle price kinds with a visible downside make a real decision distinct from the Mainframe.
- The preview-before-commit with per-purchase undo and the Heat crossing warning.
- The explicit exploit list (Heat banking, HP laundering, trade loop with `fence_value = 0`) and the sim targets.

## Q:

Q: Is Hot's Heat paid at purchase, or accrued per combat?
Q: Should the Fence exist on a netrun at all, or only at HQ?
Q: Which price kind is the market's signature, to avoid every offer looking alike?
