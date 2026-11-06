# MAILBOX DRAFT: DRAFT, not posted, waiting for designer sign-off

> **DRAFT, not posted, waiting for designer sign-off.** This entry is **not** in `HANDOFF_PACKAGE/MAILBOX.md`, and no message has been sent. Once the designer signs off on the locked combat board and on the open questions below, art-pass copies it into the mailbox as the next A number (A-116 was the next free one as of 2026-11-02; re-check it at posting time), commits it, and sends the optional wake-up. Until then, build should not act on it.

---

### A-116 · 2026-11-04 · Combat screen art port: the locked Shifting Waves board (roadmap step 8) · ASK

**The ask.** Please implement the locked combat board on the Shifting Waves fight, following `docs/concepts/combat_redesign/locked/GODOT_PORT_SPEC.md` (art-pass branch; rebuilt 2026-11-04 on the rebuilt board). It covers:
- the cutaway room and its grade (rb2-1, `backdrop/grade.json`; ART_BIBLE 3.14, DR-9);
- the corp-skinned enemy rings (neutral, Solace, and Meridian as a proof only, per A-112), per the ART_BIBLE 2.4 designer-ruling note (DR-6): the corp theme by material, the corp hue only on the rim, bezel lip, crest and cell edges, neutral slate cell fills;
- one gunmetal clock (the schedule band) on every corp, with SCHEDULE orange on the live step only;
- the xerox and linocut player spinner;
- the HOT/COLD/FAR time grammar and the pending-loss cross-hatch;
- the WPAP card hand;
- hover dimming;
- the effects, each 0.6 s or less (VfxTier T2), drawn under the HUD and the hand except the three that land on HUD rows, and the resolve beat under 4 s with skip on any input;
- the T5/T6 bits transitions (DR-10).

Everything is view-side. No game number, word or rule changes.

**The numbers, generated from the data files** (`port/src/port_spec.py`; the spec has every table):
<!-- gen:mailbox_numbers begin -->
- Effects: 32, every one at most 600 ms (T2) with 0 overrides, drawn under the HUD and the hand except `fx_hp_through`, `fx_refund`, `fx_trace_add`.
- Resolve beat: 3800 ms against 4000, skip on any input in 200 ms; loudness order damage > kill > block > state (gain ranks with state) holds on every skin.
- One gunmetal clock on every corp: fill #6E7580 (L* 49.0), lip #969EAA (L* 64.8), groove #282C34 (L* 17.9); SCHEDULE #FF8C1A on the live step only.
- Corp skins: material plus corp hue on the rim, lip, crest and cell edges; neutral slate cell fills, `kind_gain` 1.0 everywhere; rooms neutral bio, solace bio, meridian shop.
- Room grade rb2-1; graded room mean L* 31.8-32.5.
- Plate checks: draw_asserts, collisions, occlusion, hand, dashes, pixel_dot_runs, rb_a_cell_contrast, rb_b_value_order, rb_c_cap_height, rb_d_palette, rb_e_hand, stage2_hand_margin, stage2_tickets all true; pink in the enemy zone 1.39-1.39 % and the tower-zone squint 57.0-68.7 % are reported, not gated.
- Card atlas: `cards_art_atlas.png` 1696 x 1716, `cards_ref_atlas.png` 1696 x 1716, `cards_liner_atlas.png` 1696 x 1716.
<!-- gen:mailbox_numbers end -->

**Where it lands** (read-only look at game-v2 `b09f9b9d` via `D:/rc_art/godot_jackin`; please re-check at your head):
- `WavesSpinner` keeps its signals and `hit_test`, and its `_draw()` splits into layered views: rings, tower, board marks, guns, hover and the FX overlay (under the HUD, with a second slot above it for the three HUD-row effects).
- `WavesHand` becomes atlas card sprites plus Labels (and the rules bar drawn from the Label width), with the same signals.
- `WavesHud` and `WavesStepStrip` / `WavesLineupStrip` are restyled; their data moves onto the board band and tickets.
- `WavesLookData` is replaced by a new `CombatLookData`, behind a flag `waves_art_on` that defaults to false until the designer signs off.
- New data classes:
  - `CombatCorpSkin`, with three `.tres` files whose values are generated in the spec (section 7);
  - `CombatFxTiming` / `CombatFxPhase`, imported from `port/fx_timings.json`;
  - `RoomGradeData`, mirroring `backdrop/grade.json`.
