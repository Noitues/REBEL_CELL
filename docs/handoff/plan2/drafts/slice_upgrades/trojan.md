<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01Y2bjt88e8i6ocTDPQPm21s, custom_id slup__trojan; status ok; tokens in 12929 cache-write 0 cache-read 32585 out 3368; cost $0.033. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# slice_upgrades: TROJAN

## 1. Role of the type
TROJAN is the Botnet's engine: it docks a drone (5 HP, mini-wheel Shim 3 / Defrag 3) from the Hub template on its own slice, else the next free slice clockwise. When the host slice triggers, the drone triggers too. Drones also act as bodyguards, because enemy pointer attacks hit a drone on your resolved slice before you.

The type has one slice today, `trojan_1`, with `base_output` 1 = one drone. Nothing is redundant. The only overlap is Botnet Seed (Daemon), which deploys 1-HP drones on a Perfect, and the Botnet class Perfect hook, which plants a Parasite drone. Upgrades should deepen the drone rather than add a second drone-making slice.

What a TROJAN slice gives is a standing investment: it is worth little on the turn it lands and a lot on every later turn. So its levels trade size and immediate output against how much the drone contributes later. It should never act as a plain stat stick.

## 2. Level table
Drone cap is `max_drones` (Hub, 3 for Botnet). Where a level says "output", it means the drone's hosted-trigger output.

| Level | Size (ticks) | Tick quality | Deploys (`base_output`) | Extra effect | Cost / trade-off |
|---|---|---|---|---|---|
| I (base) | 5 | W G P G W | 1 drone (5 HP) | Drone docks on this slice, else the next free one | Baseline |
| II-a "Wide Bay" | 6 | W W G G W W | 1 drone, 8 HP (PERCENT 15 % of owner max HP, min 5) | If the dock slice is occupied, REPLACE the old drone (R12) and heal the new one to full | Gives up Perfect, and 6 ticks is a large share of the wheel |
| II-b "Tight Bay" | 3 | G P G | 1 drone, 5 HP | Drone's first hosted trigger each combat is a free extra trigger | Small footprint, strong tick pattern, but a fragile body |
| III-a "Hive" | 7 | W W G P G W W | 2 drones (5 HP each), spread to the next free slices | Perfect: both drones trigger twice | Big and Perfect-dependent; the wide WEAK edges deploy at 0.5× (WEAK = 1 drone, 2.5 HP, rounded up) |
| III-b "Seeder" | 4 | W G G W | 1 drone | Drone HP gain: each drone you own gets +2 max HP and 1 SHIELD-style absorb (5 % max HP, PERCENT) when this slice resolves | Never Perfect; this is a support and upkeep slice |
| IV "Swarm Core" | 5 | G P P G + one W (W G P P G reading from the left) | 2 drones | While this slice is docked and you own ≥2 drones, each Perfect anywhere on your wheel makes one drone trigger its mini-slice at 50 % (ON_PERFECT, N6) | Costs the Calibrated chip's tier-up space (see §3) and fills 5 ticks |

Level IV is a payoff for a drone build: it turns the drones into a second layer of Perfect-driven output, and Perfect play is the core skill of the game.

**Branching, not a strict ladder.** Level II and Level III each offer two branches (a fatter body versus a narrower window). The Rack flash chooses a branch. Level IV is reachable from III-a or III-b, and it keeps the identity of whichever branch led there, so III-a Hive becomes IV "Swarm Core (Hive)" with the 2 drones and ×2 trigger, while III-b keeps Seeder's upkeep as a rider. I show the merged IV above and treat the carry-over as a variant flag.

**Data mapping**
- Size: `size_ticks` (N12) on `WheelSlotData`. The Level changes this field. A TROJAN slice resource per Level: `trojan_2a`, `trojan_2b`, `trojan_3a`, `trojan_3b`, `trojan_4`.
- `base_output`: drone count.
- `extra_effects`: ON_PERFECT and ON_HIT_DEALT triggers use N6 listeners; PERCENT HP uses N1.
- New fields (SliceData):
  - `level: int` (1–4)
  - `upgrades_to: Array[SliceData]`
  - `drone_hp` with `amount_mode`
  - `on_occupied` (N13, REPLACE)
  - `drone_trigger_count`

