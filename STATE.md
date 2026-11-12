# State (2026-11-12, end: screen-mode fixes on PC; enemy fps cause narrowed; hw9 test running on the console)

Read this at the start of every session. Rewrite it in place at the end of each session (never append). Stories
behind each line: `grep` the date or topic in [docs/HISTORY.md](docs/HISTORY.md) (Riders' history:
docs/archive/riders/). Disc facts: [docs/notes/recon.md](docs/notes/recon.md).

## Where things stand

Phase 1 (boot and play). The game boots and plays its first stage on PC and on the Switch. **No release.**
**First release (user's decision, 2026-11-12): "decently runnable" on Switch and PC only** (Android and the rest
later). The agent says when it thinks that point is reached (criteria below). README Road to v1.0 card: 27%.

| Target (user's order) | Status |
|---|---|
| 1. Switch (first release) | **tested** on the OLED: title, menus, story movie, Seaside Hill (median ~58-60 fps; 41-55 fps while enemies are in view) |
| 2. Windows PC (first release) | **tested** (scripted routes + user play): logos -> Seaside Hill at 60 fps; matches Dolphin |
| 3. Android, 4. Linux / Steam Deck, 5. iOS | not started (backends inherited); not in the first release |

Repo public (teclilla18/sonic-heroes-recomp). Local `user.email` is the GitHub no-reply address.

## First release: "decently runnable" (agent's criteria, to judge when to propose it)

1. Story mode playable start to end of at least the first stages of each team on PC and Switch without crash or
   hang (Pause -> Quit crash seen once: must not return in a sweep).
2. Switch: typical stage fps >= ~50 with dips only in heavy scenes (now 41-55 with enemies: step 1 below).
3. Saves (memory card) and settings persist; aspect modes switch cleanly (4:3 crop bug below).
4. No obvious rendering faults in the stages swept (compare to Dolphin where unsure).
5. Release procedure: cold Windows Sandbox test (PC), hardware test from the release zip (Switch).
Estimate (2026-11-12): after the enemy-fps work and a stage sweep of 2-3 sessions; not yet.

## Done 2026-11-12 (HISTORY "2026-11-12" and "2026-11-12 (later)")

- Team Blast gauge fill fixed on Switch (render_deko.c OneGob tiling for h <= 8) [accepted 16:9/Fit].
- **Screen change during a stage** (4:3 crop / zoom): the HUD is laid out as the stage loads, so a change now
  waits for the next stage (settings.c settings_hold_view, called from rel.c on stage link/unlink; menu note).
  The game re-sets the stage camera's view window every frame (the old suspect was wrong). Tested PC route both
  directions [confirmed PC]; "applies after leaving the stage" and console untested.
- **Character select in Fit after a stage** (models outside panels): view-window widening now only while a stage
  REL is in (patches.txt, rel_stage_active). Implemented; console test pending (hw9).
- Debug: `SR_SCREENAT=FRAME,MODE` (screen change at the first [perf] block from FRAME, not saved).
- Enemy fps (hw8, OLED, SR_PROFILE): 43 fps = 1/2-vsync alternation, frame only slightly over budget [likely].
  Suspect: token waits in fn_801ADE4C (loop at 801AE220 calling fn_801B2894 -> GXReadDrawSync 801F37C0) before
  the game rewrites a resource the GP may still use; Switch 20k PE reads/frame vs PC 1.5k (PC: 7 waits/frame,
  0.1 ms/frame). Measuring on hardware now.

## Next steps, in order

1. **Read hw9** (console log after the user's test; fetch over FTP, sw.py): `[pewho] waits:` lines give waits per
   frame, avg/max us and ms/frame in the enemy scene. If ~1-3 ms/frame: cut GP drain latency on Switch (GP thread
   wake/batching, gx_fifo.c ring_kick/gp_thread, vertex decode) or avoid the wait (what resource is r26 in
   fn_801ADE4C: re-investigator). If small: look elsewhere in the profile (8022A650 from 80226F5C ~5%).
   Then remove the temporary counters (they are not in git; local diffs build/temp_pewho_*.diff to re-apply).
2. Check the user's hw9 results for the character select (Fit) and 4:3-during-stage fixes; mark accepted or fix.
3. **Stage sweep** PC + Eden (+ console): story stages 2-4 of each team, shader keys, crashes, rendering vs Dolphin.
4. If the Pause -> Quit crash returns (build/hw6/atmo_crash.log): same stack? Then record_backtrace / window mapping.
5. Later (after the first release): HD look, widescreen menus/HUD edges, Android.

## Hardware / console notes

- Remote: scratchpad `sw.py` (FTP + sys-botbase; copy from an older session's scratchpad: the 0c83d772 one has it),
  settings from the Riders switch-remote config (CLAUDE.local.md). Git Bash: `MSYS_NO_PATHCONV=1`, sw.py as a
  Windows path (`cygpath -m`); `py` has Pillow. After remote control: `detachController`. 
- SD `switch/sonicheroes/`: NRO = hw9 (screen fixes + temp [pewho] counters, not in git), sonicheroes.prev.nro
  (gauge fix build), sonicheroes.hw8.log (profile run), env.txt = SR_PROFILE=1 (remove after hw9), disc, saves.
  The user's hekate UMS mounts the SD as a drive (<sd>; ask each time).
- Logs: build/hw8 (enemy profile log, shot_9534 character select), hw7 (gauge fix), hw6, hw5, hw4.
- Atmosphere reports in /atmosphere/crash_reports (title 010053480d9a0000); addr2line on build/switch/sonicheroes.elf.
- Eden v0.1.1: start hidden, never minimized: `Start-Process eden.exe -ArgumentList '-g',"<sdmc>\switch\sonicheroes\sonicheroes.nro" -WindowStyle Hidden`,
  ~165 s, then Stop-Process; shots land in its sdmc folder. env.txt there now: title route, SR_SCREEN=1,
  SR_SHOTS=5000,5600,6200, SR_POKE gauge 75 (old one: env.txt.prev). SR_DUMPTEX writes to sdmc:/build/tex.

## Testing etiquette (user)

All test runs in the background, muted (`SR_NOAUDIO=1`), minimized (`SR_MINIMIZED=1`); the user plays meanwhile.
Ask before taking over the console. PC route script: scratchpad `route.sh <tag> [ENV=..]` (title, START, hold
forward + jump/homing from 4500; SHOTS=, SECS=; adds SR_FPS=0 SR_FRAMERATE=0) -> build/run1/rt_<tag>/.
PC widescreen: `SR_SCREEN=1 SR_WINDOW=1280x720`. For "play until it happens": `play_f9.cmd` (16:9, F9 captures).

## Waiting on the user

- hw9 console test (running): Fit -> character select -> Seaside Hill, 30 s at the first Egg Pawns, quit to
  character select (models in panels?), 4:3 switch during a stage (shape kept + note) then next stage (clean 4:3).
- Riders cherry-pick candidates (user's call): deko3d small-image tile fix, F9/SR_POKE/SR_SCREENAT tools, gx.vert
  2D native-grid snap, wide_anchor clear -> stretch; earlier ones in Riders' CLAUDE.local.md.

## Risks

- The OneGob tile fix touches every texture 8 rows tall or less on Switch (Eden frame diff showed no change
  elsewhere) [likely fine]. The 2D native-grid snap (2026-11-11) is still unchecked in menus/other stages.
- Big stages and 2P split screen on Switch CPU; Sofdec movie speed on Switch. Game icon is fan art (credited).

## Shared with the Riders project (not copied)

Toolchains in `<home>/AppData/Local/SonicRidersSetup/tools` (ninja at `tools/ninja/ninja.exe`; Switch ninja
needs `DEVKITPRO=<tools>/devkitpro` in the environment or the link fails); llvm-mingw / SDL2 / imgui junctions in
`build/ext/`; Eden and Dolphin in the Riders repo's `build/ext/`. build.ninja holds one target (now: switch).

## Next session

```
Continue Sonic Heroes (STATE.md). hw9 console results: <paste: character select in Fit after the stage OK?, 4:3
switch during a stage OK?, anything else seen>. Fetch /switch/sonicheroes/sonicheroes.log over FTP (scratchpad sw.py;
copy it from the fc12b70e scratchpad) into build/hw9/ and have log-reader summarise it vs build/hw8 (fps, [pewho] waits
lines, [profile] top). If the token waits (fn_801ADE4C loop at 801AE220) cost ~1-3 ms/frame with enemies, plan the cut
(plan mode: gx_fifo.c GP wake/drain, or what resource the game waits on: re-investigator). Then remove the temp counters
and env.txt from the SD (ask first). Verify: PC route + a console run, fps in the Egg Pawn area. Then the stage sweep.
```
