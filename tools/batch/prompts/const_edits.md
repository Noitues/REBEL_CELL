# Task: name literals as consts (per file), answered as exact edits, not a diff

Do what `<instructions>` says to this file, but do NOT write a unified diff: you cannot count
hunk lines reliably. Put edit blocks in the RC_PATCH section instead. Each block is exact text
copied from the file (tabs preserved); the applier does a unique exact-substring match.

```
=== INSERT_AFTER
<one existing line, copied exactly, that is unique in the file (the last line of the const block)>
--- TEXT
<the new const lines, each with its `##` comment line above it>
=== REPLACE
<the original code, copied exactly; one line or a few adjacent lines, unique in the file>
--- WITH
<the same code with the literal(s) replaced by the const name(s)>
=== END
```
- One `=== END` closes the whole list; use as many INSERT_AFTER / REPLACE blocks as needed.
- A REPLACE must change nothing but the literal -> const name. If you substituted every const
  name back to its value, the line must equal the original character for character.
- A const that is used in several places needs one REPLACE per unique snippet; make each
  snippet long enough to be unique in the file (include neighbouring text on the same line).
- Never define a const whose name already exists in the file. Never change `const` lines that
  are already there.
- Every const you add must be used by at least one REPLACE, and every REPLACE must differ from
  its original (a no-op block is an error). Define no const for a literal you do not replace.
- Keep the literal's spelling and type: `16` becomes `const X: int = 16`, `16.0` becomes
  `const X: float = 16.0`; a literal inside `Vector2(0, 16)` stays an int const. Never turn
  `x * 0.5` into `x / 2.0` or `3` into `2 + 1`; never negate a const to flip a sign
  (`-4.0` stays `-CONST` with CONST = 4.0 only if the original is `-4.0`).
- Replace literals one line at a time where possible: a REPLACE of one line is cheaper to check
  than ten lines.
- If nothing qualifies, status: skip and an empty RC_PATCH.
