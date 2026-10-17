<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TbrR3EWox75MLhXeXePGqK, custom_id inner__a; status ok; tokens in 18974 cache-write 32585 cache-read 0 out 9620; cost $0.108. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# inner_ring concept A: Detent Lens

## 1. Pitch and effect on a spin

**Pitch.** Keep the 3-segment concentric ring, but make it a chunky 3-state "lens" with fixed 10-tick detents. Each segment is one loud colour and one huge glyph, and a bright beam ties the active segment to the outer slice that resolves with it. Rotating the ring is a plain 1-nudge choice of "which modifier do I fire this turn".

**What it does to a spin, in plain language.** The outer slice decides what happens and how precisely. The ring segment sitting under the same pointer decides how that slice is modified: doubled, pierced, echoed, weakened or tempo-shifted. The player can spend a nudge to rotate the ring so a different modifier sits under the pointer.

The smallest change that fixes G1:
- the ring only rotates in whole-segment detents;
- the active segment is made unmistakable;
- every segment states its effect in one word and one glyph.

## 2. Anatomy

**Elements**
- The ring has 3 segments of 10 ticks each (120° arcs). It is concentric inside the outer slices, between the outer ring and the hub. It has 3 rotation states (detent 0, 1, 2).
- The ring is thick, about 16 % of the wheel radius, so it holds a glyph about 3× larger than today's. The ring is visibly a *different material* from the outer slices: matte dark metal with an inset coloured lens per segment.
- The active segment is the one under any pointer. Inactive segments are dimmed to about 45 % brightness.

**Colour and glyph by role** (the glyph shape carries the meaning too, for colour-blind players)

| Role | Colour | Segments | Glyph |
|---|---|---|---|
| Amplify | orange | x2, Echo | ×2 chevron stack; a ghosted double arc for Echo |
| Break | cyan | Pierce | a spear through a shield |
| Status | magenta | Weaken (was Corrupt) | a down-arrow in a drop |
| Tempo | yellow | Anchor, Accelerator | a padlock; a double chevron |
| Empty | grey | open socket | a hollow ring |

**Motion**
- On rotate, the ring clicks over one detent in 0.15 s with a hard stop and a small overshoot. Each detent shows 3 notch ticks on the hub rim.
- At every pointer, a **reader beam** (a thin bright wedge) runs from the pointer inward through the outer slice, across the ring and to the hub. Its centre line marks the exact tick being read. The beam takes the active segment's role colour. This is the "this slice × this lens" cue.
- The ring's glyph in the beam pulses once when the preview settles.

**HUD**
- The result chip next to HP gets a second line: `[slice icon] 14 ⊕ [ring glyph] ×2 = 28`. A tooltip names the segment in plain words.
- Segments with a next-turn effect (Accelerator, Anchor) leave a **charge pip** in the hub. It is a yellow dot with the glyph, shown until spent.

**Legibility test from 3 m**
- Pass if the viewer can name, within 1 s, which segment is active at the pointer and its role colour, using only the beam colour and glyph silhouette. No text is needed.
- Pass if each of the 3 segments is distinguishable in greyscale by silhouette alone.
- Fail if two segments of one wheel share a role colour with similar silhouettes. Rule: a ring may not hold two segments of the same role. Echo and x2 are both Amplify, but the glyphs differ strongly (a doubled chevron versus a ghost arc).

## 3. Manipulation

- **Ring nudge:** the existing `RingScope.INNER` nudge, now a **detent step**. It moves the ring ±1 segment, which is ±10 ticks. It costs the same as any nudge: the first one each turn is free, then 1 RAM. The ring and the outer ring **share the one free nudge**. That is the key tension: spend it on precision or on the modifier.
- **Reach:** with 3 segments, every segment is exactly 1 nudge from any other. The player is never more than one nudge from the modifier they want. A ring nudge is also never wasted by a partial tick.
- **Whole-wheel Spin** carries the ring rigidly, as today. **Flip** mirrors the wheel and swaps the ring's visible order. **Respin** randomizes the ring to a random detent from the named wheel RNG stream, inside the same checkpoint as the outer respin.
- **Resistance:** enemy resistance applies to the ring only for Spin and Flip, because those carry it. A ring nudge is a one-detent move and is **not absorbed** by resistance. Reason: resistance is a tax on tick-precision, and the ring has none.
- **Firmware:** a new "Calibrated" Firmware (R11) stays on the outer slice. It never sockets into the ring, so Firmware and ring remain separate layers.
- **Class abilities:** Ghost's free resistance-ignoring nudge may be spent on the ring, and Rigger's free nudge refunds the same way. The Perfect hooks are unchanged.
- **Preview:** hover a ring segment or a ring-nudge button, and the beam, the chip line and the enemy HP chip all update to the result of rotating there. Ghost-previews show the alternative result as a faint chip. Preview equals result because the ring state is part of the wheel state.
- **Undo:** a ring nudge is a normal staged action, so undo restores the detent. A respin is a checkpoint, as today.

