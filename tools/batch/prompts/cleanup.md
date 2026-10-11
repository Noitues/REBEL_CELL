# Task: cleanup (lint, dead code, formatting, comments)

Make the file clean without changing what it does. Allowed changes, in this order:

1. **Typing**: add missing static types to `var`, parameters and return values where the type is
   certain from the code in front of you (`-> void` on functions with no return, `: int` on
   `var n = 0`). Leave `Variant` alone when the real type is not visible.
2. **Dead code**: remove unused local variables, unreachable lines after `return`, commented-out
   code blocks older than the surrounding code, empty `pass` bodies that follow real code, and
   private functions (`_name`) that nothing in this file calls or connects — but NEVER remove a
   function whose name matches a Godot callback (`_ready`, `_process`, `_input`, `_draw`,
   `_on_*`, `_exit_tree`, `_notification`, `_get_*`, `_set_*`) or anything connected by string
   name or `Callable(self, "...")` anywhere in the file.
3. **Formatting**: one blank line between functions, two before a class-level section only if
   the file already does that, no trailing whitespace, no double blank lines, spaces around
   binary operators, `:=` only where the file already uses it.
4. **Comments**: delete comments that restate the code line below them; keep comments that say
   why. Fix typos in comments. Turn a `# TODO` into an RC_NOTES finding, don't delete it.
5. **Imports/preloads**: drop a `preload`/`const X = preload(...)` that nothing in the file uses.

Never: rename anything public, reorder functions, change a signal, a string key, a number, an
`@export`, or any behaviour. If the file has a `## ` header saying it is generated, status: skip.
Anything you see that breaks a project rule but is outside these five points goes in RC_NOTES.
