<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TbrR3EWox75MLhXeXePGqK, custom_id inner__b; status ok; tokens in 19028 cache-write 0 cache-read 32585 out 9347; cost $0.069. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# inner_ring concept B: Result Plate (a tier-gated module rack beside the wheel)

## 1. Pitch and effect on a spin

**Pitch:** the wheel stays a clean disc, and the inner ring becomes a 3-bay rack under it. The precision of each landing powers that rack up, left to right.

**Plain language:** the outer slice decides what happens, and the plate decides what extra happens. A WEAK landing powers only bay 1. A GOOD landing powers bays 1–2. A PERFECT landing powers all three. Each powered bay fires its module: ×2, Pierce, Echo and so on. Every nudge that improves your tier therefore buys more than the outer slice's 0.5× to 1.0×. The player moves the modules between bays to choose which effect needs which precision.

## 2. Anatomy

**Elements:**
- **Three bays** in a horizontal strip directly under the disc, as wide as the disc.
- **Bay 1** is the "any landing" bay (WEAK+). **Bay 2** needs GOOD+. **Bay 3** needs PERFECT.
- **Conduit wire:** a thin line runs from the pointer tick on the rim down to the plate. It is the visual link and carries the result.
- **Bay states:** DARK (not reached), LIT (fires), LOCKED (a latch overlay from an enemy), EMPTY (a blank module, a dark socket).

**Picture for the artist:**
- **Bay shape:** a chunky rounded-rectangle cartridge, about 1/3 of the disc width and 16 % of its diameter tall. It holds one large flat glyph, filled and no thinner than 8 % of the bay height.
- **Tier header:** a notch bar above each bay. Bay 1 has one notch in the WEAK colour. Bay 2 has two notches in the GOOD colour. Bay 3 has three notches with a star in the PERFECT colour. The three headers are the same three tier colours already used on the wheel.
- **Module colour by role:**

| Role | Colour |
|---|---|
| Damage amp (×2) | amber |
| Penetration (Pierce) | white-cyan |
| Duplication (Echo) | magenta |
| Status applied to the target (Corrupt) | violet |
| Tempo (Accelerator, Anchor) | green |
| Blank | grey outline |

- **Motion on resolve:**
  1. A pulse runs down the wire (~120 ms).
  2. Bays light left to right, 60 ms apart, up to the tier reached. Each lit bay punches 8 % larger and flashes.
  3. Unreached bays drop to 35 % brightness and stay dark.
- **Idle:** the plate sits dim. During planning, the previewed tier at the pointer shows the same lit and dark states statically. This is the preview.
- **Twin Pointer or multiple pointers:** two stacked lamp rows (A and B), each a different tag colour, over the same three modules. Each pointer has its own wire.
- **Enemy plates** (the schema already allows them) use the same layout at half scale, above the enemy wheel.

**Three-metre test:** the plate has three large glyphs and a binary lit/dark state per glyph. The reader needs only two reads: how many bays are lit, and which colour. "Two bays lit, amber and white" means GOOD with ×2 and Pierce. No ticks or small text are involved.

## 3. Manipulation

- **Nudge, INNER scope** (existing `RingScope.INNER`): rotates the module order one bay, cyclically: [1,2,3] → [3,1,2]. It costs the same as any nudge: the first nudge of the turn is free and shared, then 1 RAM. This replaces the old "rotate the inner ring one tick" action.
- **Spin N on INNER scope:** rotates N bays mod 3. Cards keep their data.
- **Flip (whole wheel):** also mirrors the plate, bay 1 ↔ bay 3. Flip is already a "reverse the order" action.
- **Respin:** never touches the plate. This removes the random inner-ring rotation. The plate is deterministic player-authored state, and the random element lives only in the wheel.
- **Firmware:**
  - "Calibrated" (R11) raises sub-tick tiers, which lights more bays on the same landing.
  - A new Firmware, "Bay Mod", can retune a bay's gate by one tier.
  - The old G1 idea of moving ×2 to Firmware stays possible as a data swap.
