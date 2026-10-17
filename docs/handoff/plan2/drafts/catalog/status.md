<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01VfdWxebuNLgtnS39R7FQmN, custom_id catalog__status; status ok; tokens in 13792 cache-write 32585 cache-read 0 out 6592; cost $0.087. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# catalog: statuses

## 1. Rules of a status

**Scope.** A status lives on a **slice slot** (`{status: stacks}` per slot, N8). It is anti-Firmware: it changes how a slice performs, never what it does. Entity-level statuses are limited to two exceptions (§2, justified there).

**Stacking (xN).**
- Same status on the same slot adds stacks up to that status's cap. Excess stacks are lost, never refunded.
- Different statuses coexist on a slot, up to 3 distinct types. A 4th application is refused (the preview shows "SLOT FULL"); this bounds the matrix.
- Stacks are **permanent until cleansed or combat ends**. The only decaying statuses are the two Heat-driven ones (§2).
- Flat/Percent: stacks are a count, never an amount. Magnitude per stack is data.

**Duration.** Default is none (combat-long). `duration_turns` ticks down at the owner's turn start. At 0 the status ends silently, except OVERCLOCKED, which burns out.

**Display.** One badge per status on the slice: icon plus xN. The wheel face shows the *net* effect in one line on hover ("Output −50 %, Perfect→Good"). The preview chip already includes the degraded numbers (preview = result).

**Application.**
- Landing quality does not gate application. A WEAK landing still applies (Q11 stays as proposed), unless the slice authors `min_tier`.
- **ENCRYPTED** absorbs the next *whole application*, however many stacks it carried, then is consumed. Chosen-slice and random-slice picks are both blocked.
- Where a pick is RANDOM_NON_NULL, it uses a named RNG stream with a checkpoint, as today.

**Cleanse.**
- Cleanse (card or effect) removes **all stacks of one named status** from one slice.
- A generic Cleanse removes the status with the most stacks, ties broken by catalog order.
- Sanitize-style cards remove 1 stack, via a new `stacks` field on CLEANSE. `amount` on EffectData is reused for this.
- Boss `cleanse_on_enter` (R6) uses the same cleanse, scoped OWN / PLAYER / BOTH.

**Ordering (one rule, applied identically in preview and resolve).**
1. Slice base amount (FLAT, or PERCENT of owner max HP) is computed.
2. Firmware multipliers apply (Patch+ ×1.5).
3. Statuses apply: OUTPUT multipliers add together (see below), then multiply once.
4. Tier-quality multiplier (Perfect/Good 1.0, WEAK 0.5).
5. Enemy tier damage factor (R2) applies to FLAT enemy amounts only.
6. Enrage multiplier. Block, shield, pierce and parking come last.

Percent reductions are **additive across stacks** and floor at −75 %. OUTPUT_DOWN x3 is −75 %, not −58 %. Additive keeps the preview legible and bounded.

**Tick-quality reduction vs R11 (variable sizes).**
- TIER_DOWN works on the **tier ladder, not on ticks**: each stack lowers the *read tier* one step (Perfect→Good→WEAK, floor WEAK). The sub-tick map is unchanged.
- A 4-tick slice (W G G W) has no Perfect, so TIER_DOWN x1 only hurts its Good ticks. That makes uneven sizes a natural counter: a slice that is never Perfect loses nothing to TIER_DOWN until x1 reaches Good.
- Calibrated Firmware (+1 tier per sub-tick) is applied **before** TIER_DOWN, so net = Firmware up, then status down. A 4-tick Calibrated slice (G P P G) under TIER_DOWN x1 reads W G G W.
- Perfect hooks key off the *read* tier, so TIER_DOWN also switches off Perfect hooks.

**Phase change, parking, enrage.**
- Statuses survive (R6) and remap by centre tick. Merged stacks respect the cap.
- Parked damage is not affected. Statuses do not change the HP floor.
- Enrage multiplies the final damage. Statuses never interact with it, except that enemy-slice statuses reduce the enemy's own output before enrage.

**Who removes.** Player: Cleanse, Encrypt (prevents), Strip (enemy resistance only). Enemy: phase `cleanse_on_enter`, the Sterile Field buff (cleanses its own statuses each phase). Event: a few events add or remove stacks.

