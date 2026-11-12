# State (2026-11-12, night: 0.1.0-alpha.1 released as a GitHub pre-release)

Read this at the start of every session. Rewrite it in place at the end of each session (never append). Stories
behind each line: `grep` the date or topic in [docs/HISTORY.md](docs/HISTORY.md) (Riders' history:
docs/archive/riders/). Disc facts: [docs/notes/recon.md](docs/notes/recon.md).

## Where things stand

Phase 1 (boot and play). The game boots and plays Seaside Hill and the special stage on PC and Switch; Egg Fleet
starts on PC. **No release yet.** README Road to v1.0 card: 29%.

| Target (user's order) | Status |
|---|---|
| 1. Switch | **tested** on the OLED: menus, story movie, Seaside Hill (~58-60 fps; dips with enemies now rare), special stage plays through (user) |
| 2. Windows PC | **tested** (scripted routes + user play): Seaside Hill, special stage 40, Egg Fleet start, 60 fps |
| 3. Android, 4. Linux / Steam Deck, 5. iOS | not started (backends inherited); not in the first releases |

Repo public (teclilla18/sonic-heroes-recomp). Local `user.email` is the GitHub no-reply address.

## Releases (user's decisions, 2026-11-12)

- **0.1.0-alpha.1 released** 2026-11-12 (GitHub pre-release, tag v0.1.0-alpha.1 = 2fcaac6c; PC + Switch zips;
  page = docs/releases/0.1.0-alpha.1.md with the controls section and pictures). Tests before publishing: cold Windows
  Sandbox PC zip PASS (2 installs, ~4 min; the first run FAILED: setup still had Riders' disc SHA-1, fixed f21d407c);
  Switch zip setup -NoSd PASS on this PC (warm toolchain). Launcher: Reckoman12 banner, Nibroc.Rock icon (credited).
  Release NRO is on the user's console (verified); the son's SD (F:) has the hw13 NRO (same code) + disc copy.
- First real release later: "decently runnable" on Switch + PC (criteria: memory first-release-scope).

## Done 2026-11-12 (HISTORY "2026-11-12 (evening)")

- **Special stage crash fixed** (recompiler): REL calls to main.dol out of b/bl range (modules above ~0x82000000,
  71027 calls) now use the real target (gcrecomp.py / ppc2c.py FAR_TARGETS). Special stage [accepted on console];
  Egg Fleet [confirmed PC]; other far stages (stage13D+, bosses, 26D-33D) untested on hardware.
- **Shadow GPU waits removed** (patches.txt 800B7CE4/800B7E70): 7 -> 1 waits/frame; hw10 <= 0.41 ms/frame, dips
  below 50 fps rare [likely; different play than hw9]; shadows fine [accepted].
- Special stages: bloom off, "Special stage steering" slider default 60 % [accepted].
- Dev stage select (dev_stage.c; SR_DEVSTAGE=<key> for scripted tests; menu only in --dev-menu builds) [accepted].
- Earlier today: Fit char select after a stage and 4:3 change during a stage [accepted on console, hw9].

## Open items, in order

1. **Alpha feedback**: read GitHub issues from testers; the PC launcher at <home>/Desktop/SonicHeroes-PC-0.1.0-alpha.1 is not yet installed/played.
2. **Fit HUD layout** (user, hw12 shots build/hw12/shot_6435, 12977): pause menu off-centre everywhere; the team
   switch icon and Team Blast gauge stay near the centre instead of the right edge. Heroes' stage HUD is placed from
   the widened stage camera when the stage loads (not per-piece 2D: SR_ANCHORLOG sees only the shadow corner), so
   it needs the HUD objects' position code (re-investigator) and a Dolphin 4:3 reference of the pause menu.
   The gx_render.c "edges only in manager state 5" change is implemented; saving box after a stage (hw11
   shot_17183, split in three) not re-checked.
3. **Stage sweep** with SR_DEVSTAGE (keys: notes/re/stage-select.md): every story stage + bosses on PC, then Eden /
   console; crashes, shader keys, rendering vs Dolphin (special stage looks very bright even without bloom).
4. If the Pause -> Quit crash returns (build/hw6/atmo_crash.log): same stack? Then record_backtrace.
5. Later: HD look, widescreen menus, Android.

## Hardware / console notes

- Remote: scratchpad `sw.py` (FTP + sys-botbase; copy from this session's scratchpad 9921978d or fc12b70e), settings
  from the Riders switch-remote config (CLAUDE.local.md). Git Bash: `MSYS_NO_PATHCONV=1`, sw.py as a Windows path;
  FTP login sometimes times out: retry. The log is locked while the game runs (550 busy): ask the user to close it.
- SD `switch/sonicheroes/`: NRO = hw13 build (alpha code, bug report button, no dev menu); env.txt empty (old one
  in build/hw13/env.txt.old). Logs/zips: build/hw13. The user's other SD on F: is for
  Sonic Riders (his son's console): do not touch.
- Temp wait counters ([pewho]/[rlock]) are out of git: local build/temp_pewho_rlock_gx_fifo.diff and
  build/temp_pewho_rlock_patches.txt to re-apply.
- Logs: build/hw12 (dev menu run + 3 shots), hw11 (special stage + shots 17022 pause / 17183 saving box), hw10
  (shadow fix; atmo_crash.log = special stage FATAL), hw9 (enemy waits), hw8.
- Eden v0.1.1: start hidden, never minimized (CLAUDE.md); ~165 s; shots in its sdmc folder.

## Testing etiquette (user)

All test runs in the background, muted (`SR_NOAUDIO=1`), minimized (`SR_MINIMIZED=1`). PC route script: scratchpad
`route.sh <tag> [ENV=..]` (title, START, story, run forward from 4500; SHOTS=, SECS=) -> build/run1/rt_<tag>/.
Straight to a stage: add `SR_DEVSTAGE=1D` (special) / `0E` (Egg Fleet) etc. Fit widescreen: `SR_SCREEN=3
SR_WINDOW=1280x720`. A scripted START did not open the special stage's pause menu (cause unknown).

## Shared with the Riders project (not copied)

Toolchains in `<home>/AppData/Local/SonicRidersSetup/tools` (ninja `tools/ninja/ninja.exe`; Switch ninja needs
`DEVKITPRO=<tools>/devkitpro`); llvm-mingw / SDL2 / imgui junctions in `build/ext/`; Eden and Dolphin in the Riders
repo's `build/ext/`. build.ninja holds one target (now: switch). Riders cherry-pick candidates (user's call): the
far-branch recompiler fix (Riders' single REL is in range, low value), deko3d small-image tile fix, F9/SR_POKE tools.

## Next session

```
Continue Sonic Heroes (STATE.md). If 0.1.0-alpha.1 is out, read new GitHub issues first. Then Fit HUD layout
(team icon, Team Blast gauge, pause menu; re-investigator on the HUD position code, Dolphin 4:3 reference), then
the stage sweep with SR_DEVSTAGE (every story stage + bosses on PC, then Eden / console).
```
