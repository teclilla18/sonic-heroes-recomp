#!/usr/bin/env python3
"""Run a command N times to catch rare hangs/crashes, and group the failures.

Each run gets its own folder under OUT (default build/test/loops/<timestamp>/) with the
command's stdout/stderr and copies of any --collect files (logs, watchdog dumps). A run is
"hang" if it hits --timeout, "crash" if it exits non-zero, else "ok" (or "ok?" when --expect
text is missing from the output). Failures are grouped by a signature: the last --sig-lines
non-empty lines of the chosen source with numbers and addresses normalised.

Example (host build, scripted route into a race, watchdog on):
  loop_runs.py -n 20 --timeout 180 --env GAME_WATCHDOG=30 --env GAME_INPUT=@tools/test/routes/race.txt \
      --collect build/host/game.log --sig-file build/host/game.log -- build/host/game.exe baserom/game.iso

Everything after "--" is the command. Paths in --collect/--sig-file are relative to the cwd.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

# Windows pipes default to the ANSI code page; Claude Code reads UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

NORM = [(re.compile(r"\b(?:0x)?[0-9A-Fa-f]{8,16}\b"), "<addr>"), (re.compile(r"\d+(?:\.\d+)?"), "#")]


def signature(text: str, n: int) -> tuple[str, str]:
    tail = [l.strip() for l in text.splitlines() if l.strip()][-n:]
    norm = []
    for line in tail:
        for pat, rep in NORM:
            line = pat.sub(rep, line)
        norm.append(line)
    joined = "\n".join(norm)
    return hashlib.sha1(joined.encode()).hexdigest()[:10], "\n".join(tail)


def main() -> int:
    argv = sys.argv[1:]
    if "--" not in argv:
        print(__doc__)
        return 2
    split = argv.index("--")
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=10)
    ap.add_argument("--timeout", type=float, default=120)
    ap.add_argument("--env", action="append", default=[], help="KEY=VALUE (repeatable)")
    ap.add_argument("--collect", action="append", default=[], help="file to copy after each run")
    ap.add_argument("--sig-file", help="file whose tail forms the signature (default: stdout+stderr)")
    ap.add_argument("--sig-lines", type=int, default=6)
    ap.add_argument("--expect", help="text that a successful run prints/logs")
    ap.add_argument("--out", help="output folder")
    ap.add_argument("--stop-after", type=int, default=0, help="stop after this many failures (0 = never)")
    args = ap.parse_args(argv[:split])
    cmd = argv[split + 1:]

    out = Path(args.out or f"build/test/loops/{time.strftime('%Y%m%d-%H%M%S')}")
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    for kv in args.env:
        k, _, v = kv.partition("=")
        env[k] = v

    results = []
    groups = defaultdict(list)
    failures = 0
    for i in range(1, args.n + 1):
        run_dir = out / f"run_{i:03d}"
        run_dir.mkdir(exist_ok=True)
        for c in args.collect:  # stale logs from a previous run would poison the signature
            if Path(c).exists():
                Path(c).unlink()
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, env=env, capture_output=True, timeout=args.timeout)
            status = "ok" if proc.returncode == 0 else f"crash({proc.returncode})"
            stdout, stderr = proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as exc:
            status, stdout, stderr = "hang", exc.stdout or b"", exc.stderr or b""
        elapsed = time.time() - t0
        (run_dir / "stdout.txt").write_bytes(stdout)
        (run_dir / "stderr.txt").write_bytes(stderr)
        for c in args.collect:
            if Path(c).exists():
                shutil.copy2(c, run_dir / Path(c).name)
        text = (stdout + stderr).decode("utf-8", errors="replace")
        if args.sig_file and (run_dir / Path(args.sig_file).name).exists():
            text = (run_dir / Path(args.sig_file).name).read_text(encoding="utf-8", errors="replace")
        if status == "ok" and args.expect and args.expect not in text:
            status = "ok?"
        sig, tail = signature(text, args.sig_lines)
        results.append((i, status, elapsed, sig))
        if status != "ok":
            failures += 1
            groups[(status.split("(")[0], sig)].append((i, tail))
        print(f"run {i:3d}: {status:10s} {elapsed:7.1f}s  sig {sig}", flush=True)
        if args.stop_after and failures >= args.stop_after:
            break

    summary = [f"{len(results)} runs, {failures} not ok, output in {out}"]
    for (kind, sig), runs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        summary.append(f"\n{kind} x{len(runs)} sig {sig}: runs {', '.join(str(r) for r, _ in runs)}")
        summary.append("  tail:\n    " + runs[0][1].replace("\n", "\n    "))
    text = "\n".join(summary)
    (out / "summary.txt").write_text(text, encoding="utf-8")
    print("\n" + text)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
