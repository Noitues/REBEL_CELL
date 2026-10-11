"""Submit a .jsonl payload to the Anthropic Message Batches API and fetch its results.

    python tools/batch/submit_batch.py batches/docstrings_core.jsonl            # submit, print the batch id
    python tools/batch/submit_batch.py batches/docstrings_core.jsonl --wait     # submit, poll, write results
    python tools/batch/submit_batch.py --fetch msgbatch_01ABC... --out batches/docstrings_core.results.jsonl
    python tools/batch/submit_batch.py --status msgbatch_01ABC...

Needs the official SDK (`pip install anthropic`) and credentials: ANTHROPIC_API_KEY, or a
profile from `ant auth login`. Nothing from the repo is sent except what the .jsonl holds.

The results file is one JSON object per line as the API returns them ({"custom_id", "result":
{"type": "succeeded"|"errored"|"canceled"|"expired", ...}}), in arbitrary order; ingest by
custom_id (tools/batch/ingest_results.py). Batches finish within 24 h, usually under 1 h;
results stay available 29 days. All token usage in a batch is billed at 50 %.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

try:
    import anthropic
except ImportError:  # pragma: no cover
    print("submit_batch: the anthropic package is missing: pip install anthropic")
    sys.exit(2)


def load_requests(path: Path) -> list[dict]:
    reqs = []
    with path.open(encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if "custom_id" not in obj or "params" not in obj:
                raise SystemExit(f"line {n}: not a batch request (needs custom_id and params)")
            reqs.append(obj)
    ids = [r["custom_id"] for r in reqs]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate custom_id in payload")
    return reqs


def write_results(client: anthropic.Anthropic, batch_id: str, out: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for r in client.messages.batches.results(batch_id):
            fh.write(r.model_dump_json() + "\n")
            counts[r.result.type] = counts.get(r.result.type, 0) + 1
    return counts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jsonl", nargs="?")
    ap.add_argument("--wait", action="store_true", help="poll until ended, then write the results")
    ap.add_argument("--poll", type=int, default=60, help="seconds between polls")
    ap.add_argument("--fetch", metavar="BATCH_ID", help="fetch results of an existing batch")
    ap.add_argument("--status", metavar="BATCH_ID")
    ap.add_argument("--out", default="", help="results file (default: <payload>.results.jsonl)")
    args = ap.parse_args()
    client = anthropic.Anthropic()

    if args.status:
        b = client.messages.batches.retrieve(args.status)
        print(f"{b.id}: {b.processing_status} {b.request_counts}")
        return 0

    if args.fetch:
        out = Path(args.out or f"batches/{args.fetch}.results.jsonl")
        counts = write_results(client, args.fetch, out)
        print(f"submit_batch: wrote {out} {counts}")
        return 0

    if not args.jsonl:
        ap.error("payload .jsonl required")
    payload = Path(args.jsonl)
    reqs = load_requests(payload)
    batch = client.messages.batches.create(requests=reqs)
    print(f"submit_batch: {batch.id} {batch.processing_status} ({len(reqs)} requests)")
    payload.with_suffix(".batch_id").write_text(batch.id + "\n", encoding="utf-8")
    if not args.wait:
        print(f"submit_batch: later: python tools/batch/submit_batch.py --fetch {batch.id} --out {payload.with_suffix('.results.jsonl')}")
        return 0

    while True:
        b = client.messages.batches.retrieve(batch.id)
        if b.processing_status == "ended":
            break
        print(f"  {b.processing_status}: processing={b.request_counts.processing} succeeded={b.request_counts.succeeded} errored={b.request_counts.errored}")
        time.sleep(args.poll)
    out = Path(args.out or payload.with_suffix(".results.jsonl"))
    counts = write_results(client, batch.id, out)
    print(f"submit_batch: ended; wrote {out} {counts}")
    return 0 if counts.get("errored", 0) == 0 and counts.get("expired", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
