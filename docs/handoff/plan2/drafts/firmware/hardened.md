<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__hardened; status ok; tokens in 2273 cache-write 0 cache-read 32585 out 1305; cost $0.012. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: hardened

**Verdict:** CHANGE

1. **What it does today:** the slice is permanently ENCRYPTED (`permanent_status = 3`), so the next status applied to it is absorbed. It fits any slice and is a defensive pick for any class. Its main job is shielding a key slice (a Perfect-hook slice, or Overflow) from enemy Citations, Flares, Dose and Virus.

2. **Under the new rules:**
   - **Status model.** Statuses are now the anti-Firmware layer, and ×N stacks (N8) make them more dangerous, so a status shield matters more. But "absorbs the next status" is ambiguous with stacks. The old rule can't say whether a ×3 Citation counts as one status or three.
   - **Permanence.** If ENCRYPTED is only consumed once and never returns, the chip is a one-shot (the slice is bare after one hit). If it re-arms, it is immunity, because every status is negated forever. Either reading is a poor design.
   - **Parasites.** The Parasite ring is not a status, so Hardened does nothing against it. This is a good, clear boundary. Parasites stay the "real" threat, and Cleanse still answers them.
   - **CORRUPTED.** CORRUPTED is a status, so Hardened blocks it. It protects against the double-RAM tax, which is a strong niche under Genome Core P4, where every hit corrupts you.
   - **Degenerate risk.** If it re-arms, stacking it on all six slices makes the player immune to Halcyon, Solace and Orbital. That is a dominant pick.
   - **Slice sizes.** Size doesn't matter, so no slice is dead. A 2-tick slice is a fine home.
   - **Own statuses.** Permanent ENCRYPTED could also block your own beneficial statuses (Overdrive, Overclocked).

3. **Proposed spec:**
   - **Description:** "Slice resists statuses: absorbs the first status applied each turn, and reduces ×N stack applications by 1."
   - **Rarity:** COMMON (0).
   - **Cost:** 100.
   - **allowed_slice_types:** any.
   - **Effect:** a per-turn ENCRYPTED charge. It re-arms at the start of your turn but absorbs only one application per turn. If a status lands with N stacks, Hardened removes 1 (so ×1 is fully blocked, ×3 becomes ×2).
   - **Exception:** your own Overclock and Cleanse effects pass through.
   - **Reading on the slice:** a small shield-lock pip that fills when armed and dims when spent. The preview shows "−1 stack".
   - This makes it strong against single applications (Citation, Dose) but not immunity against stacking or multi-hit sources (Genome Core P4 still corrupts a Hardened slice if two hits arrive).

4. **Data:**
   - Replace `permanent_status` with `status_guard_charges` (new int, 1 per turn) and `status_stack_reduction` (int, 1) on `FirmwareData`.
   - Add a re-arm in `combat_resolver.start_turn`.
   - Add a hook in `effect_interpreter.apply_status`.
   - Status-immunity bypass flag for own effects.
   - Depends on N8 (×N stacks) and N9 (status rules). Fallback without N8: keep the current ENCRYPTED but let it re-arm each turn (data-only for the re-arm via a trigger, but needs one small handler).
   - Size: S–M.

5. **Q:** Should Hardened also block statuses the player applies to own slices (such as Overclock from a card), or only enemy-sourced ones?
   **Q:** Should a re-armed guard be allowed on a slice that is also carrying CORRUPTED, i.e. does it stop the debuff from spreading but not remove it?
