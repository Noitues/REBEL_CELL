#!/bin/sh
# Run selected test scripts only, in the checkout this script is run from.
# usage: gt.sh logname tests/unit/test_a.gd tests/unit/test_b.gd ...
SP="${SP:-$TEMP/rebel_cell_checks}"; mkdir -p "$SP"
LOG="$SP/$1.log"; shift
T=""
for f in "$@"; do T="$T,res://$f"; done
T="${T#,}"
cd "$(git rev-parse --show-toplevel)" || exit 1
timeout 1500 godot --headless -s addons/gut/gut_cmdln.gd -gconfig="docs/handoff/art_4/process/gut_one.json" -gtest="$T" -gexit > "$LOG" 2>&1
echo "exit=$?"
grep -n "Passing Tests\|Failing Tests" "$LOG"
grep "SCRIPT ERROR\|Parse Error" "$LOG" | sort | uniq -c | sort -rn | head -15
grep -B1 -A6 "\[Failed\]" "$LOG" | grep -v "^--$" | head -80
