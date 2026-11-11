"""PreToolUse hook (Read): enforces the CLAUDE.md token budget.

A whole-file Read (no offset/limit) of a large Markdown file under docs/, or of
any large .log file, is refused. For Markdown the reply lists the headings with
line numbers, so the retry reads one section with offset/limit.
"""
import json
import os
import sys

MAX_LINES = 300
MAX_BYTES = 40_000

raw = sys.stdin.buffer.read().decode("utf-8", "replace")
try:
    ti = json.loads(raw).get("tool_input", {}) or {}
except ValueError:
    sys.exit(0)

path = ti.get("file_path") or ""
if not path or ti.get("offset") or ti.get("limit"):
    sys.exit(0)

norm = path.replace("\\", "/").lower()
is_doc = norm.endswith(".md") and "/docs/" in norm
is_log = norm.endswith(".log")
if not (is_doc or is_log) or not os.path.isfile(path):
    sys.exit(0)

try:
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
except OSError:
    sys.exit(0)

if len(lines) <= MAX_LINES and os.path.getsize(path) <= MAX_BYTES:
    sys.exit(0)

msg = [f"Blocked: {os.path.basename(path)} has {len(lines)} lines; "
       "the token budget says never read a whole file this size."]
if is_log:
    msg.append("Grep for the tags you need ([perf], [hitch], [deko3d], [crash] ...) "
               "and read only those lines, or hand the log to the log-reader subagent.")
else:
    heads = [f"{i}: {l.rstrip()}" for i, l in enumerate(lines, 1) if l.startswith("#")]
    msg.append("Grep it, or Read one section with offset/limit. Headings (line: text):")
    msg.extend(heads[:80])
    if len(heads) > 80:
        msg.append(f"... {len(heads) - 80} more headings; grep for the one you need.")
print("\n".join(msg), file=sys.stderr)
sys.exit(2)