- **Class abilities:** Anchor stays a module. The Rigger hub's free-nudge economy now also pays for plate rotations.
- **Preview:** hovering a nudge, card or Flip shows ghost glyphs sliding to their new bays. The unlocked bays' lamps update for the previewed tier. The HP chips show the final number, including every lit module.
- **Undo:** the plate order is part of the combat snapshot, so rewind restores it.

## 4. Rules

**Resolution order for one pointer:**
1. The wheel reads the landing tick. The sub-tick map (R11) gives the base tier.
2. Statuses adjust it: TIER_DOWN lowers the tier per stack, then OUTPUT_DOWN scales output. The plate reads the **effective** tier, so TIER_DOWN also darkens bays. This is the anti-Firmware status doing its job.
3. Lit bays = those whose gate ≤ the effective tier (default gates WEAK / GOOD / PERFECT).
4. The outer slice resolves at the tier multiplier (WEAK 0.5×).
5. Lit modules apply:
   - output multipliers multiply (in practice a ring holds one);
   - pierce is an OR;
   - the triggered effects (Corrupt, Accelerator, Anchor) fire in bay order 1 → 3.
6. Echo then re-triggers the outer slice at 0.5×. The plate is not re-read on the echo, so there is no recursion.
7. The class Perfect hook fires after the plate, as today.

**The plate never modifies slice choice.** It adds to the result and never changes which slice resolves.

**Segment mapping:**

| Segment | Verdict |
|---|---|
| x2 | **Keep** |
| Pierce | **Keep** |
| Blank | **Keep** (a dark bay) |
| Echo | **Keep** |
| Anchor | **Keep.** Its own `min_tier` becomes redundant when it sits in bay 3 and is fixed to bay gating. |
| Accelerator | **Keep**, shown as a charge pip on the HUD for next turn. |
| Corrupt | **Change** to apply OUTPUT_DOWN ×1 to the target slice. R9 makes CORRUPTED a RAM debuff and its effect on enemy wheels is undefined (Q:). |

**Satellites:** the plate applies only to the host wheel's resolution. Drones trigger with their host as today, but they get no plate bonuses and no echo. Satellites have no plate.

**Parasite ring:** the plate sits off the wheel face, so it never collides with the rim ring. Enemies can act on the plate through a new status, BAY_LOCKED: an anti-Firmware status that switches one bay off for N turns. Cleanse removes it. A parasite segment read by your pointer can latch a bay lock. This gives Halcyon and Orbital a clean way to hit your build without damaging you.

## 5. Class mapping

Each class keeps its Rank 1 three modules. The default left-to-right order puts the signature module where the class's Perfect fantasy lives.

| Class | Rank 1 plate (bay 1 / 2 / 3) | Identity |
|---|---|---|
| Breaker | ×2 / Pierce / — | Always doubled, Pierce at GOOD+; bay 3 is free for a Rank 3 swap |
| Wrecker | same as Breaker | Heavy Perfect hook; the plate is the same |
| Ghost | Pierce / ×2 / Echo | Hub freeze and resistance-strip stay in the hub; Echo only on a Perfect |
| Phantom | same as Ghost | |
| Rigger | Accelerator / ×2 / Echo | The nudge economy feeds plate rotation |
| Overclocker | same as Rigger | |
| Botnet | Echo / Corrupt / ×2 | ×2 at Perfect only, matching the Trojan Perfect |
| Hivemind | same as Botnet | |

**Rank 3 swap:** at HQ or in the loadout, the player replaces any module in any bay from the pool: ×2, Pierce, Corrupt, Anchor, Accelerator, Echo. They also set the **permanent starting order** (the rotation per fight starts there). The in-fight rotation is a new tactic that is not available before Rank 3's order setting. Rank 1 installs the plate with the class modules. Ranks 0–1 show the plate dark and empty so the unlock is visible.

## 6. Worked example

