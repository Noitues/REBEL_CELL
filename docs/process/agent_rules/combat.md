# Area: combat (wheels, cards, FX, HUD, netrun 2D)

Owns: `scripts/ui/combat/`, `scripts/ui/kit/` pieces the brief names, `content/config/ui_motion.tres`
entries in its items, `tests/unit/test_art2_*`, `test_anim_*_combat`, `test_b2_*`.
Reference: ART_BIBLE v2 §combat and the locked concepts the brief lists; GDD 5 (combat core);
STYLE_GUIDE §5 (motion). Presentation follows the approved art direction without asking; mechanics
never change here (G1–G16 are not built).
Checks before hand-back: layout at 1.0 / 1.6 / 2.0 (layout rules test), preview == result untouched
(`test_preview`), MotionSkip paths, reduce effects = end state, a windowed capture of each changed
state (contact sheet) with ERROR grepped from the log.
Hub files (change with care; selection falls back to the fast tier): `fx.gd`, `fx_draw.gd`, `hud.gd`.
