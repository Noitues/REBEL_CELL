## One corporation's enemy-layer look on the combat board: its material, plus the corp hue on the rim, the bezel lip, the crest
## and the cell edges only (docs/ART_BIBLE.md 2.4, designer ruling DR-6). Game marks are NOT here: the clock, HP, hatch,
## HOT/COLD/FAR, outlines, the cell fills, PLAN yellow, focus lime and player pink live in CombatLookData.

enum CellMaterial { ENAMEL_LINES, MEMBRANE, RIBS }

@export var id: StringName = &"neutral"
## The graded room this corp's fights use (backdrop/grade.json corp_room, GODOT_PORT_SPEC 4.1).
@export var room: StringName = &"bio"
## Cell, bezel, annulus and arcframe materials: ShaderMaterials on corp_ring.gdshader, uniforms filled per corp (Appendix B).
@export var cell_material: ShaderMaterial
@export var bezel_material: ShaderMaterial
@export var annulus_material: ShaderMaterial
@export var arcframe_material: ShaderMaterial
@export var material_kind: CellMaterial = CellMaterial.ENAMEL_LINES
## The skin palette (rb_patch._skins) and its hue inks: the only colours a skin draws.
@export var pal: Dictionary = {}
@export var inks: Dictionary = {}
## C family (the corp acting): the ink of its one scan line (fxk_lib.CORP_ENAMEL).
@export var c_scan_ink: Color = Color.WHITE
## Vector pieces, baked from the PIL generator (GODOT_PORT_SPEC 6.3).
@export var rim_texture: Texture2D
@export var crest_texture: Texture2D
@export var crest_count: int = 6
@export var crest_angle0_deg: float = 30.0
@export var crest_radius: float = 494.5
@export var token_frame_texture: Texture2D
@export var disc_frame_texture: Texture2D
@export var ticket_style: StyleBoxTexture
@export var ticket_style_dim: StyleBoxTexture
## Transitions (T5/T6 bits FX): no skin field (review 3.12): each bit reads the colour of its source from the board
## (section 10, "Bit colour"; ART_BIBLE 1.2).
## Meridian's stencilled numbers on empty cells (hook exists, art not drawn yet).
@export var empty_marks: bool = false

## Error codes of a bad value (empty when valid).
func validate() -> PackedStringArray:
	var e := PackedStringArray()
	if crest_count < 0: e.append("corp_skin: crest_count")
	if room == &"": e.append("corp_skin: room")
	return e
```

Retired fields of the 2026-11-02 draft, not ported: `kind_gain`, `cell_edge` / `cell_edge_w` / `frame` / `frame_groove` as typed colours (the cell edge and the frames are now the method layers of Appendix B, read into the materials and the 6.3 bakes), `shutter_slab`, `shutter_lip`, `shutter_lip_shape`, `motion_tint`, and the hazard paint (reasons below, generated).

**Per corp** (generated from `port/skin_tables.json`; the material layers of every method are in Appendix B):

<!-- gen:skins begin -->
<!-- gen:skins end -->

- **Selecting the skin.** The fight's corp (`WavesState.node` / netrun site → corporation id) picks `content/combat/skins/<id>.tres`. Neutral is the fallback. Meridian stays hibernated in the slice (A-112): a palette proof that the swap works.
- **Swapping at runtime:** set the four ShaderMaterials, swap the five textures and the room. The game marks and the cell fills do not change.
- **The clock is not a skin field.** `CombatLookData` holds the clock colours (4.4). A test asserts that no skin colour equals a game-mark token, and that every hue ink keeps dE76 15 or more from Cell lime, GAIN, FOCUS and HARM (section 13).

---

