<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01Y2bjt88e8i6ocTDPQPm21s, custom_id slup__hotfix; status ok; tokens in 13028 cache-write 0 cache-read 32585 out 3306; cost $0.033. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# slice_upgrades: HOTFIX

## 1. Role of the type
HOTFIX is the player's HP recovery slice (`target_rule` SELF, heal). It is the only slice that spends tick-space on lasting HP rather than on damage or a defense tier. It buys sustain across a netrun, since HP carries between fights, and it is the cheapest way to survive attrition. HOTFIX is a player slice here, and enemies keep their own HOTFIX slices under R2.

Today's variants are `hotfix_4` and `hotfix_6`, both 5-tick slices with FLAT base_output 4 and 6. They are redundant: the same slice with a bigger number. Level I-IV replaces this pair. `hotfix_4` becomes Level I and `hotfix_6` is retired from the pool, with an alias in the save migration.

Design question: a heal that lands a tick off should degrade smoothly. WEAK already halves it (×0.5). PERFECT stays ×1.0, so the heal pays for precision only through size and the Level effects below.

## 2. Level table
Placeholders pending the sim. The 30-tick wheel and about 6 slices mean a 5-tick slice is the baseline. Output is FLAT unless noted. Percent heals read max HP (R5) and are never scaled again (R2).

| Level | Size | Ticks | Output | Extra effect | What it costs |
|---|---|---|---|---|---|
| I | 5 | W G P G W | FLAT 4 | none | baseline |
| II | 4 | W G G W | FLAT 7 | none | no Perfect, 1 fewer tick of wheel; steadier |
| II-alt (branch) | 5 | W G P G W | PERCENT 8 % max HP | none | scales with HP pool, worse on low-HP classes |
| III | 3 | G P G | FLAT 6 | Perfect: also cleanses 1 of your CORRUPTED slices | narrow and precise, no WEAK ticks |
| IV | 6 | W W G G W W... see below | | | |

I use the branch structure below instead of a ladder, so Levels are lateral choices.

**Final table (Level I to IV):**

| Level | Size | Pattern | Output | Extra effect | Trade |
|---|---|---|---|---|---|
| I | 5 | W G P G W | FLAT 4 | none | baseline |
| II | 4 | W G G W | FLAT 7 | none | gives up Perfect for reliable, bigger heal; frees 1 tick of wheel |
| III | 3 | G P G | FLAT 6 | Perfect: cleanse 1 CORRUPTED slice of yours | gives up WEAK safety, and the heal is lower than II unless you hit the centre |
| IV | 3 | G P G | PERCENT 10 % max HP | Perfect: ×2 heal and also gain SHIELD equal to the heal (cap 15 applies) | smallest size; needs deliberate steering; the wheel has few slices |

Why these are choices:
- **I → II** trades the Perfect hook for +3 output and −1 tick. Good for classes without Perfect hooks; bad for Breaker, whose Perfect resolves twice.
- **III** is lower flat output than II, but cleanses on Perfect. It is the answer to CORRUPTED RAM tax (R9) and Genome Core P2-P4.
- **IV** at 3 ticks is the exciting one: a Perfect heals 20 % max HP plus a SHIELD, a big swing. A Good heals 10 %. It scales with the pool, so it suits tanky classes.

Mapping to existing fields:
- Size → `WheelSlotData.size_ticks` (N12).
- `base_output` stays the number; add `amount_mode` (N1, FLAT or PERCENT).
- Level III's cleanse and Level IV's shield go in `extra_effects`, gated by a Perfect trigger (ON_PERFECT exists).
- New fields: `SliceData.level` (int 1-4), `SliceData.upgrade_group` (StringName, e.g. `hotfix`), `SliceData.tick_quality` override (R11, N12).
- Each Level is its own `.tres` (`hotfix_l1` ... `hotfix_l4`). An upgrade is a lookup `upgrade_group` + `level+1`, not a mutation.

