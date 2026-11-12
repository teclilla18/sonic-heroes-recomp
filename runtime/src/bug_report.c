/* "Save a bug report" (settings menu, About): one stored (uncompressed) zip with what a report needs, so no
 * library is needed. Shared by the PC (platform_host.c) and the Switch (platform_switch.c); each platform picks
 * the folder, the file list and its own system information. Android has its own crash reports
 * (CrashReport.java). */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "runtime.h"

static uint32_t zip_crc(const uint8_t* p, size_t n) {
    uint32_t c = 0xFFFFFFFFu;
    for (size_t i = 0; i < n; i++) {
        c ^= p[i];
        for (int k = 0; k < 8; k++) c = (c >> 1) ^ (0xEDB88320u & (0u - (c & 1)));
    }
    return ~c;
}
static void put16(FILE* f, unsigned v) { fputc(v & 0xFF, f); fputc((v >> 8) & 0xFF, f); }
static void put32(FILE* f, uint32_t v) { put16(f, v & 0xFFFF); put16(f, v >> 16); }
static uint8_t* slurp(const char* path, size_t* n) {
    FILE* f = fopen(path, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (len < 0 || len > 64L * 1024 * 1024) { fclose(f); return NULL; }
    uint8_t* b = malloc((size_t)len + 1);
    *n = b ? fread(b, 1, (size_t)len, f) : 0;
    fclose(f);
    return b;
}

/* Writes zip_path holding info.txt (the text `info`) and every file of `files` that exists (missing files are
 * skipped). A name is relative to `dir` ("" or ending in '/') and stored as it is, unless it is an absolute path
 * (holds ':', e.g. "sdmc:/atmosphere/..."): that one is read as given and stored by its last part. Returns the
 * number of files stored, or -1. */
int bug_report_zip(const char* zip_path, const char* dir, const char* info, const char* const* files, int nfiles) {
    fflush(stderr);  /* the log is stderr: this run's lines up to now */
    FILE* z = fopen(zip_path, "wb");
    if (!z) return -1;
    struct { const char* name; uint32_t crc, size, off; } ent[32];
    int ne = 0;
    for (int i = -1; i < nfiles && ne < 32; i++) {
        const char* name = i < 0 ? "info.txt" : files[i];
        size_t len = 0;
        uint8_t* data;
        if (i < 0) {
            data = (uint8_t*)info, len = strlen(info);
        } else {
            char path[512];
            snprintf(path, sizeof path, "%s%s", strchr(name, ':') ? "" : dir, name);
            data = slurp(path, &len);
            if (strchr(name, ':') && strrchr(name, '/')) name = strrchr(name, '/') + 1;
        }
        if (!data) continue;
        uint32_t crc = zip_crc(data, len), off = (uint32_t)ftell(z);
        size_t nl = strlen(name);
        put32(z, 0x04034b50); put16(z, 10); put16(z, 0); put16(z, 0); put16(z, 0); put16(z, 0x21);
        put32(z, crc); put32(z, (uint32_t)len); put32(z, (uint32_t)len); put16(z, (unsigned)nl); put16(z, 0);
        fwrite(name, 1, nl, z);
        fwrite(data, 1, len, z);
        if (i >= 0) free(data);
        ent[ne].name = name, ent[ne].crc = crc, ent[ne].size = (uint32_t)len, ent[ne].off = off, ne++;
    }
    uint32_t cd = (uint32_t)ftell(z);
    for (int i = 0; i < ne; i++) {
        size_t nl = strlen(ent[i].name);
        put32(z, 0x02014b50); put16(z, 20); put16(z, 10); put16(z, 0); put16(z, 0); put16(z, 0); put16(z, 0x21);
        put32(z, ent[i].crc); put32(z, ent[i].size); put32(z, ent[i].size); put16(z, (unsigned)nl);
        put16(z, 0); put16(z, 0); put16(z, 0); put16(z, 0); put32(z, 0); put32(z, ent[i].off);
        fwrite(ent[i].name, 1, nl, z);
    }
    uint32_t cdlen = (uint32_t)ftell(z) - cd;
    put32(z, 0x06054b50); put16(z, 0); put16(z, 0); put16(z, (unsigned)ne); put16(z, (unsigned)ne);
    put32(z, cdlen); put32(z, cd); put16(z, 0);
    int bad = ferror(z);
    if (fclose(z) || bad) return -1;
    rt_log("[report] saved %s (%d files)", zip_path, ne);
    return ne;
}
