# State (2026-11-11, end: first level accepted on Switch; widescreen + controls next)

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

## User's play test (2026-11-11, OLED, overclocked as Riders) — **accepted** for the first level

"Runs really well"; ~60 fps at 1.5x resolution with the overclock; first level fine except **terrain graphical
errors and discolouration here and there** (no screenshots yet). Overlay menu: some things work; **Fit to screen
does not behave like Riders**. Logs/keys of that run: close the game, then FTP `sonicheroes.log`,
`shader_keys.txt` (locked while it runs; build/hw3 has settings.ini and old shots).

## Next steps, in order (user's priorities)

1. **Ultrawide / fit to screen without stretching, HUD at the screen edges.** *Implemented, untested:*
   config/G9SE8P/patches.txt `8019D0F0` widens RwCameraSetViewWindow (fn_8019D0CC [likely]; camera+0x68 view
   window, raster width +0xC >= 512 = screen cameras only) by `g_aspect_scale` (Hor+, culling follows). The host
   build with it compiles (2026-11-11); next: PC `SR_SCREEN=3 SR_WINDOW=2560x1080` route
   shots. Still needed for edge HUD: Heroes game-state addresses for `GAME_TOP_MODE`/`GAME_MENU_FLAG`
   (game_addrs.h `GAME_UNKNOWN`), see docs/archive/riders/ultrawide-fov.md (wide_anchor rules). fn_801AC6A4 =
   RW camera projection (reads 0x70..0x84).
2. **Modern controls** (setting `modern_controls`, default on; nothing written yet): in si.c `get_pad` live path
   map L -> X (0x400), R -> Y (0x800) (character cycle), C-stick X -> L/R camera rotate (buttons + analog), give
   the game a neutral C-stick (no first-person). Settings: settings.h field at the end of Settings + initializer
   `, 1`, settings.c load/save key, menu.cpp `tab_gameplay` (replace Riders' Chaos Emerald item). C-stick up/down
   needs Heroes camera RE (game has no tilt control).
3. Terrain errors / discolouration: get the user's screenshots (hold - menu "Save screenshot"), /ref-compare with
   Dolphin; suspects: fog range adjustment, indirect textures (`[perf]` line), 4-stage TEV with EFB copies.
4. Shader keys for more stages (merge console misses), then on-console compile plan
   (docs/notes/shader-compile-on-console.md).
5. Leftover Riders hooks (mods.c, netplay.c, perftest.c, mods_data.c), 1-px left-edge line, Android.

## Hardware / console notes

- Remote control from this project: scratchpad `sw.py` (FTP + sys-botbase), settings read from the Riders
  switch-remote config (CLAUDE.local.md "Console remote"). The forwarder tile launches the game; env.txt is
  removed after tests (scripted input would drive the user's game).
- SD `switch/sonicheroes/`: NRO (17-key build), the disc image, SonicHeroes.nsp (forwarder, title
  010053480D9A0000), saves, logs. Big uploads: FTP averaged ~1.3 MB/s (disc: 18 min); UMS via hekate is faster.

## Waiting on the user

- Riders: the Heroes fixes to cherry-pick are listed at the top of Riders' CLAUDE.local.md (user's call).
- Close the game on the console so the play-test log and shader keys can be fetched; screenshots of the terrain errors.
- Heroes Disassembly / NPDP prototypes as naming sources: download only with the user's OK.

## Risks

- 2P split screen and big stages on Switch CPU/GPU; Sofdec movie speed on Switch (Riders' was ~42 fps).
- The game icon (setup/icon.png) is somegameicons' fan art (CC BY-NC-ND on DeviantArt), credited in README as Riders does.

## Shared with the Riders project (not copied)

Toolchains in `<home>/AppData/Local/SonicRidersSetup/tools`; llvm-mingw / SDL2 / imgui as junctions in
`build/ext/`; Eden v0.1.1 and Dolphin in the Riders repo's `build/ext/` (paths: CLAUDE.local.md).

## Next session

```
Continue Sonic Heroes from STATE.md: next steps 1 and 2 (the user's priorities).
First check the widescreen patch (config/G9SE8P/patches.txt 8019D0F0) builds and works on PC with SR_SCREEN=3
SR_WINDOW=2560x1080 on the usual route (START 1300, A every 150 fields to 3700, START 3900); compare shots at 16:9/21:9.
Then find Heroes' "in a stage" / "in a menu" state for the edge HUD (game_addrs.h GAME_UNKNOWN; Riders' rules in
docs/archive/riders/ultrawide-fov.md). Then the modern-controls remap in si.c get_pad (details in STATE step 2).
Fetch the user's play-test log and shader_keys.txt from the console first (sw.py; detachController afterwards).
Verify on PC frames, then Eden, then a console run; update the Road to v1.0 card for what is tested.
```

