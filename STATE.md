# State (2026-11-11)

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
(main.dol, 18 RELs, TSonic.str, all verified) [confirmed]; starter-kit skills merged in. Not pushed: GitHub repo
`teclilla18/sonic-heroes-recomp` not created yet (user).

## Next steps, in order

1. User: create the GitHub repo `sonic-heroes-recomp` (private to start), then `git remote add origin <url>` and push.
2. dtk analysis: `build/tools/dtk.exe dol split config/G9SE8P/config.yml build/G9SE8P` (DOL + 18 modules). Check
   module IDs, sections, and how the game loads/unloads stage RELs (OSLink/OSUnlink callers).
3. SDK map: `tools/sigmatch.py` on main.dol; fill `config/G9SE8P/hle.txt` (same entries as Riders had).
4. Multi-REL design, written in docs/notes/ before code: one fixed base per REL, `rel.c` OSLink/OSUnlink for any
   of the 18, `loader.c`, `gcrecomp.py` emitting all modules. Then `disc.c` with the Shift-JIS file names.
5. Riders game hooks left in shared runtime files, to make inert or move behind a game switch so shared files stay
   cherry-pickable: `game_mods.c` / `mods_data.c` (Extreme Gear table), `game_addrs.h`, `netplay.c` save flags,
   `main.c` ISO size check, `android_icon.py` (save icon from `_Main.rel`), `setup.ps1` extract step text.
6. First PC boot (logos), then Eden v0.1.1, then the OLED.

## Waiting on the user

- The GitHub repo (step 1). SD card drive letter for /hw-test when Switch tests start.
- Heroes Disassembly / NPDP prototypes as naming sources: download only with the user's OK.

## Risks

- 18 RELs swapped at runtime (Riders: 1, linked once). RenderWare 3.5's GX use differs from Riders' engine (new
  render bugs; shader keys from scratch). Big stages and 2P split screen on Switch CPU/GPU. Sofdec movies (Riders'
  FMV was ~42 fps on Switch).

## Shared with the Riders project (not copied)

Toolchains in `<home>/AppData/Local/SonicRidersSetup/tools`, Eden v0.1.1 and Dolphin in the Riders repo's
`build/ext/` (paths: CLAUDE.local.md). The setup tool for players downloads its own into `SonicHeroesSetup/tools`.
