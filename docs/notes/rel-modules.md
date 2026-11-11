# REL modules: what the disc has, how the game loads them, multi-REL design (Current)

Found 2026-11-11 with dtk 1.8.4 (`build/tools/dtk.exe dol split config/G9SE8P/config.yml build/G9SE8P`, ~11 s) and
direct reads of the REL headers and main.dol. All addresses: G9SE8P rev 0.

## dtk run [confirmed]

- 18 modules analysed (main.dol + 17 RELs), 39,075 functions, 4,680 objects. main.dol: 6,223 functions.
  Largest RELs by function count: stage07D 3,077, stage13D 2,821, stage11D 2,695; smallest autosaveD 89.
- Config needs `links: []` on every module: by default dtk links every module with every other and stops on the
  duplicate module ID 3 (see stage00D).
- One warning per stage REL (14): `Found invalid relocation ... Rel14(...)`, a conditional branch whose target is
  the instruction 4 bytes before it (stage01D/03D/05D/07D/09D/11D/31-33D at 0x459C8, stage13D 0x459B0,
  stage26-28D 0x3E590, stage40D 0x2A720, section 0 = .text). The same shared object appears in every stage; the
  recompiler must accept a REL14 to a REL-local target [uncertain whether dtk drops it from the split].
- sigmatch (Dolphin totaldb) names 1,369 of 6,223 main.dol functions; it does not name the OSLink.c functions
  (their bodies are too generic), see below. Command: `python tools/sigmatch.py baserom/main.dol
  config/G9SE8P/symbols.txt <riders>/build/ext/totaldb.dsy build/G9SE8P/sigmatch.txt`.

## Module headers [confirmed]

| REL | module ID | imports | notes |
|---|---|---|---|
| advertiseD | 1 | self, main | loaded by name "advertise" |
| autosaveD | 2 | self, main | "autosave" |
| stage00D | 3 | self, main | **stale, unusable** (below) |
| stage01D | 3 | self, main | |
| stage03D..stage13D | 4..9 | self, main | one ID each, in disc order |
| stage26D, 27D, 28D | 10, 11, 12 | self, main | |
| stage31D, 32D, 33D | 13, 14, 15 | self, main | 31D/32D have identical code size |
| stage40D | 16 | self, main | 2P stages |
| movieD | 17 | self, main | "movie" |

All version 3 headers. **No REL imports another REL**: every module only relocates against itself and main.dol.

**stage00D is a leftover linked against a different main.dol** [confirmed]: 3,978 of its relocations point past
this DOL's bss end (0x804302D0, e.g. 0x8044AD60), and only 3.8% of its branch targets into main.dol land on a
function start (every other REL: 92-97%). It would crash a real GameCube too. It is only reachable as stage ID 1
(the unused test level) in the table below. config.yml leaves it out; the runtime should refuse it with a clear
message.

## How the game loads RELs [confirmed from the code; behaviour at runtime not yet watched]

- OSLink.c in main.dol (named by size pattern next to dtk's `__OSModuleInit`): OSNotifyLink 0x801D3B3C,
  OSNotifyUnlink 0x801D3B40, OSSetStringTable 0x801D3B44, Relocate 0x801D3B50, Link 0x801D3E0C,
  **OSLink 0x801D40EC** (wrapper around Link), Undo 0x801D4110, **OSUnlink 0x801D4348**, __OSModuleInit 0x801D451C.
  No OSLinkFixed (older SDK).
- One game function loads (0x80042310, the only OSLink caller) and one unloads (0x800421C8, the only OSUnlink
  caller). Both are methods of one global loader object at 0x8042C1C0 (sda21): **one REL is resident at a time**
  [likely; the single object implies it].
- Load: file name = name + "D" + ".REL" (strings at 0x8042AF24/0x8042AF28, opened "rb" through the game's file
  layer, so the disc's lower-case `.rel` matches case-insensitively), read into a heap buffer, flush, allocate
  bss from header +0x20, OSLink, then call the prolog through header +0x34.
- Unload: call the epilog through header +0x38, OSUnlink, free bss and buffer.
- Callers: stage loader inside 0x80019034 (load 0x8001D070, unload 0x8001B1C0), advertise (load 0x800A9ED4,
  unload 0x800A9D20), autosave (load 0x801306BC, unload 0x8013057C), movie (load 0x80139188, unload 0x80139120).
- Stage ID -> REL name table at 0x80240B10: 8-byte entries {int stage ID, char* name}, IDs 1..61, ended by -1.
  ID 1 -> stage00; pairs of IDs share a REL (2-3 stage01, 4-5 stage03, 6-7 stage05, 8-9 stage07, 10-11 stage09,
  12-13 stage11, 14-15 stage13); 16-21 reuse stage01..stage11, 22-24 stage26/27/28, 25 stage01, 26-29
  stage31/32/33/40, 30-35 and 52-61 stage40, 36-51 reuse the story-stage RELs.

## Multi-REL design (proposal; nothing implemented yet)

Riders: one REL pre-linked at `REL_BASE` 0x81800000 (above MEM1); `hle_OSLink` (runtime/src/rel.c) leaves the
game's heap copy alone and points the module header's prolog at the fixed image.

For Heroes, keep the same trick for every module:

1. **One fixed base per REL, side by side** from 0x81800000 (fixSize + bss, 64 KB aligned): 17 RELs need 15.6 MB,
   0x81800000-0x827A0000. Distinct bases keep every guest code address unique, so the one global
   address -> function table keeps working (no table swapping on load). `GUEST_RAM_SIZE` grows from 0x01C00000
   to 0x02800000 (40 MB backed; the game still sees 24 MB).
2. **gcrecomp.py** links each REL at its base (`self.rel.link(base)` per module), emits all of them, and writes a
   module table (name, ID, base, size, bss, prolog/epilog/unresolved) for the runtime.
3. **hle_OSLink(module, bss)**: identify the module by ID + size (stage01D and stale stage00D share ID 3; reject
   stage00D), copy that REL's pristine linked image back to its base and clear its bss **on every load** (the game
   expects fresh .data each time a stage loads), patch prolog/epilog/unresolved in the game's header, keep the
   OS module list as now.
4. **hle_OSUnlink**: unlink from the list, nothing else (the fixed image stays until the next load overwrites it).
5. `loader.c`: no REL is linked at boot any more (Riders linked `_Main.rel` at boot); RELs are copied from the
   disc to their bases once, at startup or on first OSLink.
6. Risk: the game's heap buffer still holds an unlinked copy; anything that reads REL data through the header's
   section table instead of the code would see that copy. Watch for it on the first stage load.
