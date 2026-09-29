#!/bin/bash
cd /c/Users/noitu/Documents/Godot/rebel_cell || exit 1
SP="${SP:-$TEMP/rebel_cell_checks}"; mkdir -p "$SP"
timeout 600 godot --headless --path . --import > "$SP/import_c.log" 2>&1
echo "import=$?"
for i in 1 2 3; do
  timeout 1200 python tools/run_tests.py -j 4 > "$SP/runner_$i.log" 2>&1 < /dev/null
  echo "runner$i=$?"
  tail -n 6 "$SP/runner_$i.log"
done
timeout 300 godot --headless --path . -s tools/schema_smoke_test.gd > "$SP/smoke.log" 2>&1
echo "smoke=$?"; tail -n 2 "$SP/smoke.log"
timeout 300 godot --headless --path . -s tools/validate_content.gd > "$SP/validate.log" 2>&1
echo "validate=$?"; tail -n 2 "$SP/validate.log"
