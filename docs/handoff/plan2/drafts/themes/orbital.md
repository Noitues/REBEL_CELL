<!-- THEMES draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01QpYFZqBxUvn2JMgwTbAhtu, custom_id theme__orbital; status ok; tokens in 15104 cache-write 0 cache-read 33457 out 10609; cost $0.071. DRAFT: designer picks. -->

# Orbital: theme options (status: options)

Orbital controls the sky: satellites, comms and strikes. Four options follow, each a full short draft. A is a blackout; B, C and D are not. A ranked recommendation (advice only) and the Q-DESIGNER lines are at the end. No art-pass plan exists for this corporation, so every option's section 6 lists the state names and values the art session needs.

---

## Option A: DEAD ZONE (communications blackout)

**Pitch:** Orbital cuts the Cell's uplink. On DARK turns your free nudge is locked, and in raids dark nodes can't be re-ordered.
**Cost:** low, mostly reuse (N7 lock, node flags). Small new code: a `dark` flag and one HQ "lit window" counter.
**Risk:** a locked nudge feels like a tax unless the schedule is readable in advance, and it can feel punishing (Q26 spirit: it is not the "always punishing" kind only if relays exist).

### 1. Rules
Street (light):
1. At map generation, 1 fight node in layers 3-6 is flagged `dark` (shown on the map before entry).
2. In a dark fight, turns 1, 4, 7, … are DARK turns. On a DARK turn the player's own-wheel nudge is locked (N7 `nudge_locked`, source `blackout`); cards still work.
3. DARK turns are shown in the turn track before the fight starts.

HQ (full):
4. Layers where `layer mod 4` is 0 or 1 are dark. Every fight on a dark layer uses DARK turns 1, 3, 5, … (one turn in two).
5. Uplink Dish nodes (3 per HQ run) are dark fights. Clearing one lights the next 2 layers (`lit_until_layer`); fights on lit layers have no DARK turns.
6. A dark Mainframe is closed: the shop is unavailable on dark layers.

Raid (one hook):
7. Each Orbital raid has a Dead Zone: the entry Site's node and its 1-hop neighbors. In setup, assets on dark nodes can't be placed or moved. Built-in defenses and projected outcomes work normally.

### 2. State and save fields
- `NetrunState.dark_nodes: Array[StringName]`, generated in map generation (existing netrun map stream; no new RNG).
- `NetrunState.lit_until_layer: int` (HQ only, default 0).
- `RaidState.dark_nodes: Array[StringName]`, a pure function of the entry Site and the graph.
- `CombatState.nudge_locks` already exists with N7; DARK turn is derived from `turn_index`.
- Save: additive fields with defaults. No version bump beyond N7's.

### 3. Preview
- Map: dark nodes carry a "no signal" glyph; HQ dark layers are tinted.
- Fight HUD: the turn track marks DARK turns ahead, and the locked nudge button states the reason ("BLACKOUT").
- Raid setup: dark nodes show a lock, and the projected outcome is exact. There is no "?" because nothing is random.

### 4. Numbers
- Street dark nodes per netrun: 1 (`config: campaign_config.street_dark_nodes`).
- Street DARK cadence: every 3 turns (`config: campaign_config.street_dark_every`).
- HQ dark pattern: `layer mod 4 in {0,1}` (`config: campaign_config.hq_dark_pattern`).
- HQ DARK cadence: every 2 turns (`config: campaign_config.hq_dark_every`).
- Lit window: 2 layers (`config: campaign_config.uplink_lit_layers`).
- Uplink Dishes per HQ: 3 (`config: campaign_config.hq_uplink_count`).
- Raid Dead Zone radius: 1 hop (`config: campaign_config.raid_dark_radius`).

### 5. Tests to write
- `test_dark_turn_locks_nudge` (fast): nudge on turn 1 of a dark fight is refused with reason `blackout`; turn 2 is allowed.
- `test_dark_schedule_matches_preview` (fast): the turn track's DARK list equals the locks actually applied.
- `test_uplink_dish_lights_next_two_layers` (fast): after the clear, the next 2 layers produce no locks.
- `test_raid_dark_nodes_refuse_placement` (fast): placement and move on a dark node is refused; the projection is unchanged.
- `test_dark_flags_deterministic` (full): the same seed gives the same dark nodes after save and reload.

