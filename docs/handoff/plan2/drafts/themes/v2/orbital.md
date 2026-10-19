<!-- THEMES2 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01BLNcf54zM6exqecvb8qLg7, custom_id themes2__orbital; status ok; tokens in 16161 cache-write 0 cache-read 34418 out 10633; cost $0.073. v2: designer answers 2026-10-19 applied. -->

# Orbital: SKY CONTROL (v2)

Merged theme: DEAD ZONE (blackouts) + OVERWATCH (telegraphed strikes). The two share one object, the **Relay satellite**: a fixed satellite (N13) whose presence causes DARK turns and whose strike is the telegraphed hit.

## 0. What changed from v1

- **A + B together:** v1 listed them as separate options. They are now one theme, with the Relay satellite carrying both rules. Killing it ends the blackout and the strike.
- **O1 (may lock nudges):** DARK turns lock the own-wheel nudge, free and paid (N7, source `blackout`). Cards still work. This is the v1 option A rule, now shown on the nudge buttons by the built `NudgeLockPencil` (a grease-pencil circle-slash, no word chip or toast). The reason text lives only in the hidden log.
- **O2 (sandboxes OK to target):**
  - A strike is pierce: it ignores BLOCK and SHIELD, never SANDBOX (R13).
  - A SANDBOXed player is a legal target, and the strike is not skipped or redirected. It spends the SANDBOX charge.
  - In raids there is no SANDBOX, so strikes aim at nodes regardless of their defenses.
- **O3 (player nodes only):** raid Dead Zone and raid strikes only target the player's claimed nodes. Neutral cleared Sites are never targeted.
- **O4 (strong everywhere, grows over the campaign):** new **Orbit Phase** P1 / P2 / P3, a pure function of site tier, ICE and Exploits taken. Street, HQ and raid each read it. The street form is present from T1 (not elite-only, as in v1 B).
- **O5 (permanent run costs OK):** v1 option C's Debris is adapted as **Debris**, a run counter (no Parasite ring, no N10). Each Relay you destroy costs −1 starting RAM for the rest of that netrun, from P2 on.
- **Dropped from v1:** the Intercept listener (option D) and the Parasite-ring Kessler (option C).
- **Not built yet:** no Orbital code exists. No code needs to change; all of this is new.

## 1. Rules

### Orbit Phase (escalation)

1. `orbit_phase = min(3, site_tier + ice_steps)`. Here `ice_steps = floor(ICE / orbit_ice_per_step)`, with `orbit_ice_per_step` = 10, and the result is at least 1.
2. HQ netruns (T4) are always P3.
3. A netrun snapshots `orbit_phase` at its start. It does not change mid-run.
4. A raid uses `max(highest tier of any cleared Orbital Site, 1) + ice_steps`, capped at 3.
5. Each Orbital Exploit taken (Intel, Breach, Virus: 0-3) adds one raid strike (rule 17). It changes nothing in street or HQ netruns.

| Phase | Names the question | Relay coverage (street) | Dark cadence | Strike cadence | Debris |
|---|---|---|---|---|---|
| P1 (T1) | "Steer without a free nudge" | Elite fights, Racks, and 1 flagged fight per netrun | every 4 turns (1, 5, …) | every 4 turns (4, 8, …) | off |
| P2 (T2) | "Kill the relay or pay for it" | All the above, plus every fight on layers 3 and up | every 3 turns (1, 4, …) | every 3 turns (3, 6, …) | on |
| P3 (T3, HQ) | "Two skies at once" | Every fight; elites, mini-bosses and bosses carry 2 Relays | every 3 turns | 3 and 4, 6 and 7 (staggered) | on |

### Street (light form)

6. A fight with a Relay satellite has DARK turns. On a DARK turn the player's own-wheel nudge is locked (N7). Cards, spins and respin cards still work.
7. The Relay is a fixed satellite (N13) docked on the enemy slice nearest tick 15. It has HP (`orbit_relay_hp_by_tier`) and one **Strike** slice on its mini-wheel: pierce, `hits` 1 (N20).
8. The Relay fires on its strike turns. The Strike slice is never NULL on a firing turn, so the sat's own mini-wheel position doesn't matter. A strike resolves at End Turn at the player's pointer and deals the pierce amount, with SANDBOX negating it (R13).
9. Pointer attacks at the Relay's host slice hit the Relay first (bodyguard, GDD 2.7). That is how you kill it.
10. A destroyed Relay (killed or REPLACED, N13) cancels its future strikes. DARK turns end when no Relay is alive in the fight.
11. **Debris (P2+):** killing a Relay adds 1 Debris to the run (cap `orbit_debris_cap`). Each Debris is −1 starting RAM in every later combat of that netrun. A REPLACED Relay costs no Debris, but the replacing satellite must come from a class, Firmware or Daemon (see Q-DESIGNER).
12. The flagged P1 fight is chosen at map generation from the existing map stream: one fight node in layers 3-6 that is not an elite. It carries a Relay and is marked on the map before entry.

### HQ (full form)

