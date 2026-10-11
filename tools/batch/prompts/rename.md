# Task: rename (per file)

`<instructions>` lists one or more `OLD -> NEW` symbol pairs. Rename every occurrence in this
file: identifiers, member accesses, string names used in `connect("...")`, `has_method("...")`,
`get("...")`, `Callable(self, "...")`, and `## ` comments. Do not rename inside other words
(`old_name` is not `older_name`). Keep behaviour and formatting identical otherwise.
Status: skip with "no occurrences" when nothing matches. List in RC_NOTES any string literal
you were unsure about (`- UNSURE: <path>:<line> "<text>"`).