## 3. Tick-quality interplay (R11)
- A 4-tick II has no Perfect, so Perfect-only effects (class hooks, Kernel Sync, Breaker doubling) never fire. That is its price.
- III and IV are G P G. With a Calibrated chip (every sub-tick one tier up), III reads P P P: any landing is Perfect, so the cleanse/shield effect becomes reliable. Calibrated is therefore strongest on III and IV, and weakest on I, where only WEAK edges improve.
- Calibrated on II (4-tick) gives G P P G: a Perfect-enabled heal at size 4. That makes II+Calibrated a real build.
- A 3-tick slice is not mandatory: II (4) and I (5) heal more reliably per landing chance. A 3-tick slice is not pointless: it has no WEAK, so its worst landing still gets ×1.0.
- No Level goes below 3 ticks. Size 1-2 slices (G G, or 1-tick) are left to other types to avoid a "tiny mandatory heal".
- A WEAK landing halves the heal (×0.5), unchanged.

## 4. Rack flash (G15)
At a Server Rack the player picks **one** of:
- **Upgrade** a chosen slice by one Level (same `upgrade_group`), or
- **Swap** it for a slice from the pool.

Offer details:
- **Choices:** the flash offers 3 cards. Each is either "upgrade slot X to Level N+1" or "swap slot X for pool slice Y". The player chooses one card. Offers draw from the `rewards` RNG stream, previewing the exact outcome, including the new tick map (R11).
- **Rarity:** Level II offers are common, III uncommon, IV rare (Rack weighting only; T3+ racks or the final Rack raise the chance). A flash cannot skip Levels.
- **Type swap:** allowed. A HOTFIX slot can swap to any pool slice at Level I (Level carries over at most one step lower, floor I). This stops a pure upgrade treadmill.
- **How HOTFIX shows up:** it appears in upgrade offers if the wheel holds a HOTFIX, and in swap offers at weight 1 as Level I. The offer UI shows the old and new tick map side by side.
- **Cost:** free (it is the Rack reward). Dropping the other Rack rewards is the cost.
- **Reward-table row:** N18 `RewardTableData` row kind `slice_flash` with `count` 3, `chance`, and conditions (node type = Server Rack, layer 4 vs 7).

## 5. Economy
- **Shop/workshop (D4 Workshop node):** upgrade a slice one Level for Cycles. Placeholders: II 60, III 90, IV 140. Swaps cost 40 (the shop wheel prices of G14 are separate). Workshop upgrades are rarer than Rack ones.
- **Firmware sockets:** a socket belongs to a slot, not a slice, so Firmware stays when the slice upgrades. If a swap changes type, the confirm names any Firmware the new type cannot take (`allowed types`, e.g. `nanite_mesh` is HOTFIX only), and the chip returns to the pack rather than being destroyed.
- **Nanite Mesh interplay:** +50 % output on a slice that cleanses itself fits Level III (6 → 9). It makes Level IV's percent heal bigger as well. It overlaps Level III's cleanse, so Nanite Mesh on III is redundant for the Perfect cleanse: acceptable, since the chip still adds output.
- **Patch+:** multiplies output; on PERCENT it is multiplicative with the percent.
- **Stacking guard:** Level IV + Patch+ + Nanite Mesh gives ~22 % max HP on a Good. Placeholder cap: heal per resolution ≤ 30 % max HP, to be checked in the sim.

## 6. Systems and data
- **N12** (slice sizes, `tick_quality`), required. No data-only fallback for sizes; fallback is keeping every Level at 5 ticks and varying only output and effects.
- **N1** amount modes for the PERCENT heal (Level IV). Fallback: FLAT only.
- **N18** reward table with `slice_flash`, M.
- **NEW: slice upgrade lookup** (`level`, `upgrade_group`, upgrade/swap action, Workshop UI), S-M.
- **NEW: Perfect-gated extra_effects** is expressible with ON_PERFECT; a cleanse of the player's own slice already exists as CLEANSE with `SlicePick.CHOSEN` (check it also supports the RANDOM pick).
- Migration: `hotfix_4` → `hotfix_l1`, `hotfix_6` → `hotfix_l2`-equivalent (output only), without a save format bump.

Q: Should Level II's 4-tick shape (no Perfect) be the default upgrade path, or is giving up Perfect too punishing for Perfect-hook classes?
Q: Should a type swap keep its Level (minus one) or always reset to Level I?
Q: Is Level IV's SHIELD-on-Perfect too close to the SHIELD slice's role?
Q: Does the PERCENT heal need a per-resolution cap (proposed 30 % max HP) on the player side, like `shield_cap`?
