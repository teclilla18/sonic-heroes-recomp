# RenderWare GCN driver: raster lock and draw-sync tokens — G9SE8P rev 0

Found 2026-11-12 by static reading of dtk's asm (tools/showfn.py). No runtime check yet.

## Device function table

- `lbl_8023C8F0` (rodata) is the driver's {RwStandardFunc id, handler} table [confirmed: ids match RW's
  rwSTANDARD* enum]. Notable: 0x04 RasterCreate `fn_801AEE38`, 0x05 RasterDestroy `fn_801AF1D8`,
  0x07 RasterSetImage `fn_801AAD2C`, 0x0D RasterClearRect `fn_801B1588`, 0x0E RasterClear `fn_801B15AC`
  (both -> `fn_801B11A4`, which locks the current context raster `lbl_8042CA58`), **0x0F RasterLock
  `fn_801ADE4C`**, 0x10 RasterUnlock `fn_801AE2A4`, 0x17/0x18 Lock/UnlockPalette `fn_801AE458`/`fn_801AE528`.
- `lbl_8042C9A4` = RwEngineInstance (RwGlobals); stdFunc[] starts at +0x48 (RasterLock at +0x84) [confirmed:
  only `fn_801A1AC8` loads +0x84 from it]. Memory funcs: +0x134 malloc, +0x138 free [likely].
- `fn_801A1AC8` = RwRasterLock(raster, level, lockMode) [confirmed]; builds flags = mode | level<<8.

## fn_801ADE4C = RasterLock handler (_rwGameCubeRasterLock) [confirmed]

- Args: r3 = void** pixels out, r4 = RwRaster* (kept in r28), r5 = flags (r23). r27 = raster->parentRaster
  (+0x00); **r26 = raster + `lbl_8042CA48`** = the driver's per-raster plugin extension (GCN raster ext).
- Accepts raster types (raster+0x20 & 7) 0 normal, 4 texture, 5 camera-texture [confirmed].
- Flags (RW names): 0x1 WRITE, 0x2 READ (untile into a temp buffer `ext+0x28`, malloc'ed via RwEngine +0x134;
  sized from width/height/bpp, not a ring), 0x4 NOFETCH, 0x8 RAW (pointer straight into the texture data
  `ext+0x1C` + mip offset). Sets raster privateFlags (+0x22) 0x02 read / 0x04 write / 0x20 raw.
- Raster ext fields used: +0x1C texture data base, +0x24 locked pointer, +0x28 temp buffer, **+0x30 u16 draw-sync
  token of the last draw that used this raster**, +0x33 locked mip level.

## The wait at 801AE1D0..801AE22C (write locks only)

- Token counter `lbl_8042BE88` (u16, wraps modulo 0xE000) = the token that the next GXSetDrawSync will carry.
  The texture-bind path `fn_801B1D0C` stamps `ext+0x30 = lbl_8042BE88` every time a raster is set for drawing.
- On a WRITE lock: if `ext+0x30 == lbl_8042BE88` (raster used since the last token was issued), it issues
  GXSetDrawSync(counter) (`fn_801F370C`) at the end of the FIFO and bumps the counter; then it spins on
  `fn_801B2894` until the token has passed [confirmed].
- `fn_801B2894(tok)` = "token passed?": reads GXReadDrawSync (`fn_801F37C0`) into `lbl_8042CA68`; a value
  >= 0xE000 counts as not passed; otherwise passed unless tok lies in (gpToken, counter] (wrap aware).
- So the wait = "GP has finished every draw that may sample this texture". If the raster was drawn this frame,
  this is a full drain of everything queued so far. No ring/arena, no size constant: enlarging anything won't
  help. Other token issuers of the same counter: 0x8015C0xx, 0x8015D0xx, 0x801ACD3C..0x801AD004 (not analysed).

## Who write-locks (candidates, per-frame one not identified) [uncertain]

- RW-internal: RasterSetImage `fn_801AAD2C` (0x5), `fn_801A3BD8`/`fn_801A41D4` (from image conversion
  `fn_801A509C`), `fn_801AB144` (0x9, from `fn_801AB834` <- game `fn_8005FAE8`), `fn_801AF368` (0x9),
  raster clear `fn_801B11A4` (0x9 / 0x3).
- Game: `fn_800B7C88` (0x9, 0xB), `fn_800BE2E8` (0xA), `fn_800BE56C` (0x9), `fn_800BEEF0`/`fn_800BF794` (0xB),
  `fn_8012F3D0` (0x3); reached from `fn_80019F80`/`fn_8001C484` (a big state switch) — look like loaders.

## The per-frame write locks in a stage (2026-11-12, static reading + PC lock counts from the caller)

PC Seaside Hill run: 7 write locks/frame = all 7 token waits; 6 EFB->texture copies/frame (= 2 per shadow x 3).

