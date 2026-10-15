# CONTENT_CONCEPTS: enemies, bosses, events and raids (content design pass, D1)

**Status: concepts only.** Nothing in this document is approved. Every option waits for a designer ruling (DECISIONS
2026-10-13, "Designer rulings: twin pointer, resting hand cards, a content design pass", ruling 3). Drafted
2026-10-15 by a read-only Plan agent; the orchestrator saved it.

**Inputs:**
- `docs/GDD.md` v0.9;
- DECISIONS (the locked decisions, V4, the content-pass ruling);
- `content/`;
- the PB-PT-002 / PB-PT-003b findings D1 / D3;
- `state/SA-002_heuristic_calibration.md`;
- `plan2/G_REEVAL.md`.

**Conventions:**
- "NEW SYSTEM" marks anything the current schema or resolver can't express, with its cost.
- Every number names the file it lives in.
- Size: S (content only, or a few lines of code), M (a new field or handler, plus tests), L (a new mechanic with UI).
- G ids (G3, G4, G6, G9, G12) mark the options that would realize those art-pass items.

## 0. What exists today (inventory)
| Kind | Where | Count | Notes |
|---|---|---|---|
| Enemies (incl. satellites, elites, mini-bosses, bosses) | `content/enemies/` | 57 | Five corporations + REBEL_CELL |
| Bosses | `renewal_engine`, `the_manifest`, `civic_core`, `commons_array`, `dispatch_core` | 5 | **All five share one template** |
| Mini-bosses (the final Rack of every netrun) | `account_manager`, `logistics_director`, `city_manager`, `mission_director`, `the_handler` | 5 | 150–170 HP at T1; phases at 50 % / 25 % |
| Enemy slices with riders | `dose`, `citation`, `priority`, `solar_flare`, `*_drain`, `shim_8_weight` | ~6 | `SliceData.extra_effects`, so new riders are data |
| Terminal events | `content/events/` | 124 | Every choice is a fixed trade. No conditions, no risk, no link to combat or the wheel. |
| Raids | `content/raids/` | 40 | 8 triggers × (shared + 4 corps); usually **one wave** |
| Threats | `content/threats/` | 17 | `lander.tres` exists (2 edges per step) |
| Assets | `content/assets/` | 8 | turret, ice_lock, decoy, flak_array, railgun, sentry, tar_pit, honeypot_node |

**Schema features no enemy uses yet:** `WheelData.inner_ring` (an enemy inner ring), `WheelSlotData.firmware`
(enemy Firmware), non-even `pointer_ticks` on a normal enemy. These are the cheapest new wheel mechanics, needing one
test each.

## 1. Diagnosis
### 1.1 The Genome Core is a 1,475 HP sponge with one real mechanic; two Exploits cancel parts of it
| Fact | Value | Source |
|---|---|---|
| Base HP | 360 | `renewal_engine.tres` `hp` |
| Tier scale | ×1.6^3 = ×4.096 → **1,475 HP** | `campaign_config.tres` `enemy_scale_per_tier = 1.6` |
| Output scale | ×1.3^3 = ×2.197 (Shim 14 → ~31, Overflow 24 → ~53, Defrag 12 → ~26) | `enemy_damage_scale_per_tier = 1.3` |
| Auto-Renew heal | **10 per turn, flat** (`EffectInterpreter._scaled`, not `output_scale`) | `fx_heal.amount` |
| Phases | 66 %: Multiply (0, 15). 33 %: Orbit 3 + `wheel_emergency` + 2 drones (~20 HP each) | `phase_multiply`, `phase_orbit` |
| V4 | Won at 53 / 60 HP in about 20 turns, "tediously long" (≈ 74 net damage per turn) | DECISIONS V4 |

**Why it is long and boring:**
1. **75 % of the HP pool is the tier factor.** The player's damage doesn't scale with tier, so content HP × global
   factor gives a number neither was chosen for.
2. **The only boss rule, Auto-Renew, is irrelevant at T4.** Hub Breach saves 10 of 1,475. The same holds for every
   boss's flat hub sustain.
3. **Breach erases phase 2.** `min_exploits_for_breach = 3` and Solace has exactly three Exploit types, so Breach
   always comes along. `_phase_layout` trims (0, 15) back to (0). By the pointer rule (GDD 2.7), a second boss
   pointer would have doubled the player's hits, so Breach also makes the fight longer.
