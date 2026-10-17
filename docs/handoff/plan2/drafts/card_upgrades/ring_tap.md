<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__ring_tap; status ok; tokens in 5094 cache-write 0 cache-read 32585 out 1233; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: ring_tap

1. **Role:** Cheap, precise inner-ring trim, letting the player set the ring modifier (×2 / Pierce / Corrupt / etc.) for the turn without touching the outer ring or spending the free nudge.

2. **Upgraded card: Ring Tap+** (one level only; no second level needed)
- RAM cost: 1 (unchanged). Cycle cost multiplier: ×1.5 (50 → 75).
- Text: "Two ±1 nudges on your inner ring. Your next inner-ring nudge this turn is free."
- Effects (in order):
  1. NUDGE: target OWN_WHEEL, ring_scope INNER, amount 2 (as today).
  2. CUSTOM-free alternative: reuse the existing Calibrate mechanism, a "free nudge" grant of 1 (the same counter Calibrate and Torque Wrench use, today's GAIN free nudge), amount 1. It is restricted to inner-ring nudges, so it is not a general free-nudge card.
- Exhaust: false. wheel_target: OWN (0).
- Why a rider rather than a bigger number: 2 nudges already cover most inner-ring alignments (segments are 10 ticks, so ±2 is a fine trim). Extra reach would turn it into Gear Shift. The free inner nudge turns it into a three-tick adjustment for 1 RAM, which stays an inner-ring card.
- Sidegrade check: it does not dominate Fine Tune or Tap Tap. Those work on one chosen ring (including outer), while Ring Tap+ stays inner-only. The outer-ring precision market is untouched.

3. **Interplay:**
- Corruption as double RAM: nudges read the acting pointer's slice, so on a CORRUPTED slice the free inner nudge saves 2 RAM, not 1. That makes the + version a natural counter to the corruption tax, and it is a deliberate synergy.
- Variable slice sizes and sub-ticks do not change the card, because the inner ring is separate and its quality is measured on the outer ring only (GDD 6.4).
- Rigger and Overclocker keep their deck role.

4. **Data (changes against the current .tres):**
- `cycle_cost` 50 → 75.
- `description` updated.
- `display_name` "Ring Tap+".
- Add a second `EffectData`. There is no existing free-nudge-grant EffectType in the enum (Calibrate and Deep Calibrate must be implemented by a CUSTOM handler, per the enum list). The simplest data-only option: reuse the Calibrate CUSTOM handler script with amount 1 and a new ring filter parameter. That needs a small handler change (a ring-scope restriction on the free-nudge counter). Mark as **NEW: ring-scoped free nudge** (size S, no N# fits).
- Fallback that is data-only: drop the rider and instead set `ram_cost` 0 with cycle ×1.5. That is a plain cost reduction (a free two-tick inner trim). It is weaker for Overclocker, whose ring decisions need RAM-neutral reuse, but it needs no new code and also does not dominate, because it adds no free nudge.

5. **Q:**
- Q: Should the free inner nudge be ring-restricted (as proposed), or should it use the generic free-nudge counter that Calibrate uses, so the + version equals "Fine Tune plus a free nudge"?
- Q: Do the Overclocker and Rigger class files need a different + choice? Overclocker leans on the inner ring heavily, and a 0-RAM + may fit it better than the rider.
