---
name: analyze-log
description: Analyse a runtime log, profile, watchdog dump or crash report from the port (PC, emulator or hardware) and return a short evidence-based verdict on what limits performance or what went wrong. Use whenever a log or dump is more than a few hundred lines, after every hardware test, and when the user pastes or points to log files.
context: fork
agent: log-reader
argument-hint: "[log file or folder] [question]"
---

Analyse: $ARGUMENTS

1. Start with the summariser instead of reading the file:
   `python .claude/skills/analyze-log/scripts/summarize_log.py <log>`
   It groups `[tag]` lines by shape and gives min/median/p95/max per number. Use `--tags` to focus,
   `--worst TAG:SLOT:N` for the worst lines, `--from/--to` for a time window.
2. Read only the specific line ranges the summary points at.
3. Map guest addresses to names with the symbols file and the linker map listed in
   CLAUDE.local.md (both are local, in build/ or config/; never copy them into docs).
4. If there is a previous comparable run (earlier hardware test, PC baseline), compare the same
   numbers side by side.

Answer in this shape, under ~40 lines:
- **Verdict**: one or two sentences (e.g. "game-thread bound: 19 ms work per frame vs 16.7 ms").
- **Evidence**: the numbers, each with its log line reference.
- **Anomalies**: anything unexpected, even if unrelated to the question.
- **Hypotheses**: ranked, each tagged [likely]/[uncertain], each with the measurement that would
  confirm or kill it.
- **Next measurement**: the cheapest one that splits the top hypotheses.
Quote at most five log lines in total.
