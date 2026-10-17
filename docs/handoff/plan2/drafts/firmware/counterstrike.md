<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__counterstrike; status ok; tokens in 2569 cache-write 0 cache-read 32585 out 1429; cost $0.013. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: counterstrike

**Verdict:** CHANGE

1. **What it does today:** A DETOUR slice also deals 4 flat damage to the pointer target (trigger 5 = ON_SLICE_TRIGGER, min_tier WEAK). It only fits DETOUR, so it suits Ghost (2 Detour... actually 1 Detour slice) and any build that picked up a Detour slice. Role: turns the evade slice into a mixed defense/offense slice. Today it's a mild damage rider on a dead-ish slice.

2. **Under the new rules:**
   - **Name and rules drift.** DETOUR becomes SANDBOX (R13): it negates one whole attack, which is every hit of one resolution. The chip's text and its allowed type must follow the rename. The enum int stays 3.
   - **Pointer-rule scaling.** DEAL_DAMAGE on POINTER_TARGET hits every pointer, so against a 2-needle boss (Genome Core P3–P4) it lands twice. That is fine and readable.
   - **Size problems.** On a 2-tick slice (G G) or a 4-tick slice (W G G W) the chip fires on WEAK landings, so a WEAK landing still deals the full 4 and 4 damage ignores quality. This makes narrow slices free value. It is weak design: precision should matter.
   - **Flat 4 vs tier scaling.** Enemy HP is banded by tier, so a flat 4 is worth less at T4 (~60 HP) than at T1 (~32). It needs to scale with the slice's output, not stay flat.
   - **Pierce and bodyguards.** Pierce ignores BLOCK and SHIELD but not SANDBOX. Counterstrike gives the player a reason to land SANDBOX, since the slice still deals damage when the enemy hit is negated.
   - **Listener interplay.** Clawback-style listeners punish Perfects. Counterstrike pays on any landing, so it is the anti-listener pick.
   - **Statuses.** OUTPUT_DOWN reduces the damage (−25 % per stack), but not the negate. That is correct anti-firmware behavior. TIER_DOWN pushes a Perfect to Good and cuts the Perfect bonus below. CORRUPTED doubles the RAM cost of cards and nudges that act on this slice, so a corrupted Counterstrike slice is expensive to steer onto.
   - **No loops.** There is no RAM or heal return, so no infinite loop. It is not dominant, since a SANDBOX slice is rarely the damage dealer.

3. **Proposed spec:**
   - Description: "SANDBOX slice also deals 4 damage to the pointer target; ×2 on a Perfect. Deals nothing on a WEAK landing."
   - Rarity 1 (uncommon). Cycle cost 110 (unchanged).
   - allowed_slice_types: [3] (the former DETOUR, now displayed as SANDBOX).
   - Triggered effects: one DEAL_DAMAGE (FLAT, 4, target 3) at min_tier GOOD, and a second DEAL_DAMAGE (FLAT, 4) at min_tier PERFECT, so a Perfect deals 8 in total. Flat amounts are not enemy amounts, so the tier damage factor doesn't apply. This is a player chip.
   - On the slice: a small crossed-blade glyph on the socket. The preview chip reads "+4 / +8 counter".

4. **Data:** Edit `counterstrike.tres`: raise min_tier on te0 to 1 (GOOD), add te1 with min_tier 2 and a second effect. Update the description. The display rename depends on N14 (a strings change only). `amount_mode` (N1) is only needed if a PERCENT variant is wanted, which it isn't. Size S, data only.

5. **Q:**
   - Does the counter still fire if the SANDBOX absorbs nothing (the enemy has no attack this turn)? I propose yes: the slice triggers on its own.
   - Should the counter damage be blocked by an enemy's BLOCK or SHIELD, or should it pierce? I propose it does not pierce, so it stays a small chip.
