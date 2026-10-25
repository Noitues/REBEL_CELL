# L8 GDScript contract (shared by every tools/raid_lab_city file)

## Data shapes (plain Dictionaries and Arrays, JSON-compatible)
- **Cell:** `Vector2i(x, y)` in code. In JSON it is `[x, y]`. HOME is the String `"HOME"`.
- **Leg:** `L8Rules.leg_from_json(d)` turns the golden's `leg` object into a Dictionary:
  - `{seed, values: {Vector2i: int}, exploits: Array[Vector2i], start: Array[Vector2i], raids: Array[raid]}`;
  - a raid is `{b1, extra1, extra2: line, perm: Array[String], cands: Array[line] (3 routes), real: int,
    hunter_type: String, hunter_street: int}`;
  - a line is `{kind: "ROUTE"|"STREET", index: int, cells: Array[Vector2i], type: "D"|"N"|"E", home: bool}`.
- **State:**
  - `{heat: int, bank: int, home_hp: int, owned: {Vector2i: "OK"|"DOWN"|"TAKEN"}, sentries: {Vector2i: type},
    pool: {D, N, E: int}, kit: {ghost: int, spoof: int}}`;
  - `L8Rules.state_from_json(d)` and `L8Rules.state_to_json(st)` convert to and from the golden's `state_json` form,
    where owned and sentries are lists of `[x, y, s]` in cell order (y, then x).
- **Place:** `{sentries: {Vector2i: type}, ghost: Vector2i | "HOME" | null}`.
- **Response:** `["HOLD"]`, `["JAM"]` or `["REDEPLOY", Vector2i from, Vector2i to]`.
- **Touch:** `[cell_or_HOME, "hit"|"block"|"home"]`.
- **Trace entry:** `[beam, cell_or_HOME, kind]`, where beam is one of beam1, extra1, extra2, sealed or hunter.

## L8Rules (class_name L8Rules, extends RefCounted, static functions only; port of tools/raid_concepts/sweep_l8.py)
Same names and semantics as the Python, with the Python as the oracle.
- **Leg and capture:**
  - `config() -> Dictionary`;
  - `leg_from_json(d)`;
  - `initial(leg)`;
  - `capture_options(leg, st) -> Array[Vector2i]` (cell order);
  - `capture(leg, st, cell)`.
- **Placement:** `placements(leg, st) -> Array[place]`, in the same order as the Python generator.
- **Raid:**
  - `resolve(leg, raid: int, st, cand: int, place, response) -> {state, touches}`;
  - `trace(...) -> Array`;
  - `hunter_line(...) -> line or null`;
  - `response_options(leg, raid, st, cand, place) -> Array`, in the Python order.
- **Outcome:** `tier(before, after, touches) -> String`, and `score(leg, st, mid := false) -> float`.
- **Between raids:**
  - `between(leg, st, repair, build, intensity)`, where repair is a Vector2i or null and build a String or null;
  - `between_options(leg, st) -> Array[[repair, build, intensity]]`, in the Python order.
- **Forecast:** `forecast(leg, raid, st, place) -> Array`, one entry per candidate:
  `{cand, hold: {state, touches, tier}, best: {response, state, touches, tier}}`.
- **JSON:** `state_from_json`, `state_to_json`.

Tuning constants come from `const` blocks at the top of l8_rules.gd, mirroring sweep_l8.py's constants. The Python
module is the source of truth.

## Golden: `res://tools/raid_lab_city/data/l8_golden.json`
- **`config`:** sweep_l8.config().
- **`legs`:** `[{seed, leg, greedy: [step], naive: [step]}]`. A step has:
  - `raid`, `before_capture` (state_json), `capture` (cell or null);
  - `before` (state_json after the capture), `place` (`{sentries: [[x, y, t]], ghost}`), `cand`, `response` (JSON
    form);
  - `trace` (`[[beam, cell, kind]]`), `hunter` (line or null), `tier`;
  - `after_raid`, `score_raid`, `between` (`{repair, build, intensity}` or null), `after`, `score_after`.
- **`random_raids`:** `[{leg (seed), raid, before, place, cand, response, trace, hunter, tier, after_raid,
  score_raid}]`.
- **`random_betweens`:** `[{leg, before, repair, build, intensity, after}]`.
- **`random_captures`:** `[{leg, state, options}]`.

**Legs are never generated in GDScript** (no port of make_leg or random.Random). The lab and the parity check load
each leg from the golden's `legs[i].leg` object with `leg_from_json`, so only the golden seeds (0, 3, 5, 8) are
playable. `random_*` entries name their leg by seed.
