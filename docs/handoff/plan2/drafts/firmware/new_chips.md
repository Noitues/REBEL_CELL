<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__new_chips; status ok; tokens in 18111 cache-write 0 cache-read 32585 out 11789; cost $0.080. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: new chips

## 1. Design goals and gaps in the current 18 chips

All 18 chips are flat numbers or "also does X" riders on ON_SLICE_TRIGGER. Nothing touches the new rules (R8-R13, N-systems). Gaps:

- **Slice types:** no chip for TROJAN, INFECT or HOTFIX (only Nanite Mesh), and only Recycler for NULL.
- **Defense trio:** only DEFRAG, SANDBOX (today's shield) and DETOUR (today's evade) riders exist. Nothing links BLOCK to SHIELD, and nothing rewards a whole-attack SANDBOX against multi-hit attacks.
- **Statuses:** only Hardened and Nanite Mesh interact with statuses. Nothing counters OUTPUT_DOWN or TIER_DOWN, or lets you ride CORRUPTED or OVERCLOCKED.
- **Wheel geometry:** nothing for tick quality (R11), nudge precision, satellites (R12) or rim gates (N15).
- **Boss mechanics:** nothing for parasites (N10), enemy listeners (N6) or threshold parking (R3).
- **Scaling:** every amount is flat, so a 45 HP operative and a 60 HP operative get the same value.

Goals:
- Every chip is a build-around with a cost.
- Each chip names what it must not break.
- Chips are few in count, each owning one question.
- Socket scarcity (one chip per slice) stays the main limit on stacking.

## 2. Chip table

All chips have a working id and placeholder numbers. "Fb" = data-only fallback. Cost is in Cycles.

