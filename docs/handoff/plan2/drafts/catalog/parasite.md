<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01VfdWxebuNLgtnS39R7FQmN, custom_id catalog__parasite; status ok; tokens in 13806 cache-write 0 cache-read 32585 out 12832; cost $0.081. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# catalog: parasites

## 1. The ring

**Geometry**
- The ring is a thin outermost band on the **player's** wheel, using the same 30-tick grid as the outer slices.
- It is enemy-owned: only enemies and events write to it.
- Each parasite is a segment `[start_tick, size_ticks]` (R11 sizes 2–6). Segments never overlap.
- **Cap:** 3 segments and 14 ticks total (~47% of the rim).
- **Full ring:** a new latch replaces the oldest segment (same logic as R12 REPLACE). The preview names the segment that will be replaced.
- If a placement overlaps another segment, it slides clockwise to the first free span. If none fits, it replaces the oldest.

**Frame (answers N10's Q10)**
- The ring is **bound to the wheel's frame**. Spins, nudges, Flip and the start-of-turn respin carry it with the slices.
- Flip mirrors segment spans with the wheel (t → 2p+15−t).
- A parasite is therefore "stuck to a slice region", not to the pointer. You dodge it by landing on another slice or on the uncovered ticks of a slice.
- Segments are placed to straddle slice edges, so a precise landing can avoid them. This is the R11 sub-tick tension.
- It is independent of the inner ring (which rotates on its own). It sits outside the outer slices, so the inner-ring redesign does not affect it.
- One extra field, `ring_offset`, lets a card slide the ring relative to the wheel (see §4).

**Who reads it, and when**
- There is no ring pointer. Every **player pointer** reads the ring at the tick it is on, at the same moment the outer slice resolves at End Turn.
- If the pointer's tick lies inside a segment, that segment fires. Quality does not matter; any tick of the span triggers it.
- Each segment declares one phase:
  - **MODIFIER:** alters the outer slice's resolution. This runs before the defensive pass.
  - **OFFENSIVE:** resolves with the enemy's offense pass, after the enemy's own hits.
  - **STATUS:** resolves in pass 3.
- Enemy intents show before commit. The ring does nothing during staging, so previews equal results.
- Randomness comes only from the start-of-turn respin, which is already a checkpoint. Latch placement is a pure function (see §3).

**Reading from afar**
- Colour by category: red = damages you, amber = drains or weakens, violet = status.
- Each segment has a fixed rim glyph, minimum 2 ticks wide.
- A "pointer-lit" arc marks the segment under each pointer. The result chip carries the same line ("Leech Bite −6", "Dampener −50%").
- After the respin, the chips show exactly what will fire.

**Amounts** (R2, R5): flat enemy amounts × the tier damage factor; percent amounts read max HP and are not scaled again. Parasite damage is blockable by BLOCK, SHIELD and SANDBOX unless marked **pierce**.

## 2. Segment types

Chance to be read: a segment of size s is read on about s/30 of respins per pointer if you do not steer. With steering, the player decides, so the damage numbers are set for the reads that actually occur.

| id (working) | Size | Phase | Effect (placeholder) | Mirrors | Removal | What ignoring it costs / what removal costs |
|---|---|---|---|---|---|---|
| Leech Bite | 6 | Offense | 6 dmg (FLAT, ×factor) per read, persists | Shim | Solvent, Cleanse, Scrape | Chip damage; dodging costs slice choice |
| Rot | 4 | Offense | 2 dmg × your CORRUPTED slices (min 1), separate hits. This replaces `corrupted_damage_per_major`. | Genome IV | Cleanse removes it, or clear your CORRUPTED slices | Rises with your corruption, so cleansing is double duty |
| Snare Mine | 4 | Offense | 12 dmg **once**, then consumed | Overflow | Consumed on read; Solvent | Predictable: read it once and it is gone, or dodge it for several turns |
| Cutter | 3 | Offense | 5 dmg, **pierce** (ignores BLOCK and SHIELD; SANDBOX still stops it) | Adrenaline | Solvent, Scrape | Forces SANDBOX or steering instead of BLOCK |
| Dampener | 6 | Modifier | Your slice's output −50% on read | boss defense | Solvent, Scrape, Cleanse | You give up your biggest slice's tick range |
| Tithe | 5 | Modifier | The boss heals 25% of the damage your resolve deals (PERCENT of damage) | Hotfix | Solvent, Scrape | Costs tempo; cutting it short means landing off-slice |
| Ward Leak | 5 | Defensive | Boss gains BLOCK 10 (FLAT, ×factor) before your offense | Defrag | Solvent, Cleanse | Costs about 10 damage, which you recover only by dodging |
| Static | 4 | Status | Applies OUTPUT_DOWN ×1 to the slice read; persists | Infect | Encrypt on that slice absorbs it; Solvent | Stacks if you keep landing there |
| Sour Cut | 3 | Status | Applies CORRUPTED to the slice read (RAM ×2 on it, R9); persists | Infect (CORRUPTED) | Solvent, Scrape | Your best slice becomes expensive to use |
| Stripper | 4 | Status | **Removes** ENCRYPTED / OVERCLOCKED from the slice read; consumed | Cleanse | Solvent, Scrape | Punishes Encrypt prep; read it on a bare slice to waste it |
| Downshift | 3 | Status | Applies TIER_DOWN ×1 to the slice read (Perfect → Good) | Infect (TIER_DOWN) | Cleanse, Solvent | Wipes the Perfect bonus on that slice |
| Blank | 3 | Modifier | The slice under it resolves as NULL | Null | Scrape (odd size), Solvent | A tiny segment that costs a whole turn if read |
| Tollbooth | 6 | ON_NUDGE listener (N6) | Your free nudge costs 1 RAM while it is attached; time-limited, 4 turns | Priority drain | Solvent, time | You choose between nudging and RAM |
| Splice | 4 | Offense | When read, latches a new Leech Bite beside it (if room); never loops past the cap | Trojan | Solvent, Scrape | Grows the ring if you keep reading it |
| Seize | 5 | Modifier | When read, disables the inner-ring segment under the pointer for that resolve and rotates the inner ring one segment | threat to the inner ring | Solvent, Cleanse | Forces you to resolve without the inner modifier |

This table has 15 rows; Splice and Seize can be cut if the cast needs trimming. Required coverage:
- Status apply or remove: Static, Sour Cut, Stripper, Downshift.
- Reduce damage to the boss: Dampener, Tithe, Ward Leak.
- Damage the player: Leech Bite, Rot, Snare Mine, Cutter.
- Pure threat to the wheel and inner ring: Seize (Blank threatens a slice's turn).

**Scrape (general rule).** If the pointer reads a segment's **centre tick** (odd sizes only) and the slice landing is PERFECT, the segment does not fire and is removed.
- Segments are placed so their centre is at least 2 ticks from the slice's centre. You must trade Perfect precision against scraping, or settle for Good and let it fire.
- Even-sized segments have no centre and cannot be scraped. These are the stickier ones (Leech Bite 6, Dampener 6, Tollbooth 6).

## 3. Placement and removal

**Sources**
- **Enemy slice rider:** a new effect `LATCH_PARASITE` carries a `segment_id` and a placement rule:
  - `UNDER_ENEMY_HIT`: centred (offset by authored ticks) on the tick the player's pointer read this resolve. Deterministic given the resolve.
  - `ON_SLOT(n)`: covers a fixed slice of the player's wheel.
  - `ON_BEST`: the player's highest-output slice (ties by lowest index).
- **Boss phase entry:** `on_enter_latches`, e.g. Meridian P2 latches a Dampener every other turn (max 2), and the Genome Core's Code Blue hub rule can latch Rot.
- **Satellites:** their latches are **tethered**. If the satellite dies, its parasites disappear, which gives players a clear target.
- **Events:** a choice can latch a parasite as the cost of a deal ("a deal gone wrong"). It lasts the next N fights or until removed.
- **Raids:** no. Raids are not wheel content, per pillar 4.

**Caps and stacking**
- 3 segments and 14 ticks total.
- At most 2 segments of the same id.
- Replacing the oldest is the full-ring rule.
- Segments with `lifetime_turns` (Tollbooth 4, Dampener 5) count down at start of turn.

**Phase change:** parasites **persist**. A boss with a cleansing phase uses `cleanse_on_enter: PLAYER` (R6). Parasites live on your wheel, not on the boss's slices, so there is nothing to remap. Persistence keeps pressure continuous and makes cleansing a deliberate boss mechanic, consistent with statuses surviving. Tethered parasites still die with their satellite.

**Between fights:** the ring is cleared at combat end, unless an event authors a "carry" parasite.

## 4. Counterplay and teaching

**New hooks (descriptive names)**
1. **Solvent (card):** 1 RAM, removes the parasite under your pointer. A cheap general answer.
2. **Slide (card):** 2 RAM, shifts the parasite ring ±3 ticks relative to the wheel (`ring_offset`). It moves danger off a landing without moving the slices.
3. **Insulated (Firmware):** parasites read on this slice at Perfect are Scraped regardless of centre tick. This resolves the odd/even rule.
4. **Antibody (Firmware):** when a parasite fires on this slice, gain 3 BLOCK.
5. **Bounty (Daemon):** each parasite removed (Scrape, Solvent, Cleanse): +1 RAM.
6. **Heavy Nudge (Firmware or Daemon):** your nudges also drag the ring 1 tick opposite.

Existing cards also apply: Cleanse removes any parasite or CORRUPTED, Encrypt blocks Static, and the Snap-to-centre family makes Scrape reliable.

**Teaching**
- **L1:** no ring.
- **L2:** one normal enemy latches a lone Leech Bite on a Null edge with `lifetime_turns` 3. Land elsewhere and nothing happens.
- **L3:** Dampener and Static, one at a time, with Solvent offered in the Rack or shop pool.
- **L5–6:** combinations: Tollbooth + Dampener, Seize + Blank. Elites cap at 2 live parasites.

**Bosses**
- **Meridian mini-boss P2 (Packages):** Dampener + 2 RAM drain.
- **Halcyon:** Static as the Citation analogue (OUTPUT_DOWN ×1, stacking to ×3).
- **Genome Core P2–P4:** Rot as the Parasite-ring expression of "your corruption is your damage".
- **REBEL_CELL Override:** Blank on the Perfect-hooked slice.
- **Orbital:** satellite-tethered Splice, with the satellite as the kill target.

## 5. Existing PARASITE migration
- `RC.Status.PARASITE` (ordinal 4) is kept for saves. On load it becomes **OUTPUT_DOWN ×2** (N8 migration). It is a status, not a ring parasite.
- `parasite_pulse` and `leech_worm` keep their cards and now apply OUTPUT_DOWN ×2 to an enemy slice. The slice's output is cut by about half, as today. Descriptions change to say "OUTPUT_DOWN ×2". They are the player's anti-Firmware, not ring parasites.
- Botnet's Perfect Trojan applies the same OUTPUT_DOWN ×2 on an enemy slice. Its drone-dock text goes. Botnet's player-facing name should say "Output Down" rather than "Parasite" so the two concepts stay separate.
- Enemy Citation and any slice that applies PARASITE to the player becomes OUTPUT_DOWN ×1 (a status), unless a corporation wants it as a ring segment (Halcyon Static, above). The usage report shows 0 enemies currently apply a status, so this is a data-only rename check: 3 slices and 8 cards.

## 6. Data and systems

**Resources**
- **`ParasiteSegmentData`:**
  - `id`, `size_ticks`, `phase` (MODIFIER / DEFENSIVE / OFFENSIVE / STATUS)
  - `trigger` (ON_READ / ON_NUDGE / ON_CARD_PLAYED / ON_TURN_START)
  - `effects: Array[EffectData]`
  - `consume_on_fire`, `lifetime_turns`, `pierce`, `min_scrape_tier`, `glyph`, `colour`
- **`WheelState`:** `parasites: Array[{id, start_tick, age, source_uid, tether_uid}]` and `ring_offset`. It is saved and undo-clean. Save version bump alongside N8.
- **New effect types:** `LATCH_PARASITE`, `REMOVE_PARASITE`.
- **New `EffectTarget`:** `PLAYER` (anti-slice damage to the player).
- **Modifier hook:** `OUTGOING_DAMAGE_MULT` / `BOSS_BLOCK` / `BOSS_HEAL`, applied in `_collect_resolutions`.

**System numbers**
- This is N10 (L), depending on N1 (amount modes), N8 (×N stacks) and N9 (OUTPUT_DOWN, TIER_DOWN, corruption as RAM).
- Tollbooth also needs N6 (an ON_NUDGE listener).
- Seize needs the inner ring's modifier path (G1 redesign).
- Build order: N1 → N8 → N9 → N10 core (state, read, preview, 3 types) → remaining types → UI after the inner-ring redesign.

**Data-only fallback** (before N10)
- Leech Bite, Static, Sour Cut and Downshift can be enemy slice riders on existing slices using `APPLY_STATUS`.
- Dampener and Tithe are not expressible, since they need to modify the player's resolution.
- There is no ring, so the dodge-by-ticks puzzle is lost. This is acceptable only as a stop-gap.

**Tests**
- Segment read at tick boundaries; ring bound to wheel through spin, Flip (mirrored spans), respin and nudge.
- Overlap shifting, cap and oldest-replacement; placement determinism per rule.
- Preview chips equal the result for each type, with BLOCK, SHIELD and SANDBOX applied (and pierce for Cutter).
- Undo and redo within a turn keep the ring identical.
- Scrape: odd sizes only, PERFECT only, no fire.
- Tethered parasites vanish when their satellite dies.
- Phase change keeps parasites; `cleanse_on_enter: PLAYER` clears them.
- Save and load round trip; PARASITE migration to OUTPUT_DOWN ×2.
- Parasite damage uses the tier damage factor; percent heals are not rescaled.

## 7. Open questions

Q: Should Dampener and Tithe be one segment ("tax") to keep the roster smaller, with the percent as the dial? Splitting them gives different counters (Tithe punishes damage dealt, Dampener punishes the slice).

Q: Is the ring bound to the wheel (proposed) or to the pointer's frame (Q10)? The wheel-bound frame is what makes dodging by landing possible, but it makes Flip a strong anti-parasite tool.

Q: Should parasite damage be blockable by default (proposed), with only Cutter piercing, or should some always bypass BLOCK?

Q: Should the player ever place parasites on an enemy wheel (Botnet's mirror), or stay with statuses only?

Q: Does Heat (HUNTED band) add a free Leech Bite on the first enemy hit each fight, or does Heat stay out of the ring?
