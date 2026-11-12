# State (2026-11-12, end: Team Blast gauge fixed on Switch (accepted); next: enemy fps profile, 4:3 crop, stage sweep)

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

## Done 2026-11-12 (HISTORY "2026-11-12")

- **Team Blast gauge fill in pieces on Switch: fixed** (render_deko.c make_image). Cause [confirmed Eden]: deko3d
  block-linear images 8 rows tall or less (the fill: C4 64x8) were written and sampled with different block
  heights: every second 64-byte GOB column came from outside the image. Fix: explicit DkTileSize_OneGob for h <= 8
  (non render targets). Tested Eden 4:3 + 16:9 (gauge poked to 75), whole-frame diff vs before = animation only;
  console (OLED handheld): user "z bar looked fine" in 16:9 and Fit window [accepted]; 4:3 not checked (crop bug).
  It was never a wide_anchor problem: Heroes' HUD is perspective, z always; PC was always fine.
- Debug tools: **F9 on PC** (RAM dump + shot + draw log of that frame), **SR_POKE=ADDR,HEXBYTES[,FROM]**
  (multi-byte, from frame FROM; from boot it stalls the logos), double-retire check (`[tex] id N retired twice`).
  Gauge value: float at **0x80303D94** (0..100; 100 = TEAM BLAST ready) [confirmed PC]. 0x803FEC38 is not it.
- Test runs must pass `SR_FPS=0 SR_FRAMERATE=0`: the user's saves/settings.ini now has pc_fps=-1 (300 pictures/s
  moves SR_SCREENSHOT's frame clock) and fullscreen=1 (ignored with SR_MINIMIZED).

## Next steps, in order

1. **Enemy fps drop on Switch** (user: drops as soon as enemies appear, back to 60 once they are defeated).
   build/hw7/sonicheroes.log: 41-55 fps with enemies, draws/frame unchanged (~1850), GPU 12 ms (fine), game thread
   idle 1.2 ms/frame -> game-thread CPU bound [likely]. Do: env.txt `SR_PROFILE=1` on the SD over FTP (ask first),
   user plays to the first Egg Pawns and stays ~30 s; read the `[profile]` lines (callee charged with the caller's
   work after a call). Then check whether a hot function is an HLE/runtime cost (PE reads 34k/frame, collision math,
   paired-single code) vs plain game code.
2. **4:3 after 16:9/Fit window crops the picture** (shot build/hw7/shots/shot_8045.bmp: wide 3D view, right side
   cut). Suspect the RwCameraSetViewWindow patch (patches.txt) keeps the widened view window until the camera is set
   again; fix: apply the scale every frame or when the setting changes. Check PC first (change screen in the menu).
3. **Stage sweep** PC + Eden (+ console): story stages 2-4 of each team, shader keys, crashes, rendering vs Dolphin.
4. If the Pause -> Quit crash returns (build/hw6/atmo_crash.log): same stack? Then record_backtrace / window mapping.
5. Later (after the first release): HD look (bloom/grade on Switch, SSAO, shadows), widescreen menus/HUD edges,
   Android.

## Hardware / console notes

- Remote: scratchpad `sw.py` (FTP + sys-botbase; copy from an older session's scratchpad: the 0c83d772 one has it),
  settings from the Riders switch-remote config (CLAUDE.local.md). Git Bash: `MSYS_NO_PATHCONV=1`, sw.py as a
  Windows path (`cygpath -m`); `py` has Pillow. After remote control: `detachController`. No env.txt on the SD now.
- SD `switch/sonicheroes/`: NRO (gauge fix), sonicheroes.prev.nro (before it), disc image, forwarder, saves, logs.
  The user's hekate UMS mounts the SD as a drive (<sd>; ask each time).
- Logs: build/hw7 (gauge fix session: log, shots 7632 16:9 / 8045 4:3), hw6, hw5, hw4.
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

- Go-ahead to put the profiling env.txt on the SD and play to the first enemies (next step 1).
- Riders: candidates to cherry-pick (user's call): this deko3d small-image tile fix (Riders uses the same
  render_deko.c), F9/SR_POKE tools, gx.vert 2D native-grid snap, wide_anchor clear -> stretch; earlier ones in
  Riders' CLAUDE.local.md.

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
Continue Sonic Heroes (STATE.md). First release goal: "decently runnable" on Switch + PC (criteria in STATE).
1) Enemy fps drop on Switch (41-55 fps while Egg Pawns are in view, Seaside Hill, game-thread bound per
   build/hw7/sonicheroes.log). Ask me, then put env.txt with SR_PROFILE=1 on the SD over FTP (scratchpad sw.py);
   I play to the first enemies for ~30 s; fetch the log and read the [profile] lines; find what is hot and fix it.
2) 4:3 after 16:9/Fit window crops the picture (build/hw7/shots/shot_8045.bmp): check on PC, likely the
   RwCameraSetViewWindow patch not re-applied on a setting change.
3) Then a stage sweep (PC routes + Eden) toward the first release; tell me when you think it is ready.
All PC/Eden runs in the background, muted and minimized; test runs pass SR_FPS=0 SR_FRAMERATE=0.
```