| id | Slices | Rar / Cost | Exact effect | Needs | Enables / must not break |
|---|---|---|---|---|---|
| **tuned** | any | C / 90 | Every WEAK sub-tick of this slice reads GOOD. | N12 | Edge safety on big slices. Must not give any Perfect. |
| **calibrated** | any slice of size ≤ 4 | U / 120 | Every sub-tick reads one tier higher (§3). | N12 | Perfect-hook builds on small slices. Must not work on size ≥ 5. |
| **pinpoint** | any slice of size ≥ 5 | R / 140 | The GOOD sub-ticks read PERFECT. WEAK edges stay WEAK. Output −10 %. | N12 | A wide Perfect with risky edges. Must not remove the edge risk. |
| **swivel_mount** | any | U / 120 | Sets `can_move_satellites`. Once per turn, free: move one of your satellites to an adjacent slice (§4). | N13 | Botnet positioning. Must not allow replace-by-accident (a REPLACE move needs a confirm). |
| **tether** | TROJAN, any | U / 110 | Your free nudge each turn may target one satellite's mini-wheel (±1 satellite slice). Satellite wheels stay un-nudgeable otherwise. | N13 | Satellite as a tuned second action. Must not make extra nudges free: the free nudge is spent. |
| **swap_plate** | any | R / 140 | Once per combat, swap the slices of two satellites on the same wheel (no replacement, no loss). | N13 | Rearrange guards or drones. Must not touch enemy `anchored` satellites. |
| **pivot_hook** | SHIM, OVERFLOW | R / 150 | On Perfect, move the enemy guard satellite on the pointer's slice one slice clockwise. If that slice is occupied, REPLACE applies (the guard there is lost). | N13 | Opens a Fortress lane. Must not shift Retainers every turn (once per turn, never on `anchored`). |
| **flak_purge** | OVERFLOW | R / 160 | A Perfect destroys the satellite on the target's pointer slice, then deals the hit to the host. Once per combat. Counts as destroyed (Q). | N13 | A one-shot answer to a bodyguard. Must not be repeatable. |
| **stabilizer** | any | U / 110 | Ignores one OUTPUT_DOWN stack and one TIER_DOWN stack on this slice (min 0). | N8, N9 | Halcyon Citation counter. Must not stack with Hardened (a socket conflict, so it can't). |
| **self_clean** | any | U / 110 | After resolving at Good or better, remove 1 status stack from this slice (any status, not ENCRYPTED). | N8 | Anti-attrition for stack bosses. Must not undo OVERCLOCKED's intended burn-out. |
| **heat_sink** | any | C / 100 | When this slice's OVERCLOCKED burns out, it becomes ENCRYPTED instead of CORRUPTED. | N9 | A safe overclock cycle. Must not stack with Burner (Burner never burns out). |
| **tainted_gain** | any | R / 130 | While CORRUPTED, this slice's output is ×1.5. The doubled RAM cost stays. | N9 | A build that lives on corruption. Must not be Patch+ with no downside: it is dangerous against IV and Genome Core P2. |
| **phage** | SHIM | U / 120 | On Perfect, remove the Parasite segment under the pointer (a Cleanse of the ring). | N10 | Parasite-ring counter. Must not clear every segment (one per resolve). |
| **muffler** | any | R / 150 | The first Perfect each turn that resolves from this slice doesn't fire enemy ON_PERFECT listeners. | N6 | Account Manager / Handler counter. Must not suppress other listener types. |
| **detent** | any | C / 90 | A paid nudge that leaves this slice's centre under the acting pointer refunds 1 RAM (once per turn). | none (Fb: none) | Uneven-needle nudge puzzles. Must not allow net-positive loops (the refund is capped at the paid cost). |
| **plating** | DEFRAG | C / 100 | BLOCK + 10 % of your max HP (round, min 1). | N1 | Class-scaling defense: Breaker 60 → +6. Must not apply to SHIELD (it has its own cap). |
| **spillway** | DEFRAG | U / 110 | At the start of your turn, unused BLOCK converts to SHIELD at 50 % (cap `shield_cap` 15). | N14 | A block-to-shield bridge. Must not exceed the cap. |
| **airlock** | DETOUR (SANDBOX) | U / 110 | When this SANDBOX negates an attack with ≥ 3 hits, gain 3 RAM. | N14, N20 | Counters IV / Medicine-style multi-hit. Must not trigger on single hits. |
| **salvage** | SHIM, OVERFLOW | U / 120 | When this slice's hit is parked at a phase floor, gain 1 RAM per 5 lost excess damage (max 3 RAM, once per park). | N3 | Rewards bursting past a threshold. Must not be farmable: at most once per phase transition. |

**19 chips.** Fallbacks: only `detent` needs no new system (a nudge-based trigger is partly expressible with ON_NUDGE and an effect refund). `tuned`, `calibrated` and `pinpoint` need N12 and have no fallback.

## 3. Calibrated family

**Rule:** quality is by distance d from the centre (R11): d = 0 is PERFECT, d ≤ 1 is GOOD, else WEAK. The chip's `tick_step` field is the number of tiers a sub-tick is raised (capped at PERFECT). Sizes 1 and 8 are not in the R11 table, so I extrapolate (see the Q).

| Size | Default | tuned (WEAK→GOOD) | calibrated (+1, size ≤ 4) | pinpoint (GOOD→PERFECT, size ≥ 5) |
|---|---|---|---|---|
| 1 | P | P | P (cap) | n/a |
| 2 | G G | G G | P P | n/a |
| 3 | G P G | G P G | P P P | n/a |
| 4 | W G G W | G G G G | G P P G | n/a |
| 5 | W G P G W | G G P G G | n/a | W P P P W |
| 6 | W W G G W W | G G G G G G | n/a | W W P P W W |
| 7 | W W G P G W W | G G G P G G G | n/a | W W P P P W W |
| 8 | W W W G G W W W | G G G G G G G G | n/a | W W W P P W W W |

**Why the size limits:**
- Calibrated on size 5 would read G P P P G, 60 % Perfect. With Breaker's "resolves twice" hook that is too strong, so it is capped at size ≤ 4.
- Size 3 (G P G) → P P P is the best case: a whole Perfect slice. Its cost is the small slice's single-slice limits: the 3-tick slice is also hard to land on with bad rotation, and a Perfect only matters if you land there.
- Pinpoint is the opposite trade for big slices: the Perfect rate rises but the WEAK edges stay.

**Interplay with Level I-IV slice upgrades:**
- Levels change output and rider strength. They never change `size_ticks` or the tick map.
- A Level change is applied after the chip, so Calibrated is multiplicative with Level (more Perfects × higher Perfect hook value).
- There is one socket per slice, so Calibrated can't share a slice with Patch+ or Hardened. That is the cost.
- Level IV slices could unlock a second socket, which would make Calibrated + Patch+ possible. I'd rule that out for now (Q).
- The loadout screen shows the sub-tick map after the chip.

## 4. Satellite movers

**Rules (R12 + N13):**
- A satellite is fixed to its slice. Only effects from a chip with `can_move_satellites`, an operative class, or a Daemon may move it.
- **Shift:** a move to an adjacent slice (±1), never across the wheel. An occupied target is REPLACE: the satellite there is removed, and the mover's card or chip shows a confirm.
- **Swap (`swap_plate`):** two satellites exchange slices. No replacement and no loss. Once per combat.
- **Satellite wheel:** a mini-wheel can't be nudged except by the `tether` chip or a class effect. `tether` spends the free nudge, so there is no extra action.
- **Respin:** I did not include a respin chip, because it would set a checkpoint and use the RNG stream. If wanted later, it must set a rewind checkpoint like any random event.
- **Limits:**
  - one move per turn per chip;
  - `anchored` satellites can't be moved;
  - boss satellites are anchored unless the authored phase says otherwise;
  - a moved satellite keeps its HP.
- **Determinism:** every move is pure state with no random input. Moves are previewed (the preview shows where the satellite sits after the move) and are undone with the rewind.
- **Interplay:** `pivot_hook` and `flak_purge` act on enemy satellites during resolve, so the preview must include them.

## 5. Risks: the three most abusable chips

1. **calibrated.** The most dangerous chip: it makes Perfect hooks routine, and pairs with every Perfect-based Daemon (Kernel Sync). Bound: size ≤ 4 only, so the player needs a small slice; one socket; Rare-equivalent price 120 → raise to 140 if the sim shows it dominates.
2. **flak_purge / pivot_hook.** They delete the Fortress and Retainer puzzles. Bound: pivot once per turn, purge once per combat, never on `anchored` satellites (bosses and the Solace mini-boss P1 Retainers are anchored by default).
3. **muffler.** It nullifies one boss listener per turn (Clawback, Echo). Bound: once per turn, only ON_PERFECT, and it consumes the Perfect hook for that slice that turn (the Perfect still counts for hooks, only the listener is skipped). If the sim shows listener bosses collapse, make it once per combat.

Also watch `tainted_gain` + Genome Core P2 (IV multiplies by your corrupted slices), which is intended tension, and `salvage` RAM (a hard cap of 3 per park).

## 6. Data & systems

**New `FirmwareData` fields:**
- `tick_step: int` and `allowed_slice_sizes` (min and max).
- `can_move_satellites: bool`.
- `status_ignore_stacks`, for `stabilizer`.
- `suppress_listener: Trigger`, for `muffler`.
- `limit_per_turn`, next to the existing `limit_per_combat` on triggered effects.
- `amount_mode` on effects (N1).

**New effect types** (CUSTOM until added): SHIFT_SATELLITE, SWAP_SATELLITES, DESTROY_SATELLITE, CLEANSE_STACK, CLEAR_PARASITE, and a hook for the parked-excess RAM payout.

**Systems by chip:**
- tick-map chips: N12;
- satellite chips: N13;
- stack chips: N8 and N9;
- parasite chips: N10;
- listener chip: N6;
- defense chips: N14 and N20;
- parking chip: N3;
- PERCENT chip: N1.

**Build order:** Foundation chips (`plating`, `detent`) first; N12 chips with N12; boss-counter chips after N5.

Q: Sizes 1 and 8 are outside R11's table. Allow them, or cap slices at 2-7?
Q: Does a satellite removed by REPLACE or `flak_purge` count as destroyed for Daemons and rewards (Q7)?
Q: Should a Level IV slice get a second socket (which would allow Calibrated + Patch+)?
Q: Should Calibrated cap at size ≤ 4 for all classes, or only for classes with Perfect hooks?
Q: Is `muffler` too strong for the Account Manager and Handler minis (both rely on Perfect listeners)? Should it be once per combat?
