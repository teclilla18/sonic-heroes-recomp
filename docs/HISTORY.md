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
