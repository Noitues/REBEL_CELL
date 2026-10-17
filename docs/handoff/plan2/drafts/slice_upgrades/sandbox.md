<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01Y2bjt88e8i6ocTDPQPm21s, custom_id slup__sandbox; status ok; tokens in 13028 cache-write 0 cache-read 32585 out 3073; cost $0.032. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# slice_upgrades: SANDBOX

## 1. Role of the type
Under R13 the SliceType value 4 (today's SANDBOX, "shield") is **SHIELD**: lingering, capped by `shield_cap` = 15. The new SANDBOX (negate one whole attack) is today's DETOUR (value 3) and is not designed here. SHIELD is the slow bank. It is the one defense that pays off over several turns, so it rewards planning and Perfects on turn N for damage on turn N+3.

**Today's variants:** `sandbox_5` and `sandbox_8` differ only in output, so they are the same slice at two Levels. They are replaced by one slice with a Level field.

**Redundant firmware:** `bulkhead` (+50 % on DEFRAG and SANDBOX) overlaps the Level output curve, and `power_cell` is a RAM rider that fits Level III. I propose retiring `bulkhead` or narrowing it to BLOCK. `static_coat` (a DEFRAG slice that also gives shield) stays; it is the BLOCK-to-SHIELD bridge.

**The cap problem:** with a cap of 15, output above ~10 is wasted. Levels therefore must not just raise output. They change *how* the shield fills and what it does once banked.

## 2. Level table
Output mode: SHIELD amounts are **FLAT** at Level I–II (small numbers are legible) and **PERCENT of max HP** at III–IV (R5), so they scale with an operative's HP (45–60). Percent is capped by `shield_cap` anyway.

| Level | Size | Ticks (W/G/P) | Output | Extra effect | Cost / tradeoff |
|---|---|---|---|---|---|
| I (base) | 5 | W G P G W | 5 FLAT | none | none (today's `sandbox_5`) |
| II-a "Wide Plate" | 7 | W W G P G W W | 7 FLAT | none | Takes 2 ticks from other slices; the Perfect window stays 1 tick. |
| II-b "Dense Plate" | 4 | W G G W (no Perfect) | 8 FLAT | none | Smaller and steadier, but never a Perfect and never triggers Perfect hooks. |
| III-a "Reactive" | 5 | W G P G W | 15 % max HP (~8) | On a Perfect: +4 shield and restore 1 RAM | Same size; a pure precision reward. |
| III-b "Capacitor" | 6 | W W G G W W | 20 % max HP (~11) | If shield is already ≥ 10 when it resolves, the overflow converts to 1 RAM per 3 wasted | Big and blunt; no Perfect; anti-waste. |
| IV-a "Aegis" | 5 | G P P P G... see §3 (5-tick map `G G P G G`) | 25 % max HP (~14) | The shield cannot be stripped by status effects; the first enemy hit each turn against shield is reduced by 50 % | Output hits the cap in one landing; the slice is an anchor, with no scaling past it. |
| IV-b "Reflector" | 3 | G P G | 15 % max HP | Shield absorbed this turn is dealt back as damage to the pointer target, up to 8 | Only 3 ticks, so it is easy to miss but rarely WEAK: a tiny, always-Good slice. |

**Why these are choices, not a ladder:**
- Size: II-a costs board space and II-b gives up the Perfect.
- III-a rewards precision; III-b rewards sloppy play.
- IV-a is the "hold the line" build; IV-b is the aggressive size-3 build that pairs with Perfect-only firmware.

**Why IV is exciting:** each IV changes how the wheel is played rather than raising a number (a stripped-shield immunity or a damage reflect).

**Field mapping:**
- Level → one `SliceData` per branch (e.g. `shield_l3a`), so content stays data-only.
- Fields: `size_ticks` (N12), `base_output`, `amount_mode` (N1), `extra_effects` (riders, N20).
- **New fields:** `level: int`, `upgrades_to: Array[SliceData]` (up to 2 branches), `tick_quality` override (N12). `overflow_to_ram` is a NEW rider (see §6).

## 3. Tick-quality interplay (R11)
- A slice's *base* map comes from its size. Levels only override the map where it matters: IV-a authors `G G P G G` (the WEAK edges become GOOD). This is a slice-authored quality bump, so a size-5 shield feels Perfect-forgiving.
- **Calibrated** (a chip: every sub-tick up one tier) stacks on the slice's own map but never above PERFECT. On IV-a it turns `G G P G G` into `P P P P P`, which is strong but costs the socket. It does not stack with the IV-a quality bump beyond that, which keeps it fair.
- **Perfect-only effects:** III-a's +4 shield and +1 RAM, and the class Perfect hooks, need a Perfect. Size-4 (II-b) has none, so it trades them for a flat bonus.
- **Sizes 2–3 stay viable:** IV-b is a size-3 slice with a dedicated payoff. A size-2 slice (G G) exists only as a Level II-c option for a very dense build; not authored now.
- **Not mandatory:** the cap (15) means going big has diminishing returns. Four 5-tick shields would waste output. SHIELD is best as 1 slice per wheel.

## 4. Rack flash (G15)
The Server Rack offers a **flash** row: pick one, upgrade OR swap.
- **Offers:** 3 choices drawn from the player's wheel and pool, rolled on the `rewards` RNG stream and fixed on entry (preview = result).
- **Upgrade:** a slice of this type offers its next-Level branches (II-a and II-b both shown, so the choice is visible). At III and IV the offers show both branches.
- **Swap:** replace the slice with another of the pool at the same Level. The **type can change** (SHIELD to a BLOCK slice) at Level I only; a swapped slice resets to Level I of the new type.
- **Rarity:** Level III branches appear at Racks only on Racks after layer 4; Level IV only from the final Rack or a Mini-Boss Rack. This keeps IV exciting and rare.
- **Cost:** free at a Rack. The Rack reward is a one-of-N choice.
- **Sizing:** an upgrade that changes size must fit; if the wheel's total would exceed 30, the flash screen asks which neighbor shrinks by a tick and shows it.
- **Reward-table row (N18):** `kind = slice_flash`, `count = 3`, conditions: node = Rack, layer ≥ 4; IV filtered by `min_level_layer`.
- **How SHIELD shows up:** weighted up for operatives with ≥ 1 SHIELD slice; at most 1 SHIELD offer per flash screen.

## 5. Economy
- **Shop (Mainframe):** the slice wheel sells upgrades at placeholder costs: Level II 100, III 160 Cycles (G14 prices apply to the top slice). Level IV is not sold.
- **Workshop (D4 node):** one upgrade for free or a Level II to III at a discount, once per visit.
- **Firmware:** each slice has one socket. Upgrading keeps the chip, but the chip's allowed types are rechecked; if invalid, it returns to the inventory. `bulkhead` becomes redundant, so retire it or change it to PERCENT mode.
- **Campaign:** Levels reset on death. The operative keeps them on completion (like Firmware).

## 6. Systems & data
- N12 (`size_ticks`, `tick_quality`), L; fallback: only 5-tick Levels I, III-a, IV-a.
- N1 (amount modes), S–M; fallback: use FLAT numbers for all Levels.
- N14 (defense trio rename), S–M.
- N20 riders (`on_perfect_bonus`, `overflow_to_ram`, `shield_immune`, `reflect`), S–M. NEW: `overflow_to_ram` and `reflect` riders, plus a `damage_reduction_first_hit` rider. A data-only fallback is III-a and IV-a without their riders.
- N18 `slice_flash` row, M; waits for this pass.
- NEW: `SliceData.level` and `upgrades_to`, S, data only.

**Q:** Should Level IV branches be exclusive (one pick, permanent), or can a Rack respec a branch?
**Q:** Is a 50 % first-hit reduction too strong against the Genome Core's multi-hit IVs?
**Q:** Does a shield cap raise at Level IV (e.g. 20) make Level IV more exciting than the stripped-immunity design?
**Q:** Should the shop sell Level II only, leaving III and IV for Racks?
