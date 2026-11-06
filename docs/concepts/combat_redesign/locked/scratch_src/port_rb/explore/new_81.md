### 8.1 Resources
<!-- gen:fx_counts begin -->
<!-- gen:fx_counts end -->

Each entry has: `id`, `family`, `title`, `kind` (damage, kill, block, state, gain: the loudness tier), `skins`, `total_ms`, `phases[{name, start_ms, end_ms, ease, ease_raw}]`, `reduce_phases` (MPST: timed phases; CDHL: empty, the reduce form is the timed `reduce_motion` text), `keyframes_ms`, `reduce_motion`, `layer` (`board` or `hud`), `source`, `max_flashes_per_s` (full) and `reduce_max_flashes_per_s`, the O-30 total (`total_ms_o30`), and the transient loudness per skin. Import it into Resources:
```gdscript
class_name CombatFxPhase extends Resource
@export var name: StringName
@export var start_ms: int
@export var end_ms: int
@export var ease: StringName        # LINEAR, IN_QUAD, IN_CUBIC, OUT_CUBIC, IN_OUT_CUBIC, OUT_BACK, IN_OUT_SINE, STEP, HOLD

class_name CombatFxTiming extends Resource
@export var id: StringName
@export var family: StringName      # M P C D H L S T
@export var kind: StringName        # damage kill block state gain (8.4 loudness order)
@export var layer: StringName = &"board"   # board: under the HUD and the hand; hud: only the three HUD-row effects (section 1)
@export var total_ms: int
@export var phases: Array[CombatFxPhase] = []
@export var reduce_phases: Array[CombatFxPhase] = []   # MPST from the data; CDHL authored from the reduce_motion text
@export var tier: int = 2            # VfxTier T2 (outcome, max 0.6 s) for every effect; no override
@export var flash_events_ms: PackedInt32Array = PackedInt32Array()   # the frames counted as flashes, for FlashLimiter
```
