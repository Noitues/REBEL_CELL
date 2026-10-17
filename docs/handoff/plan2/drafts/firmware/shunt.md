<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__shunt; status ok; tokens in 2309 cache-write 0 cache-read 32585 out 1478; cost $0.013. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: shunt

**Verdict:** CHANGE

1. **What it does today:** When you land off-centre, it resolves the neighbor on the side you landed toward at 1.5×, and nothing happens on Perfect. It works on any slice type. It is a gamble chip: it rewards Good and WEAK landings and punishes Perfect, so it is the opposite of Mirror. It suits Breaker and Ghost wheels that sit a strong slice next to a weak one (Overflow next to Null).

2. **Under the new rules:**
   - **Variable sizes (R11).** Landing "toward a side" is clean in a 5-tick slice (±1, ±2). In a 4-tick slice (W G G W) no tick is the centre, so every landing is off-centre and Shunt always fires. In a 3-tick slice (G P G) only the Perfect tick escapes it. In a 2-tick slice (G G) it is permanent. Hence a "nothing on Perfect" drawback that varies from 20 % of landings down to 0 %. The 4-tick case is a degenerate dominant pick: a free 1.5× neighbor with no downside.
   - **Calibrated Firmware.** A 4-tick slice that reads G P P G makes the Perfect ticks off-centre, and the "side" is undefined there.
   - **Quality loss.** The slice's own action is lost whenever Shunt fires, and that includes the slice's own Perfect hook.
   - **Statuses.** OUTPUT_DOWN and TIER_DOWN are read on the neighbor, so you must be able to see the neighbor's state. ENCRYPTED and Cleanse on the neighbor become part of planning. If TIER_DOWN lowers a Perfect to Good, Shunt starts firing, which is an odd interaction. Pointer rule: evaluate Shunt on the tier before TIER_DOWN.
   - **Parasites.** A Parasite read on the Shunt slice should still apply.
   - **Corruption.** The corrupted RAM tax is paid on the acting slice, not the neighbor. Shunt is a cheap way to use a corrupted slice's neighbor at 2× RAM.
   - **Defense trio.** Shunting into SANDBOX, SHIELD or BLOCK is a good redirect.
   - **Satellites.** Fixed satellites on the neighbor do not resolve; only the slice does.

3. **Proposed spec:**
   - **Description:** "When you land off-center, resolves the neighbor on that side at 1.5× instead of this slice. A Perfect resolves this slice normally. Needs a slice of 5+ ticks."
   - **Change:** Perfect now resolves this slice at 1.0×. This removes the dead-Perfect penalty, so the chip is a cheap alternative to Mirror and not a trap.
   - **Allowed:** any slice type, restricted to size_ticks ≥ 5 (new `min_slice_ticks` = 5). Sockets on 2–4 tick slices are refused, which kills the always-on case.
   - **Multiplier:** 1.5 → 1.25 to offset the safer Perfect.
   - **Rarity and cost:** rarity 1 (uncommon), 110 Cycles (up from 100).
   - **Reads on the slice:** an arrow on each side edge with a ×1.25 badge, and the loadout sub-tick map tints the off-centre ticks "→ neighbor".

4. **Data:** `firmware_data.gd` gets `min_slice_ticks` (new int, default 0). `neighbor_multiplier` = 1.25, `rarity` = 1, `cycle_cost` = 110, and the resolver changes the Perfect branch to resolve self. Sub-tick "side" uses sign(d) from the slice centre; a tie on an even-sized slice is off-centre and never "Perfect". Depends on N12 (size and sub-tick map), and `min_slice_ticks` is NEW: socket size gate. Fallback: with 5-tick slices only, the data change alone works. Size: S–M.

5. **Q:** Should a Calibrated chip's raised P ticks on even slices count as "centre" for Shunt, or is Shunt keyed to the geometric centre only?
   Q: Should Shunt be allowed on 4-tick slices if the neighbor multiplier is cut to 1.0×, as a pure redirect?
