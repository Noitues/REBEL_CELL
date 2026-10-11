# Task: rule-compliance report (no patch)

Read the file and report every violation of the project rules and style, one per line, in
RC_NOTES. Produce NO patch (RC_PATCH empty, status: ok). Check, in this order:

- R1 core purity: a `scripts/core/` or `scripts/state/` file that references a Node, a scene,
  `get_tree()`, `SignalBus`, `ContentRegistry` or any autoload by name.
- R2 randomness: any `randi`, `randf`, `randomize`, `shuffle()` without an RNG stream, `RandomNumberGenerator.new()` outside `RngService`.
- R3 resource mutation: assignment into a loaded `Resource` (`.tres`) field at runtime.
- R4 views changing state: a `scripts/ui/` file that writes a state object's fields or calls a
  core resolver instead of emitting a signal.
- R5 magic numbers: numeric literals other than 0, 1, -1, 2, 0.5 used in rules, timings, sizes,
  colours (except in `const` definitions or `tools/`).
- R7 nondeterministic tie-breaks: iteration over a Dictionary's keys to pick a winner, `hash()`
  ordering, `sort()` without a comparator on compound items.
- S1 missing static types; S2 non-snake_case; S3 missing `##` on public funcs; S4 rules-written
  English that reaches the player (string literals shown in UI that are not TextDb keys).

Line format: `- <path>:<line> <rule-id> <what> -> <suggested fix in under 15 words>`.
List **violations only**: never a line for something that passes, is fine, is allowed, or that
you merely "checked" or want "confirmed". A `const` definition is not a magic number. If you are
not sure a line breaks a rule, leave it out. End with `- COUNT: <n>` (violations only) so the
report is machine-countable. Say `- none` when clean.
