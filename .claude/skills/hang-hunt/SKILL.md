---
name: hang-hunt
description: Hunt a rare or intermittent hang, freeze, deadlock or crash (for example "stuck on Now Loading 1 in 4 times") by running the build many times with the watchdog on, grouping failures by signature, and testing hypotheses one at a time. Use for any bug that does not reproduce every run, and for boot stalls or loading hangs.
argument-hint: "[symptom] [pc|switch-emulator]"
---

# Hang and crash hunting

Symptom: $ARGUMENTS

## 1. Make it repeatable
- Find the shortest scripted route that can hit it (committed under `tools/test/routes/`).
- Run it many times with the watchdog and event logging on:
  `python .claude/skills/hang-hunt/scripts/loop_runs.py -n 20 --timeout 180 --env ... --collect <log> --sig-file <log> -- <command>`
  Each run keeps its output in `build/test/loops/<time>/run_NNN/`; failures are grouped by the
  normalised tail of the log. Note the failure rate: it is the baseline for every fix.
- If the rate changes with machine load, the bug is timing-dependent; say so.

## 2. Read the dumps (delegate to log-reader for big ones)
For each signature: the last device accesses and DMA, every guest thread with state, priority,
wait queue and backtrace, pending interrupts and masks, and what the stuck thread is polling
(watch that address with a watchpoint variable).

## 3. Check the usual suspects (all seen on Sonic Riders)
- a resume that arrives before the matching suspend and is lost (suspend count clamped at 0)
- data expected to arrive *during* a DMA arriving only at completion (streaming decompressors)
- an interrupt delivered after the guest acknowledged it, or not re-raised when a mask is enabled
  while the status bit is still set
- an interrupt handler's stack overwriting a small thread stack
- a host helper thread sharing a core with the game thread (starvation on the Switch)
- an SDK timing loop that never sees the hardware timing it expects (sample counters, timeouts
  armed after the command was issued)
- write-gather/FIFO bytes not flushed before the guest waits on them

## 4. One hypothesis at a time
Change one thing, rerun the same loop with the same N, compare rates. A fix is [confirmed] only
when the failure rate drops to 0 over enough runs to matter (at least 3x the runs that previously
produced a failure). Record disproved theories in docs/HISTORY.md, with the rate data.
