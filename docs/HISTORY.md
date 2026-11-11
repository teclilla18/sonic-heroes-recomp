# History

Dated sessions and hardware tests, oldest first. The Sonic Riders port's history (2026-10-15 to the fork) is in
[archive/riders/HISTORY.md](archive/riders/HISTORY.md); grep both when a problem looks familiar.

## 2026-11-11: fork

- Forked from the Sonic Riders port's `main` (309 commits; its private DX branch left out). Remote `riders` points
  at the local Riders repo for cherry-picks both ways.
- Player-facing names changed (app/exe `sonicheroes`, `SonicHeroes-*` zips, Switch title 0x010053480D9A0000,
  Android `net.srnative.sonicheroes`, update checker → `teclilla18/sonic-heroes-recomp`). Internal `SR_*` debug
  variables kept on purpose so shared files stay identical for cherry-picks.
- Riders data removed: `config/G9SE8P/` emptied (hle, patches, hot functions, shader keys), perf results, the 2P
  race route, Riders fan art (banner, cedry2kio icon). Guard and `tools/extract_iso.py` know Heroes' hashes.
- Starter-kit skills added (`/recon`, `/emu-run`, `/render-bisect`, `/hang-hunt`, `/ref-compare`, `/analyze-log`),
  plus the re-investigator agent and the recompiler / device-model rules.
- Disc copied to `baserom/`, hash equal to the original [confirmed]; `extract_iso.py` extracted main.dol, 18 RELs
  and TSonic.str, all verified [confirmed]. Nothing built yet: the runtime still expects Riders' single REL.

- First push to `teclilla18/sonic-heroes-recomp` (private). GitHub guard failed on old versions of the credited
  fan art inherited from Riders' history (`--history` scans every version); fixed with `PAST_ART` (a09bbbb),
  green on GitHub [confirmed]. Riders' public guard fails on the same 3 pictures; the fix applies to riders/main
  cleanly and keeps its fan art (tested on a temporary copy) [confirmed]; not applied to Riders (user's call).

## 2026-11-11 (later): dtk analysis of main.dol + the RELs

- First dtk 1.8.4 split stopped on "Duplicate module ID 3": stage00D and stage01D share ID 3. Every REL imports
  only itself and main.dol, so `links: []` on each module fixes the link step [confirmed].
- Next stop: stage00D relocates against 0x8044AEA8, past main.dol's bss. stage00D is a stale build for a different
  main.dol: 3,978 relocations past the DOL, 3.8% of its calls land on function starts (others 92-97%)
  [confirmed]; the stage table maps it only to stage ID 1 (unused test level). Left out of config.yml.
- Split then ran clean: main + 17 RELs, 39,075 functions, 4,680 objects, 11 s; 14 Rel14 warnings (one shared
  object in every stage REL, branch to the previous instruction) [confirmed]; whether it matters for recompiling
  [uncertain].
- Loader found: OSLink 0x801D40EC / OSUnlink 0x801D4348, each with one caller (0x80042310 load, 0x800421C8 unload)
  on one global loader object 0x8042C1C0, so one REL resident at a time [likely]. Stage ID -> REL table at
  0x80240B10 (IDs 1..61). sigmatch named 1,369 of 6,223 main.dol functions. Multi-REL design proposed (17 fixed
  bases side by side, 15.6 MB from 0x81800000; re-copy the pristine image on every OSLink): docs/notes/rel-modules.md.
- `.gitignore`: per-module dtk outputs `config/*/*/symbols.txt`, `splits.txt` were not covered; added.
- Nothing runs yet; no hardware or emulator test this session (nothing builds for Heroes).

## 2026-11-11 (evening): hle.txt, multi-REL recompiler/runtime, first PC boot

- `config/G9SE8P/hle.txt` filled from sigmatch + dtk names: OSSaveContext 801D2618 / OSLoadContext 801D2698,
  __OSInitAudioSystem 801D1C90 / __OSStopAudioSystem 801D1E4C / __OSInitMemoryProtection 801D46F4 (nop),
  OSLink 801D40EC, OSUnlink 801D4348 (new hle_OSUnlink), memcpy 800031E8, memset 80003100, memmove 801C0290.
  Riders' frame_end / vi_wait_retrace hooks are game code: not found for Heroes yet.
- Multi-REL (implemented, generic so Riders' single `_Main` uses the same code): module list from config.yml
  (`gcbin.read_modules`), section map from dtk splits.txt (`rel_section_names`; Riders' _Main still 1..4,
  checked read-only on the Riders repo), one fixed base per REL (0x81800000-0x8279FD94), `g_rel_modules[]`
  table, `rel_link_module` (relinks from the disc on every OSLink), `GUEST_RAM_SIZE` 0x02800000. Recompile:
  39,105 functions in ~170 s [confirmed]; host build links [confirmed].
- Link errors found five Riders addresses hard-coded in the runtime (`f_<addr>_orig` in hle_misc.c and
  frame_pacing.c); now looked up by hle.txt name (`hle_orig`).
- First PC boot died at once: "dispatch to 80010650" = Riders' __OSReschedule in `game_addrs.h`. SDK addresses
  there now Heroes' (RunQueue 803F23B8, RunQueueBits/Hint/Reschedule 8042CB98/9C/A0, __OSReschedule 801D6994,
  DecrementerExceptionCallback 801D1640, OSExitThread 801D6BAC by checksum match, DVD statics 8042CC18.. and
  DummyCommandBlock 803F2EC0) [confirmed by dtk names]; Riders game-state addresses point at an always-zero
  spot (`GAME_UNKNOWN`). The fatal dispatch message now dumps the SR_WATCHDOG trace.
- Second boot: runs 40 s, 3 game threads, DSP/AX, GL renderer, 8 disc reads, all 17 RELs linked at boot
  [confirmed]; then stuck after frame 2: main thread sleeps in fn_801ACC6C (RenderWare GC video driver, queue
  8042CA20) waiting for its VISetPostRetraceCallback (fn_801ABB9C) / GXSetDrawDoneCallback (fn_801AB9E0)
  wakers; the other threads wait in VIWaitForRetrace [confirmed from the watchdog dump]. Cause not looked at
  [uncertain]: retrace interrupts stop, or draw-done never signalled.

## 2026-11-11 (night): boot blocker fixed; logos, title, menus, story movie and Seaside Hill on PC

- Stall after frame 2: the main thread slept in RenderWare's GC video driver (fn_801ACC6C, queue 8042CA20) on
  a full frame-buffer ring. Its wakers (fn_801AB9E0 via GXSetBreakPtCallback 801F24B4, fn_801ABB9C via
  VISetPostRetraceCallback 801DBFC4) advance the ring when the **CP FIFO breakpoint** fires (GXEnableBreakPt
  801F24F8 / GXDisableBreakPt 801F2584 [likely, by position in GXFifo.c]). Found by: SR_DETTRACE (VI delivered
  ~60/s, no PE interrupts), SR_WATCH on the retrace queue (retrace threads fine), `[pe]` logs (no draw done
  issued), reading the wakers. Fix: gx_fifo.c models the breakpoint (hit once the GP has drained, status bit 4,
  OS interrupt 17) [confirmed: boot continues].
- Then: advertiseD -> movieD -> title -> menus -> story movie (Sofdec renders) -> stage01D, OSLink/OSUnlink for
  each [confirmed]. Stage frames showed the title card frozen over the HUD while the game ran: the 3D scene failed
  the depth test because RenderWare's **full-screen clear quad** (first main-scene draw, z always + update) lies
  outside the depth range and was clipped, leaving last frame's colour and depth. Found with SR_SKIPSAME (no
  block of draws made the overlay), SR_GXDEBUG(_ALL) (copies: the XFB copy does not clear; the clear quad covers
  0..640 x 0..480) and an SR_DEPTHCLAMP test. Fix: depth clamping instead of near/far clipping, as GX and Dolphin
  (GL_DEPTH_CLAMP; deko3d depthClampEnable; Vulkan depthClamp feature) [confirmed on PC; Switch/Vulkan not run].
