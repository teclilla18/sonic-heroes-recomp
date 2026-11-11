# Instructions for coding agents (Claude Code and others)

Goal: play Sonic Heroes (GameCube, USA, G9SE8P rev 0) natively by static recompilation: the PowerPC code becomes C
on each contributor's machine from their own disc; this repo holds only our source. Targets in order (user's
decision, 2026-11-11): **Nintendo Switch first**, then Windows PC, Android, Linux / Steam Deck, iOS. The PC build
is still the fast test loop; it is just not released first.

Current status (loaded automatically):
@STATE.md

## This repo is a fork of the Sonic Riders port

- Forked 2026-11-11 from the Riders port's `main`; git remote `riders` is the local Riders repo. Keep the layout
  and every shared file identical to Riders so fixes cherry-pick both ways (`git fetch riders`,
  `git cherry-pick <sha>`; Heroes fixes that help Riders go back the same way).
- So: internal names stay as Riders has them (`SR_*` variables, `sr_` code names). Only player-facing names say
  Heroes (app `sonicheroes`, zips `SonicHeroes-*`, folders, title/package IDs). Game-specific code and data go in
  `config/G9SE8P/` and clearly marked game files, not scattered through shared runtime files.
- Docs marked **Inherited** still hold Riders' facts; Riders' history is in `docs/archive/riders/` (read-only).

## Hard rules