13. Every HQ fight has Relays per the P3 row. Layers with `layer mod 4 in {0, 1}` are **dark layers**. On a dark layer the Mainframe (shop) is closed, and DARK turns are every 2 turns instead of 3.
14. **Uplink Dish** nodes (3 per HQ run) are Relay fights. Clearing one makes the next 2 layers **lit**: no DARK turns and Mainframes open. Strikes still fire on lit layers.
15. **Targeting Console** node (once per HQ run): choose which enemy slice the next fight's Relay docks on. It is stored as a slice index.
16. A fight with 2 or 3 Relays staggers their strikes (turns 3, 4, 5). Strike damage uses the tier damage factor (R2).

### Raid (one hook)

17. At setup, each raid shows its strikes: `1 + exploits_taken` strikes (cap `orbit_raid_strikes_max`). Strike *i* lands at step `orbit_raid_strike_step + 4*i`. Each targets the player's node with the most assets (ties: lowest node id), then the next-most for the next strike.
18. A strike deals `orbit_raid_strike_damage` integrity to its node. A Decoy asset on any player node redirects every strike to the Decoy's node, and the first Decoy in node id order wins.
19. **Dead Zone:** the entry Site's node and its player-owned neighbors within `orbit_dark_radius` hops (P1: 0, P2: 1, P3: 2) are dark. Assets cannot be placed on or moved onto or off dark nodes during setup. Built-in defenses and projected outcomes work as normal.
20. Raid strikes never pick neutral Sites, DOWN nodes or TAKEN nodes (O3).

## 2. State and save fields

- `NetrunState.orbit_phase: int` (1-3, snapshot at netrun start).
- `NetrunState.dark_nodes: Array[StringName]`: the P1 flagged fight (P2+ are derived from layer, not stored). Generated in map generation on the existing map stream, no new RNG.
- `NetrunState.lit_until_layer: int` (HQ, default 0).
- `NetrunState.debris: int` (default 0, reset per netrun).
- `NetrunState.console_choice: int` (slice index, −1 = none).
- Per-satellite spawn data (not state): `strike_period`, `strike_offset`, `is_relay`, `hp`. A strike countdown is derived from `turn_index`, so it is never stored.
- `RaidState.orbit_phase: int`, `RaidState.dark_nodes: Array[StringName]`, `RaidState.strikes: Array[{node: StringName, step: int}]`. All are derived at setup from the graph, assets and Decoys.
- **Save impact:** additive fields with defaults. No version bump beyond N7's. Raid fields recompute on load. No RngService streams besides the existing map generation.

## 3. Preview

