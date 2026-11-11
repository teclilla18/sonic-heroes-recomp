---
name: hw-test
description: Prepare a Switch hardware test - build the NRO, smoke-test it in Eden, put it on the SD card with the right env.txt, and write the user a short test checklist. Also use when the user brings back hardware logs or results. Use whenever the user mentions testing on the Switch, the console, the SD card, a hardware test, or Eden.
---

# Switch hardware test

The exact commands and paths live in `docs/notes/build-and-test.md` (see **Quick commands**) and the debug variables in `docs/notes/debug-variables.md`. Grep them rather than reading whole files. The SD card location and console setup are in `CLAUDE.local.md`.

## 1. Decide what the test should prove

Write down, from STATE.md's "next hardware test", what this build changes and what result would confirm it. One or two questions per test, so the answer is clear.

## 2. Build

- `python configure.py --target switch ...` (flags in the build note), then `ninja`.
- Stop on build errors. Don't hand the user a stale NRO.
- After any shader change, every dksh in `build/switch/shaders/` must report `per_warp_scratch 0`.

## 3. Smoke-test in Eden

- Eden **v0.1.1 only** (v0.2.1 fails in dkDeviceCreate).
- Never start it minimized; use `-WindowStyle Hidden`. Minimized gives a zero-size surface and stalls or crashes.
- Look at frames only through the port's own captures (`SR_SCREENSHOT`, `shot_*.bmp`), never desktop screenshots.
- Eden numbers are not hardware numbers, especially CPU timings. Use Eden only to check it boots and renders.

## 4. Deploy

- Copy the NRO to the SD folder from `CLAUDE.local.md`.
- Set `env.txt` for what this test needs (for example `SR_PROFILE=1` for a CPU profile). Remove variables from earlier tests that would skew this one.
- Never put the NRO, the disc image or keys anywhere tracked.

## 5. Give the user a short checklist

At most ~8 lines:
- what to do (which mode, track, player count),
- what to look at,
- what to report: **docked or handheld, and the clocks** (the test console is overclocked; every hardware number needs mode and clocks), FPS counter readings, and screenshots via the settings menu's "Save screenshot" for anything that looks wrong,
- which log files to bring back.

## 6. When results come back

Hand the logs to the **log-reader** subagent instead of reading them here. Then record the result in STATE.md with the right status word. Hardware confirmation by the user means **tested**; "it plays fine" from the user means **accepted**.
