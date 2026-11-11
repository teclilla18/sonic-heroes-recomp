/* Tables emitted by tools/recomp/gcrecomp.py (build/gen/table.c). */
#pragma once
#include "ppc.h"

typedef struct { uint32_t addr; PpcFunc fn; } RecompEntry;
typedef struct { uint32_t addr; const char* name; PpcFunc orig; } RecompHle;
typedef struct { uint32_t lo, hi; } RecompRange;
/* a REL module at its fixed base (gcrecomp.py Module): addresses absolute, 0 = none */
typedef struct RecompModule {
    const char* name;
    uint32_t id, fix_size, bss_size, base, bss, prolog, epilog, unresolved;
} RecompModule;

#ifdef __cplusplus
extern "C" {
#endif
extern const RecompEntry g_recomp_funcs[];
extern const unsigned g_recomp_func_count;
extern const RecompHle g_recomp_hle[];
extern const unsigned g_recomp_hle_count;
extern const uint32_t g_recomp_entry_point;
extern const RecompModule g_rel_modules[];
extern const unsigned g_rel_module_count;
extern const RecompRange g_code_ranges[];
extern const unsigned g_code_range_count;
#ifdef __cplusplus
}
#endif