### 6. Art answers
State names and values:

| State | Values |
|---|---|
| `dark` per node | true / false |
| `signal` per layer | LIT / DARK |
| `lit_until_layer` | int |
| `raid_dark` per raid node | true / false |
| `dark_turn` per combat turn | true / false |

### 7. Reuse and dependencies
- Reuses N7 (nudge lock with reasons) and the existing map and raid node data.
- New code: the dark flag and a schedule function (S).
- No Parasite ring, no rim gates.
- Fallback without N7: dark fights give −1 RAM income on DARK turns, which is data-only.

---

## Option B: OVERWATCH (orbital strike satellite; not a blackout)

**Pitch:** Orbital can bomb anyone. A fixed Strike satellite is docked on the enemy and fires a telegraphed pierce shot on a known turn. You break it or soak it.
**Cost:** low to medium. Reuses fixed satellites (N13), N14, N20 pierce and `hits`. New: strike scheduling and the raid strike.
**Risk:** it overlaps the satellite bodyguard design of the Orbital mini-boss, and pierce damage can feel unfair if the telegraph is unclear.

### 1. Rules
Street (light):
1. Elite fights carry a Strike satellite (fixed, N13) docked on the enemy slice nearest tick 15. Normal fights carry none.
2. The satellite's mini-wheel has one Strike slice: pierce damage, `hits` 1. It fires every 3rd turn (3, 6, …). The slice is never NULL on a firing turn.
3. Destroying the satellite (it has HP) or replacing it (N13 REPLACE) cancels the strike. A SANDBOX charge negates it (Q39).

HQ (full):
4. Every fight has a Strike satellite, and a second Strike satellite appears each layer past layer 4, up to 3. Strikes fire on staggered turns (3, 4, 5).
5. A "Targeting Console" HQ node, once per run, lets you pick which enemy slice a Strike docks on for the next fight.