### Character shadow textures: fn_800B7BDC / fn_800B7C88 [confirmed static; "3 = team members" likely]

- `fn_800B7BDC` (called from the frame loop `fn_80019034` at 8001A178, right before `fn_800BEEF0` and before the
  main camera `lbl_8042C1F8` is cleared / begun for the new frame) walks the 8-slot request table
  `lbl_80253A34`, calls `fn_800B7C88(req)` for each non-null slot and clears it. Shadow camera = `lbl_8042C3AC`
  (+0x60 frame buffer, +0x64 z raster `lbl_8042C3BC`); scratch texture raster `lbl_8042C3B8` (128x128).
- Requests are queued by `fn_800B80E8(req)` (slot index req+0x00, kind req+0x01): stores req into the table,
  `RwTextureSetRaster` (`fn_801A45A0`) of texture `lbl_80304000[kind]` to req+0x20, and RwFrameTransform
  (`fn_8019ECCC`) of frame `lbl_802539C4[kind]` from req+0x2C. Callers: `fn_8006B908`, `fn_80076560`,
  `fn_800813F4` (three call sites each) [likely: per-character draw code; 3 active slots = 3 team members].
- `fn_800B7C88(req)` [confirmed]: camera fb = req+0x20, **RwRasterLock(req+0x20, 0, 0x9) at 800B7CE4: return value
  discarded** (r3 reloaded at once); paints the clumps req+0x30/+0x34 with a flat material colour
  `lbl_80253A64` (set by `fn_800B7B04` as 1 - shadow colour; default 0.3,0.3,0.23) via
  RpClumpForAllAtomics `fn_8014FFBC` / material callback `fn_8005DB40`; clears once per frame
  (`lbl_8042C3C0` flag, RwCameraClear `fn_8019CF28` mode 3); BeginUpdate, render, EndUpdate.
  Then **RwRasterLock(`lbl_8042C3B8`, 0, 0xB) at 800B7E70: return value discarded**; EFB -> `lbl_8042C3B8`
  copy (`fn_801AD1B8`); Im2D tristrip quad (`fn_801942C0`, 4 verts, screen 2..126, UV 0.05..0.95, white,
  blend ONE/ONE, clamp, bilinear) textured with `lbl_8042C3B8` = additive slightly-enlarged re-draw (soft
  edge); unlock `lbl_8042C3B8`; clear + EFB -> req+0x20 copy; unlock req+0x20 (`fn_801A16A0` = RwRasterUnlock).
- Alternate path (if `fn_80018EA8(lbl_8029C310)`): only the EFB -> req+0x20 copy [uncertain what the test is].
- `fn_801AD1B8(raster, ?)` = EFB-to-raster copy: GXSetTexCopySrc `fn_801F3F50`, GXSetTexCopyDst `fn_801F4000`,
  GXSetCopyFilter `fn_801F4528`, GXCopyTex `fn_801F48AC` (clear flag `lbl_8042C9D0`, set by `fn_801AD5D0`),
  GXPixModeSync `fn_801F384C` [likely: by size/order vs the SDK]. `fn_800A7614` restores the render-mode
  copy filter.
- The CPU never touches the pixels of either raster: both locks are only "GP done sampling it" barriers before
  an EFB copy overwrites it. RAW skips the untile/retile; with READ on a type-5 raster the lock only does a
  DCFlushRange. Unlock with write: DCFlushRange + `fn_801F5AD0` (GXInvalidateTexAll, likely).
- What they wait for: 800B7CE8 = last frame's world draws that projected req+0x20; 800B7E74 = the previous
  shadow's Im2D quad in this frame (an intra-frame drain of the shadow pass), the first one last frame's.

### Indirect-texture offset maps: fn_800BEEF0 (TEffIndirectCtrl) [confirmed static]

- Called from 8001A17C each frame. Walks the 8-entry list `lbl_80304268`; for each object with +0x3C set it
  RwRasterLock(*(obj+0x34), 0, 0xB) at 800BEF8C and **keeps the pointer** at obj+0x28; advances scroll phases
  obj+0x58/+0x5C (wrapped), then calls a per-type member function (type = *(obj+0x30)+0, table `lbl_80253D20`,
  filled by `fn_800BFA80`): `fn_800BEA18`, `fn_800BEC5C`, `fn_800BEA8C`. Each memcpy's 0x1000 bytes (64x64
  8-bit) from a base image obj+0x2C into the locked texture, then warps it (e.g. `fn_800BF1C8`). Unlock, clear +0x3C.
  Strings nearby: "TEffIndirectCtrl", "./textures/%s_indirect.txd".
- This is a real CPU write into guest RAM: the wait protects draws still queued that sample the old map.
