# Task: `##` doc comments

Add a `##` doc comment to every public function (no leading underscore), signal, and
`class_name` declaration that lacks one. Public `const` and `@export` members get one only when
their name does not already say what they are.

- One line when possible, two at most. Present tense. What it does and when it is called; name
  the rule it implements when the body makes it obvious ("Applies spin resistance before a
  flip (GDD 5.3)") — never invent a GDD reference.
- Do not describe parameters one by one unless a parameter's meaning is not obvious from its
  name and type.
- Leave existing `##` comments alone unless they are wrong about what the code does; if so,
  fix them and say so in the summary.
- Private functions (`_name`) get nothing unless the body is longer than 30 lines and does
  something a reader could not guess.
- status: skip when every public member already has a doc comment.
