---
name: release
description: Release checklist for a new tagged version - guard, CHANGELOG, release zips, the cold Windows Sandbox test on PC and Android, then publishing. Only run when the user types /release.
disable-model-invocation: true
argument-hint: "<version, e.g. 0.6.0>"
---

# Release $ARGUMENTS

The exact commands live in `docs/notes/build-and-test.md`. Grep it for "release" and "sandbox" and follow it; this file is the checklist and the rules around it. If the two disagree, the note wins; tell the user so this skill can be fixed.

## Before building

1. Read STATE.md. List what goes into this version and its status: implemented, tested, accepted. Anything only "implemented" or a partial test gets flagged to the user before going further. Releases are built from tested work.
2. Check that `CHANGELOG.md` has an entry for this version covering every user-visible change. Draft it if missing and show it to the user.
3. Run `python tools/check_no_game_data.py` and `git status --ignored`. Stop and ask if anything questionable shows up.

## Build the release

4. Build the release zips with `tools/make_release.py --version $ARGUMENTS` (it zips the files tracked at HEAD, guard-checked).
5. **Ask the user before launching** the cold Windows Sandbox test (`tools/sandbox_test.py`). It runs from the release zips with no download cache, for **PC and Android**. Report the result for each platform separately.

## Publish

6. Only after both sandbox tests pass, ask the user before tagging and before uploading anything. Never publish on your own.
   The release page text is `docs/releases/<version>.md` when it exists (`gh release create ... --notes-file`); alpha and beta versions go up as pre-releases (`--prerelease`).
7. Update STATE.md: the shipped items are now **released** in $ARGUMENTS.

## If a release turns out broken

Revert the change first and publish that, then look for the real fix. Never stack an untested fix on a broken release.