1. **Game-data guard.** Never commit, paste or upload anything derived from the game: ISO/disc images, DOL, REL,
   `baserom/`, extracted assets, disassembly, recompiled output (`build/`, `build/gen/`), `.nro`/`.nsp`/`.exe`,
   dtk output (`config/*/symbols.txt`, `splits.txt`), saves, console keys. Small facts (addresses,
   function names, register values) are fine; blocks of disassembly or recompiled code are not. One exception
   (user's decision, 2026-11-07): the shader-key list `config/G9SE8P/shader_keys.txt` (GPU TEV register settings)
   is tracked, because release builds without it run Switch races at ~30 fps; other key files stay local.
2. Before every commit and push run `python tools/check_no_game_data.py` and check `git status --ignored`. If
   anything questionable would be included, **stop and ask the user**. Never `--no-verify` or weaken the check.
3. **Push to GitHub at the end of every session**, after rule 2 passes.
4. No personal details in tracked files (home paths, SD drive letters, console setup, emails): write `<repo>`,
   `<home>`, `<sd>`. Machine-specific notes go in `CLAUDE.local.md` (gitignored, loads automatically).
5. Never modify the user's original disc image. Work on copies.

## Hard-won lessons

- Shared GLSL (deko3d's uam compiler miscompiles): never index a vector or a local array with a runtime value (use
  `pick()`, `comp()`, `cinput()`, `ainput()`, `reg()`); in vertex shaders no loop-carried vec4 accumulator seeded
  from a parameter and no `continue` in vector-accumulating loops. After shader changes every dksh in
  `build/switch/shaders/` must report `per_warp_scratch 0`.
- Every host helper thread on the Switch is pinned off core 0 (the game thread). Horizon does not time-slice equal
  priorities: a thread that must keep up (the audio mixer) runs one step above its core neighbour.
- Eden: v0.1.1 only (v0.2.1 fails in dkDeviceCreate); never start it minimized (use `-WindowStyle Hidden`).
- Look at frames through the port's own captures (`SR_SCREENSHOT`, `shot_*.bmp`, switch-remote screenshots), never
  desktop screenshots. PC test runs use `SR_MINIMIZED=1` (the user may be using the PC).
- Switch CPU gains can't be measured on PC or Eden; only hardware. The test console (OLED) is overclocked: docked CPU 1785
  / GPU 1152 / MEM 2133, handheld CPU 1785 / GPU 614 / MEM 2133; state the mode and clocks with every hardware number. Hardware `[profile]` charges a caller's work
  after a call to the callee.
- In hardware logs check `[deko3d]` "specialized shaders for N of M states": a fallback to the ubershader silently
  multiplies GPU time (shader keys must contain only bits the shader reads).

## Where things are (open only what the task needs; grep, don't read whole files)

- **STATE.md**: imported above (status, open items, next hardware test); rewritten at the end of every session.
- **docs/notes/recon.md**: the Heroes disc (executables, 18 RELs, libraries, risks).
- **docs/REFERENCE.md**: a short index of the topic notes in `docs/notes/` (build-and-test with **Quick commands**,
  android, debug-variables, architecture). Open only the note you need, grep inside it.
- **docs/HISTORY.md**: dated sessions and hardware tests since the fork, oldest first (Riders': `docs/archive/riders/`).
  Grep a date, `#issue`, address or `SR_` (`grep -rn <x> docs/HISTORY.md docs/archive/`).
- **docs/MAP.md**: where each topic lives (file + function names). Use it before opening code.
- docs/ONLINE.md (online play), docs/PERF.md (perf test), docs/MODDING.md, docs/BUILDING.md, CONTRIBUTING.md.
- Code: `tools/recomp/` recompiler, `config/G9SE8P/` (`hle.txt`, `patches.txt`), `runtime/src/` devices and runtime,
  `runtime/src/platform/{switch,host}/`, `runtime/shaders/` shared GX shader.

## Status words and regressions

- Keep four states apart, in STATE.md and HISTORY.md: **implemented** (code in), **tested** (by us: say how, e.g.
  PC route, phone with adb taps, hardware + clocks), **accepted** (the user played it and said it is fine),
  **released** (in a tagged version). Evidence tags [confirmed] / [likely] / [uncertain] are about what a test proved.
- A partial test is never reported as full validation; "not reproduced" is not "fixed".
- A regression in a release: revert the change first and publish, then look for the real fix. Never stack an
  untested fix on a broken release.

## Token budget

- Search first (`grep -n`, MAP.md), then read only those lines; never read a whole file over ~200 lines.
- Cap every output (`| head`, `| tail`, `grep -c`, `cut -c1-120`); no raw logs or big directory listings.
- Long runs go to a file in the background; read only the result lines. Look at images only when the picture is
  what is being checked, shrunk or cropped first.
- Keep `build/` tidy: old test outputs go to `build/old/`. Two or three related items per session.

## Build and test (the PC build is the fast test loop)

- Skills: `/recon`, `/emu-run`, `/hw-test`, `/render-bisect`, `/hang-hunt`, `/ref-compare`, `/analyze-log`,
  `/release`, `/wrap-up`. Subagents: `log-reader` (logs), `re-investigator` (what a function/address does).

- First time: `setup\setup.ps1 -Iso <image.iso> -Target both -NoSd -Yes`. Then `python configure.py --target host
  --toolchain mingw --llvm-mingw <tools>\llvm-mingw --sdl <tools>\sdl2` (or `--target switch --devkitpro
  <tools>\devkitpro`), `--imgui <tools>\imgui` once, and `ninja`. Variables: docs/notes/debug-variables.md.
- **Before every release: the cold Windows Sandbox test, PC and Android** (`tools/sandbox_test.py`, from the
  release zips, no download cache; ask the user before launching). Procedure: docs/notes/build-and-test.md.

## End of every session

Run the `/wrap-up` skill (`.claude/skills/wrap-up/SKILL.md`). Never skip it. It covers:


1. Rewrite STATE.md in place (never append; under ~120 lines; newest facts only).
2. Add a short dated entry at the end of docs/HISTORY.md: what was wrong, how it was found, the fix, what is
   unproven; mark [confirmed] / [likely] / [uncertain]. Durable facts (addresses, variables, procedures) also go
   into the matching `docs/notes/` file (new topic: new note + a row in REFERENCE.md; superseded: `git mv` to
   `docs/archive/`). User-visible changes go in CHANGELOG.md.
   **Road to v1.0 card (user's rule, 2026-11-11):** after every change that moves an area (a stage or mode plays,
   a platform boots, a hardware fps change, a feature lands), update AREAS/UPDATED in `tools/make_progress.py`, run
   it (redraws `docs/images/progress.svg`) and update README's "Road to v1.0" table and alt text in the same commit.
   Bars go up only for what was **tested** (PC route, Eden, hardware), never for code that is only written.
3. Guard + `git status --ignored`, commit, push. PRs: one topic; say what changed, why and how it was tested (PC
   route and frames, emulator, hardware, `[perf]` numbers); end commit messages with your agent's co-author line.