## 2. Catalog

Magnitudes are placeholders. "Slice" means the slot's slice.

| id | Status | Applies to | Effect per stack | Cap | Duration | Applied by | Cleanse | Anti-of (Firmware) | Read at a glance |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **CORRUPTED** (exists; changes) | Slice | Cards/nudges acting there cost ×2 RAM (not per stack; binary). Damage retired. | 1 | Combat | Enemy (Dose, Immunization, Code Blue), player's Corrupt on enemies | Cleanse, Sanitize | Leech (RAM refund) | Purple static, ×2 RAM tag |
| 2 | **OVERCLOCKED** (exists) | Slice | ×1.5 next trigger, then it becomes CORRUPTED. Not a debuff on player slices; hostile on an enemy's Solar Flare use. | 1 | Until trigger | Player (Overdrive, Hot Patch), Orbital Flare | Cleanse | Burner (permanent OC) | Orange glow, lightning |
| 3 | **ENCRYPTED** (exists) | Slice | Absorbs the next application. | 1 | Until consumed | Player (Encrypt, Armor Plate); enemy Hardened | Consumed, or Cleanse | Hardened | Padlock |
| 4 | **OUTPUT_DOWN** (new; absorbs PARASITE status) | Slice | −25 % output per stack, additive, floor −75 % | 3 | Combat | Halcyon Citation, Botnet Leech Worm on enemy | Cleanse, Sanitize (−1 stack) | Patch+ | Red down-arrow xN |
| 5 | **TIER_DOWN** (new) | Slice | Read tier −1 per stack | 2 | Combat | Halcyon ordinance, Handler Echo | Cleanse | Calibrated | Hollow diamond xN |
| 6 | **BRITTLE** (new) | Slice | Defensive slices (BLOCK, SHIELD, SANDBOX) here give −25 % per stack. Offensive slices unaffected. | 3 | Combat | Enemy riders (Genome Core Immunization alt, Meridian customs) | Cleanse | Hardened's counterpart on defense | Cracked shield |
| 7 | **DRAG** (new) | Slice | Resistance: nudges moving the pointer onto/off this slice cost +1 RAM per stack. Does not stack with CORRUPTED's ×2; it adds first, then doubles. | 2 | Combat | Meridian Package/Weight, Compliance Lock | Cleanse | Mirror/Shunt neighbour chips (movement) | Anchor chain |
| 8 | **STATIC** (new) | Slice | Chip effects (Firmware riders) on this slice stop firing while stacked. Does not stop base output or Calibrated tick maps. | 1 | Combat | Orbital (jamming), Handler Override | Cleanse | Any rider Firmware (Mirror, Shunt, Leech) | Fuzzy chip outline |
| 9 | **DAMPED** (new) | Slice | The slice's Perfect multiplier and hooks (×4 Medicine, Perfect hook) are lost; Perfect pays as Good. Distinct from TIER_DOWN because it ignores sub-tick maps and affects only Perfect effects. | 1 | Combat | Genome Core, Solace Compliance | Cleanse | Perfect-hook Firmware, class Perfect hook | Flat bell curve |
| 10 | **LEAK** (new) | Slice | Triggering this slice drains 1 RAM per stack (cost is paid at resolution, not play). | 3 | Combat | Meridian Priority/Airmail | Cleanse | Leech | Dripping drop xN |
| 11 | **MARKED** (new) | Slice | Enemy listeners (N6) fire on this slice's Perfects: Clawback or Echo hit once per stack-less mark. Binary, a targeting flag rather than damage. | 1 | 2 turns | Account Manager, Handler | Cleanse; expires | Perfect hooks | Crosshair |
| 12 | **SLOW** (new) | Slice | Slice tick-width counts as −1 on the quality map when read, edge ticks first (a 5-slice reads W W G W W at the centre-side). Applies only to slices of size ≥4. | 1 | Combat | Orbital debris | Cleanse | Calibrated (size-based) | Narrowing wedge |
| 13 | **SEALED** (new) | Slice | The slice cannot be the target of friendly nudges *onto* it (the pointer can still arrive by respin). | 1 | 2 turns | Halcyon Curfew (alt to wheel lock) | Cleanse | Snap | Crossed ring |
| 14 | **FLAGGED** (new, Heat-bound) | Slice | +1 Heat on trigger per stack | 2 | Combat | Raid/Heat events | Cleanse | Cold Exit/Scrubber daemons | Red dot |

