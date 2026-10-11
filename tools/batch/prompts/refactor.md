# Task: mechanical refactor (per file)

Apply exactly the refactor described in `<instructions>` to this file and nothing else. Typical
instructions: "rename symbol X to Y (call sites only; the declaration is done)", "replace calls to
`A.b(x)` with `A.c(x, false)`", "move the literal 0.35 to `CONFIG.hover_delay`", "split function F
into F and G at the comment marker".

- Make every occurrence consistent; grep the whole file, including strings used as signal names
  or dictionary keys when the instructions say they are in scope.
- Keep behaviour identical unless the instructions say otherwise. Keep types static.
- If the refactor would need a change in a file you do not have (a declaration, a `.tres`, a
  test), do your part and list the other file in RC_NOTES as `- NEEDS: <path> <what>`.
- If the file is not affected by the instructions, status: skip, summary "no occurrences".
