# Task: player-facing text audit (no patch)

Find every string the player can see that is not a TextDb key / `tr()` call, and every
`strings.csv`-style key whose English reads like a rules document rather than a game line.
No patch: RC_NOTES only, status: ok.

For a GDScript file: list `- <path>:<line> LITERAL "<text>" -> key suggestion <SCREEN_NOUN_VERB>`.
For a strings.csv slice: list `- <key> RULESY "<text>" -> <rewrite under 6 words, imperative or
noun phrase, in the game's voice: terse, capitalised cyberpunk labels (JACK IN, BREACHED,
HOLDS)>`, and `- <key> TOO_LONG <n> chars for a <label|toast|tooltip>` when a label is over 18
characters or a toast over 60.
End with `- COUNT: <n>`. `- none` when clean.
