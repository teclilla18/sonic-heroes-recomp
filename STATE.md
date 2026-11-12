# State (2026-11-12, end: 0.1.0-alpha.1 released as a GitHub pre-release)

Read this at the start of every session. Rewrite it in place at the end of each session (never append). Stories
behind each line: `grep` the date or topic in [docs/HISTORY.md](docs/HISTORY.md) (Riders' history:
docs/archive/riders/). Disc facts: [docs/notes/recon.md](docs/notes/recon.md).

## Where things stand

Phase 1 (boot and play). The game boots and plays Seaside Hill and the special stage on PC and Switch; Egg Fleet
starts on PC. **Released: 0.1.0-alpha.1 (test build, not for playing).** README Road to v1.0 card: 30%.

| Target (user's order) | Status |
|---|---|
| 1. Switch | **released** (alpha.1 test build); tested on the OLED: menus, story movie, Seaside Hill (~58-60 fps overclocked), special stage plays through (user) |
| 2. Windows PC | **released** (alpha.1 test build); tested (scripted routes + user play): Seaside Hill, special stage 40, Egg Fleet start, 60 fps |
| 3. Android, 4. Linux / Steam Deck, 5. iOS | not started (backends inherited); not in the first releases |

Repo public (teclilla18/sonic-heroes-recomp). Local `user.email` is the GitHub no-reply address.

## Releases (user's decisions)

- **0.1.0-alpha.1 released 2026-11-12**: GitHub pre-release, tag v0.1.0-alpha.1 = 2fcaac6c, PC + Switch zips, page
  text docs/releases/0.1.0-alpha.1.md (big TEST BUILD warning, how to report, controls section with pictures).
  Before publishing: cold Windows Sandbox PC zip PASS (2 installs, ~4 min; the first run FAILED on Riders' disc
  SHA-1 left in setup, fixed f21d407c); Switch zip setup -NoSd PASS on this PC (warm toolchain; the cold toolchain
  download for Switch untested). The launcher GUI itself was not opened by us.
- **Next release, user's request (2026-11-12): replace the launcher's plain blue with an image the user will
  provide then** (launcher/launcher.cpp: the blue window/side-panel colours; the banner strip already has the
  Reckoman12 art). Ask for the image when preparing the next release.
- Launcher art: banner launcher/banner.jpg (Reckoman12, 1800x519 crop), icon launcher/icon_256/32.png (Nibroc.Rock);
  README credits; pinned by SHA-1 in the guard's OWN_ART.
- First real release later: "decently runnable" on Switch + PC (criteria: memory first-release-scope).
- make_release.py needs `<LOCALAPPDATA>/SonicHeroesSetup/tools`; on this PC run it with LOCALAPPDATA set to a scratch
  folder holding a junction `SonicHeroesSetup/tools` -> `SonicRidersSetup/tools` (HISTORY "2026-11-12 (night)").

## Done 2026-11-12 (HISTORY "late" and "night")

- Switch "Save a bug report" (About tab): zip in switch/sonicheroes/ with info, this and the last run's log,
  settings, env.txt, newest Atmosphere crash report; the open log is copied by log_snapshot (the SD card locks it)
  [confirmed on console, handheld CPU 1785 / GPU 614 / MEM 2133]. Zip writer shared: runtime/src/bug_report.c.
- Setup checks the Heroes disc (SHA-1 dd752c8a), region IDs G9SP8P / G9SJ8P [confirmed by Sandbox].
- Earlier today: special stage crash fixed (far REL calls) [accepted]; shadow GPU waits cut [likely]; special stage
  bloom off + steering slider [accepted]; dev stage select (dev builds only) [accepted].

## Open items, in order

1. **Alpha feedback**: read GitHub issues from testers. The PC release is unpacked at
   <home>/Desktop/SonicHeroes-PC-0.1.0-alpha.1 (not yet installed or played; the user may try the launcher).
2. **Remove the Chaos Emerald gear option** (user, 2026-11-12: a Sonic Riders feature): the launcher's checkbox
   (launcher/launcher.cpp ~1011, setting chaos_emerald_shop), g_settings.chaos_emerald (settings.c, game_mods.c,
   GAME_GEAR_* in game_addrs.h) and other Riders gear leftovers (mods_data.c gear names). Keep shared files
   cherry-pickable (game-specific code clearly marked, CLAUDE.md fork rules).
3. **Fit HUD layout** (user, hw12 shots build/hw12/shot_6435, 12977): pause menu off-centre everywhere; the team
   switch icon and Team Blast gauge stay near the centre instead of the right edge. Heroes' stage HUD is placed from
   the widened stage camera when the stage loads (not per-piece 2D: SR_ANCHORLOG sees only the shadow corner), so
   it needs the HUD objects' position code (re-investigator) and a Dolphin 4:3 reference of the pause menu.
   The gx_render.c "edges only in manager state 5" change is implemented; saving box after a stage (hw11
   shot_17183, split in three) not re-checked.
4. **Stage sweep** with SR_DEVSTAGE (keys: notes/re/stage-select.md): every story stage + bosses on PC, then Eden /
   console; crashes, shader keys, rendering vs Dolphin (special stage looks very bright even without bloom).
5. Camera tilt direction in scripted runs: CY=+110 raised the camera (looks down) in build/run1/cam; the user chose
   "stick up = view up" on hardware. Check the SR_INPUT CY sign vs a real pad before relying on it [uncertain].
6. If the Pause -> Quit crash returns (build/hw6/atmo_crash.log): same stack? Then record_backtrace.
7. Later: HD look, widescreen menus, Android. Guard --history still lists 5 pre-fork Riders pictures.

## Hardware / console notes

- Remote: scratchpad `sw.py` (FTP + sys-botbase; copy from session scratchpad 2294dac9, 9921978d or fc12b70e),
  settings from the Riders switch-remote config (CLAUDE.local.md). Git Bash: `MSYS_NO_PATHCONV=1`, sw.py as a
  Windows path; FTP login sometimes times out: retry. The log is locked while the game runs (550 busy).
- User's console SD `switch/sonicheroes/`: NRO = the 0.1.0-alpha.1 release build (built by the Switch zip's setup,
  copy in build/hw13/sonicheroes-alpha1.nro); env.txt empty (old one in build/hw13/env.txt.old). Logs: build/hw13.
