# Task: targeted GUT unit tests for a core class

Write ONE new GUT test script for the class in the file you were given. Output it as a patch
that creates `tests/unit/test_<basename>.gd` (a `--- /dev/null` / `+++ b/tests/unit/...` diff).
If `<instructions>` names an existing test file, extend that one instead.

Scope — business rules only, not coverage:
- Every public function that implements a rule: the happy path, the boundary (0, max, empty),
  and one case the GDD calls out by name when the `##` comment names it.
- Determinism: when the class takes an `RngService` stream or a seed, one test proves two runs
  with the same seed give the same result, and one that a different seed can differ.
- Preview == result where the class exposes both (`preview_*` / `resolve_*`).
- Nothing for getters, setters, `to_dict`/`from_dict` round trips unless they carry logic.

Conventions (match the project's tests, which `extends GutTest`):
- `extends GutTest`, functions `func test_<what>_<when>() -> void:`, typed locals.
- Build inputs with the class's own constructors / `new()`; use `RngService.new(<seed>)` streams
  when the API in front of you takes one; never `randi()`.
- One assert idea per test; `assert_eq`, `assert_true`, `assert_almost_eq` for floats.
- No `await`, no scene tree, no Nodes: the class is pure `RefCounted`.
- Leave a `## Tier: fast` comment at the top; the orchestrator adds the manifest entry.

If the class cannot be tested without a Node or an autoload, status: skip and say why.
