"""PreToolUse hook (Bash and PowerShell): enforces CLAUDE.md hard rules 1-3.

- blocks --no-verify (the game-data guard must never be bypassed)
- blocks force pushes
- before any git commit or push: requires core.hooksPath = tools/git-hooks
  and a passing `python tools/check_no_game_data.py`

Exit 2 blocks the command; the stderr text is shown to Claude as the reason.
"""
import json
import os
import re
import subprocess
import sys

raw = sys.stdin.buffer.read().decode("utf-8", "replace")
try:
    cmd = json.loads(raw).get("tool_input", {}).get("command", "") or ""
except ValueError:
    sys.exit(0)

repo = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def block(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


# One git invocation = text up to the next ; | & or newline.
GIT = r"\bgit\b[^;|&\n]*?"

if re.search(r"--no-verify\b", cmd) or re.search(GIT + r"\bcommit\b[^;|&\n]*\s-n\b", cmd):
    block("Blocked: never bypass the game-data guard (CLAUDE.md hard rule 2). "
          "Fix whatever the check reports, or stop and ask the user.")

if re.search(GIT + r"\bpush\b[^;|&\n]*(--force|\s-f\b)", cmd):
    block("Blocked: force pushes are not allowed from Claude Code. Ask the user.")

if re.search(GIT + r"\b(commit|push)\b", cmd):
    hp = subprocess.run(["git", "-C", repo, "config", "core.hooksPath"],
                        capture_output=True, text=True).stdout.strip()
    if not hp.replace("\\", "/").rstrip("/").endswith("tools/git-hooks"):
        block("Blocked: the pre-commit guard is not active in this clone. "
              "Run `git config core.hooksPath tools/git-hooks`, then retry.")
    check = os.path.join(repo, "tools", "check_no_game_data.py")
    if not os.path.isfile(check):
        block("Blocked: tools/check_no_game_data.py not found. Ask the user.")
    r = subprocess.run([sys.executable, check], cwd=repo,
                       capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        tail = (r.stdout + r.stderr).strip()[-1500:]
        block("Blocked: tools/check_no_game_data.py failed. Do not commit or push; "
              "show the user this output and ask what to do:\n" + tail)

sys.exit(0)
