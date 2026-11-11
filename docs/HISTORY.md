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
