- **Cell fill (unit cells), DR-6:** the cell fill is the same neutral slate on every skin: one kind wash per unit kind and ring, at the ring value, and the empty fill per ring. The skin only adds its material over it (low chroma; `targets.cell_tint_max_chroma`). There is no per-skin push: `kind_gain` is retired (1.0 on every ring of every skin), and so is the `CorpKindWash` compute step. The fills are constants in `CombatLookData`:

<!-- gen:cells begin -->
<!-- gen:cells end -->

- **T (bake once per corp with PIL; corp-specific vector pieces):**
  - the rim strip;
  - 6 crests;
  - the token frame and disc frame;
  - the ticket 9-patch.

  See section 6.3.
- **C:** each cell's edge line (`cell_detail`) is drawn in the skin's hue ink as its `cell_detail` method lists it (Appendix B): the cell edge is one of the four places the corp hue may appear (DR-6).
- **N:** `CorpRingLayer` and `UnitCellLayer` replace `_draw_rings` and the fill and outline in `_draw_unit`. `WavesSpinner._band()` geometry gives way to section 2's radii.
- **Never touched by a skin:** the clock (4.4), HP, hatch, HOT/COLD/FAR, outlines, PLAN yellow, focus lime and pink.

### 4.4 Schedule band: the gunmetal clock, the live step, HOLD plates (time grammar)
- **C:** flat colours, drawn directly. **One gunmetal clock on every corp** (DR-6 note, `docs/ART_BIBLE.md` 2.4): the engraved band and its cells in gunmetal, the lip and groove light, the groove; **SCHEDULE orange only on the live step** (its cell edge, a soft glow under it, its chevrons) and in the clock's own motion (rings step, Hold). The silver THIS TURN tape of the 2026-11-02 draft and its remap table are retired; no clock colour is a skin field. Colours and draw calls, read from `rb_patch.py`:

<!-- gen:clock begin -->
<!-- gen:clock end -->

- HOLD plates and the Adjuster arc keep amber (`CRT_AMBER`). On Meridian a black gap of at least 2 px separates them from the rim rust; the bezel inner lip is black (section 7, Appendix B `bezel`).
- Digits draw on their own layer above everything on the board. Each digit **punches a hole** of boss r + 2.6 px in the band/plate layer and the label layer: draw the digit's disc with `BLEND_MODE_SUB` alpha, or use a stencil-like mask Control. Digit 0 sits at -4.5°.
- **N:** `ScheduleBand` and `BoardDigits` take the printed rotation from `WavesStepStrip`'s data (this END TURN's step, next, the one after). The SET dial buttons stay a UI Control (section 0.2, Hold is OPEN).

