# State (2026-11-11, evening: multi-REL in, first PC boot)

Read this at the start of every session. Rewrite it in place at the end of each session (never append). Stories
behind each line: `grep` the date or topic in [docs/HISTORY.md](docs/HISTORY.md) (Riders' history:
docs/archive/riders/). Disc facts: [docs/notes/recon.md](docs/notes/recon.md).

## Where things stand

Phase 0 (recon + fork). **Nothing builds for Heroes yet**: the runtime and recompiler are the Riders port's, set up
for one REL (`_Main.rel` at `REL_BASE`); Heroes has 18.

| Target (user's order) | Status |
|---|---|
| 1. Switch (first release target) | not started |
| 2. Windows PC (also the fast test loop) | not started |
| 3. Android, 4. Linux / Steam Deck, 5. iOS | not started (backends inherited from Riders) |

Done 2026-11-11 (HISTORY "fork"): forked from Riders' `main` with history (remote `riders`); player-facing names,
Switch title ID 0x010053480D9A0000, Android `net.srnative.sonicheroes`, update checker repo changed; Riders game data
and fan art removed; guard + `tools/extract_iso.py` know Heroes' hashes; disc copied to `baserom/` and extracted
(main.dol, 18 RELs, TSonic.str, all verified) [confirmed]; starter-kit skills merged in. Pushed to
`teclilla18/sonic-heroes-recomp` (private, remote `origin`); GitHub guard green after PAST_ART (a09bbbb: earlier
versions of the credited fan art are accepted by the history scan only).

Done 2026-11-11 later (HISTORY "dtk analysis"; docs/notes/rel-modules.md): dtk split works (main + 17 RELs);
**stage00D is a stale REL for a different main.dol**, left out [confirmed]. Loader: OSLink 0x801D40EC / OSUnlink
0x801D4348, one loader object (one REL resident at a time) [likely]. Stage ID -> REL table at 0x80240B10.

Done 2026-11-11 evening (HISTORY "multi-REL"): hle.txt filled (10 entries); multi-REL recompiler + runtime
**implemented** (generic, Riders-compatible), 39,105 functions, **host build links** [confirmed];
`game_addrs.h` SDK addresses now Heroes' (Riders game-state ones inert via `GAME_UNKNOWN`). **First PC boot**:
runs 40 s, threads/audio/GL up, all 17 RELs linked at boot [confirmed], then **stuck after frame 2**: the main
thread waits in RenderWare's video driver (fn_801ACC6C, queue 0x8042CA20) for a post-retrace (fn_801ABB9C) or
draw-done (fn_801AB9E0) callback; other threads wait in VIWaitForRetrace. Cause not known [uncertain].
OSLink not reached yet, so per-load relinking is untested.

**For Riders (user's call, not done):** cherry-pick a09bbbb (guard PAST_ART) and optionally aa7cb5f. The shared
multi-REL commit (gcbin/gcrecomp/loader/rel/hle_misc/frame_pacing/configure) should also work for Riders as
is (section map checked; not built there).

## Next steps, in order

1. Boot blocker: why retrace / draw-done stops after frame 2 (vi.c retrace timer and VI interrupt mask, GX
   draw-done/PE finish in gx_fifo.c, `SR_GPTL`). Use /hang-hunt or the watchdog dump; then logos.
2. Find Heroes' frame end (for frame_pacing hooks) and game-state addresses to replace `GAME_UNKNOWN`
   (top mode, menu flag) once the game runs.
3. Remaining Riders hooks in shared files: `mods.c` ("_Main.rel cannot be replaced" -> any translated REL),
   `netplay.c` SAVE_DATA, `perftest.c` SCENE_KEY, `mods_data.c` REL bss read, `main.c`/`android_icon.py`/
   `setup.ps1` text. Then `disc.c` Shift-JIS names (if any file needs them).
4. Then Eden v0.1.1 and the OLED.

## Waiting on the user

- SD card drive letter for /hw-test when Switch tests start.
- Heroes Disassembly / NPDP prototypes as naming sources: download only with the user's OK.

## Risks

- 18 RELs swapped at runtime (Riders: 1, linked once). RenderWare 3.5's GX use differs from Riders' engine (new
  render bugs; shader keys from scratch). Big stages and 2P split screen on Switch CPU/GPU. Sofdec movies (Riders'
  FMV was ~42 fps on Switch).

## Shared with the Riders project (not copied)

Toolchains in `<home>/AppData/Local/SonicRidersSetup/tools`, Eden v0.1.1 and Dolphin in the Riders repo's
`build/ext/` (paths: CLAUDE.local.md). The setup tool for players downloads its own into `SonicHeroesSetup/tools`.

## Next session

```
Continue Sonic Heroes from STATE.md: next step 1, the first boot blocker.
The PC build boots for 40 s then stalls after frame 2: the main thread waits in fn_801ACC6C (RenderWare video
driver) for its post-retrace / draw-done callbacks; other threads wait in VIWaitForRetrace (HISTORY 2026-11-11
"multi-REL"). Look at runtime/src/vi.c (retrace interrupts, VI mask) and gx_fifo.c (draw done / PE finish).
Start with /hang-hunt or one SR_WATCHDOG=40 SR_GPTL run (build commands: CLAUDE.local.md "PC build").
Verify: frames keep presenting (SR_SCREENSHOT=60,300,900 shots exist); goal: the logos.
```
