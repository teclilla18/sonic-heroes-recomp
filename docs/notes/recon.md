# Sonic Heroes disc recon

**Current.** Started 2026-11-11. Tags: [confirmed] checked directly, [likely], [uncertain].

## Disc

- Sonic Heroes (USA) (En,Ja,Fr,De,Es,It), disc ID `G9SE8P`, revision 0, 1,459,978,240 bytes [confirmed].
- SHA-1 `dd752c8aa64f2f043c32be0f0bd5b8617357bfe6` (the copy in `baserom/` matches the original and a second copy
  in the user's Downloads) [confirmed]. Not yet checked against Redump's entry [uncertain].
- 4053 FST entries. Five file names are Shift-JIS (`\x82\x93\x82\x94\x82\x87` + `29E00.bmp` etc.); `disc.c` path
  matching has only seen ASCII names so far [confirmed: names; uncertain: impact].

## Executables (SHA-1s in tools/extract_iso.py and tools/check_no_game_data.py)

- `main.dol`: 2,740,672 bytes, entry 0x80005318 [confirmed].
- 18 RELs, 21 MB in all [confirmed]: advertiseD, autosaveD, movieD, stage00D, 01D, 03D, 05D, 07D, 09D, 11D, 13D,
  26D, 27D, 28D, 31D, 32D, 33D, 40D (largest: stage07D, 2.2 MB). Riders had one REL, linked once at boot.
  The game loads and unloads these at runtime [likely], so `rel.c`/`loader.c` (single REL at `REL_BASE`) must
  handle many modules: each one recompiled at its own fixed base. **The biggest change from the Riders port.**
- `TSonic.str`: 511 bytes (Riders' counterpart: `SonicR.str`) [confirmed].

## Libraries

- Dolphin SDK banners in main.dol: AI, AR, ARQ, AX, CARD, DSP, DVD, EXI, GX, OS, PAD, SI, VI: **the same 13 as
  Sonic Riders** [confirmed]. AX means the Riders AX/DSP HLE should carry over [likely].
- CRI ADX: `ADXT/GC Ver.8.84 Build:May 9 2003` [confirmed]. 67 `.adx` files on disc.
- RenderWare: "RenderWare Application" strings [confirmed]; the PC version names RW 3.5 (`RW35Active`) [confirmed
  on the PC exe]. RW's GX pipeline will use GX differently from Riders [likely].
- Movies: `.sfd` (Sofdec) on the PC disc copy (`E0000_GC.sfd`, ...) [confirmed on PC]; on the GC disc [uncertain].

## Reference material (no downloads without the user's OK)

- Heroes Hacking Central's Heroes Disassembly (PC executable): function names transfer by matching [likely].
- The user's PC install (`Tsonic_win.exe`, x86, D3D8) is reference only; it is not the port's base.
- GameCube NPDP prototypes exist (TCRF, Hidden Palace): a possible naming source.

## Next

1. dtk analysis with `config/G9SE8P/config.yml` (DOL + 18 modules); check REL module IDs and how the game loads them.
2. `tools/sigmatch.py` over main.dol for the SDK map; fill `config/G9SE8P/hle.txt`.
3. Design the multi-REL layout (bases, OSLink/OSUnlink) before touching `rel.c`/`loader.c`.
