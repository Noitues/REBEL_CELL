#!/bin/bash
# Orchestrator gate: fast checks on main, push ONLY if all green (never push red).
cd "$(git rev-parse --show-toplevel)" || exit 1
SP="${SP:-$TEMP/rebel_cell_checks}"; mkdir -p "$SP"
JOBS="${JOBS:-4}" bash docs/handoff/art_2/process/checks_fast.sh > "$SP/gate.txt" 2>&1
grep -E "=|tests|ALONE" "$SP/gate.txt"
if grep -q "^import=0" "$SP/gate.txt" && grep -q "^fast=0" "$SP/gate.txt" && grep -q "^smoke=0" "$SP/gate.txt" && grep -q "^validate=0" "$SP/gate.txt"; then
  git push origin main 2>&1 | tail -1
else
  echo "NOT PUSHED: checks red"; exit 1
fi
