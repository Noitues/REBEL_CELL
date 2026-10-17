<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__triage_unit; status ok; tokens in 18053 cache-write 0 cache-read 32007 out 3482; cost $0.039. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# triage_unit: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, no enrage. Solace, appears L1-2 (teaching) and L5-6 (pressure, at T3-T4).
- **Concept:** a triage nurse that treats whoever is hurt worst. It carries one small heal that only works if you don't hit its **Hotfix window**. The fight is about reading its two Hotfix slices and keeping them off the pointer, or hitting while it is exposed.
- **The one question:** "Which slice is under its needle, and can I make it the Shim or Null instead of the Hotfix?" It replaces the current "out-race a 6 heal and two 8 blocks" attrition.
- **Answer that shortens the fight:** one 1-tick nudge turns a Hotfix landing into Null or Shim. A Perfect on your best slice during a Null turn kills it fast.
- **Teaching value:** it is the first enemy where steering the enemy wheel clearly pays.

## 2. Phase plan (single phase, no threshold)

| Field | Value |
|---|---|
| Phase | 1 of 1, no floor, no transition |
| Needles | 1, tick 0, FIXED |
| Hub | Triage Protocol: heals **PERCENT 4 %** of max HP at the start of its own turn **only if it took no damage during your previous turn**. Not a slice. |
| Statuses / parasites | none |
| Listeners | none |

**Wheel (sizes sum to 30):**

| # | Slice | Size | Effect | Mode |
|---|---|---|---|---|
| 1 | Triage Block | 5 | DEFRAG 6 (BLOCK) | FLAT |
| 2 | Hotfix | 4 | HOTFIX 5 HP | FLAT (× tier damage factor) |
| 3 | Shim | 6 | SHIM 6 damage | FLAT |
| 4 | Null | 5 | nothing | n/a |
| 5 | Hotfix | 4 | HOTFIX 5 HP | FLAT |
| 6 | Triage Block | 6 | DEFRAG 6 (BLOCK) | FLAT |

- Tick sum: 5+4+6+5+4+6 = 30.
- **Sub-tick maps (R11):** 4-tick Hotfix slices read W G G W, so a Hotfix **never** lands Perfect. A 6-tick slice reads W W G G W W, so Shim and Block never Perfect either.
- Only the 5-tick Null has a Perfect centre, and it does nothing.
- Hotfix output is halved on WEAK, so a WEAK Hotfix heals only 2 to 3 HP.
- Two Hotfix slices are 8 of 30 ticks, and a Hotfix at WEAK heals 50 %. The edge case becomes the common case, which helps the player.
- **Lowered from today:** Hotfix 6 to 5 flat, and Defrag 8 to 6. The unit stops being a wall.

**Hub rule detail:** the Hub heal is a PERCENT heal (R5), so it is never scaled again (R2). It is the only extra sustain besides the Hotfix slices, but see section 3: the two never both fire in a typical turn.

## 3. Sustain and intake

**Sustain sources (one):** the Hotfix slices. The Hub heal is a *conditional* bonus that exists only on turns the player does not hit it, so it is a tempo penalty, not a second regeneration source. I count it at T3 as worst case.

Reference damage (R2): [9, 11, 14, 18] per turn.

| Tier | Hotfix 5 × dmg factor | Chance a landing is Hotfix (8/30 ticks) | Avg heal/turn | Hub heal | 30 % cap |
|---|---|---|---|---|---|
| T1 | 5 | 0.27 | 1.3 | 0 if you attack | 2.7 |
| T2 | 6.5 | 0.27 | 1.7 | 0 if you attack | 3.3 |
| T3 | 8.5 | 0.27 | 2.3 | 0 if you attack | 4.2 |
| T4 | 11 | 0.27 | 2.9 | 0 if you attack | 5.4 |

- Worst case adds the Hub (4 % max HP): T3 about 2.2 + 2.3 = 4.5, slightly over the 4.2 cap. This only happens on turns you dealt no damage, which is already a lost turn. I accept it.
- The BLOCK slices are defense, not sustain.
- Intake at the reference player is reduced by the Shim at 6 flat × tier damage factor. Probability of Shim landing is about 6/30 = 0.2.

**Intake per turn** (Shim 6 × factor × 0.2, minus nothing since the player rarely blocks):

