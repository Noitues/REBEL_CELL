<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__mirror; status ok; tokens in 2297 cache-write 0 cache-read 32585 out 1459; cost $0.013. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: mirror

**Verdict:** CHANGE

1. **What it does today:** When the pointer lands off-centre, the slice also fires its clockwise or counter-clockwise neighbour at 1.0×. On a Perfect it fires both neighbours. It fits any slice type and costs 100. It is a build-around for offense and defense lines, because it turns one slice into a 2–3 slice resolve. It works best on a slice sitting between two strong neighbours, such as Breaker's Shim/Overflow cluster.

2. **Under the new rules:**
   - **Good:** neighbour choice depends on which side of the centre you landed. Variable sizes make that readable and tunable. A 6- or 7-tick slice has a wide off-centre band, so Mirror fires nearly every time and rarely sees a Perfect.
   - **Breaks on even sizes:** a 4-tick slice (W G G W) has no centre tick, so "the side you landed" is ambiguous. A 2-tick slice (G G) is always off-centre and never Perfect, so Mirror is a guaranteed single neighbour. The "both on Perfect" bonus is dead on sizes 2, 4 and 6. This is a dead-chip risk.
   - **Needs a definition:** with uneven slice sizes, "neighbour" is just the adjacent slice by cumulative boundaries. A WEAK landing near a boundary copies the neighbour at full strength, which exceeds the base WEAK output (0.5×). That is the current behaviour and should stay.
   - **Calibrated Firmware:** it raises sub-ticks a tier, which makes Perfect more common on a 4-tick slice. That is a good synergy, since both-neighbour fires become reachable.
   - **Degenerate:** Mirror on a DEFRAG/SANDBOX slice flanked by Shim and Overflow fires three effects per resolve. Fire Mirror next to a Mirror slice and it could chain, so neighbour copies must not trigger the neighbour's Firmware. That is true today too, so state it explicitly.
   - **Statuses:** OUTPUT_DOWN and TIER_DOWN on the host slice reduce the landing tier (Perfect → Good), which loses the second neighbour. TIER_DOWN is therefore a strong anti-Mirror tool. Copied neighbours carry their own statuses. CORRUPTED doubles RAM only on the acting slice, so it is fine. ENCRYPTED is unaffected.
   - **Parasite ring:** a parasite that reads at the pointer is independent of Mirror, so there is no conflict.
   - **Enemy listeners:** "counter on any Perfect" punishes the Perfect-both bonus, which is healthy tension.

3. **Proposed spec:**
   - Description: "Also fires the neighbor on the side you landed. On a Perfect, fires both. On a slice with no center tick (even size), fires the neighbor on the side of your landing, and a GOOD at the middle fires both."
   - Rule for even sizes: the two middle ticks count as "centre" (both neighbours) only if they read Perfect, which Calibrated allows. Otherwise they copy the nearer-side neighbour. Ticks left and right of the middle copy their own side.
   - Rarity: 1 (uncommon). Cost 110, up from 100, since Mirror is one of the strongest chips.
   - `allowed_slice_types`: any. `neighbor_multiplier`: 1.0 on the first copy, 0.75 on the second copy on a Perfect. This caps the triple-resolve spike.
   - Reads on the slice as small "◄ ►" arrows on the sub-tick map. Only the side your landing falls on lights up.

4. **Data:** add `perfect_second_multiplier` (default 1.0) to `firmware_data.gd`; change `mirror.tres` to 0.75, rarity 1, cost 110. The even-size rule needs N12 (S, in `wheel_math` neighbour lookup). Data-only fallback: 0.75 and the cost change, keeping today's resolution.

5. **Q:** On a 2-tick slice, should Mirror always fire a single neighbour, or is it excluded (`min_size` 3)?
   Q: Should a copied neighbour fire its own Firmware riders, or only its base slice?
