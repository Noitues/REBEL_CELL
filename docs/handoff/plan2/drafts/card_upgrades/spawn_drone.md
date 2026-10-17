<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__spawn_drone; status ok; tokens in 5120 cache-write 0 cache-read 32585 out 1172; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: spawn_drone

1. **Role.** Botnet's deliberate drone placement: it docks a 5 HP bodyguard and a bonus trigger on a slice you choose. It costs RAM and a card where the TROJAN slice docks one for free.

2. **Upgraded card: "Spawn Drone+"** (one + level is enough).
   - RAM cost: 2 → 1.
   - Cycle cost multiplier: ×1.5 (75 → 113, rounded to 115).
   - Exhaust: false (unchanged). wheel_target: OWN (0).
   - Text: "Dock a drone on a chosen slice of your wheel. If that slice already holds a drone, it is restored to full HP instead."
   - Effect list:
     1. DEPLOY_DRONE (type 18), target SELF (0), amount 1, slice_pick CHOSEN, ring_scope OUTER. Unchanged.
     2. **New rider:** on a slice that already holds a drone, no extra drone is created (`max_drones` and the one-drone-per-slice rule hold). The drone's HP resets to its template maximum (5).
   - The rider is a conditional on DEPLOY_DRONE, not a second effect, so there is no new status and no amount mode. All amounts here are FLAT.

   **Why this shape:** the base card needs 2 RAM and a free slot, so it is dead when the drone cap is full or the drones are already placed. The + version is cheaper and gains a use when the cap is full (a heal for a damaged drone). It is not strictly dominant: it costs more Cycles, and it does nothing for you when the target slice has no drone and the cap is already reached. That case is a refusal in the base card too, so nothing is lost there. I prefer a cost cut plus a rider over "dock two drones", which would break the `max_drones` cap that the Hub sets.

3. **Interplay.**
   - Slice sizes (N12): a drone triggers when its slice does, so a 7-tick or 3-tick slice with a Perfect is the best dock point. The slice map on the loadout screen shows where.
   - Parasite ring (N10): drones are bodyguards, and the Parasite ring will attack the wheel. A refreshed drone gives the Botnet a way to hold a guard slice against sustained anti-slice damage.
   - Fixed satellites (R12): drones are not satellites, so `on_occupied = REPLACE` doesn't touch them.

4. **Data.**
   - Fields changed: `ram_cost` 2 → 1; `cycle_cost` 75 → 115; description. Create a new file `spawn_drone_plus.tres` with id `spawn_drone_plus`.
   - New field: `DEPLOY_DRONE` needs a "refresh on occupied slice" behaviour. Fallback with no code change is a data-only upgrade: RAM 1 and a Cycle cost of 115 only, with no rider. That is weaker but valid.
   - Code: S, in the `DEPLOY_DRONE` handler of `effect_interpreter`. No N# applies. The upgrade path needs the future card-upgrade system (a pass of its own, and not N18).

5. **Q:**
   - Q: Should the refresh also work on a drone docked by the TROJAN slice, or only on drones from this card?
   - Q: Is the 1 RAM cost too cheap next to TROJAN's free drone? Does it need to stay at 2 with the refresh as the entire upgrade?