| Tier | Shim | Per turn |
|---|---|---|
| T1 | 6 | 1.2 |
| T2 | 7.8 | 1.6 |
| T3 | 10.1 | 2.0 |
| T4 | 13.2 | 2.6 |

All above 0. The current unit's 0.39 to 0.77 improves 3×.

## 4. HP by tier
R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70.

Budget = reference dpt × 3.5 turns × needles (1) − sustain × 3.5.

| Tier | dpt × 3.5 | − sustain × 3.5 | Budget | `hp_by_tier` |
|---|---|---|---|---|
| T1 | 31.5 | −4.6 | 26.9 | **30** |
| T2 | 38.5 | −6.0 | 32.5 | **36** |
| T3 | 49 | −8.1 | 40.9 | **46** |
| T4 | 63 | −10.2 | 52.8 | **58** |

Numbers sit on the low side of the band because the Block slices also absorb about 15 % of hits (BLOCK 6 at 11/30 ticks). Today's 45 HP at T3 times the 1.3 factor becomes 46 flat, same feel but without the heal-stall.

## 5. Enrage
None (normal, R4). The Hub heal's "no damage" condition and the Shim give the fight its own pressure; a stalling player is the only one punished.

## 6. Buffs and Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:** reads the preview, uses the free nudge to move the needle off a 4-tick Hotfix onto the adjacent Null or Shim. Plays burst cards on Block-free turns. Always deals some damage each turn to keep the Hub heal off.
- **Better player:** nudges so the needle sits on the W edge of a Block or Hotfix (half effect), saving RAM for a Perfect on its Null.
- **Weak player:** spends RAM on nudges but forgets the Hub heal condition, plays defensively for a turn, and watches 4 % come back. Fights drag to 6+ turns and the Shim chips them.

## 8. Systems needed
- N1 (amount modes: PERCENT heal on the Hub, flat × tier factor on the slices). Fallback: FLAT only, set Hub heal to 2 flat.
- N2 (`hp_by_tier`). Fallback: keep `hp` and use the single multiplier, 45 base.
- N12 (variable slice sizes, 4 and 6 tick). Fallback: 5-tick slices, accept Perfect Hotfix landings (the heal then fires at full output more often, so lower Hotfix to 4).
- The conditional Hub heal needs a "took damage last turn" flag. NEW: `hub_condition` (a boolean on `hub_core_data`). Fallback: an unconditional 2 % heal.
- N4 not needed.

## 9. Delta vs today
- **Kept:** id, corporation, six slices of the same family, Null, one needle at tick 0, `cycle_reward` 15.
- **Changed:** Defrag 8 to 6, Hotfix 6 to 5, slice sizes 5/4/6/5/4/6, `hp_by_tier` = [30, 36, 46, 58] replaces `hp` 45, and the new conditional Hub heal.
- **Retired:** the stalemate where heal exceeded damage (observed 3.9 heal turns at T4).
- **`heat_effects`:** none are authored on this normal, so none are kept.

## 10. Predicted sim check
Baseline (T1 to T4): 2.9 / 4.2 / 7.4 / 12.8 turns, 100 % win everywhere, taken/turn 0.39 to 0.77.

| Tier | Expected turns | Win % | Why |
|---|---|---|---|
| T1 | 3.0 | 100 | 30 HP at 16.6 dealt, heal small |
| T2 | 3.4 | 100 | 36 HP, bot nudges off Hotfix |
| T3 | 3.9 | 98 | 46 HP, Block and Shim intake of 2.0 |
| T4 | 4.5 | 93 | 58 HP; the 2.6 intake and the heal reach 4 turns only on a bad run |

T4 at 4.5 is slightly over the 3-4 target; I would trim T4 HP to 54 if the sim confirms. The big change is T3/T4 turns dropping from 7.4/12.8 to about 4/4.5, because the heal is now a smaller, steerable slice.

## 11. Open questions
- Q: Should the conditional Hub heal show a "ARMED / SPENT" chip, or is a plain tooltip enough?
- Q: Does a heal that the player's hit cancels count as damage if a Block absorbed all of it?
- Q: Is a 4 % Hub heal too punishing at T4 (about 2.3 HP) for a player who deliberately defends?
- Q: Should Triage Unit keep any hint of its old "heals faster than you cut" identity at L5-6 via a Heat-scaled Hub heal?
- Q: Do the 4-tick Hotfix slices make the first-time player feel cheated that Perfect never works on them?
