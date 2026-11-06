### 4.1 Room backdrop and grade (rb2-1)
- **Which room:** `docs/ART_BIBLE.md` 3.14 (designer ruling DR-9): Site and HQ-run fights show the cutaway room; the boss fight keeps the perspective close-up. The skin picks the room (`bd_grade.CORP_ROOM`, below).
- **T, recommended:** bake each graded room offline with `D:/rc_scratch/combat_redesign/locked/corp/src/bd_grade.py` (`room_grade()`, rb2-1) and the parameters in `backdrop/grade.json`: one PNG per room in Appendix C (the `shop_meridian` corp variant included), at 1920x1080, `res://assets/backdrops/combat_v3/room_<name>_graded.png`. Bake the board scrim into the same image, because the board centre is fixed.
  - Keep the bare rooms (`combat_backdrop/v3_1/room_<n>_bare.png`) as well. T5 crossfades bare to graded (section 10).
  - Runtime cost: one texture.
- **S, for rooms not yet baked and for tuning:** `shaders/combat/room_grade.gdshader`, a canvas_item shader on the room TextureRect. It runs on sRGB-encoded values; in Godot 4 canvas textures arrive as sRGB, so no conversion is needed. It runs the grade.json steps below, in order, with the uniforms below. The hull is a signed-distance texture baked once from `hull_poly`; the blur ramp and the local tone's blurred luma are mip LOD taps (the room texture needs mipmaps). The step6-1 shader and its room squint bars in the 2026-11-02 draft are retired with step6-1; rb2-1 is gated by the room L* (section 13.3).

<!-- gen:room begin -->
<!-- gen:room end -->

- **N:** `CombatBackdrop` keeps choosing the room (`BackdropCatalog.place_for`). The art pass adds the `room_<n>` → graded-texture lookup and the per-room uniforms, read from a `RoomGradeData` resource array that mirrors `grade.json` (Appendix C).
- **Test hook:** with the shader on `room_bio_bare.png`, the mean absolute error against the baked PNG is at most 3/255, allowing for the mip blur. The room L* gate and the data test are in 13.3 ("room grade").