**Entity-level exceptions (two, justified).**
- **EXPOSED (enemy, ×1.25 damage taken, 2 turns, cap 1)** is the enemy-wheel mirror of ENCRYPTED. It is a *player-applied* offensive status; the ruling is about enemy-applied degradation of player slices, and a player-side buff to damage needs a home. It is data on the enemy entity, not a slice.
- **OVEREXTENDED (player, +1 RAM cost on the next card, 1 turn)** exists only as an event/trap cost, not combat. Skip unless events need it.

I recommend building **only EXPOSED**; the rest of the table is slice-bound.

**Existing content changes.**
- PARASITE → OUTPUT_DOWN x2 (R8); the enum value is kept for saves and migrates.
- CORRUPTED loses self-damage, gains the RAM rule.
- OVERCLOCKED still burns out into CORRUPTED.
- ENCRYPTED unchanged.

**Priority cut for the first build:** CORRUPTED, OVERCLOCKED, ENCRYPTED, OUTPUT_DOWN, TIER_DOWN, LEAK, DAMPED, MARKED. The other six wait for roster need.

## 3. Pairings

| Status | Player counterplay | Roster users |
|---|---|---|
| CORRUPTED | Cleanse, Sanitize, Encrypt (pre-empt), steer pointer away | Genome Core (Immunization, Code Blue), Solace Dose, Account Manager P2 |
| OVERCLOCKED | Choose the burn-out slice; cleanse the hot slice before it turns | Orbital Flares, Overheater-style probe |
| ENCRYPTED | Lasts one status; use as insurance on the best slice | Enemy Hardened (Cipher Clerk) |
| OUTPUT_DOWN | Cleanse, Sanitize (−1), Encrypt, route landings around the stack | Halcyon Citation (x1→x3), Leech Worm (player→enemy) |
| TIER_DOWN | Cleanse; use 4-tick slices (no Perfect to lose); Calibrated as a buffer | Halcyon Martial Law, Handler Echo |
| BRITTLE | Prioritise SANDBOX (not scaled by it); Encrypt the defense slices | Genome Core variant, Meridian Customs |
| DRAG | Plan nudges around marked slices; Cleanse; Spin cards bypass | Meridian Weight/Package |
| STATIC | Cleanse; prefer chip-free slices | Orbital, Handler Override |
| DAMPED | Cleanse; Calibrated does not help; accept Good | Genome Core P2 Medicine counter, Compliance Officer |
| LEAK | Cleanse; Rigger refunds; Leech Firmware | Meridian Priority/Airmail |
| MARKED | Land Good instead of Perfect; Cleanse; 2-turn expiry | Account Manager P2, Handler P2 |
| SLOW | Cleanse; don't rely on edge ticks | Orbital Debris |
| SEALED | Cards, not nudges | Halcyon Curfew alt |
| FLAGGED | Cleanse; Cold Exit | Heat-driven raids |
| EXPOSED | Player applies it (Hub Breach card, Strip); counter by being fast | n/a (player offensive) |

## 4. Interaction matrix: six dangerous combinations

| Combo | Danger | Bound |
|---|---|---|
| CORRUPTED + DRAG on one slice | Nudge costs (1+1)×2 = 4 RAM, a dead slice | DRAG cap 2; additive-then-double; one slice only; Cleanse removes both separately |
| OUTPUT_DOWN x3 + TIER_DOWN x2 | A slice reads as near-nothing (−75 %, WEAK always = 0.125×) | OUTPUT floor −75 %; slot limit of 3 distinct statuses; TIER_DOWN floor WEAK; the minimum output is 1 |
| LEAK + CORRUPTED + Code Blue | RAM spiral: drain per trigger, ×2 cost, nothing left | LEAK is resolution-time and floors RAM at 0; total drain per turn capped at 4 (`leak_cap_per_turn`); Encrypt/Cleanse in hand |
| DAMPED + TIER_DOWN | Double Perfect deny, so Medicine stays ×1 even on a lucky nudge | Both are cleansed by one Cleanse each; per-slice status limit; the enemy needs two applications |
| MARKED + Echo/Clawback + enrage | Perfects become self-damage, then enrage scales it | Marks expire in 2 turns; the listener fires once per resolve; Echo is 50 % and enrage multiplies the 50 % base; hits are parked/floored |
| BRITTLE + pierce + Code Blue | Defenses gone, no shield, pierce | Pierce already ignores BLOCK/SHIELD, so BRITTLE only matters on SANDBOX-less builds; SANDBOX (not scaled) is the answer; BRITTLE is not offered in the last phase of the Genome Core |

