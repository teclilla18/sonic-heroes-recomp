---
name: wrap-up
description: End-of-session routine for this repo - rewrite STATE.md, add the dated HISTORY.md entry, update notes and CHANGELOG, run the game-data guard, commit and push, then hand the user a ready-to-paste prompt for starting the next session. Use whenever the user says wrap up, end the session, we're done, save progress, commit and push, or when a work session is clearly finishing.
---

# Wrap up the session

Every session ends with these steps, in this order. The next session starts from STATE.md alone, so anything not written down here is lost.

## 1. Rewrite STATE.md

- Rewrite it in place. Never append. Keep it under ~120 lines, newest facts only.
- Keep the four status words apart: **implemented** (code in), **tested** (by us; say how: PC route, phone with adb taps, hardware with mode and clocks), **accepted** (the user played it and said it's fine), **released** (in a tagged version).
- A partial test is never reported as full validation. "Not reproduced" is not "fixed".
- Update "open items" and "next hardware test" so the next session can start immediately.
- Put the next-session prompt (step 5) in a `## Next session` section at the end of STATE.md, so it survives even if the chat is lost.

## 2. Add the HISTORY.md entry

Add a short dated entry at the end of `docs/HISTORY.md`: what was wrong, how it was found, the fix, and what is unproven. Mark claims [confirmed] / [likely] / [uncertain].

The file is large and the read guard refuses whole-file reads, so read only its last ~40 lines (Read with an offset) before editing, or append with a shell command.

## 3. Durable facts and user-visible changes

- Addresses, debug variables and procedures also go into the matching `docs/notes/` file.
- A new topic gets a new note plus a row in `docs/REFERENCE.md`. A superseded note is `git mv`'d to `docs/archive/`.
- User-visible changes go in `CHANGELOG.md`.
- **Road to v1.0 card:** if anything this session moved an area (stages/modes playable, graphics, Switch fps,
  platforms, 2-player, features), edit AREAS and UPDATED in `tools/make_progress.py`, run it, and update the README
  "Road to v1.0" table and the image's alt text to match. Do it in the same commit as the change when you can.
- If the user corrected you this session in a way that will matter again, propose a one-line addition to CLAUDE.md (don't add it without asking).

## 4. Guard, commit, push

1. Run `python tools/check_no_game_data.py` and `git status --ignored`. If anything questionable would be included, **stop and ask the user**.
2. Commit. One topic per commit; the message says what changed, why, and how it was tested. End it with your co-author line.
3. Push.

The guard hook in `.claude/hooks/guard.py` also runs the check before every commit and push. If it blocks, show the user its output and ask. Never work around it.

## 5. Hand over the next-session prompt

End with a short summary (what was done, what is still unproven), then the **next-session prompt** in its own code block, so the user can copy it straight into a fresh session.

STATE.md loads automatically at the start of every session, so the prompt must not recap history. Its job is to point the next session at the right work in the right way:

- **One goal.** One or two related items, the most valuable open item first.
- **Where to look.** The files and functions (from `docs/MAP.md`), the `docs/notes/` file, the HISTORY date or `#issue` to grep. This saves the next session a search.
- **How to start.** Say whether to begin in plan mode (several files, or the approach is unclear) or go straight to the fix. Name the skill or subagent to use (`/hw-test`, `log-reader`).
- **What's waiting on the user.** If results are pending (a hardware test, a screenshot, a playtest), leave a placeholder in angle brackets for the user to fill in.
- **How to verify.** The test that proves it: PC route and frames, Eden, hardware with mode and clocks, `[perf]` numbers to compare.
- At most ~8 lines. Plain sentences, no headers.

Example of the shape (contents invented):

```
Continue the 4-player Switch fps work (#2).
Hardware test 23 results: <paste the user's report; logs are in build/switch/hw23/>.
Have log-reader summarise those logs against hw17 first.
Then plan the next cut to GP-thread cost (docs/MAP.md -> gx_render.c, decode_fast); plan mode, it touches several files.
Verify on the PC 4P route with SR_GPSLOW, then prepare the next console test with /hw-test.
Still unproven: whether the faster vertex decode helps on hardware [uncertain].
```