## 4. Rules

**Resolution order for one outer slice**
1. The pointer picks the outer slice and tier from the tick: Perfect (d = 0), Good (d ≤ 1), Weak (otherwise), plus any R11 override map.
2. The ring segment is read at the same pointer tick, as `floor(((tick − ring_offset) mod 30) / 10)`. The ring has **no tier of its own**. Precision is measured on the outer ring only, as in the GDD.
3. Output = base × Firmware × tier multiplier × segment `output_multiplier` × status multiplier (R8 OUTPUT_DOWN).
4. The ring segment's flags apply: pierce ignores BLOCK and SHIELD, not SANDBOX and not satellites.
5. The class Perfect hook then resolves, repeating steps 3–4.
6. `triggered_effects` fire in the status pass (statuses, charge pips).

**WEAK and x2.** WEAK (×0.5) with x2 gives ×1.0. The ring never changes the tier, so Perfect hooks cannot be faked by it.

**Segment equivalents**

| Segment | Verdict | Change |
|---|---|---|
| seg_x2 | keep | none |
| seg_pierce | keep | none |
| seg_blank | **retire** | replaced by the "open socket" state (grey), filled at Rank 3 or by an Armory item |
| seg_echo | keep | the slice triggers again at 0.5×. It repeats once per slice trigger, **not** once per Perfect-hook repetition. It reuses the same tier and ring read and does not re-trigger Echo. |
| seg_corrupt | **change → Weaken** | applies OUTPUT_DOWN ×1 (R8, N9) to the target's slice under the pointer, instead of CORRUPTED, because R9 turns CORRUPTED into a player RAM tax. The segment stays "status". |
| seg_anchor | keep | a lock charge pip shows until spent |
| seg_accelerator | keep | a visible charge pip: "next turn's nudge cards trigger twice" |

**Satellites.** The ring modifies the outer slice resolving at the pointer. If a satellite bodyguard absorbs the hit, the ring multiplier applies to the hit that lands on the satellite, and pierce still does not bypass it. Satellites have no ring (R12, fixed).

**Parasite ring.** It sits on the **outer rim**, outside the outer slices. The inner ring sits inside. They are different layers with different owners: the player's inner ring is a modifier, the enemy's parasite ring is a hostile read. Enemies cannot latch onto the inner ring. If a later pass wants to attack it, the legal move is "lock the ring" (N7 `nudge_locked` scoped to the ring), which draws a padlock over it.

**Variable slice sizes (R11).** The ring ignores slice boundaries completely. Its 10-tick arcs are independent of 3-, 4- or 7-tick outer slices. That is the whole point of making the beam the read-out: the player sees both the outer sub-tick quality and the ring segment at one line.

## 5. Class mapping

| Class | Rank 1 ring | Notes |
|---|---|---|
| Breaker | x2 / Pierce / open | open socket for Rank 3 |
| Ghost | Pierce / x2 / Echo | the free nudge can be spent on the ring |
| Rigger | Accelerator / x2 / Echo | the free-nudge refund works with ring nudges |
| Botnet | Echo / Weaken / x2 | Weaken replaces Corrupt, and it is a status, so the Parasite identity stays |
| Wrecker, Phantom, Overclocker, Hivemind | inherit their base class's ring | alternatives differ by Hub core only (decision 2026-09-24) |

**Rank 3 swap becomes "Retune":**
- At HQ or the loadout, replace **one** segment with any from the 6-segment pool.
- Segments cannot repeat on one ring, and a ring cannot hold two segments of the same role (the legibility rule).
- If a segment is removed, its place is filled by the new one in the same position.
- Rank 1 still "installs the ring", with the Breaker's third segment open. Rank 3 does not unlock position choices, because positions do not matter (every segment is 1 nudge away).

## 6. Worked example

Breaker, 60 HP. Enemy: 80 HP, BLOCK 20 (from its Defrag this turn), one pointer. The wheel is a standard 6×5-tick wheel. The player's Overflow is 14 damage. After the start-of-turn respin: the pointer reads tick 28 on the **Overflow** slice (centred on tick 0/30), offset −2 = WEAK. The ring reads **Pierce**.

