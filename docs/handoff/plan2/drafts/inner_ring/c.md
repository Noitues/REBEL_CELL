<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TbrR3EWox75MLhXeXePGqK, custom_id inner__c; status ok; tokens in 19034 cache-write 0 cache-read 32585 out 4111; cost $0.043. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# inner_ring concept C: Needle Riders

## 1. Pitch and effect on a spin

**Pitch:** The inner ring stops being a spinning disc. It becomes a set of **Riders**: small modifier tabs clipped to the pointer (needle) and to tick-quality bands, so the modifier follows where you land and how well.

**Effect on the outcome of a spin:** Nothing spins on its own any more. The outer slice still decides the action. Each Rider adds a rule to that action: x2, pierce, echo, and so on. Which Rider fires depends on the landing tier at the pointer (Perfect, Good or WEAK) and on which pointer read the slice. Landing precisely is how you choose the modifier.

## 2. Anatomy

- **Riders:** 3 slots per wheel, each tied to a landing tier. Slot **P** is Perfect, slot **G** is Good, slot **W** is WEAK. Each slot holds one segment or is blank.
  - This replaces today's 3 rotating segments of 10 ticks.
  - A slot is either LIVE (this turn's landing tier matches it) or DORMANT.
- **Needle tab:** each pointer has a small collar around its needle that shows the glyph of the slot its current landing would fire. The preview is the collar glyph.
  - If the slice has no Rider for that tier, the collar is a hollow ring.
- **Tier ladder on the rim:** a thin 3-step ladder at the outer rim shows P/G/W as a gold diamond, a white dot and a grey dash.
  - It sits beside each pointer, not on a disc.
  - Role colours match the Rider kinds: amber for power (x2, echo), cyan for evasion or targeting (pierce, anchor), magenta for status (corrupt), green for tempo (accelerator).
- **Motion:**
  - The LIVE slot pulses.
  - When the landing changes (nudge or spin), the collar glyph slides one step along the ladder, 150 ms.
  - Nothing else moves.
- **Multiple pointers:** each needle has its own collar. Each collar reads that needle's landing tier, so uneven needles give different Riders at once.
- **Variable slice sizes (R11):** the collar reads the sub-tick quality map.
  - A 4-tick slice has no P step, so its ladder shows only G and W.
  - Calibrated Firmware turns the P step on.
- **Three-metre test:** the viewer sees one big glyph at each needle and a gold or white or grey pip beside it. There are no small segments on a disc, so there is nothing to read while rotating.
  - The failure mode is two close needles whose collars overlap. Collars stack vertically, ordered by needle.

## 3. Manipulation

- **Nudge or spin:** changes the landing tier, and so which Rider fires. The collar updates live. It is free information, with no new cost.
- **Swap Riders between P, G and W slots:**
  - At HQ only, on the loadout screen. It costs nothing in a run and is not a priority.
  - One in-run option: a card, "Retune", swaps two Riders for 1 RAM. It is a Rank 3 card and optional.
- **Firmware:** a new socket type, a Rider socket. Calibrated Firmware raises the tier map, so more landings read P. This is the strongest lever and it is data-only on N12.
- **Class abilities:** hub Perfect hooks stay as they are. They fire after the P Rider.
- **Anchor and the free action:** none new.
- **Preview:** the existing result chips include the Rider effect, with a collar glyph tooltip.
- **Undo:** nothing persistent exists besides slot contents, so undo is trivial. Rider state is a pure function of landing and loadout.

## 4. Rules

**Resolution order for one pointer:**
1. Read the landing: slice, tier (R11 sub-tick map), pointer index.
2. Outer slice base output, with the tier multiplier (WEAK 0.5) and status modifiers (OUTPUT_DOWN, TIER_DOWN).
   - TIER_DOWN lowers the tier before the Rider lookup, so it can switch off a P Rider. This is the anti-firmware hook.
3. Look up the Rider for the final tier. Apply `output_multiplier` and `pierce`.
4. Defensive pass, then offensive pass (GDD 2.2 order unchanged).
5. Run the Rider's `triggered_effects`.
6. Run the hub Perfect hook, if it applies.

**Segment mapping:**

| Segment | Verdict | New behaviour |
|---|---|---|
| x2 | Keep | Slot-bound. Strongest in P. In G it is a power Rider; in W it buys back the 0.5×. |
| Pierce | Keep | Same, any slot. |
| Echo | Keep | Retrigger at 0.5×, slot-bound. |
| Corrupt | Keep | Applies CORRUPTED to the target slice. CORRUPTED is now a RAM debuff (R9), so it is a tax Rider. |
| Anchor | Change | Skip the respin only when it fires from slot P. Otherwise it is identical. |
| Accelerator | Change | It is a tempo Rider. It fires from any slot but only doubles nudge cards next turn. |
| Blank | Keep | An empty slot. |

**Satellites:** a satellite has no Riders of its own, since it has no ring. It reads the host's collar, because it docks on a slice. A guard hit by an attack takes the Rider effect like any pointer hit. Pierce does not bypass satellites (GDD 2.7 and R12).

**Parasite ring:** a parasite is an anti-Rider. It can sit on a tier slot and replace a Rider with its own effect, e.g. "your G Rider is blanked".
- It is read on the same collar, in red, so you see which Rider is jammed.
- It is placed by an enemy, so it takes a Rider slot and no new geometry.
- N10 stays L, but its inner-ring UI cost drops because the collar is already the display.

**Enemies:** enemy needles have collars too. An enemy Rider is an enemy modifier, e.g. a boss with Pierce in P and Echo in G.
- This uses `inner_ring`, which the schema already provides and no enemy uses yet.
- It makes "only one needle can be Perfect" matter: the Perfect needle fires the P Rider and the others fire G or W.

## 5. Class mapping

| Class | Rank 1 | Today's ring | New P / G / W | Rank 3 swap |
|---|---|---|---|---|
| Breaker | Rank 1 | x2 / Pierce / blank | P: x2, G: Pierce, W: blank | Swap any Rider: Corrupt, Anchor, Accelerator or Echo |
| Wrecker | Rank 1 | Breaker's | P: x2, G: Pierce, W: blank | Same swap options |
| Ghost | Rank 1 | Pierce / x2 / Echo | P: Pierce, G: x2, W: Echo | Same |
| Phantom | Rank 1 | Ghost's | P: Pierce, G: x2, W: Echo | Same |
| Rigger | Rank 1 | Accelerator / x2 / Echo | P: x2, G: Echo, W: Accelerator | Same |
| Overclocker | Rank 1 | Rigger's | P: x2, G: Echo, W: Accelerator | Same |
| Botnet | Rank 1 | Echo / Corrupt / x2 | P: x2, G: Corrupt, W: Echo | Same |
| Hivemind | Rank 1 | Botnet's | P: x2, G: Corrupt, W: Echo | Same |

- **Identity:** each class keeps its three segments. I assign each to a tier slot by its identity, with x2 on P by default for the damage classes. The Ghost's freeze identity stays in its hub hook.
- **Rank 3 swap:** it becomes a **Rider retune**. Pick one of the 3 slots and replace its Rider from the pool (Corrupt, Anchor, Accelerator, Echo, plus the others).
- **Rank 1 and Rank 3 gates are unchanged.** Rank 1 installs the 3 slots and Rank 3 unlocks the retune.

## 6. Worked example

A Breaker has one needle, 4 RAM and a Shim 8 slice. Its hub is breaker_core and its Riders are P: x2, G: Pierce, W: blank.

- The respin lands the needle on the Shim slice at offset +1, which is GOOD.
- The collar shows a cyan Pierce glyph. The enemy has Block 6.
- Preview: 8 × 1.0 = 8 damage, pierced, so 8 to the enemy HP. The chip says "8 PIERCE".
- Spending 1 RAM nudges the needle to offset 0, which is PERFECT. The collar slides to the gold x2.
- Preview: 8 × 2 = 16. The Perfect hook fires after the Rider, resolving the slice again.
  - Second resolution: 16 more.
  - Block 6 absorbs 6 of the first hit, so 10 + 16 = 26.
- The player chooses between the nudge (26 damage, −1 RAM) and keeping the RAM (8 pierced damage).
- If an enemy TIER_DOWN is on the slice, the Perfect reads as Good and the collar goes back to Pierce. The preview shows this before commit.

## 7. Data and systems

- **`InnerRingData`:**
  - `segments` is replaced by `rider_perfect`, `rider_good` and `rider_weak` (each a `RingSegmentData`).
  - `validate` checks 3 slots.
- **`RingSegmentData`:** add `min_tier`. `output_multiplier`, `pierce` and `triggered_effects` stay.
- **`WheelData`:** no change.
- **Parasite ring:** `ParasiteSegmentData` gets `jams_rider_tier` (N10).
- **Dependencies and size:**
  - N11 (any-tick pointers) and N12 (tick quality) are both required.
  - Tier lookup needs `combat_resolver._resolve_pointer`, plus a collar HUD node. Size **M**.
  - N9 (TIER_DOWN) is needed for the anti-firmware interplay.
- **Migration:** the 4 `content/rings/*.tres` files are rewritten to the slot form, and the 7 segment files gain `min_tier`. Saves keep their segments as an ordered list, mapped to P/G/W in order. This is small.
- **Data-only fallback:** none for the HUD collar. A fallback is to keep rotating segments and just add `min_tier` gating. That is weaker.

## 8. Risks, comparison and open questions

**Risks:**
- Riders no longer need a manipulation loop of their own, so players have fewer decisions on the ring. Some will say the ring is no longer a puzzle.
- Rider choice is bundled with tier skill, so a skilled player always hits P and the G and W Riders matter little.
  - Mitigation: weak classes get strong G Riders, and enemy TIER_DOWN pushes landings down.
- Collars on 3+ needles crowd the face.

**Against the other two concepts I can imagine:**
- A **fixed track on the rim** with static Riders is simpler to draw but loses the pointer coupling.
- A **separate rotating mini-disc** keeps the skill expression but fails the 3-metre test, which is the original G1 complaint.
- Needle Riders trade skill expression for legibility and for tight R11 and R9 fit.

**Q:**
- Should P Riders always include an x2-style multiplier, or can classes be flexible?
- Should W Riders buff WEAK landings, making low-precision play viable?
- Does the Rank 3 retune apply to the slot or to the Rider?
- Can an enemy parasite replace a Rider, or only jam it for one turn?
- Is the Retune card needed, or is the HQ swap alone enough?
