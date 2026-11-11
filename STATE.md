# State (2026-11-11, night: plays on Switch hardware at ~60 fps; repo public)

Read this at the start of every session. Rewrite it in place at the end of each session (never append). Stories
behind each line: `grep` the date or topic in [docs/HISTORY.md](docs/HISTORY.md) (Riders' history:
docs/archive/riders/). Disc facts: [docs/notes/recon.md](docs/notes/recon.md).

## Where things stand

Phase 1 (boot and play). The game boots and plays its first stage on PC and on the Switch. **No release** (v0.5.0
comes once it is playable on Switch and Android; README has a v1.0 progress estimate, 25%).

| Target (user's order) | Status |
|---|---|
| 1. Switch (first release target) | **tested** on the OLED (handheld, GPU 384 MHz set by the app): title, menus, story movie, Seaside Hill at 59.4 fps; HOME-screen forwarder installed |
| 2. Windows PC (test loop) | **tested** (scripted routes): logos -> stage01D at 60 fps; 5-min stage soak, no crash |
| 3. Android, 4. Linux / Steam Deck, 5. iOS | not started (backends inherited; Vulkan depth clamp in, not compiled) |

Done 2026-11-11 (HISTORY, four entries): fork; dtk analysis (stage00D stale, links []); multi-REL recompiler +
runtime (generic, 17 RELs at fixed bases from 0x81800000, OSLink relinks per load) [confirmed: advertiseD, movieD,
stage01D load/unload]; hle.txt + Heroes SDK addresses in game_addrs.h (Riders game-state ones inert:
GAME_UNKNOWN); **CP FIFO breakpoints** modelled (RenderWare paces its frame ring with them) and **depth clamping**
instead of near/far clipping (RenderWare's clear quad) [confirmed PC, Eden, hardware]; 17 shader keys
(hardware 30.0 -> 59.4 fps, GPU 19.9 -> 4.37 ms/frame).

Repo: **public** since 2026-11-11 (teclilla18/sonic-heroes-recomp, recreated: history rewritten so no commit
carries the user's Gmail; local `user.email` is the GitHub no-reply address; GitHub guard green). Commit ids
before 3020e9d changed (old -> new map: the note at the top of Riders' CLAUDE.local.md).

## Next steps, in order

1. **Shader keys for the rest of the game:** PC routes with `SR_SHADER_KEYS=<file>` through more stages/teams and
   modes (2P), merge console misses (`sdmc:/switch/sonicheroes/shader_keys.txt`), rebuild; check the `[deko3d]`
   "N of M" line on hardware.
2. **Play further:** stage select / other teams / bosses / special stages on PC; watch for the next RE gaps
   (frame end for frame_pacing, game-state addresses for GAME_UNKNOWN, `[perf]` indirect-texture matrices).
3. On-console shader compile: plan in docs/notes/shader-compile-on-console.md (shared with Riders; not started).
4. Riders hooks left in shared files: `mods.c` "_Main.rel" check, `netplay.c` SAVE_DATA, `perftest.c` SCENE_KEY,
   `mods_data.c`; NRO icon (hbmenu shows a garbled one: `setup/icon.png` missing); the 1-px red line at the
   left screen edge (PC).
5. Android build (v0.5.0 needs it), then the setup tool.

## Hardware / console notes

- Remote control from this project: scratchpad `sw.py` (FTP + sys-botbase), settings read from the Riders
  switch-remote config (CLAUDE.local.md "Console remote"). The forwarder tile launches the game; env.txt is
  removed after tests (scripted input would drive the user's game).
- SD `switch/sonicheroes/`: NRO (17-key build), the disc image, SonicHeroes.nsp (forwarder, title
  010053480D9A0000), saves, logs. Big uploads: FTP averaged ~1.3 MB/s (disc: 18 min); UMS via hekate is faster.

## Waiting on the user

- Riders: the Heroes fixes to cherry-pick are listed at the top of Riders' CLAUDE.local.md (user's call).
- Heroes Disassembly / NPDP prototypes as naming sources: download only with the user's OK.

## Risks

- 2P split screen and big stages on Switch CPU/GPU; Sofdec movie speed on Switch (Riders' was ~42 fps).
- The forwarder icon art is CC BY-NC-ND (somegameicons): kept out of the repo; credited in README.

## Shared with the Riders project (not copied)

Toolchains in `<home>/AppData/Local/SonicRidersSetup/tools`; llvm-mingw / SDL2 / imgui as junctions in
`build/ext/`; Eden v0.1.1 and Dolphin in the Riders repo's `build/ext/` (paths: CLAUDE.local.md).