**Setup:** Breaker with Rank 1 plate [×2 | Pierce | —]. Overflow base 14. Target: an enemy with BLOCK 6. Hub: Perfect resolves the slice twice.

1. Respin lands WEAK (offset −2). Bay 1 is lit. The preview: 14 × 0.5 = 7, ×2 = 14, blocked 6, **8 damage**.
2. Free nudge → offset −1 = GOOD. Bays 1 and 2 are lit. Outer 14 × 1.0 × 2 = 28, Pierce ignores block: **28**.
3. 1 RAM (3 → 2) for a second nudge → PERFECT. Bay 3 is blank. Overflow resolves twice: 28 × 2 = **56**.
4. Alternative: spend the free nudge to rotate the plate → [Blank | ×2 | Pierce]. At GOOD, ×2 is lit but Pierce is not. The preview shows 28 less 6 block = 22. This is the trade-off.
5. The player rewinds, restores the plate, and resolves at PERFECT for 56.

## 7. Data and systems

- **`InnerRingData`:** keep `segments` (3). Add `bay_gates: PackedInt32Array = [0, 1, 2]` (a `PrecisionTier` per bay).
- **`RingSegmentData`:** keep all fields. Add `role` (enum for colour, e.g. AMP, PIERCE, DUP, STATUS, TEMPO, BLANK) and `icon` (glyph id).
- **`WheelData`:** unchanged. Rotation state on `WheelState` becomes a bay offset 0–2. Saves load the old tick offset modulo 3.
- **New status:** BAY_LOCKED. This is "NEW: bay lock" in the N8/N9 family. It can fall back to a plain duration status without stacks.
- **Resolver:** replace the tick-to-segment lookup with the tier-to-bay lookup. This is ~M inside `combat_resolver._resolve_pointer` and the preview.
- **UI:** new "plate" widget, wire effect, and ghost-slide preview. **NEW: Result Plate (M–L)**, mostly UI.
- **Dependencies:**
  - N12, for sub-tick tiers.
  - N9, for TIER_DOWN and OUTPUT_DOWN.
  - N10, for the parasite bay-lock effect.
- **Content migration:** the segment `.tres` files and ring `.tres` files are unchanged. Only the rotation int in saves changes. No re-authoring is needed.
- **Fallback without N12:** the plate still works on 5-tick slices (Perfect only at d = 0). There is no data-only fallback for the plate UI itself.

## 8. Risks and cost against the other concepts

**Risks:**
- The plate costs screen space and detaches the ring from the wheel. The wire and lamp pulse are the mitigation.
- Perfect-only bays are dead weight on slices without a Perfect (4-tick or 6-tick slices). The loadout screen must show which slices can light bay 3.
- Stacking: if several multiplier modules become lit together, damage compounds. Cap multipliers at one per ring, or add them rather than multiply them.
- The old "rotate the ring to line up" spatial fantasy is lost. Respin no longer randomizes the ring.
- Rank 3 swap choice becomes bay position, a pure planning decision with no skill element.

**Against the two other concepts I can imagine:**
- **A: on-face dial.** Better spatial coupling and no extra screen space, but it hurts legibility, which is the problem we are solving.
- **C: a persistent chain or combo counter.** Richer play across turns, but harder to preview and a much bigger rules cost.
- **B** is the cheapest to read, the most precision-forward (it ties directly to PERFECT/GOOD/WEAK), and the cleanest with R11 and the Parasite ring. It gives up spatial feel and adds an M–L UI build.

**Q:**
- Q: Should CORRUPTED on enemy wheels exist at all, or does Corrupt become OUTPUT_DOWN permanently?
- Q: Should Rank 3 let players choose the gates (WEAK/GOOD/PERFECT order), or are the three gates fixed?
- Q: Should module multipliers multiply or add when several are lit?
- Q: Should BAY_LOCKED be a status that lasts N turns, or a parasite effect that lasts as long as its segment stays latched?
- Q: Should enemy plates be shown at all, or hidden unless an Exploit reveals them?