- SD on F: is the user's son's console (Sonic Riders + now Sonic Heroes in switch/sonicheroes/: hw13 NRO, same code
  as the release, + disc copy, done at the user's request). Touch it only when the user asks.
- Temp wait counters ([pewho]/[rlock]) are out of git: local build/temp_pewho_rlock_gx_fifo.diff and
  build/temp_pewho_rlock_patches.txt to re-apply.
- Eden v0.1.1: start hidden, never minimized (CLAUDE.md); ~165 s; SR_BUGREPORT=1 works there via env.txt.

## Testing etiquette (user)

All test runs in the background, muted (`SR_NOAUDIO=1`), minimized (`SR_MINIMIZED=1`). PC route script: scratchpad
`route.sh <tag> [ENV=..]` (title, START, story, run forward from 4500; SHOTS=, SECS=) -> build/run1/rt_<tag>/.
**Use a fresh card** (`SR_CARD=<scratchpad>/fresh.raw`, deleted first): build/host-mingw's card has a save that
starts Casino Park. Straight to a stage: `SR_DEVSTAGE=1D` (special) / `0E` (Egg Fleet). Fit widescreen:
`SR_SCREEN=3 SR_WINDOW=1280x720`. Image work: scratchpad venv with Pillow (not in the shared tools Python).

## Shared with the Riders project (not copied)

Toolchains in `<home>/AppData/Local/SonicRidersSetup/tools` (ninja `tools/ninja/ninja.exe`; Switch ninja needs
`DEVKITPRO=<tools>/devkitpro`); llvm-mingw / SDL2 / imgui junctions in `build/ext/`; Eden and Dolphin in the Riders
repo's `build/ext/`. build.ninja holds one target (now: host). Riders cherry-pick candidates (user's call): the
far-branch recompiler fix, deko3d small-image tile fix, F9/SR_POKE tools, the shared bug_report.c + Switch button.
Local git also holds Riders' tags (v0.1.0..v0.8.0, never pushed): dev builds report "v0.8.0-..." as their version.

## Next session

```
Continue Sonic Heroes (STATE.md). First check GitHub issues on 0.1.0-alpha.1 (gh issue list) and triage them.
Then take the Chaos Emerald gear option out (a Sonic Riders feature): the launcher's checkbox and the setting
behind it (open item 2); check the launcher and the F1 menu after. Then the Fit HUD layout: team icon, Team Blast gauge and pause menu (open item 2). Start in plan mode: ask
re-investigator for the HUD objects' position code, and get a Dolphin 4:3 reference of the pause menu (/ref-compare).
Verify with PC shots in Fit (SR_SCREEN=3 SR_WINDOW=1280x720, fresh SR_CARD), then a console check with /hw-test.
After that: the stage sweep with SR_DEVSTAGE. Next release: ask me for the launcher background image.
```