Raid (one hook):
6. Each raid has one Orbital Strike. At setup it is shown targeting the node with the most assets. The strike lands at step 10 and deals integrity damage to that node. A Decoy asset on any node redirects it there (Decoy's existing role).

### 2. State and save fields
- `CombatState` has satellites already; add `strike_period: int` on the satellite spawn data. It is data, no new RNG.
- `NetrunState.console_choice: StringName` (default empty).
- `RaidState.strike_target: StringName` and `strike_step: int`, derived at setup from assets and Decoys.
- Save: additive; no bump.

### 3. Preview
- The satellite shows "STRIKE IN n" on its slice and the exact hit amount after BLOCK / SHIELD / SANDBOX.
- Raid: the target node is outlined with its projected damage. Nothing is random, so there is no "?".

### 4. Numbers
- Strike damage: 10 pierce × the tier damage factor (`config: campaign_config.strike_damage`).
- Strike period: 3 turns (`config: campaign_config.strike_period`).
- Satellite HP: 12 (`config: campaign_config.strike_sat_hp`).
- HQ extra satellites: max 3 total (`config: campaign_config.hq_strike_max`).
- Raid strike step: 10 (`config: campaign_config.raid_strike_step`).
- Raid strike integrity damage: 20 (`config: campaign_config.raid_strike_damage`).

### 5. Tests to write
- `test_strike_fires_on_period_turns` (fast): a strike lands on turns 3 and 6 and not on others.
- `test_strike_pierce_ignores_block_not_sandbox` (fast): BLOCK and SHIELD are bypassed; a SANDBOX charge negates it.
- `test_replace_satellite_cancels_strike` (fast): REPLACE fires `ON_SATELLITE_DESTROYED` and cancels the strike.
- `test_raid_strike_redirects_to_decoy` (fast): with a Decoy placed, the strike target is the Decoy's node.
- `test_strike_preview_equals_result` (full): previewed damage equals applied damage over 20 seeds.

### 6. Art answers
State names and values:

| State | Values |
|---|---|
| `strike_countdown` per satellite | int turns |
| `strike_target_slice` | slice index |
| `raid_strike_target` | node id |
| `raid_strike_step` | int |
| `console_choice` | slice index or none |

### 7. Reuse and dependencies
- N13, N14, N20 (pierce, `hits`), N3 for elite phases.
- The Orbital mini-boss design already uses fixed satellites; this option extends it.
- New code: the strike period field and the raid strike (S–M).
- No Parasite ring or rim gates.
- No fallback needed for the street form: it is entirely satellite data. The raid hook falls back to a flat integrity hit on the highest-value node.

---

## Option C: KESSLER (debris cascade; not a blackout)

**Pitch:** every satellite destroyed in a netrun leaves Debris on your wheel for the rest of the run, so killing guards has a growing price.
**Cost:** high. Depends on the Parasite ring (N10) and N8/N9.
**Risk:** N10 readability, and a snowball if the player kills many satellites.

### 1. Rules
Street (light):
1. When a satellite or drone is destroyed (trigger `ON_SATELLITE_DESTROYED`, cause killed or replaced), a 3-tick Debris segment latches on the player's Parasite ring. It rotates with the wheel.
2. Debris, when read by a needle, deals 3 damage to the player (FLAT, × tier factor). It stays until Cleanse.
3. Max 3 Debris on the ring; extra destroyed satellites add nothing.

HQ (full):
4. Destroyed satellites also leave Debris on the enemy wheel: a 3-tick segment that reduces the enemy's damage by 25 % when read. Both sides carry debris.
5. A "Debris Field" node (Rest variant) removes all Debris from your ring in exchange for losing 10 % max HP (PERCENT).

Raid (one hook):
6. When an asset is destroyed, that node is left with Debris. The next threat to enter it takes 2 damage and is delayed 1 step.

### 2. State and save fields
- `WheelState.parasite_ring` segments (N10), with a new `kind: DEBRIS` in `ParasiteSegmentData`.
- `NetrunState.debris_count: int` as a derived readout.
- `RaidNodeState.debris: bool`.
- Save: N10 and N8 already change the save; Debris adds no extra bump.

### 3. Preview
- The debris segment is shown on the rim with its damage ("3") when under a needle.
- The kill preview on a satellite shows "leaves Debris" before you commit the attack.
- Raid: debris nodes are marked. Nothing is random.

### 4. Numbers
- Debris segment size: 3 ticks (`config: campaign_config.debris_ticks`).
- Debris damage to player: 3 (`config: campaign_config.debris_damage`).
- Debris cap: 3 (`config: campaign_config.debris_cap`).
- Enemy debris damage reduction: 25 % (`config: campaign_config.debris_enemy_dmg_pct`).
- Debris Field HP cost: 10 % max HP (`config: campaign_config.debris_field_hp_pct`).
- Raid debris damage and delay: 2 damage, 1 step (`config: campaign_config.raid_debris_damage`, `raid_debris_delay`).

### 5. Tests to write
- `test_destroyed_satellite_latches_debris` (fast): a kill and a REPLACE both add a Debris segment.
- `test_debris_cap` (fast): the 4th destruction adds nothing.
- `test_debris_damage_on_read_and_cleanse` (fast): a needle reading Debris deals 3; Cleanse removes it.
- `test_debris_rotates_with_wheel` (fast): after a spin, the segment's tick range is shifted by the same amount.
- `test_raid_debris_delay` (full): a threat entering a debris node is delayed 1 step.

### 6. Art answers
State names and values:

| State | Values |
|---|---|
| `parasite_ring[].kind` | DEBRIS |
| `parasite_ring[].start_tick` | 0-29 |
| `parasite_ring[].size` | 3 |
| `debris_count` | 0-3 |
| `raid_node.debris` | true / false |

### 7. Reuse and dependencies
- Depends on N10 (Parasite ring, L), N8, N9, N13 and N6 for the trigger.
- New code: a DEBRIS kind on the ring plus the raid debris flag.
- Fallback without N10: Debris becomes an OUTPUT_DOWN ×1 status on the slice that was under the satellite (N8 only), which is much weaker.

---

## Option D: INTERCEPT (the enemy reads your orders; not a blackout)

**Pitch:** Orbital taps every channel. The first card you play each turn is intercepted, and the enemy answers it.
**Cost:** medium. N6 listeners, plus a routing tweak in raids.
**Risk:** a bland tax on the first card, and rewarding "play a cheap card first" is not deep.

### 1. Rules
Street (light):
1. In Orbital elite fights only, a listener fires on the first card played each turn (`ON_CARD_PLAYED`, once per turn).
2. The enemy gains BLOCK equal to the card's RAM cost × 2 (FLAT, × tier factor). A 0-cost card gives 0.
3. Playing a nudge instead of a card is not intercepted.

HQ (full):
4. The listener applies to every fight. The interception also marks the card's slice type: the enemy's next landing of the same type resolves at +25 % damage. Intel disables the damage rider (Exploit as buff counter).
5. A "Scrambler" node (once per run) removes interception for the next 2 fights.

Raid (one hook):
6. Threats route to the node whose asset was repositioned last in setup (the player's last move is intercepted). Routing becomes WEAKEST_NODE for that wave only.

### 2. State and save fields
- Listener data on `EnemyData` (N6); no new state beyond `CombatState.intercepted_this_turn: bool`.
- `NetrunState.scrambled_fights: int`.
- `RaidState.last_moved_node: StringName`.
- Save: additive; no bump.

### 3. Preview
- Hovering the first card shows "intercepted: enemy +N block", computed exactly. The second card shows nothing.
- Raid setup: the last-moved node is flagged as the threat's target. Nothing is random.

### 4. Numbers
- Block per RAM: 2 (`config: campaign_config.intercept_block_per_ram`).
- Marked-type damage rider: +25 % (`config: campaign_config.intercept_dmg_pct`).
- Scrambler fights: 2 (`config: campaign_config.scrambler_fights`).
- Raid reroute: 1 wave (`config: campaign_config.raid_intercept_waves`).

### 5. Tests to write
- `test_intercept_first_card_only` (fast): the 1st card triggers; the 2nd does not.
- `test_intercept_undo_clean` (fast): undoing the card removes its block (preview = result).
- `test_zero_cost_card_gives_zero_block` (fast).
- `test_scrambler_skips_two_fights` (fast): the listener is off for 2 fights, then on again.
- `test_raid_routes_to_last_moved` (full): a wave's target is the last-moved node.

### 6. Art answers
State names and values:

| State | Values |
|---|---|
| `intercepted_this_turn` | true / false |
| `intercept_block` | int |
| `marked_slice_type` | slice type or none |
| `scrambled_fights` | int |
| `raid_target_node` | node id |

### 7. Reuse and dependencies
- N6 (listeners; they must be undo-clean), N1, N14.
- New code: the one raid routing override (S).
- Fallback without N6: none for the fight rule. Fallback for the whole option is a plain per-turn block on the enemy.

---

## 8. Shared

### Ranked recommendation (ADVICE, not a ruling)
1. **B, OVERWATCH.** Cheapest of the strong options and the most direct read of "can bomb anyone". It reuses fixed satellites and pierce and extends the planned mini-boss. Its telegraph is exact.
2. **A, DEAD ZONE.** Closest to the stated leaning. Cheap and readable, but its core feel (a locked nudge) is the weakest of the four and it needs the relay escape to avoid feeling punishing.
3. **D, INTERCEPT.** A comms theme without a blackout, but shallow.
4. **C, KESSLER.** The most original, but gated on N10 and the readability of the inner ring, so it lands last.

A and B can combine later, but that breaks the one-mechanic-per-corp rule.

Q-DESIGNER: Do you want the blackout (A) to be the corporation theme, or is a strike theme (B) acceptable even though the direction leaned toward blackouts?
Q-DESIGNER: May a theme lock the player's nudge (A) given that nudges are the core skill, or must blackouts only cost resources?
Q-DESIGNER: Should Orbital strikes be allowed to deal damage that ignores SANDBOX in any form, or never?
Q-DESIGNER: In raids, should the theme affect the player's own nodes only, or can it hit neutral cleared Sites?
Q-DESIGNER: Is the HQ allowed to be the only place the full form appears, with street runs limited to one flagged node or elite?
Q-DESIGNER: Do you want a Debris-style permanent run cost (C) at all, given the "games should be fun" ruling?