4. **Virus is wiped at 33 %:** `_apply_wheel_override` resets `slice_statuses`. CORRUPTED self-damage is flat (3, +1
   per MAJOR), which is noise at 1,475 HP.
5. **Orbit adds no puzzle under the start-of-turn respin** (a uniformly random rotation plus a constant shift). That
   doesn't hold for Frozen or Anchored wheels.
6. **Every turn asks the same question:** about 13 turns of one puzzle, then about 7 more with drones.
7. **One template for all five bosses,** so fixing the Genome Core sets the pattern for all of them.

### 1.2 Normal fights: the skill gap dominates, but content turns the gap into stalemates
| Measure | Value | Source |
|---|---|---|
| Best-plan damage per turn (T1) | 14.7–20.1 | PB-PT-003b D1 |
| Tester damage per turn | 3.2–5.0 | PB-PT-003b D1 |
| T1 normal HP | 25–50 | `content/enemies/*.tres` |
| T1 elites | Claims Adjuster 112, Recall Unit 106 | M7 +25 % |
| T1 mini-boss, every netrun | Account Manager 150 (240 at T2, 384 at T3) | `account_manager.tres` |
| Fight length (testers) | 9–16 turns; a 20-turn Triage Unit | PB-PT-003b D3, PB-PT-002 D3 |

**Triage Unit** (45 HP; Defrag 8, Hotfix 6, Shim 6, Hotfix 6, Defrag 8, Null): four of six slices are sustain.
Expected mitigation ≈ 4.7 per turn, against a tester's 3.2–5.0 output. The result is a fight that can't end and can't
be lost. **Elites and the mini-boss** are long by HP, not mechanics; the Account Manager is fought at the end of
every netrun, so it is the biggest total time sink.

**Unused GDD levers:** multi-pointer precision splits, satellites as positional puzzles, Flip combined with
resistance, Freeze on enemies, statuses on enemy slices, enemy Firmware and inner rings, Heat-gated behaviour.

## 2. Enemies and modifiers that use the wheel
Deterministic between random events. Numbers are placeholders that would live in the named `.tres`.

| # | Name | Hook | Counterplay | Reuses | Size |
|---|---|---|---|---|---|
| E1 | **Fortress** | A low-HP host; its 5 non-Null slices carry docked Defrag / Null guard satellites. Pointer attacks hit the guard, **except when its own Null is under its pointer**: steer it to Null, then burst. | Steer to Null; Undock; SWEEP; Snap | satellites (`dock_slot`), bodyguard rule | S; ruling: Undock onto an occupied slice (G2) |
| E2 | **Flip Trap** | Opposite pairs (Overflow / Null, Shim / Defrag); high hub resistance blocks Flip until Strip. Teaches Strip + Flip. | Strip + Flip; Hub Breach; Jam | resistance, Flip, Strip | S; check against Heat ≥ 50 +1 resistance |
| E3 | **Skew** | Two pointers at a non-multiple-of-5 spacing (e.g. 0 / 12): when one reader is Perfect, the other is WEAK. Your attacks hit both, so it dies fast. | Choose which reader lands WEAK on the danger; Freeze | `pointer_ticks`, precision tiers | S; **ruling: GDD 2.1 even spacing** |
| E4 | **Overheater** | Hub ON_TURN_START: OVERCLOCKED on its own random slice (1.5× this turn), which then turns CORRUPTED (self-damage). The fight shortens itself. | Steer onto CORRUPTED; Encrypt / Cleanse are anti-synergy | OVERCLOCKED → CORRUPTED | S; G4 EMPOWERED |
| E5 | **Metronome** | Hub FREEZE SELF; the wheel holds every other turn (re-freeze is blocked after a skip). With Orbit 5, its intents advance a slice per turn. | Respin card; Flip; plan Perfects on held turns | Freeze, `pointer_orbit_per_turn` | S; **NEW SYSTEM (S)** `skips_respin` for "never respins"; G4 LOCKED / FROZEN |
| E6 | **Phisher** | PHISHING: INFECT PARASITE on the slice **you** just landed (halved next time). Punishes repeating one plan. | Encrypt the best slice; Cleanse; vary | `citation.tres` pattern | S; G4 PHISHING |
| E7 | **Lockstep** | Your manipulation moves its wheel too (an enemy Linked Bus); a shared good rotation always exists. | Jam / Strip only its wheel; Freeze | Linked Bus handler | **NEW SYSTEM (M):** enemy listeners on the player's ON_NUDGE / ON_CARD_PLAYED |
| E8 | **Cipher Clerk** | Enemy Firmware: Hardened on its Overflow (absorbs Dose, Corrupt, Virus); Mirror on its Defrag. | Precision on its wheel; Strip | `WheelSlotData.firmware` | S + one test; G4 ENCRYPT |
| M1 | **Escalation** (Heat-gated affix) | At Heat ≥ 50 an enemy gains E4's rule, so high Heat gives shorter, spikier fights. | As E4 | `HeatGatedEffectData` | S per enemy, or NEW SYSTEM (S): a corporation affix list |
| M2 | **Two Readers** (elites) | Replaces the M7 +25 % HP with a second Skew pointer: spikier, shorter. | E3 | `pointer_ticks` | S |

