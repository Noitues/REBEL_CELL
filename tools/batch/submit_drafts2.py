"""Submit round-2 design-draft batches: one Message Batch per <name>.jsonl, ids merged into <dir>/batch_ids.json.

    python tools/batch/submit_drafts2.py <dir> station,firmware      # names = jsonl stems in <dir>
    python tools/batch/submit_drafts2.py <dir> retry                 # retry.jsonl -> batch id key "retry<N>"

Credentials: ANTHROPIC_API_KEY or the Windows user variable of that name; never printed.
Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_drafts import api_key  # noqa: E402


def main() -> int:
    d = Path(sys.argv[1])
    names = [n for n in sys.argv[2].split(",") if n]
    client = anthropic.Anthropic(api_key=api_key())
    ids_path = d / "batch_ids.json"
    ids = json.loads(ids_path.read_text(encoding="utf-8")) if ids_path.exists() else {}
    for n in names:
        reqs = [json.loads(l) for l in (d / f"{n}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        b = client.messages.batches.create(requests=reqs)
        key = n if n != "retry" else f"retry{sum(1 for k in ids if k.startswith('retry')) + 1}"
        ids[key] = b.id
        ids_path.write_text(json.dumps(ids, indent=1), encoding="utf-8")
        print(f"{key}: {len(reqs)} requests -> {b.id} ({b.processing_status})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