- Reused as they are: `FlashLimiter`, `VfxTier`, `Settings.reduce_motion` and `reduce_effects`, `BitPath` / `BitsSeam` / `binary_bits.gdshader`, and `CombatBackdrop` / `BackdropCatalog`.

**What art supplies.**
- The spec, with shader code or uniforms for:
  - the pending-loss hatch;
  - the shared print include (hatch, Ben-Day, tower textures, X-halftone);
  - hover dim;
  - card states;
  - offset print;
  - the S glitch;
  - the H flood;
  - the room grade (rb2-1 steps and uniforms);
  - the T5/T6 ring reveal.
- The texture and atlas list with sizes and bake commands.
- The card atlas, baked from the module that renders the new card sheet: art-only cells with no words and no rules bar, the worded reference and the played liners (`port/cards_atlas.json`, `port/cards_proof.jpg`); text stays as Labels so translation works.
- Art can run the remaining PIL bakes (tower sheets, corp rim/crest/frame/ticket sheets, graded rooms, effect sprites) on request and hand over the PNGs. Say whether you want them in a branch or as a folder.

**Order** (spec section 12): data resources and tests → full-screen layout → room → corp rings → schedule band → tower → board marks (with draw asserts and the collision test) → hand → HUD → hover → effects (T/M/P first) → T5/T6 → plate-parity captures through `tools/run_windowed.py`.

**Tests requested** (spec sections 13.1 and 13.3), each in `tests/test_manifest.json`:
- look, skin and timing data: `test_combat_look_data`, `test_combat_corp_skin` ("no skin colour equals a game-mark colour"; no retired field), `test_combat_fx_timings` (the 0.6 s cap, no override, the HUD-layer list, the beat limit, flash-stream safety);
- the art's plate checks as GUT equivalents: `test_waves_cell_contrast`, `test_combat_look_values`, `test_waves_text_caps` (16 px cap floor), `test_combat_palette_de` (dE76 15), `test_waves_hand_layout`, `test_room_grade_data`;
- board: hit-test parity, draw asserts from a draw log, the mark and occluder collision test (hand radius ≥ 455), the no-dashed-lines grep, preview equals result for hover ghosts, hover dim maths.

Plus windowed squint, flash and loudness captures against the art plates; the tower-zone squint and the pink share in the enemy zone are reported, not gated.

**Open, needs an answer before those pieces are wired** (spec sections 0.2 and 14):
1. Concept unit Jammer vs game `glitch`; game `halo` has no art.
2. Concept card Firewall vs game `scorch`; the concept Hold card vs the game SET dial; game `bug` has no art.
3. Shove bump (a RULES question): do both units lose HP? The art draws no HP change until the game rule says so.
4. Twist render (a RULES question): the resolve beat's ring +1 during the Twist track is marked not to ship until the designer rules.
5. D4 scope: not until this board passes; what it then covers is open.
6. Tower squint vs ink value (VISUAL_PLAN A.1): the tower-zone loud share is over the old 50 % target while the value order holds; the designer decides which governs.
7. The resolve-beat skip has no on-screen word.
8. Pink in the enemy zone is above the 2026-11-02 bar; the bar needs restating for the rebuilt board.

**Known not done** (spec section 14): the thin 1 px ring and band lines are not gated; section 9 (hover) still carries the 2026-11-02 hover numbers while `hover/` is rebuilt; P stock is not yet a token in `rb_tokens`.

**Rules carried in the spec** (designer): no dashed or dotted lines; no needle; cross-hatch = HP lost at this END TURN (hatch colour = cause: red enemy, blue soak, pink ours); the arrowed outline is kept and means movement only (DR-1); HOT/COLD/FAR time grammar; corp skins per ART_BIBLE 2.4 (DR-6), one gunmetal clock; no reserved fill colours (DR-5); pink belongs to the player. Art-pass calls carried as rules (REVIEW_RESPONSE): effects under the HUD, every effect 0.6 s or less, the resolve beat under 4 s with skip.

Source plates and notes: `combat_redesign/locked/final/`, `corp/`, `effects/`, `hover/`, `backdrop/`, `transitions/`.