**Triage Unit options:**
- **(A)** Swap a Hotfix → Shim and a Defrag → Dose.
- **(B)** Move the heal to its Hub (Hub Breach answers it) and add one attack slice.
- **(C)** Fortress-lite: guards on the Hotfixes.

Normal enemies can't have phases (`EnemyData.validate`).

## 3. Bosses
### GC-1 "Repair the template" (S)
- **Phase 1:** one pointer; Auto-Renew sized for T4 (a share of max HP).
- **Phase 2 (0.66):** Multiply to two pointers; **Breach no longer trims phase pointers** (G6: "Hub breached N
  turns" or "skips phase 1").
- **Phase 3 (0.33):** `wheel_emergency` **keeps statuses**; drones are speed bumps.
- **Target:** 10–12 turns.
- **NEW SYSTEM (S):** hub HEAL scaled by `output_scale` or as a percent of max HP; an `ExploitData` field for Breach's
  new meaning; `keep_statuses` on `BossPhaseData`.
- **Risk:** it fixes "long" more than "boring", and it applies to all five bosses.

### GC-2 "Helix" (M): the recommended direction
Each phase **migrates** the readers to a new non-even spacing, telegraphed (MIGRATE, GDD 2.11).
1. **Transcribe:** 2 readers at Skew spacing (0 / 12). Only one can be Perfect; your hits land twice.
2. **Replicate (≈ 0.6):** MIGRATE to 3 readers (offsets o, o+2, o−1): one Perfect, one Good and one WEAK per
   rotation. The wheel is in safe opposite pairs, so Strip + Flip finds the safe triple. Your hits land three times.
3. **Express (≈ 0.25):** `wheel_override` to a Null-adjacent vulnerability layout; 2 drones dock on its attack slices
   (Fortress rule).

- **Target:** 8–10 turns. The pointer rule multiplies player damage ×2–×3, so HP can stay large while turns drop.
- **Exploits (G6):** Breach removes the 3rd reader; Intel shows migrations 2 turns ahead; Virus pre-corrupts.
- **Code:** GC-1's status-keep plus slice amounts retuned.
- **Risks:**
  - three intents at ×2.197 can one-shot a 45–60 HP operative, so amounts must be authored for three readers;
  - the readability of three pointers;
  - GDD 2.1 / 2.11 wording on uneven spacing.

### GC-3 "Splice" (L)
- **Latch:** a Parasite ring (a 10-tick segment) latches onto **your** inner track; your output also heals the Core
  when you read it. Auto-Renew is removed (Gear Shift / Ring Tap / Ring Lock).
- **Splice (0.6):** the override keeps your CORRUPTED slices, and self-damage scales with tier.
- **Express (0.3):** the ring jumps to your outer track (a WEAK zone).
- **Target:** 9–12 turns.
- **NEW SYSTEM (L):** enemy-owned ring segments on the player wheel. **G3**, G4.
- **Risk:** the inner ring is still judged illegible; it is the biggest build.

### NB-1 DISPATCH finale "Sync Strike" (L)
- Three short Mirror "lock" combats (3–4 turns each, one per living operative), then the core (4–6 turns).
- Each cleared lock removes a phase or buff (ROOTKIT / HIJACK / CIPHER).
- **Target:** about 16 turns over four fights.
- **NEW SYSTEM (L):** a multi-combat boss run. **G12**, G6.
- **Risk:** it needs 3 living operatives, and it depends on the route / HQ redesign.

### NB-2 "Final Notice" mini-boss (S–M)
- Account Manager: one phase, lower HP, two Retainer satellites docked on Overflow and Dose (Fortress), a single
  telegraphed MIGRATE at 50 %. The Heat 75 heal stays.
- **Target:** 4–6 turns.
- **Risk:** the Rack loses its "big fight" feel; keep it through the reward.

## 4. Events and raids that create decisions
### Events (today: 124 fixed trades)
| # | Concept | Decision | Size |
|---|---|---|---|
| EV1 | **Recon buy** (G4 RECON): pay to set up the next combat (enemy Frozen, −1 resistance, a satellite removed, phase reveal) | Spend now for a shorter next fight | NEW SYSTEM (S–M): a run-level "next combat overrides" store |
| EV2 | **Optional ambush:** fight a guarded cache, or walk away | HP risk vs reward; answers D2 attrition | NEW SYSTEM (M): `EventChoiceData.starts_combat` |
| EV3 | **Jailbroken slice:** Null → Overflow + Burner Firmware (+1 Heat per trigger) | Power vs Heat | S–M |
| EV4 | **Dial the vault:** a 6-slice reward wheel, N nudges, extra nudges cost HP / Heat | A precision puzzle that teaches nudging | NEW SYSTEM (M): an event-wheel page |
| EV5 | **Deal + raid:** a big reward now, a STORY raid next interlude | Raid readiness vs loot | M |
| EV6 | **Clinic thinning:** remove up to 2 cards for HP | Deck quality vs HP | S–M |

### Raid modifiers (G9)
| # | Modifier | Decision | Size |
|---|---|---|---|
| R1 | **EXPOSED spotlight:** one node takes extra damage; move it along a link for Heat or Schematics | Defend, move or sacrifice | NEW SYSTEM (S–M); G9 EXPOSED |
| R2 | **Encrypted routes:** at high Heat a threat's path is dashed until decrypted (Ghost, Intel, 1 Schematic) | Spend to know, or plan for the worst | M; G9 intel |
| R3 | **Vehicle types:** LANDER enters inside the network; FLYING ignores ICE Lock and Tar Pit; HEAVY halves Turret damage | Mixed Armory | M; G9 vehicle types |
| R4 | **Heat-scaled second wave + ultimatum:** pay Schematics or Heat to cancel, or take it for the reward | A Schematics sink (D6) | S–M; G9 waves |

Decoys that get destroyed and routes that revert (G9) are a follow-up.

## 5. Fight length levers (content side)
| # | Lever | Where | Effect |
|---|---|---|---|
| L1 | HP per enemy | each `.tres` `hp` | Linear; halving the Account Manager saves ~3–5 turns per netrun |
| L2 | Sustain density | wheel `slots` | Removes stalemates (Triage A: ~4.7 → ~2 per turn) |
| L3 | Threat density | wheel `slots` | Fights resolve both ways |
| L4 | Extra pointers on big enemies | `pointer_ticks` | Doubles or triples player hits; the strongest shortener |
| L5 | Phases that change the question, not the pool | `BossPhaseData` | Fewer dead turns |
| L6 | Self-damage clocks | hub `passive_effects` | Fights end themselves (T1–T2) |
| L7 | Vulnerability windows | phase `wheel_override` | A burst turn every phase |
| L8 | Tier-sized sustain / self-damage | NEW SYSTEM (S): enemy hub effects × `output_scale` | Breach and Virus matter at T4 |
| L9 | Exploits shorten, not weaken (G6) | `ExploitData` | e.g. skip phase 1 |
| L10 | Satellites as puzzles, not HP sinks | satellite `hp`, `dock_slot` | No overkill waste |
| L11 | Mini-bosses at one phase | `account_manager.tres` + peers | The most campaign time saved |
| L12 | Turn-count phase trigger (soft enrage) | NEW SYSTEM (S): `BossPhaseData.turn_threshold` | A hard length ceiling |
| L13 | Boss tier-scale exemption | NEW SYSTEM (S): `EnemyData.hp_scale_override` | Author the boss pool directly |

## 6. Recommended first slice and the designer's questions
### 6.1 First slice (fixes "boring + long" for the boss and the worst long fights)
1. **Genome Core → GC-2 Helix** (phases 1–2), plus GC-1's two code fixes (statuses kept on override; Breach = Hub
   breached N turns), and phase 3 drones Fortress-style. M.
