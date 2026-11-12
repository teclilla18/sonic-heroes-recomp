# Stage selection (game manager, story tables, debug stage select) — G9SE8P rev 0

Found 2026-11-12 by static reading of dtk's asm (tools/showfn.py) plus 28 existing PC RAM dumps
(`build/run1/*/ramfield_*.bin`, Team Sonic story, Seaside Hill). No poke test yet.

## Global game state

- `0x8042C180` (sda) = pointer to the game state struct, allocated at boot (ctor `fn_8001F5A0`, defaults copied
  from `0x802412C0` / `0x802412EC`). Value `0x80452C20` in every PC dump [confirmed, 28 dumps from several runs].
- Setter `fn_8001F4E8(state, field, value)` [confirmed]: field < 0x2C stores a byte at state+field; 0x2C..0x32
  stores a word at state + field*4 - 0x88. So field 0x30 = word +0x38, field 0x31 = word +0x3C.
- state+0x38 = top-level mode read by the main loop `fn_80015F14` [confirmed]: 0/1 front end (task
  `0x80303EC8`), 2 game manager (`0x8029C310`), 3 debug stage select (`0x8042C458`), 5 task `0x803EC340`.
  Task table `0x80253068` holds those four objects. The loop re-reads +0x38 only when the running task's exec
  returns nonzero; after the debug select it takes +0x3C as the next mode. Dumps in Seaside Hill: +0x38 = 2.

## Game manager `0x8029C310` (vtable `0x80240E2C`, exec `fn_8001B120`)

- +0x0C state (0..0x11, jump table `0x80240E64`), +0x28 index into the sequence, +0x2C current stage key,
  +0x30 pointer to the key -> stage-descriptor table (heap), +0x34 current descriptor (descriptor +0x04 = stage
  number), +0x3C s32[64] stage-key sequence (0 ends it), +0x23C s32[4] player teams (-1 = none), +0x284 REL handle.
  Dumps in Seaside Hill: key 2, stage number 1, sequence 2,3,16,4,5,17,6,7.. (Team Sonic), teams 0,-1,-1,-1
  [confirmed].
- Helpers [confirmed]: `fn_8001938C` clears the sequence; `fn_8001936C(gm, i, key)` sets seq[i] (i < 64,
  key < 0x3E); `fn_8001934C(gm, i, team)` sets +0x23C[i]; `fn_800191F8(gm, a, b)` sets play-mode bytes.
- Stage numbers 40..49 and 80..89 take a special path in `fn_8001B120` (checks at 8001B2E8 / 8001B710).

## Stage keys (what the sequence holds) [confirmed: name table `0x80254B10`, REL table `0x80240B10`]

Key = index in the name table; the REL table `0x80240B10` maps key -> module name (`stageNN`, strings at
`0x8042AE20..`). Stage number = the suffix of the name.

| key | name (stage number) | REL |
|---|---|---|
| 1 | PRACTICE_00 | stage00 (stale) |
| 2..15 | action stages 01..14 (OCEAN 01/02, HOTPLANT 03/04, CASINO 05/06, TRAIN 07/08, BIGPLANT 09/10, GHOST 11/12, SKYEGG 13, SKYEGG2 14) | pairs: stage01,03,05,07,09,11,13 |
| 16..24 | bosses 20..28 (EGGHAWK 20, VSCHARA1ST 21, ZAKORUSH 22, EGGALBATROSS 23, TEAMBATTLE2 24, ZAKORUSH 25, KINGPAWN 26, LASTBOSS1ST 27, LASTBOSS2ND 28) | 01,03,05,07,09,11,26,27,28 |
| 25 | TUTORIALSTAGE_29 | stage01 |
| 26..28 | BOUNUSSTAGE_31..33 | stage31, 32, 33 |
| 29..35 | SPECIALSTAGE_40..46 | stage40 |
| 36 | ACTIONSTAGE_TRAIN_50 (Team Chaotix's stage 8 slot) | stage07 |
| 37..51 | BATTLE2P_* 60..74 (2P arenas) | various |
| 52..61 | BOUNUSSTAGE_80..89 | stage40 |

Player-facing names (community order, [likely]): 13 Egg Fleet, 14 Final Fortress, 26 Egg Emperor,
27 Metal Madness, 28 Metal Overlord. What 31..33 and 40..46 / 80..89 are in-game (2P bobsled/bonus, emerald vs
bonus challenge) is [uncertain].

## Story tables `0x8028CA48` [confirmed]

5 x {pointer, count}: Sonic `0x8028C448` (27), Dark `0x8028C58C` (27), Rose `0x8028C6D0` (28), Chaotix
`0x8028C820` (27), Last `0x8028C964` (8). Entries are 12 bytes {id, type, value}: type 0 = stage key, 1 = event,
2 = end. `fn_80138C78(obj, team)` (story start from the menu, advertiseD) and `fn_80138A9C(obj)` (start at a
chosen entry) clear the sequence, set the team, then copy the type-0 values from the start entry on.
Team Sonic entry 1 = {1, 0, 2} (Seaside Hill), its value word at `0x8028C45C`.

## Debug stage select (left in the game)

- Task object `0x8042C458` (vtable `0x80254C5C`: init `fn_800C8C5C`, exec `fn_800C8B38`, dtor `fn_800C8C28`),
  run when state+0x38 = 3. Draw `fn_800C85D4` ("A: Push Stage", "B: Pop Stage", "T_L/T_R: team"), input
  `fn_800C7E34`. Data `0x80304580`: +0 cursor key, +4 count, +8 key stack[64], +0x108 teams [likely].
  START copies the stack into the manager's sequence, sets the teams, sets state+0x3C = 2 and ends [confirmed
  static]. Not reached by any normal path found; entering it needs +0x38 = 3 at a task boundary [uncertain].