- PC result: Seaside Hill at 60 fps, 2,600-2,700 draws/frame; START skips the story movie (the user's tip).
  Not implemented yet (from `[perf]`): fog (~2,000 draws/frame use it), indirect textures, Z textures.

## 2026-11-11 (late night): Switch hardware, shader keys, forwarder, public repo

- Switch NRO built (GCC, ~5 min), Eden v0.1.1 smoke test: title -> stage01D at 60 fps, frames correct
  (`SR_SHOTS`, not SR_SCREENSHOT, on the Switch). Disc image uploaded by FTP (18 min).
- Hardware test 1 (OLED handheld, GPU 384 MHz set by the app; sys-clk overclock not checked): Seaside Hill 30.0
  fps, GPU 19.9 ms/frame, "specialized shaders for 0 of 31,743 states" [confirmed]. The console recorded 17
  distinct keys (Eden the same 17). Test 2 with them built in: **59.4 fps**, GPU 4.37 ms/frame, all states
  specialized, render thread no longer waits [confirmed].
- Forwarder NSP (tools/nsp/make_forwarder.py; had kept Riders' title id, fixed to 010053480d9a0000), icon =
  somegameicons' art on a dark blue (the user's choice), user's keys passed by path. Installed by the user;
  launching from HOME works [confirmed].
- SwitchWakerHD studied: it compiles shaders on the console (uam as a library + worker + SD cache); plan in
  docs/notes/shader-compile-on-console.md; Riders told via its CLAUDE.local.md.
- Repo made public: the 12 Heroes-only commits carried the user's Gmail (Riders' public history only has the
  no-reply address), so they were rewritten to the no-reply address and the GitHub repo was deleted (by the user)
  and recreated public; guard green. Old -> new ids: a09bbbb -> 89e93e2, aa7cb5f -> 1cb9ac8, 3dd787e -> 9cc7934,
  8d5e14d -> 64086c6, 2b63b6d -> a7573d9, fb1459a -> 3020e9d.