- Preview now: 14 × 0.5 = 7, pierce → **7 damage**.
- Option P (precision, pierce kept): the free nudge outer +1 → tick 29, GOOD → 14 pierce. A 1 RAM nudge outer +1 → tick 30/0, **Perfect**. The hook resolves twice: 14 + 14 = **28 pierce** (block irrelevant). Cost: 1 RAM.
- Option X (modifier): the same two outer nudges (free + 1 RAM), then a ring nudge +1 detent (1 RAM) → x2. Perfect, resolving twice: each hit is 14 × 2 = 28. Hit 1 spends 20 BLOCK → 8 through, hit 2 → 28 through. **36 damage.** Cost: 2 RAM.

Total: 36 for 2 RAM versus 28 for 1 RAM. The extra RAM buys 8 damage, only because the enemy has BLOCK. Against a no-BLOCK enemy, x2 would do 56. The preview chip shows both numbers, so the choice is visible before committing. Undo restores the original reading at any time. Preview and result are equal.

## 7. Data and systems

**Changes**
- `RingSegmentData`: add `role` (enum AMPLIFY / BREAK / STATUS / TEMPO / EMPTY), `glyph_id`, `short_label` (≤ 6 characters), and `charge_text` (for Accelerator and Anchor).
- `InnerRingData`: add `detent_locked: bool = true` (the ring steps in whole segments), and `unique_roles` validation (no two segments with the same role).
- `wheel_data.gd`: no change to the schema. Runtime: the ring offset in `WheelState` moves in 10-tick steps when `detent_locked`.
- `RC`: add the `RingRole` enum.
- **Content migration:** 8 segments (retire `seg_blank` → an `open` segment; `seg_corrupt` → `seg_weaken`; the others get role and glyph) plus 4 `.tres` ring files (3 segment references each). Class files are unchanged for Rank 1.
- **Systems:**
  - Detent nudge: NEW: ring detent. The existing nudge handler gains a ring-scope step of 10. **S–M.**
  - Beam, glyphs and the HUD chip line: art and UI, `wheel_face.gd`, `ring_mods.gd`. **M.**
  - Weaken needs **N9** (OUTPUT_DOWN) and **N8** (the stack model for ×N). Fallback: Corrupt stays as the status APPLY_STATUS CORRUPTED, with no change to data.
  - A segment-lock effect (the optional "lock the ring" attack) needs **N7**. Not required for this concept.
  - Variable slice sizes (**N12**): no dependency, since the ring reads a tick, not a slice.
- **Data-only fallback:** ship only roles, glyphs, labels and the beam art (no rules change). The ring still rotates in 1-tick nudges. This fixes legibility but not manipulation.

## 8. Risks and cost against other concepts

**Risks**
- Sharing the one free nudge between the outer ring and the ring may feel punishing early, since the free nudge is the most precious thing. Mitigation: Breaker's open socket and Rigger and Ghost class tricks. If too punishing, give the ring its own free detent step.
- 3 states is shallow. It is a pick-a-lens, not a puzzle. The depth comes from interaction with blocks, shields and Perfect hooks.
- With two pointers (boss layouts), the beams must be distinguishable. Each pointer gets its own beam, so there may be two different lens segments active at once. That is correct, but the screen is busy.
- Retiring `seg_blank` changes Breaker's Rank 1 look.

**Against concepts I can imagine**
- **B (a socket per slice, "ring as Firmware"):** much deeper manipulation, but it competes with Firmware and with R11 and needs far more UI. A is a much smaller change.
- **C (a modular hangar or sub-needle that moves independently):** the richest puzzle, but the largest build and the weakest legibility from afar. A deliberately gives up depth to fix G1 first.
- A keeps all existing content and class identity, and keeps the door open to B or C later: roles and glyphs transfer to either.

**Q: The ring and the outer ring share one free nudge. Is that the right tension, or should the ring get its own free detent step each turn?**
**Q: Is "no two segments of the same role" acceptable? It forbids x2 + Echo on one ring, which a Rigger player might want.**
**Q: Should Weaken replace Corrupt (a status on the enemy slice), or should CORRUPTED stay on enemy wheels as a RAM debuff (R9 / Q3)?**
**Q: Should the ring be attackable by enemies (a lock effect) in a later pass, or stay purely player-owned?**
**Q: Should Rank 3 let the player swap two segments, since positions no longer matter, or is one swap enough?**
