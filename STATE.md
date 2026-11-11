# State (2026-11-11, after the dtk analysis)

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

Done 2026-11-11 later (HISTORY "dtk analysis"; facts in docs/notes/rel-modules.md): dtk split works (main + 17
RELs, 39,075 functions; `links: []` per module) [confirmed]. **stage00D is a stale REL for a different main.dol**,
left out (only stage ID 1, the test level, maps to it) [confirmed]. No REL imports another. Loader: OSLink
0x801D40EC / OSUnlink 0x801D4348, one caller each, one global loader object (one REL resident at a time) [likely].
Stage ID -> REL table at 0x80240B10. sigmatch: 1,369 of 6,223 main.dol functions named (build/G9SE8P/sigmatch.txt).

**For Riders (user's call, not done):** cherry-pick a09bbbb (turns Riders' failing GitHub guard green; Riders keeps
its fan art, tested on a copy of riders/main) and optionally aa7cb5f (pre-commit hook path).

## Next steps, in order

1. SDK map into `config/G9SE8P/hle.txt`: the Riders sections (context switch, __OSInitAudioSystem/
   __OSStopAudioSystem/__OSInitMemoryProtection, OSLink 0x801D40EC + OSUnlink 0x801D4348, memcpy/memset,
   frame-rate modes). sigmatch output is in build/G9SE8P/sigmatch.txt (regenerate: docs/notes/rel-modules.md).
2. Multi-REL code per the design in docs/notes/rel-modules.md: gcrecomp.py links each REL at its own base and
   emits a module table; `rel.c` hle_OSLink/hle_OSUnlink for any module (re-copy pristine image + clear bss on
   every load, reject stage00D); `loader.c`; `GUEST_RAM_SIZE` 0x01C00000 -> 0x02800000. Then `disc.c`
   Shift-JIS names. Check the Rel14 warning case in the recompiler.
3. Riders game hooks left in shared runtime files, to make inert or move behind a game switch so shared files stay
   cherry-pickable: `game_mods.c` / `mods_data.c` (Extreme Gear table), `game_addrs.h`, `netplay.c` save flags,
   `main.c` ISO size check, `android_icon.py` (save icon from `_Main.rel`), `setup.ps1` extract step text.
4. First PC boot (logos), then Eden v0.1.1, then the OLED.

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
Continue Sonic Heroes Phase 0 from STATE.md: next steps 1 and 2.
First fill config/G9SE8P/hle.txt from build/G9SE8P/sigmatch.txt (rerun dtk + tools/sigmatch.py if build/ is gone;
commands in docs/notes/rel-modules.md), using the Riders sections listed in the file header.
Then plan the multi-REL code in plan mode (docs/notes/rel-modules.md "Multi-REL design"; tools/recomp/gcrecomp.py
REL_BASE, runtime/src/rel.c, runtime/src/loader.c, runtime/src/runtime.h GUEST_RAM_SIZE).
Verify: gcrecomp emits all 17 modules and the host build links; PC boot to logos is the step after.
```
