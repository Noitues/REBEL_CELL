class_name TestScope
extends RefCounted
## Test helper (designer ruling 2026-10-13, DECISIONS "Designer ruling: finalize gameplay at
## text 1.0"): gameplay is finalized at text scale 1.0 with mouse and keyboard. Text scale
## above 1.0, high contrast, gamepad (pad focus, pad glyphs), colour-blind and greyscale
## checks are DEFERRED until gameplay is final. A test script that is only about those is in
## the manifest's `deferred` tier (skipped by every default run; `run_tests.py --tier
## deferred` runs them). A mixed script gates just those cases with `deferred()` / `scales()`.
## To bring them all back: set DEFERRED to false (and move the scripts back to fast / full).

## True while the deferred checks are switched off.
const DEFERRED := true
## The pending message of a gated case.
const REASON := "deferred: text scale / hc / pad"


## True while text scale > 1.0, high contrast, gamepad and colour-blind cases are deferred.
## Use as `if TestScope.deferred(): pending(TestScope.REASON); return`.
static func deferred() -> bool:
	return DEFERRED


## `all` (a list of text scales) without the scales above 1.0 while those are deferred; the
## list unchanged otherwise. A loop over scales keeps its 1.0 case.
static func scales(all: Array) -> Array[float]:
	if not DEFERRED:
		return Array(all, TYPE_FLOAT, "", null)
	var kept: Array[float] = []
	for s in all:
		if float(s) <= 1.0:
			kept.append(float(s))
	return kept
