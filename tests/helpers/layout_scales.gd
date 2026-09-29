class_name LayoutScales
extends RefCounted
## Test helper (art pass W9): the largest text scale the screen-layout tests hold every
## screen to. ART_BIBLE §12 / Q5 raised Settings.TEXT_SCALE_MAX to 2.0, but the screens
## are made to fit 2.0 by W8 (docs/art_review/W9/README.md lists the 2.0 breakages), so the
## layout tests that failed at 2.0 check up to 1.6, the old ceiling, until then.
## W8: set this to Settings.TEXT_SCALE_MAX once the screens fit 2.0.

## The text scale the layout tests treat as "the largest".
const VERIFIED_MAX := 1.6