## 3. Tick-quality interplay (R11)
- The quality pattern comes from the default map for the size, plus an optional `tick_quality` override. Level II-a shows why: moving to size 6 removes the Perfect, a pure trade.
- **Calibrated chip (raises each sub-tick one tier):**
  - Level I (W G P G W) becomes G P P P G, an almost fully Perfect slice. TROJAN benefits unusually, because a Perfect lets Botnet's hook plant a Parasite drone on the enemy.
  - Level II-b (G P G) becomes P P P, a guaranteed Perfect from any of its 3 ticks. That is the best size-for-quality trade in the game, so it is the intended showcase.
  - Level II-a (W W G G W W) becomes W G P P G W, restoring a Perfect and offsetting the Level's cost.
  - Level IV is already G P P G, so Calibrated only turns the single W into G. The chip has diminishing value there, which keeps IV from stacking with it.
- **PERFECT-only effects:** III-a's "both drones trigger twice" and IV's ON_PERFECT chain depend on landing Perfect. III-a has one Perfect tick; IV has two. If you can't land Perfect, III-a still deploys (smaller, at WEAK) and works as a basic drone dock.
- **Small slices:** size 3 (II-b) is a deliberate, valuable option, not a mandatory one. Size 2 and below never appear for TROJAN, because a drone dock needs a landing, and a 2-tick G G slice has no Perfect for Botnet's hook. Every branch stays viable: size 6–7 for body and volume, size 3–4 for precision.

## 4. Rack flash (G15)
The Rack flash row (`slice_flash`, N18) offers 3 choices, all for the Botnet's current TROJAN slice (and for any slice in the wheel if the player picks a different one):
1. **Upgrade** this slice by one Level. If a branch exists, show both branches as two choices.
2. **Swap** it for a random uncommon slice from the pool (same rarity roll as the Rack: ~60 % uncommon, 30 % rare, 10 % common). The type can change, so a TROJAN can become OVERFLOW, but that dismantles the Botnet build and the UI warns "removes drone source".
3. **Decline.** Banking the Schematics stays regardless.

How TROJAN appears: a flash offers an upgrade when the slice has a Level above it; at Level IV it offers only swap or decline, and a "refit" (re-roll between branches, kept for Q). Chance of the upgrade row appearing is 100 % on Racks for Botnet players with TROJAN, and the offer is deterministic from the `rewards` RNG stream, checkpointed. Cost: free on the Rack at Levels II; Level III costs 30 Cycles; Level IV costs 60 Cycles plus the Rack's own Schematics.

The reward-table row: `kind = slice_flash`, `pool = slice_levels`, `count = 3`, `conditions = node:server_rack`, and layer ≥ 4 for Level III or IV offers.

## 5. Economy
- **Shop / Workshop:** upgrades are sold at the Workshop node (D4), Level II at 80 Cycles, III at 140, IV at 220 (placeholders). The shop wheel's 100 / 80 / 100 prices remain for slices; upgrades are separate stock, one offer per visit, never more than one Level up.
- **Firmware sockets:** each slot keeps one socket. Upgrading a slice keeps the socketed chip, unless the new size makes it illegal (e.g. a chip that needs a Perfect tick on Level II-a). The UI warns first (the confirm from G14).
- **Interaction:** Patch+ on TROJAN increases drone HP by 50 %, not the count. Hardened keeps the drone's slice ENCRYPTED. Burner gives 1.5× drone trigger output and +1 Heat per trigger. No drone-specific chip exists yet, which keeps Calibrated as the main sink.

## 6. Systems & data
- N12 (variable sizes, `tick_quality`): required; no fallback for sizes other than 5. A data-only fallback is Level I-only 5-tick slices with output upgrades, losing the size choice.
- N1 (PERCENT drone HP): S–M.
- N6 (ON_PERFECT listeners for IV): M. Fallback: IV drops its chain and instead triggers all drones on a Perfect of this slice only.
- N13 (REPLACE on an occupied slice): S–M.
- N18 (`slice_flash` row, `reward_table_data.gd`): M.
- NEW: slice `level` and `upgrades_to` fields (S, data-only, no engine change).
- NEW: drone `trigger_count` and drone HP rider (S–M).

Q: Should Level IV carry its branch (Hive vs Seeder) or merge into one slice?
Q: Is replacing a drone through REPLACE a "destroyed" drone for Daemons?
Q: Does Botnet Seed (1-HP drones) stack with Level III-a's 2-drone deploy past the cap?
Q: Should a "refit" re-roll between Level II and III branches exist, and at what price?
