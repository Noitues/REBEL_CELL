Raw ease strings in the data (generated):

<!-- gen:eases begin -->
<!-- gen:eases end -->

### 8.2 Runtime rules
- **Slot:** `WavesFxOverlay`, **under the HUD and the hand** (z 12.5, section 1; `docs/ART_BIBLE.md` 6.4; review 1.6). Only `fx_hp_through`, `fx_refund` and `fx_trace_add` (they land on HUD rows) use the second slot above the HUD (z 14). No effect draws above the hand.
- **Length:** every effect is VfxTier T2, 0.6 s or less, with no per-effect override (`docs/ART_BIBLE.md` 5.3; REVIEW_RESPONSE 2.11). The importer asserts it (13.1).
- **The resolve beat** (review 2.11) plays its effects as **concurrent tracks** in the HUD chain order, each at its own timing, and lasts under 4 s; **any input skips it**: the frame dissolves to the settled frame. The flash meter was run on the whole beat (full and reduce), not only per effect. Every flash also goes through `FlashLimiter.request()` (3 per second, `Settings.flash_limiter`). The beat as rendered (`effects/resolve_beat.gif`, `timings_MPST.json` `resolve_beat`):

<!-- gen:beat begin -->
<!-- gen:beat end -->

- **Reduce motion:** when `Settings.reduce_motion` is set, play `reduce_phases` (MPST) or the timed `reduce_motion` text (CDHL). Every reduce form drops travel, overshoot, sparks and glitch steps; state changes become short dissolves (each effect's length in Appendix A).