**Global bound:** an enemy can apply at most 2 new statuses per resolve (`status_applies_per_resolve` = 2). This keeps preview readability and prevents "every slice dead on turn 2".

## 5. Data and systems

**Schema.** Make `Status` a `StatusData` resource (`content/statuses/*.tres`) while keeping the enum ints for saves:
- `id`, `display_name`, `enum_id` (legacy int), `icon`, `max_stacks`, `duration_turns`
- `output_pct_per_stack`, `tier_shift_per_stack`
- `ram_cost_mult` (CORRUPTED = 2.0), `ram_drain_per_trigger_per_stack` (LEAK)
- `blocks_firmware_riders`, `blocks_perfect_hooks`, `defense_pct_per_stack`
- `nudge_cost_per_stack`, `heat_per_trigger_per_stack`
- `absorb_next` (ENCRYPTED), `on_trigger_becomes` (OVERCLOCKED→CORRUPTED), `on_trigger_effects[]`
- `cleansed_by` tags; `hostile` flag for UI colour.

`EffectData.status` becomes a `StatusData` reference (with the enum kept as a fallback loader). EffectData gains `stacks` (default 1, used by APPLY_STATUS and CLEANSE).

**Dependencies.**
- **N8** (xN stacks, save 2→3, `wheel_state` 13 call sites): required for everything except binary statuses. This is the M–L gate.
- **N9** (status rules, CORRUPTED as RAM cost, OUTPUT_DOWN, TIER_DOWN): the first rules.
- **N12** (variable sizes): TIER_DOWN works without it; SLOW needs it.
- **N6** (listeners): MARKED.
- **N10** (Parasite ring): independent. Parasites do the damage that CORRUPTED lost.
- **N3**: remap and `cleanse_on_enter`.
- NEW: **status resource registry + preview integration** (S–M), folded into N9.

**Migration.** Content using status today is small: 8 cards, 3 slices, no enemies, firmware or daemons. Mapping: PARASITE → OUTPUT_DOWN x2 (leech_worm, parasite_pulse, the Botnet Perfect Trojan); CORRUPTED/OVERCLOCKED/ENCRYPTED keep their ids. The save migration (v2→v3) wraps each slot's single status as `{status: 1}`, PARASITE as `{OUTPUT_DOWN: 2}`. Text updates for the Codex, tutorial and cards (sanitize, cleanse, corrupt_packet).

**Size.** Core catalog (first 8): M for the resource and rules on top of N8's L. The other six are S each once the resource exists.

**Data-only fallback.** No N8: keep one status per slot with a binary flag, and ship CORRUPTED (RAM), ENCRYPTED, OVERCLOCKED, and OUTPUT_DOWN as fixed "x2" only (the PARASITE equivalent). No stacking, no TIER_DOWN. That keeps Halcyon's Citation stacking ×3 impossible, so the Halcyon mini-boss P1 needs N8.

## 6. Questions

Q: Should the 3-distinct-status slot limit stay, or is a single status-slot limit simpler to read?
Q: Is EXPOSED (a player-offensive entity status) acceptable under the anti-Firmware ruling, or should player damage amplification live only in cards?
Q: Does CORRUPTED's ×2 RAM apply to the free nudge (i.e. does the free nudge cost 1 on a corrupted slice)? This is open question 3 in V2.
Q: Is DAMPED needed alongside TIER_DOWN, or does TIER_DOWN cover the "deny Medicine's Perfect" need?
Q: Should OUTPUT_DOWN's floor be −75 % (proposed) or −50 % so a slice is never nearly dead?
