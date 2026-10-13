"""API-equivalent cost of a Claude Code agent transcript (for playtester benchmarks, doc 05).

    python tools/playtest/bench_transcript.py <transcript.jsonl> [--json out.json]

Sums the usage of every assistant message (deduplicated by message id) per model and prices it
at first-party API rates, so a `playtester` subagent run can be compared with a harness.py run
(whose cost.json uses the same table). Cache writes are priced by their TTL when the transcript
records it (5 min 1.25x, 1 h 2x input), else at 1 h. Also counts tool calls (= game actions,
roughly) and screenshots read.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# $ per million: input, output, cache read
PRICES = {
    "claude-haiku-5-5": (0.10, 0.50, 0.01),
    "claude-sonnet-5-5": (2.00, 10.00, 0.20),
    "claude-opus-5-5": (4.00, 20.00, 0.20),
}


def price_for(model: str) -> tuple[float, float, float]:
    for k, v in PRICES.items():
        if model.startswith(k):
            return v
    return PRICES["claude-sonnet-5-5"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("transcript")
    ap.add_argument("--json")
    a = ap.parse_args()
    seen: dict[str, dict] = {}
    tools: dict[str, int] = {}
    shots = 0
    first_t = last_t = None
    for line in Path(a.transcript).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = e.get("timestamp")
        if ts:
            first_t = first_t or ts
            last_t = ts
        msg = e.get("message") or {}
        if msg.get("role") == "assistant" and msg.get("usage"):
            seen[msg.get("id") or str(len(seen))] = {"model": msg.get("model", ""), "usage": msg["usage"]}
            for b in msg.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    tools[b.get("name", "?")] = tools.get(b.get("name", "?"), 0) + 1
                    if b.get("name") == "Read" and str((b.get("input") or {}).get("file_path", "")).lower().endswith(".png"):
                        shots += 1
    per: dict[str, dict] = {}
    for m in seen.values():
        u = m["usage"]
        pin, pout, pcr = price_for(m["model"])
        cc = u.get("cache_creation") or {}
        w5 = cc.get("ephemeral_5m_input_tokens")
        w1 = cc.get("ephemeral_1h_input_tokens")
        cw = u.get("cache_creation_input_tokens", 0) or 0
        if w5 is None and w1 is None:
            w5, w1 = 0, cw
        usd = ((u.get("input_tokens", 0) or 0) * pin + (u.get("output_tokens", 0) or 0) * pout
               + (u.get("cache_read_input_tokens", 0) or 0) * pcr + (w5 or 0) * pin * 1.25 + (w1 or 0) * pin * 2) / 1e6
        p = per.setdefault(m["model"], {"n": 0, "in": 0, "out": 0, "cache_read": 0, "cache_write": 0, "usd": 0.0})
        p["n"] += 1
        p["in"] += u.get("input_tokens", 0) or 0
        p["out"] += u.get("output_tokens", 0) or 0
        p["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
        p["cache_write"] += cw
        p["usd"] += usd
    total = sum(p["usd"] for p in per.values())
    out = {"calls": per, "usd": round(total, 4), "tool_calls": tools, "screenshots_read": shots,
           "blackbox_calls": tools.get("Bash", 0), "first": first_t, "last": last_t}
    print(json.dumps(out, indent=1))
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
