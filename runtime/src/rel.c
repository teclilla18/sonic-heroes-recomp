/* OSLink / OSLinkFixed / OSUnlink. The game reads a REL into a buffer from its heap and links it there;
 * the recompiled module code instead lives at the fixed base it was translated for (g_rel_modules,
 * tools/recomp/gcrecomp.py), first linked at boot by loader.c. So linking relinks that fixed image fresh
 * (code, .data, cleared bss: a stage expects pristine data every time it loads), finishes the game's header
 * the way Link would (prolog, epilog, unresolved become absolute addresses: here, those of the fixed image)
 * and reports success. The game then calls module->prolog, which reaches the recompiled code.
 * Not done: the OS module list (__OSModuleList); only debuggers read it. */
#include <string.h>

#include "recomp_table.h"
#include "runtime.h"
#include "settings.h"

static const RecompModule* g_linked_mod;  /* the module OSLink last linked (for the log) */
/* Sonic Heroes: the module id of the stage REL (stageNND) that is linked, 0 when none. The wide screen
 * HUD goes to the screen edges while a stage is in (gx_render.c); Riders' modules have no such names. */
static volatile uint32_t g_stage_id;

int rel_stage_active(void) { return g_stage_id != 0; }

/* the game's header -> our module: same ID, fixSize (+0x48) and bss size (+0x20). Heroes' stale
 * stage00D shares ID 3 with stage01D but has other sizes, so it is refused here. */
static const RecompModule* find_module(uint32_t m) {
    uint32_t id = ld32(m + 0x00), version = ld32(m + 0x1C), bss_size = ld32(m + 0x20);
    uint32_t fix_size = version >= 3 ? ld32(m + 0x48) : 0;
    for (unsigned i = 0; i < g_rel_module_count; i++) {
        const RecompModule* r = &g_rel_modules[i];
        if (r->id == id && r->bss_size == bss_size && (!fix_size || r->fix_size == fix_size)) return r;
    }
    rt_fatal("OSLink of a module that was not recompiled (id %u, version %u, bss %X, fixSize %X at %08X)", id,
             version, bss_size, fix_size, m);
    return 0;
}

void hle_OSLink(Cpu* c) {
    uint32_t m = c->r[3], bss = c->r[4];
    const RecompModule* r = find_module(m);
    rel_link_module(r);
    st32(m + 0x34, r->prolog);
    st32(m + 0x38, r->epilog);
    st32(m + 0x3C, r->unresolved);
    uint32_t vi_field_count(void);
    rt_log("[rel] field %u: OSLink(%08X, bss %08X): %s (id %u) runs from its fixed image at %08X (prolog %08X)",
           vi_field_count(), m, bss, r->name, r->id, r->base, r->prolog);
    g_linked_mod = r;
    if (!strncmp(r->name, "stage", 5)) {
        g_stage_id = r->id;
        settings_hold_view(1);  /* a screen change during the stage applies after it (settings.c) */
    }
    if (!strcmp(r->name, "_Main")) game_mods_linked();  /* Sonic Riders' gameplay options; Heroes has none yet */
    c->r[3] = 1;
}

/* nothing to undo: the fixed image stays until the next OSLink relinks it. The game has already called
 * the module's epilog. */
void hle_OSUnlink(Cpu* c) {
    uint32_t m = c->r[3];
    if (g_stage_id && ld32(m + 0x00) == g_stage_id) {
        g_stage_id = 0;
        settings_hold_view(0);
    }
    rt_log("[rel] OSUnlink(%08X): module %u%s%s", m, ld32(m + 0x00), g_linked_mod ? ", last linked " : "",
           g_linked_mod ? g_linked_mod->name : "");
    c->r[3] = 1;
}