2. **Triage Unit option A.** S.
3. **Account Manager → NB-2.** S.
4. **Elites: M2 "Two Readers"** replaces the +25 % HP. S.
5. **A probe enemy: E4 Overheater** (data only).

**Verification:**
- the balance sim (`docs/handoff/plan2/BALANCE_SIM.md`): boss / fight modes for turn counts and win rate, plus
  `--lookahead 2`;
- one designer attempt on boss save seed 1017 for "boring".

### 6.2 Questions for the designer
1. **Target lengths** (best-plan turns): normal / elite / mini-boss / Central Server? Proposal: 3–4 / 5–6 / 4–6 /
   8–10.
2. **Genome Core direction:** GC-1, GC-2 or GC-3 (or GC-2 now, GC-3 later)?
3. **Boss HP and the tier factor:** keep ×4.096 at T4 and author around it, or exempt bosses and mini-bosses (L13)?
4. **Uneven pointer spacing for enemies** (E3, M2, GC-2): it amends GDD 2.1.
5. **Breach (G6):** Hub breached N turns / skip phase 1 / remove a pointer only in 3+ phases / boss starts stunned?
   Is the ROOTKIT / HIJACK / CIPHER set wanted now, or with NB-1?
6. **Virus:** do statuses survive a phase override?
7. **Enemy sustain at tier (L8):** scale hub heal, shield and CORRUPTED self-damage? It affects all five bosses.
8. **Same fix for all five bosses** in the same pass?
9. **Mini-bosses:** NB-2 for all corporations, or Solace first?
10. **Triage Unit:** A, B or C?
11. **Which enemy concepts go forward** (E1–E8, M1–M2)? Undock onto an occupied slice (G2 / E1)? A `skips_respin`
    flag (E5)?
