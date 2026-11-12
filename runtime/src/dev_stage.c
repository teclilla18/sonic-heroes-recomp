/* Sonic Heroes only (developer testing): "Story starts at" a chosen stage.
 *
 * The story menu fills the game manager's stage list (0x8029C310 +0x3C) from each team's story table
 * (pointer/count pairs at 0x8028CA48; 12-byte entries {id, type, value}; type 0 = a stage key) as a story
 * starts (docs/notes/re/stage-select.md). With a stage chosen, every stage entry of every team's table
 * holds that key, so a new or continued story of any team goes straight to it (and after it, to it again).
 * Off puts the original keys back. A story already running has copied its keys into the manager's sequence
 * (+0x3C s32[64], 0 ends it; +0x23C team of player 1), so a change rewrites that too: a stage key everywhere,
 * or for Off the team's own keys (the sequence is the tail of the team's stage entries). Shown in the menu (Gameplay tab) only in builds
 * configured with --dev-menu and run with SR_DEVMENU=1 (never in releases);
 * SR_DEVSTAGE=<hex key> chooses one from the start (test runs). Not saved. */
#include <stdlib.h>

#include "runtime.h"

#define STORY_TABLES 0x8028CA48u
#define STORY_TEAMS 4
#define MAX_ENTRIES 64
#define GAME_MANAGER 0x8029C310u
#define GM_SEQUENCE (GAME_MANAGER + 0x3C)
#define GM_TEAM0 (GAME_MANAGER + 0x23C)

static int g_dev_key = -1;  /* -1: not read from SR_DEVSTAGE yet; 0: off */
static int g_applied;       /* the key now written (0: originals) */
static uint32_t g_orig[STORY_TEAMS][MAX_ENTRIES];
static int g_saved;

static int table(int team, uint32_t* ptr) {
    uint32_t p = ld32(STORY_TABLES + 8u * team), n = ld32(STORY_TABLES + 8u * team + 4);
    if (p < 0x80000000u || p >= 0x81800000u || n > MAX_ENTRIES) return 0;
    *ptr = p;
    return (int)n;
}

static void write_keys(int key) {
    for (int t = 0; t < STORY_TEAMS; t++) {
        uint32_t p;
        int n = table(t, &p);
        for (int i = 0; i < n; i++) {
            uint32_t e = p + 12u * i;
            if (ld32(e + 4) != 0) continue;  /* not a stage entry */
            if (!g_saved) g_orig[t][i] = ld32(e + 8);
            st32(e + 8, key ? (uint32_t)key : g_orig[t][i]);
        }
    }
    g_saved = 1;
}

/* the running story's sequence (see the top) */
static void write_sequence(int key) {
    int len = 0;
    while (len < 64 && ld32(GM_SEQUENCE + 4u * len)) len++;
    if (!len) return;
    if (key) {
        for (int i = 0; i < len; i++) st32(GM_SEQUENCE + 4u * i, (uint32_t)key);
        return;
    }
    int team = (int)ld32(GM_TEAM0);
    uint32_t p;
    int n = team >= 0 && team < STORY_TEAMS ? table(team, &p) : 0;
    uint32_t keys[MAX_ENTRIES];
    int nk = 0;
    for (int i = 0; i < n; i++)
        if (ld32(p + 12u * i + 4) == 0) keys[nk++] = g_orig[team][i];
    if (nk < len) return;
    for (int i = 0; i < len; i++) st32(GM_SEQUENCE + 4u * i, keys[nk - len + i]);
    rt_log("[dev] the running story (team %d) has its own %d stages back", team, len);
}

int dev_stage_get(void) { return g_dev_key > 0 ? g_dev_key : 0; }
void dev_stage_set(int key) {
    g_dev_key = key;
    rt_log("[dev] story starts at stage key %02X%s", key, key ? "" : " (off: the game's own order)");
}

/* once a presented frame (game_mods.c): the tables are main.dol data, in place from boot */
void dev_stage_frame(void) {
    if (g_dev_key < 0) {
        const char* e = getenv("SR_DEVSTAGE");
        g_dev_key = e ? (int)strtol(e, NULL, 16) : 0;
        if (g_dev_key) rt_log("[dev] SR_DEVSTAGE: story starts at stage key %02X", g_dev_key);
    }
    if (g_dev_key == g_applied) return;
    if (!g_saved && !g_dev_key) return;
    write_keys(g_dev_key);
    write_sequence(g_dev_key);
    g_applied = g_dev_key;
}
