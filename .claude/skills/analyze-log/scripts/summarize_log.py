#!/usr/bin/env python3
"""Summarize a port log made of "[tag] ..." lines without reading it all into context.

For every tag, lines are grouped by "shape" (the line with each number replaced by #).
Each shape gets a count, an example, and min/median/p95/max for every number slot, so
"[perf] 58.2 fps, game 12.1 ms, gpu 3.0 ms" becomes one row with stats per slot.

Also lists lines that look like errors, and optionally the worst N lines of one shape.

Usage:
  summarize_log.py LOG [--tags perf,hitch] [--worst hitch:0:10] [--from N] [--to N]
    --worst TAG:SLOT:N   show the N lines with the largest number in SLOT (0-based)
                         among lines of TAG, with line numbers
"""
import argparse
import re
import statistics
import sys
from collections import defaultdict

# Windows pipes default to the ANSI code page; Claude Code reads UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

TAG = re.compile(r"^\s*(?:\S+\s+)?\[([A-Za-z0-9_.:-]+)\]")
NUM = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w.])")
HEX = re.compile(r"\b(?:0x)?[0-9A-Fa-f]{8}\b")
ERRORISH = re.compile(r"\b(error|abort|assert|panic|crash|fatal|exception|fail(?:ed|ure)?|timeout|hang|stuck)\b", re.I)


def shape_of(line: str) -> str:
    s = HEX.sub("<addr>", line.strip())
    return NUM.sub("#", s)


def numbers(line: str) -> list[float]:
    s = HEX.sub(" ", line)
    return [float(x) for x in NUM.findall(s)]


def pct(values, p):
    values = sorted(values)
    k = min(len(values) - 1, max(0, round(p * (len(values) - 1))))
    return values[k]


def fmt(v: float) -> str:
    return f"{v:.0f}" if abs(v - round(v)) < 1e-9 and abs(v) >= 10 else f"{v:.3g}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--tags", help="comma-separated tags to include (default: all)")
    ap.add_argument("--worst", help="TAG:SLOT:N")
    ap.add_argument("--from", dest="start", type=int, default=1)
    ap.add_argument("--to", dest="end", type=int, default=10**12)
    ap.add_argument("--max-shapes", type=int, default=8, help="shapes shown per tag")
    args = ap.parse_args()
    wanted = set(args.tags.split(",")) if args.tags else None

    groups = defaultdict(lambda: defaultdict(list))   # tag -> shape -> [(lineno, line, nums)]
    errors, untagged = [], 0
    total = 0
    with open(args.log, encoding="utf-8", errors="replace") as fh:
        for n, line in enumerate(fh, 1):
            if n < args.start or n > args.end:
                continue
            total += 1
            m = TAG.match(line)
            if ERRORISH.search(line) and len(errors) < 40:
                errors.append((n, line.rstrip()[:200]))
            if not m:
                untagged += 1
                continue
            tag = m.group(1)
            if wanted and tag not in wanted:
                continue
            groups[tag][shape_of(line)].append((n, line.rstrip(), numbers(line)))

    print(f"{args.log}: {total} lines in range, {untagged} untagged, {len(groups)} tags")
    for tag in sorted(groups, key=lambda t: -sum(len(v) for v in groups[t].values())):
        shapes = groups[tag]
        count = sum(len(v) for v in shapes.values())
        print(f"\n[{tag}] {count} lines, {len(shapes)} shapes")
        for shape, rows in sorted(shapes.items(), key=lambda kv: -len(kv[1]))[: args.max_shapes]:
            print(f"  x{len(rows)}  first@{rows[0][0]} last@{rows[-1][0]}")
            print(f"    e.g. {rows[-1][1][:180]}")
            width = min(len(r[2]) for r in rows)
            if width and len(rows) > 1:
                stats = []
                for slot in range(min(width, 12)):
                    vals = [r[2][slot] for r in rows]
                    if max(vals) == min(vals):
                        continue
                    stats.append(f"#{slot}: min {fmt(min(vals))} med {fmt(statistics.median(vals))} "
                                 f"p95 {fmt(pct(vals, 0.95))} max {fmt(max(vals))}")
                for s in stats:
                    print(f"    {s}")
        if len(shapes) > args.max_shapes:
            print(f"  ... {len(shapes) - args.max_shapes} rarer shapes not shown (use --tags {tag})")

    if errors:
        print("\nError-like lines (first 40):")
        for n, line in errors:
            print(f"  @{n}: {line}")

    if args.worst:
        tag, slot, count = args.worst.split(":")
        slot, count = int(slot), int(count)
        rows = [r for shapes in [groups.get(tag, {})] for v in shapes.values() for r in v if len(r[2]) > slot]
        rows.sort(key=lambda r: -r[2][slot])
        print(f"\nWorst {count} [{tag}] lines by number slot {slot}:")
        for n, line, _ in rows[:count]:
            print(f"  @{n}: {line[:200]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