- **Map:** each node shows an `ORBIT P1/P2/P3` pencil badge. Relay fights show a no-signal glyph, and dark layers in the HQ are tinted. The Debris count shows in the run HUD.
- **Fight, turn track:** DARK turns and strike turns for the whole fight are shown ahead of time (they depend only on `turn_index`, so they're exact). The nudge slash appears on DARK turns.
- **Strike chip:** the Relay shows "STRIKE IN n". When the pointer is settled the chip shows the exact damage after BLOCK, SHIELD and SANDBOX (preview = result, per R3 and R13). Hovering an attack at the Relay's host slice shows "kills relay: +1 DEBRIS" (P2+).
- **"?" only where a stream is read:** the start-of-turn respin and a respin card landing (Q19, built). The schedule, strike damage and raid targets have no random part.
- **Raid setup:** dark nodes are lock-marked. Each strike target is outlined with its step and projected integrity damage. The projected outcome includes strikes.

## 4. Numbers

- Orbit ICE step: 10 (`config: campaign_config.orbit_ice_per_step`).
- Dark cadence by phase: [4, 3, 3] (`config: campaign_config.orbit_dark_every_by_phase`).
- HQ dark cadence: 2 (`config: campaign_config.hq_dark_every`).
- Strike period by phase: [4, 3, 3] (`config: campaign_config.orbit_strike_period_by_phase`).
- Strike base damage: 10 pierce × the tier damage factor (`config: campaign_config.orbit_strike_damage`).
- Relay HP by tier: [12, 14, 17, 20] (`config: campaign_config.orbit_relay_hp_by_tier`).
- Relays per fight by phase and class: P3 elite, mini-boss and boss 2; HQ cap 3 (`config: campaign_config.orbit_relays_p3_elite`, `hq_relay_max`).
- P2 Relay coverage: from layer 3 (`config: campaign_config.orbit_p2_relay_min_layer`).
- Debris cost: −1 starting RAM per Debris, cap 3 (`config: campaign_config.orbit_debris_ram`, `orbit_debris_cap`).
- Dark layer pattern: `layer mod 4 in {0, 1}` (`config: campaign_config.hq_dark_pattern`).
- Uplink Dishes per HQ: 3, lit window 2 layers (`config: campaign_config.hq_uplink_count`, `uplink_lit_layers`).
- Raid strike step: 10, spacing 4, max 3 strikes (`config: campaign_config.orbit_raid_strike_step`, `orbit_raid_strike_spacing`, `orbit_raid_strikes_max`).
- Raid strike damage: 20 integrity (`config: campaign_config.orbit_raid_strike_damage`).
- Dark radius by phase: [0, 1, 2] (`config: campaign_config.orbit_dark_radius_by_phase`).

## 5. Tests to write

| Name | Tier | Asserts |
|---|---|---|
| `test_orbit_phase_function` | fast | tier, ICE and HQ give the expected phase; a netrun snapshot survives a save and reload |
| `test_dark_turn_locks_nudge` | fast | DARK turn refuses the free and paid nudge with source `blackout`; cards work; the next turn is allowed |
| `test_dark_schedule_matches_preview` | fast | the turn track's DARK list equals the locks actually applied |
| `test_strike_pierce_not_sandbox` | fast | BLOCK and SHIELD are bypassed; a SANDBOX charge negates and is consumed; a sandboxed target is still struck |
| `test_strike_fires_on_period` | fast | strike turns per phase; staggered with 2 and 3 Relays |
| `test_killing_relay_cancels_strike_and_ends_dark` | fast | the last Relay dying stops DARK turns and strikes; a 2-Relay fight keeps DARK until both die |
| `test_relay_kill_adds_debris_p2_only` | fast | P1 kill: 0 Debris; P2 kill: +1; capped at 3; REPLACE adds none |
| `test_debris_reduces_start_ram` | fast | each Debris is −1 starting RAM; run-scoped; reset at the next netrun |
| `test_strike_preview_equals_result` | full | previewed damage equals applied damage over 20 seeds |
| `test_uplink_dish_lights_layers` | fast | after a clear, the next 2 layers have no DARK turns and the Mainframe is open |
| `test_dark_layer_closes_mainframe` | fast | the shop is refused on a dark layer |
| `test_console_choice_docks_relay` | fast | the chosen slice holds the Relay in the next fight only |
| `test_raid_strikes_scale_with_exploits` | fast | 0-3 Exploits give 1-4 strikes (capped); steps spaced |
| `test_raid_strike_redirects_to_decoy` | fast | a Decoy on any player node takes all strikes |
| `test_raid_dark_refuses_placement` | fast | place and move refused on dark nodes; the projection is unchanged |
| `test_raid_strikes_player_nodes_only` | fast | neutral, DOWN and TAKEN nodes are never targets |
| `test_orbit_flags_deterministic` | full | same seed gives the same flagged node and layout after reload |

## 6. Build slices

1. **Orbit Phase function + config tables** (S): the pure `orbit_phase`, per-phase arrays, snapshot into `NetrunState`. No dependencies.
2. **DARK turn lock rule** (S): the schedule function and the N7 `blackout` lock source. Reuses built N7 and the nudge slash; needs turn-track data from slice 1.
3. **Relay satellite data** (M): `is_relay`, `strike_period`, `strike_offset`, Strike slice (pierce, `hits` 1, N20), HP by tier, docking rule. Depends on N13, N14, N20 and slices 1-2.
4. **Strike and kill logic** (M): cancel on kill or REPLACE, the DARK end condition, the P1 flagged-fight map flag. Depends on 3.
5. **Debris run cost** (S): counter, starting RAM hook, cap, HUD readout. Depends on 4.
6. **Fight UI** (M): turn track, "STRIKE IN n", hover "kills relay: +1 DEBRIS", map phase badge. Depends on 2-5. Art-pass owns the pencil and satellite look.
7. **HQ form** (M): dark layers, Mainframe closed, Uplink Dish node, Targeting Console node, 2-3 Relay stagger. Depends on 3-4 and the HQ netrun art in W2.
8. **Raid form** (M): derived strikes, Decoy redirect, dark nodes, raid setup UI. Depends on 1 and the raid setup view. Strike count reads existing Exploit state.
9. **Sim metrics** (S): per-phase intake from strikes, Relay kill rates, Debris reached. Depends on N19, then a balance pass.

## 7. Q-DESIGNER

Q-DESIGNER: Should the Relay's death be the escape from the blackout as designed (kill it and pay a Debris at P2+, or replace it free), or should DARK turns be unavoidable and only the strike cancellable? (Recommended: kill or replace both end DARK, since the player needs an answer.)
Q-DESIGNER: Do Orbital Exploits taken add raid strikes (a retaliation cost for progress), or should they instead weaken Orbital (e.g. Breach removes a Relay in HQ)? (Recommended: add strikes, because it follows Heat's retaliation logic and needs no new content.)
Q-DESIGNER: May a player remove Debris during a netrun (a Rest option for 10 % max HP), or is it permanent until the run ends? (Recommended: permanent until the run ends, capped at 3, per O5.)
Q-DESIGNER: Should `ice_steps` push a T1 site to P2 (ICE 10) or should phase follow site tier only? (Recommended: ICE pushes it, capped at P3, so high ICE feels different in early sites.)
Q-DESIGNER: May a DARK turn coincide with a strike turn (it can at cadence 3 only when offsets are changed)? (Recommended: never, with strike turns offset so a strike turn is always one where nudges work.)
Q-DESIGNER: Does the raid phase use the highest cleared Orbital Site tier, or the campaign's overall tier progress? (Recommended: the highest cleared Orbital Site tier, since it is already stored.)