12. **NEW SYSTEM approvals:** enemy listeners on player actions (E7, M); `skips_respin` (S); turn-based phase trigger
    (L12, S); event next-combat overrides (EV1); event combat (EV2, M); event wheel (EV4, M); Parasite ring (GC-3,
    L, G3); Sync Strike (NB-1, L, G12).
13. **G4 names:** which enemy-side types and states become content? Should BURNING be a new status (M)?
14. **Raid modifiers (G9):** which of R1–R4 first? Is R4 the Schematics sink for D6?
15. **Events:** keep the trade-only lore events and add decision events alongside, or convert a share of the 124?
16. **Naming:** should the boss take the Site's name ("The Genome Core" vs "Renewal Engine")?

### Critical files
- `content/enemies/renewal_engine.tres`
- `content/corporations/solace.tres` (`ex_breach`, `ex_virus`)
- `scripts/core/combat_resolver.gd` (`_phase_layout`, `_apply_wheel_override`, `_scale_enemy`, the pointer-rule hit
  loop)
- `content/config/campaign_config.tres`
- `content/enemies/triage_unit.tres`, `account_manager.tres`, `claims_adjuster.tres`, `recall_unit.tres`
- schemas: `scripts/data/boss_phase_data.gd`, `effect_data.gd`, `event_choice_data.gd`, `threat_data.gd`

**Code facts behind the diagnosis** (read from the source, not run):
1. Hub HEAL isn't tier-scaled.
2. Breach trims MULTIPLY pointers through `_phase_layout`.
3. `_apply_wheel_override` replaces `slice_statuses`.
4. E5's "every other turn" relies on `freeze_blocked` when `respin_skipped` and the respin → hub ON_TURN_START order
   (`combat_resolver.gd` ~340–395).
5. Enemy Firmware and inner-ring paths exist in the schema but are unused; each needs a test before shipping.
