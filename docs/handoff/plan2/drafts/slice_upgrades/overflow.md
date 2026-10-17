<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01Y2bjt88e8i6ocTDPQPm21s, custom_id slup__overflow; status ok; tokens in 13837 cache-write 0 cache-read 32585 out 2995; cost $0.032. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# slice_upgrades: OVERFLOW

## 1. Role of the type
OVERFLOW is the burst slice: one big hit, slow to land. Breaker opens with one, and it carries the class Perfect hook (resolves twice). Its question is "do I pay for precision to cash in the big number?"

Today's variants:
- `overflow_12`, `14`, `15`, `16`, `24` differ only by `base_output` on a 5-tick slice, so they are redundant as separate types. They become Level and pool-rarity values.
- `overflow_12_drain` (hit also drains 2 RAM from the target) is the only distinct variant. It stays as a branch flavor.

All Overflow content collapses into **one family with a Level**. Output scales with enemy tier through the player's Level instead.

## 2. Level table
Output is FLAT (a hit; PERCENT of enemy HP would break the R2 phase budgets). Sub-tick maps follow R11: P = Perfect, G = Good, W = Weak.

| Level | Size | Quality map | Output | Extra effect | Cost / give-up |
|---|---|---|---|---|---|
| I (base) | 5 | W G P G W | 12 | none | none (today's `overflow_12`) |
| II | 4 | W G G W | 16 | none | No Perfect: the class hook never fires from here. Smaller target, +33 % output. |
| II-alt | 6 | W W G G W W | 14 | none | Wide but never Perfect; safer landing, costs 1 tick of wheel space. |
| III | 3 | G P G | 20 | Perfect: ×1.5 (30) | A tiny target, but no WEAK ticks. Every landing is at least Good. |
| IV-A "Detonate" | 3 | G P G | 24 | Perfect: ×2 (48), and drains 2 RAM from the target | Pays out only on exact alignment. Perfect is 1 tick in 30. |
| IV-B "Overrun" | 5 | W G P G W | 22 | Hits twice on Good or Perfect (second hit at 50 %) | Keeps the wide target and a modest ceiling: reliable, not spiky. |

**Why each level is a choice:**
- I → II trades the Perfect hook (a Breaker-core loss) for output, and II-alt trades output for width. Breaker players care about the hook; Ghost/Rigger/Botnet players mostly do not.
- III shrinks the slice to 3 ticks, which frees 2 ticks of wheel space for other slices. That is the real price and the real gain: a Level III Overflow pays in space, not in resources.
- IV is a fork between a gamble (A) and consistency (B). Neither is a strict upgrade of III.

**Why IV is exciting:** Detonate is a 48-damage hit on one tick of 30, about the same as a T1 normal enemy's full HP. Preview shows the exact result, and nudges set it up. It makes Overflow the "solve the landing" slice. A Level IV-A plus two nudges to align is a deliberate turn, and the extra drain makes the payoff double.

**Field mapping.** Level is a derived value, not a stored one:
- Size is the new `size_ticks` on the slot (N12).
- `base_output` is the output column.
- Perfect multiplier and double hit use `perfect_multiplier` and `hits` (N20).
- Drain stays an `extra_effects` row (as in `overflow_12_drain`).
- The upgrade chain is `SliceData.upgrade_options` **(NEW: Array of {slice, label}, pointing at the next-level SliceData; data-only)**.
- `SliceData.level` **(NEW: int, 1–4, display and filtering only)**.
- `WheelSlotData.size_ticks` is already N12.

## 3. Tick-quality interplay (R11)
- The sub-tick map is the upgrade's main axis. Size 4 and 6 carry no Perfect, so Level II is a real sacrifice. A Perfect-reliant build (Kernel Sync, Zero Day, Clean Signal) should skip it.
- **Calibrated** (all sub-ticks one tier up):
  - On Level II (4 ticks) it reads G P P G, which returns Perfect to the slice and makes II + Calibrated stronger than Level I. The chip then pays for the Perfect that the level removed.
  - On Level III (3 ticks, G P G) it reads P P P: every landing is Perfect. This is the "build around it" combination, and Level IV-A with Calibrated becomes a guaranteed ×2. That would be too strong, so **IV-A's Perfect multiplier is applied only if Calibrated is not socketed** (a stated exception) or Calibrated is limited to slices of size ≥ 4. I choose the second: Calibrated's allowed sizes are 4–7, which keeps 3-tick slices honest.
- Size 1–2 Overflow slices do not exist. The floor is 3 ticks for output slices, because a 2-tick slice (G G) with ×2 Perfect is neither skill-expressive nor mandatory, and 1-tick has no Weak/Good gradient to read.
- Nothing forces the player to shrink: Level II-alt and IV-B keep or widen the slice, so big wheels stay viable.

## 4. Rack flash (G15)
- A flash offers **3 choices**, drawn by the `events`/`rewards` stream so previews equal results:
  1. Upgrade one Overflow slice by one Level (both branches shown at II and IV).
  2. Swap it for another slice of the pool, same type family only for common flash; one rare offer of any type.
  3. Skip, for +10 Cycles.
- Rarity: Level I–II come from the common pool, III from uncommon, IV only at layer-7 Racks or after a Mini-Boss. Overflow appears in a flash with weight proportional to how many Overflows the wheel holds, plus a fixed 15 % "you have none, here is one" row. This gives Breaker-less classes a way into burst.
- Cost: free at the Rack. The price is that it replaces the Schematics or Armory banking choice (pick one reward kind per Rack), so it competes with the existing reward.
- Row kind: `slice_flash` in `RewardTableData` (**N18**), with condition fields: node type = Rack, layer ≥ 4, tier.

## 5. Economy
- **Workshop** (D4 node): upgrade one level for 60 Cycles at I→II, 100 at II→III, 160 at III→IV (placeholders). Branch choice is made at the upgrade.
- **Shop**: Level I–II Overflows sold at the wheel-slice prices (100/80/100); no Level III–IV for sale, so those are earned at Racks and Workshops.
- **Firmware sockets** are kept across an upgrade; the resulting size may invalidate a chip (e.g. Calibrated on a 3-tick slice). The upgrade preview then shows "chip will unsocket", and a confirm appears (the G14 confirm). The chip returns to inventory rather than being destroyed.
- `overvolt` (+25 % to SHIM/OVERFLOW) and `tracer` (strips resistance on a Perfect) overlap lightly with Level III–IV. That is fine: IV-A with `tracer` is a Perfect that strips resistance, a deliberate combo. `patch_plus` stacks multiplicatively and needs checking in the sim.

## 6. Systems and data
- **N12** (slice sizes, `tick_quality`): needed for every level except I. No data-only fallback; without it only Level I and output upgrades (`base_output`, riders) exist.
- **N20** (`hits`, `perfect_multiplier`): needed for III and IV. A fallback is flat output only, which loses the Perfect payoff.
- **N18** (`slice_flash` row), S–M.
- NEW: `SliceData.upgrade_options` and `level`, data-only S, with a lint test that sizes sum to ≤ 30 after upgrade.
- NEW: Workshop upgrade page (the D4 node), M.
- N1 is not required: Overflow stays FLAT.

**Q:** Should the Level II no-Perfect penalty be softened for classes whose hook depends on Perfect (Breaker), for example by giving Breaker's wheel a hook variant that triggers on a 4-tick Good?
**Q:** Is the Calibrated restriction (sizes 4–7 only) acceptable, or should IV-A's multiplier be capped when Calibrated is socketed?
**Q:** Does a swap in a flash keep the Level (a Level III Overflow swapped for a Shim arrives as Level III), or reset to I?
**Q:** Should a size shrink require free wheel ticks to be reassigned manually, or are freed ticks distributed automatically to neighbours?
