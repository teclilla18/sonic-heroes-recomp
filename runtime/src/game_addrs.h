/* Addresses in Sonic Heroes (G9SE8P rev 0) main.dol that the native runtime uses. SDK ones found with
 * decomp-toolkit's names + tools/sigmatch.py (2026-11-11; Riders' values were GXEE8P's, same SDK layout).
 * Low-memory globals are the Dolphin OS ABI. */
#pragma once

/* Game-state addresses not found for Heroes yet point here: past the last REL module, inside the backed
 * area (GUEST_RAM_SIZE) and never written by the game, so reads give 0 and writes go nowhere. */
#define GAME_UNKNOWN(n)     (0x827FFF00u + 4u * (n))

/* OS globals (low memory) */
#define OS_CURRENT_CONTEXT  0x800000D4u  /* OSContext* */
#define OS_CURRENT_THREAD   0x800000E4u  /* OSThread*  */
#define OS_INTERRUPT_MASK   0x800000C4u  /* __OSInterruptMask (OS) */
#define OS_USER_MASK        0x800000C8u  /* user interrupt mask */

/* OSThread.c statics */
#define OS_RUNQUEUE         0x803F23B8u  /* RunQueue; same OSThread.o bss layout as Riders (__OSThreadInit) */
#define OS_IDLE_CONTEXT     (OS_RUNQUEUE + 0x730)
#define OS_DEFAULT_THREAD   (OS_RUNQUEUE + 0x418)
#define OS_RUNQUEUE_BITS    0x8042CB98u
#define OS_RUNQUEUE_HINT    0x8042CB9Cu
#define OS_RESCHEDULE       0x8042CBA0u

/* Sonic Heroes game state (DOL bss; found 2026-11-11 by RAM dumps at VI fields, running vs paused in
 * Seaside Hill, 3 + 2 dumps): 0 while a stage runs, 1 while its pause menu is open [likely]. Next to it
 * 8029C31C went 5 -> 6 (a game state number?) [uncertain]. */
#define HEROES_PAUSED        0x8029C334u
/* the game manager's state (0x8029C310 +0x0C, docs/notes/re/stage-select.md): 5 while a stage plays, 6 while
 * paused (PC RAM dumps in Seaside Hill: 24 x 5, 4 x 6, 2026-11-12) [confirmed]; others in loads, results, saves */
#define HEROES_GM_STATE      0x8029C31Cu
#define HEROES_GM_PLAYING    5u

/* Sonic Riders' game data (GXEE8P), not found for Heroes: inert here (GAME_UNKNOWN).
 * Riders: _Main.rel: the unlock data (REL bss at the runtime's fixed 819FF380; a GameCube runs it from 805FB080,
 * where these are 806A9048 / 806A90A0). One status byte per Extreme Gear (0 locked, 1 the default gear,
 * 2 owned) and per character. The Chaos Emerald is gear 18: race code tests the player's gear
 * (player +0x1034) against 18 and 19, the two gears that run on rings. */
#define GAME_GEAR_STATUS     GAME_UNKNOWN(0)   /* Riders 0x81AAD348 */
#define GAME_GEAR_CHAOS_EMERALD 18
#define GAME_CHAR_STATUS     GAME_UNKNOWN(8)   /* Riders 0x81AAD3A0 */
#define GAME_PLAYERS         GAME_UNKNOWN(16)  /* Riders 0x81A0D740, _Main.rel bss: the 8 racers (code indexes it by i * 0x1080) */
#define GAME_PLAYER_SIZE     0x1080u
#define GAME_GEAR_TABLE      GAME_UNKNOWN(24)  /* Riders 0x819EA240, _Main.rel data: 41 Extreme Gear records of 0x1D0 bytes (game_mods.c) */

/* main.dol .sdata: the game's top-level mode. 1 on the intro, title, attract screens and menus (Player Entry
 * seen), 8 in races (demo and Free Race seen; 2026-11-03). Other modes not looked at yet. */
#define GAME_TOP_MODE        GAME_UNKNOWN(32)  /* Riders 0x8021B8C0 */
#define GAME_TOP_MODE_MENUS  1u
#define GAME_TOP_MODE_RACE   8u   /* demo and Free Race seen (notes/game-addresses.md) */
/* mode 8 is not "racing": it can stay on in menus (Player Entry seen; the user's Extras/Theater after
 * story mode). This .sdata word is 1 in every menu dumped and 0 in races, paused or not (2026-11-07,
 * RAM dumps: Free Race, pause, quit dialog vs title, Player Entry, Normal Race, Extras) [likely]. */
#define GAME_MENU_FLAG       GAME_UNKNOWN(33)  /* Riders 0x8021C1AC */
/* main.dol .bss: 0x10 before a race, 0xE during it (Free Race; 1P and 2P demo races), 0xA from the moment the
 * player crosses the finish line through the results screen; never flickered over a whole 3-lap Free Race
 * (2026-11-07, SR_RAMSAMPLE every step) [likely]. Story/Tag/Survival and 2P with one player finished: not
 * seen. Rejected: 0x8021C1B8 and the racer array at 0x801D746C (both flip for seconds during races). */
#define GAME_RACE_PHASE      GAME_UNKNOWN(34)  /* Riders 0x801DFC80 */
#define GAME_RACE_FINISHED   0xAu

/* dvd.c statics (hang dumps only) */
#define DVD_EXECUTING        0x8042CC18u  /* DVDCommandBlock* */
#define DVD_PAUSE_FLAG       0x8042CC24u
#define DVD_PAUSING_FLAG     0x8042CC28u
#define DVD_FATAL_ERROR_FLAG 0x8042CC30u
#define DVD_CURR_COMMAND     0x8042CC34u
#define DVD_RESUME_FROM_HERE 0x8042CC40u
#define DVD_DUMMY_BLOCK      0x803F2EC0u

/* functions */
#define FN_OSSaveContext                 0x801D2618u
#define FN_OSLoadContext                 0x801D2698u
#define FN_OSExitThread                  0x801D6BACu  /* matched to Riders' by sigmatch's checksum */
#define FN_DecrementerExceptionCallback  0x801D1640u
#define FN_OSReschedule                  0x801D6994u  /* __OSReschedule */

/* OSContext layout */
#define CTX_GPR   0x000
#define CTX_CR    0x080
#define CTX_LR    0x084
#define CTX_CTR   0x088
#define CTX_XER   0x08C
#define CTX_FPR   0x090
#define CTX_SRR0  0x198
#define CTX_SRR1  0x19C
#define CTX_STATE 0x1A2
#define CTX_GQR   0x1A4

#define MSR_EE 0x8000u
