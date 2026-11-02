# MAILBOX DRAFT: DRAFT, not posted, waiting for designer sign-off

> **DRAFT, not posted, waiting for designer sign-off.** This entry is **not** in `HANDOFF_PACKAGE/MAILBOX.md`, and no message has been sent. Once the designer signs off on the locked combat board and on the open name questions below, art-pass copies it into the mailbox as the next A number (A-116 is the next free one as of 2026-11-02; re-check it at posting time), commits it, and sends the optional wake-up. Until then, build should not act on it.

---

### A-116 · 2026-11-02 · Combat screen art port: the locked Shifting Waves board (roadmap step 8) · ASK

**The ask.** Please implement the locked combat board on the Shifting Waves fight, following `docs/concepts/combat_redesign/locked/GODOT_PORT_SPEC.md` (art-pass branch). It covers:
- the cutaway room grade;
- the corp-skinned enemy rings (neutral, Solace, and Meridian as a proof only, per A-112);
- the neutral silver THIS TURN tape;
- the xerox and linocut player spinner;
- the HOT/COLD/FAR time grammar and the pending-loss cross-hatch;
- the WPAP card hand;
- hover dimming;
- 32 effects;
- the T5/T6 bits transitions.

Everything is view-side. No game number, word or rule changes.

**Where it lands** (read-only look at game-v2 `b09f9b9d` via `D:/rc_art/godot_jackin`; please re-check at your head):
- `WavesSpinner` keeps its signals and `hit_test`, and its `_draw()` splits into layered views: rings, tower, board marks, guns, hover and the FX overlay.
- `WavesHand` becomes atlas card sprites plus Labels, with the same signals.
- `WavesHud` and `WavesStepStrip` / `WavesLineupStrip` are restyled; their data moves onto the board band and tickets.
- `WavesLookData` is replaced by a new `CombatLookData`, behind a flag `waves_art_on` that defaults to false until the designer signs off.
- New data classes:
  - `CombatCorpSkin`, with three `.tres` files whose values are filled in the spec;
  - `CombatFxTiming` / `CombatFxPhase`, imported from `port/fx_timings.json`;
  - `CorpKindWash`, pure, with a golden in `port/skin_tables.json`.
- Reused as they are: `FlashLimiter`, `VfxTier`, `Settings.reduce_motion` and `reduce_effects`, `BitPath` / `BitsSeam` / `binary_bits.gdshader`, and `CombatBackdrop` / `BackdropCatalog`.

**What art supplies.**
- The spec, with shader code for:
  - the pending-loss hatch;
  - the shared print include (hatch, Ben-Day, tower textures, X-halftone);
  - hover dim;
  - card states;
  - offset print;
  - the S glitch;
  - the H flood;
  - the room grade;
  - the T5/T6 ring reveal.
- The texture and atlas list with sizes and bake commands.
- The card atlas proof bake (`port/cards_proof.jpg`, art-only cells of 424 x 572; text stays as Labels so translation works).
- Art can run the remaining PIL bakes (tower sheets, corp rim/crest/frame/ticket sheets, graded rooms, effect sprites) on request and hand over the PNGs. Say whether you want them in a branch or as a folder.

**Order** (spec section 12): data resources and tests → full-screen layout → room → corp rings → schedule band → tower → board marks (with draw asserts and the collision test) → hand → HUD → hover → effects (T/M/P first) → T5/T6 → plate-parity captures through `tools/run_windowed.py`.

**Tests requested** (spec section 13): 10 new GUT scripts, each in `tests/test_manifest.json`:
- skin and look validation;
- "no skin field equals a game-mark colour";
- the kind-wash golden;
- the timing invariants and flash-stream safety;
- hit-test parity;
- draw asserts from a draw log;
- the mark and occluder collision test, including hand radius ≥ 455;
- the no-dashed-lines grep;
- preview equals result for hover ghosts;
- hover dim maths.

Plus windowed squint and flash captures against the art plates.

**Open, needs an answer before those pieces are wired** (spec section 0.2 and 14):
1. Concept unit Jammer vs game `glitch`; game `halo` has no art.
2. Concept card Firewall vs game `scorch`; the concept Hold card vs the game SET dial; game `bug` has no art.
3. Shove bump: do both units lose HP? The art draws no HP change until the game rule says so.
4. Tower loudness on the p2/p3 beats is 57-58 % against a 50 % target (designer call).
5. The combined resolve sequence was never flash-measured as a whole. The spec spaces effects at least 100 ms apart and gates them through `FlashLimiter`. Please run the capture check once it is wired.

**Rules carried in the spec** (designer): no dashed lines; no needle; cross-hatch = HP lost at this END TURN (hatch colour = cause: red enemy, blue soak, pink ours); arrowed outline = movement only; HOT/COLD/FAR time grammar; corp skins are colour plus material with one neutral silver tape; pink belongs to the player.

Source plates and notes: `combat_redesign/locked/final/`, `corp/`, `effects/`, `hover/`, `backdrop/`, `transitions/`.
