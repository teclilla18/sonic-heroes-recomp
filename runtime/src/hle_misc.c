/* Small native replacements shared by several SDK functions (config/G9SE8P/hle.txt). */
#include <string.h>

#include "recomp_table.h"
#include "runtime.h"

/* the game's own code behind an hle.txt entry, found by its NAME (no game addresses in the runtime) */
PpcFunc hle_orig(const char* name) {
    for (unsigned i = 0; i < g_recomp_hle_count; i++)
        if (!strcmp(g_recomp_hle[i].name, name)) return g_recomp_hle[i].orig;
    rt_fatal("hle.txt has no entry named %s", name);
    return 0;
}

/* hardware set-up/tear-down that has nothing to do natively; returns 0 */
void hle_nop(Cpu* c) { c->r[3] = 0; }

/* The SDK's memcpy (overlap-safe, byte at a time), memset and memmove. Natively when both ranges
 * lie inside MEM1 or the locked cache; anything else (hardware registers, odd addresses) runs the
 * game's own code. Only r3 (the destination) is meaningful on return. */

static int plain_range(uint32_t ea, uint32_t n) {
    uint32_t pa = ea & PPC_PHYS_MASK;
    if (PPC_IS_MMIO(ea)) return 0;
    if (pa < 0x01800000u) return n <= 0x01800000u - pa;
    if (pa >= 0x20000000u && pa < 0x20004000u) return n <= 0x20004000u - pa;
    return 0;
}

static void hle_move(Cpu* c, void (*orig)(Cpu*)) {
    uint32_t d = c->r[3], s = c->r[4], n = c->r[5];
    if (!plain_range(d, n) || !plain_range(s, n)) { orig(c); return; }
    memmove(ppc_ptr(d), ppc_ptr(s), n);
}
void hle_memcpy(Cpu* c) {
    static PpcFunc orig;
    if (!orig) orig = hle_orig("memcpy");
    hle_move(c, orig);
}
void hle_memmove(Cpu* c) {
    static PpcFunc orig;
    if (!orig) orig = hle_orig("memmove");
    hle_move(c, orig);
}

void hle_memset(Cpu* c) {
    uint32_t d = c->r[3], n = c->r[5];
    static PpcFunc orig;
    if (!plain_range(d, n)) {
        if (!orig) orig = hle_orig("memset");
        orig(c);
        return;
    }
    memset(ppc_ptr(d), (int)(c->r[4] & 0xFF), n);
}
